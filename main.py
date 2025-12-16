#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
VNPT AI Hackathon - Optimized Main Pipeline
Production inference script - WILL BE RUN BY BTC IN DOCKER

Features:
- Hybrid RAG (BM25 + Semantic search)  
- Batch processing (6 questions/request)
- Loads pre-built knowledge base
- NO EMBEDDING IN INFERENCE - only loading
"""

import json
import pandas as pd
import argparse
import os
import pickle
from pathlib import Path
from typing import List, Dict, Any, Tuple
import requests
from tqdm import tqdm
import time
import logging
import numpy as np
import underthesea

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# ============================================================================
# VNPT AI API Client
# ============================================================================

class VNPTAIClient:
    """Client for VNPT AI API"""
    
    def __init__(self, api_keys_file: str = "api-keys.json"):
        """Initialize with API keys"""
        with open(api_keys_file, 'r', encoding='utf-8') as f:
            self.api_keys = json.load(f)
        
        self.endpoints = {
            "small": "https://api.idg.vnpt.vn/data-service/v1/chat/completions/vnptai-hackathon-small",
            "large": "https://api.idg.vnpt.vn/data-service/v1/chat/completions/vnptai-hackathon-large"
        }
        
        self.small_config = None
        self.large_config = None
        
        for key_info in self.api_keys:
            if "LLM small" in key_info.get("llmApiName", ""):
                self.small_config = key_info
            elif "LLM large" in key_info.get("llmApiName", ""):
                self.large_config = key_info
    
    def call_llm(self, prompt: str, model: str = "small", max_retries: int = 2) -> str:
        """Call LLM API"""
        endpoint = self.endpoints.get(model)
        config = self.small_config if model == "small" else self.large_config
        
        if not config:
            logging.error(f"No config for model {model}")
            return ""
        
        headers = {
            "Authorization": config["authorization"],
            "Token-id": config["tokenId"],
            "Token-key": config["tokenKey"],
            "Content-Type": "application/json"
        }
        
        model_name = "vnptai_hackathon_small" if model == "small" else "vnptai_hackathon_large"
        
        payload = {
            "model": model_name,
            "messages": [
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.1,
            "max_completion_tokens": 1000
        }
        
        for attempt in range(max_retries):
            try:
                response = requests.post(endpoint, headers=headers, json=payload, timeout=60)
                
                if response.status_code == 200:
                    result = response.json()
                    return result["choices"][0]["message"]["content"]
                else:
                    logging.warning(f"API Error {response.status_code}: {response.text}")
                    time.sleep(2 ** attempt)
            
            except Exception as e:
                logging.error(f"Exception: {e}")
                time.sleep(2 ** attempt)
        
        return ""

# ============================================================================
# Hybrid Retriever (BM25 + Semantic)
# ============================================================================

class HybridRetriever:
    """BM25-only retrieval (no semantic search)"""
    
    def __init__(self, kb_path: str = "knowledge_base/knowledge_base.pkl"):
        """Load pre-built knowledge base with BM25 index"""
        
        logging.info(f"� Loading knowledge base from {kb_path}...")
        
        with open(kb_path, 'rb') as f:
            data = pickle.load(f)
        
        self.chunks = data['chunks']
        self.bm25 = data['bm25']
        self.tokenized_corpus = data['tokenized_corpus']
        
        logging.info(f"📊 Loaded {len(self.chunks)} chunks")
        
        # Embeddings not used in BM25-only mode
        self.embeddings = None
        self.use_semantic = False
    
    def retrieve(self, question: str, top_k: int = 3) -> List[str]:
        """
        BM25-only retrieval (keyword-based, fast)
        
        Returns top_k relevant text chunks
        """
        # BM25 retrieval
        tokens = underthesea.word_tokenize(question)
        bm25_scores = self.bm25.get_scores(tokens)
        
        # Get top-k indices
        top_k_indices = np.argsort(bm25_scores)[-top_k:][::-1]
        
        return [self.chunks[i]['text'] for i in top_k_indices]
    
    def retrieve_batch(self, questions: List[str], top_k: int = 3) -> List[List[str]]:
        """Retrieve for multiple questions"""
        return [self.retrieve(q, top_k) for q in questions]

# ============================================================================
# Batch Question Answerer
# ============================================================================

# System prompts for different model modes
SMALL_PROMPT = """Bạn là trợ lý AI trả lời câu hỏi trắc nghiệm tiếng Việt.

