#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Step 4: Build BM25 index - FIXED VERSION
"""

import json
import pickle
from tqdm import tqdm
import underthesea
from rank_bm25 import BM25Okapi

CHUNKS_FILE = "data/chunks.json"
BM25_FILE = "data/bm25_index.pkl"

def build_bm25_index():
    """Build BM25 index with Vietnamese tokenization"""
    
    print("[*] Loading chunks...")
    with open(CHUNKS_FILE, 'r', encoding='utf-8') as f:
        chunks = json.load(f)
    
    print(f"[INFO] Total chunks: {len(chunks)}")
    
    # Tokenize all chunks
    print("[*] Tokenizing with underthesea...")
    tokenized_corpus = []
    
    for chunk in tqdm(chunks, desc="Tokenizing"):
        tokens = underthesea.word_tokenize(chunk['text'])
        tokenized_corpus.append(tokens)
    
    # Build BM25 index
    print("[*] Building BM25 index...")
    bm25 = BM25Okapi(tokenized_corpus)
    
    # Save
    with open(BM25_FILE, 'wb') as f:
        pickle.dump({
            'bm25': bm25,
            'tokenized_corpus': tokenized_corpus
        }, f)
    
    print(f"[OK] Saved BM25 index to {BM25_FILE}")
    print(f"[INFO] Corpus size: {len(tokenized_corpus)}")

if __name__ == "__main__":
    build_bm25_index()