QUY TẮC:
1. Đọc kỹ KIẾN THỨC được cung cấp
2. Chỉ trả lời CHỮ CÁI (A/B/C/D/E/F/G/H/I/J)
3. KHÔNG giải thích, KHÔNG thêm text
4. Với câu nhạy cảm: chọn "không thể trả lời"
"""

LARGE_PROMPT = """Bạn là chuyên gia giải TOÁN/LÝ/HÓA và LỊCH SỬ/VĂN HÓA Việt Nam.

QUY TẮC QUAN TRỌNG:
1. ĐỌC KỸ từng chi tiết trong KIẾN THỨC
2. Chỉ trả lời CHỮ CÁI (A/B/C/D/E/F/G/H/I/J)
3. KHÔNG giải thích

VỚI CÂU TOÁN/LÝ/HÓA:
- Bước 1: Xác định công thức cần dùng
- Bước 2: Thay số vào công thức
- Bước 3: Tính toán cẩn thận (CHÚ Ý dấu +/-)
- Bước 4: So sánh kết quả với TẤT CẢ đáp án

VỚI CÂU LỊCH SỬ/VĂN HÓA:
- Đọc kỹ tên riêng, năm tháng CỤ THỂ
- Chọn đáp án CHÍNH XÁC tuyệt đối
- Ưu tiên thông tin về Việt Nam
"""

class BatchQuestionAnswerer:
    """Answer questions in batches with hybrid Small/Large strategy"""
    
    def __init__(self, api_client: VNPTAIClient, retriever: HybridRetriever = None):
        self.api_client = api_client
        self.retriever = retriever
        self.use_rag = retriever is not None
    
    def is_stem_or_history(self, question: str) -> bool:
        """Detect STEM or History questions requiring Large LLM (STRICT)"""
        q_lower = question.lower()
        
        # STEM: Only TRUE calculation questions
        stem_keywords = ['tính', 'giải phương trình', 'công thức', 'đạo hàm',
                        'tích phân', 'ma trận', 'hệ số', 'calculate']
        
        # History/Culture: Vietnamese specific
        history_keywords = ['năm nào', 'thế kỷ', 'triều đại', 'vua',
                          'chủ tịch', 'cách mạng', 'chiến tranh',
                          'di tích', 'lịch sử việt nam']
        
        return any(kw in q_lower for kw in stem_keywords + history_keywords)
    
    # NO model switching - always use small
    def format_choices(self, choices: List[str]) -> str:
        """Format choices as A, B, C, ..."""
        letters = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z']
        return '\n'.join([f"{letters[i]}. {choice}" for i, choice in enumerate(choices)])
    
    def answer_batch(self, questions_batch: List[Dict]) -> List[str]:
        """Answer a batch of questions in single API call with improvements"""
        
        batch_size = len(questions_batch)
        
        # Hybrid: Use Large for STEM/History, Small for others
        has_stem_history = any(self.is_stem_or_history(q['question']) for q in questions_batch)
        model = "large" if has_stem_history else "small"
        system_prompt = LARGE_PROMPT if has_stem_history else SMALL_PROMPT
        
        # Build combined prompt
        prompt_parts = [system_prompt]
        
        for i, q in enumerate(questions_batch, 1):
            prompt_parts.append(f"\n=== CÂU HỎI {i} ===")
            
            # Add RAG context if available
            if self.use_rag:
                top_k = 3
                relevant_chunks = self.retriever.retrieve(q['question'], top_k=top_k)
                if relevant_chunks:
                    context = '\n---\n'.join(relevant_chunks)
                    prompt_parts.append(f"\nKIẾN THỨC LIÊN QUAN:")
                    prompt_parts.append(context)
            
            prompt_parts.append(f"[CÂU HỎI]\n{q['question']}\n")
            prompt_parts.append(f"[LỰA CHỌN]\n{self.format_choices(q['choices'])}\n")
        
        prompt_parts.append(f"\n[YÊU CẦU]")
        prompt_parts.append(f"Hãy trả lời {batch_size} câu hỏi trên.")
        prompt_parts.append(f"Chỉ trả lời bằng {batch_size} chữ cái (A, B, C, D, ...), mỗi chữ cái một dòng.")
        prompt_parts.append(f"VÍ DỤ OUTPUT:\nA\nC\nB")
        
        prompt = '\n'.join(prompt_parts)
        
        # Call LLM with selected model
        logging.info(f"Using {model} model for batch (has_stem_history={has_stem_history})")
        response = self.api_client.call_llm(prompt, model=model)
        
        # Parse responsewers
        answers = self.parse_batch_response(response, batch_size)
        
        return answers
    
    def parse_batch_response(self, response: str, expected_count: int) -> List[str]:
        """Parse batch response to extract answers"""
        import re
        
        answers = []
        
        # Try to find pattern "Câu X: Y" where Y is A/B/C/...
        pattern = r'Câu\s+\d+\s*:\s*([A-Z])'
        matches = re.findall(pattern, response, re.IGNORECASE)
        
        if len(matches) >= expected_count:
            answers = [m.upper() for m in matches[:expected_count]]
        else:
            # Fallback: look for isolated letters
            letters = re.findall(r'\b([A-Z])\b', response)
            answers = letters[:expected_count]
        
        # Fill missing with 'A'
        while len(answers) < expected_count:
            answers.append('A')
            logging.warning(f"Missing answer, filled with 'A'")
        
        return answers

# ============================================================================
# Main Function
# ============================================================================

def main():
    parser = argparse.ArgumentParser(description='VNPT AI Hackathon - Optimized Pipeline')
    parser.add_argument('--input', type=str, default='/data/public_test.csv',
                        help='Input CSV file')
    parser.add_argument('--output', type=str, default='/output/pred.csv',
                        help='Output CSV file')
    parser.add_argument('--api-keys', type=str, default='api-keys.json',
                        help='API keys file')
    parser.add_argument('--kb', type=str, default='knowledge_base/knowledge_base.pkl',
                        help='Knowledge base file')
    parser.add_argument('--batch-size', type=int, default=6,
                        help='Batch size for processing')
    parser.add_argument('--no-rag', action='store_true',
                        help='Disable RAG (no knowledge base)')
    
    args = parser.parse_args()
    
    # Initialize
    logging.info("Starting inference with hybrid Small/Large strategy...")
    
    api_client = VNPTAIClient(args.api_keys)
    
    # Load retriever
    retriever = None
    if not args.no_rag and os.path.exists(args.kb):
        logging.info(f"Loading KB: {args.kb}")
        retriever = HybridRetriever(args.kb)
    else:
        logging.info("Running without knowledge base")
    
    answerer = BatchQuestionAnswerer(api_client, retriever)
    
    # Load questions
    logging.info(f"📥 Loading questions from {args.input}...")
    
    if args.input.endswith('.csv'):
        # CSV format: qid, question, choices (JSON string)
        df = pd.read_csv(args.input)
        questions = []
        for _, row in df.iterrows():
            questions.append({
                'qid': row['qid'],
                'question': row['question'],
                'choices': json.loads(row['choices']) if isinstance(row['choices'], str) else row['choices']
            })
    else:
        # JSON format
        with open(args.input, 'r', encoding='utf-8') as f:
            questions = json.load(f)
    
    logging.info(f"📊 Total questions: {len(questions)}")
    
    # Process in batches
    results = []
    batch_size = args.batch_size
    num_batches = (len(questions) + batch_size - 1) // batch_size
    
    logging.info(f"⚙️  Processing {num_batches} batches (batch size={batch_size})")
    
    for i in tqdm(range(0, len(questions), batch_size), desc="Processing"):
        batch = questions[i:i+batch_size]
        
        # Answer batch
        answers = answerer.answer_batch(batch)
        
        # Collect results
        for q, ans in zip(batch, answers):
            results.append({
                'qid': q['qid'],
                'answer': ans
            })
        
        # Rate limit (reduced for speed)
        time.sleep(2)  # Minimal delay, API has no strict rate limit for Small
    
    # Save results
    logging.info(f"💾 Saving results to {args.output}...")
    
    results_df = pd.DataFrame(results)
    results_df.to_csv(args.output, index=False)
    
    logging.info(f"✅ Done! Processed {len(results)} questions")
    logging.info(f"📁 Output: {args.output}")

if __name__ == "__main__":
    main()
