#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Step 3: Embed chunks using VNPT Embedding API - NO EMOJIS
Preprocessing script - RUN ONCE OFFLINE

This will take ~3-4 hours for 246K chunks!
Rate limit: 500 requests/minute -> ~8 req/sec
"""

import json
import numpy as np
import time
from tqdm import tqdm
import sys
import os

# Add parent to path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from main import VNPTAIClient

CHUNKS_FILE = "data/chunks.json"
EMBEDDINGS_FILE = "data/embeddings.npy"
CHECKPOINT_FILE = "data/embeddings_checkpoint.npz"

def embed_chunks(resume_from: int = 0):
    """Embed all chunks using VNPT API"""
    
    # Load chunks
    print("[*] Loading chunks...")
    with open(CHUNKS_FILE, 'r', encoding='utf-8') as f:
        chunks = json.load(f)
    
    total = len(chunks)
    print(f"[INFO] Total chunks to embed: {total}")
    
    # Load checkpoint if exists
    checkpoint_pkl = CHECKPOINT_FILE.replace('.npz', '.pkl')
    if resume_from > 0 and os.path.exists(checkpoint_pkl):
        with open(checkpoint_pkl, 'rb') as f:
            checkpoint = pickle.load(f)
        embeddings = checkpoint['embeddings']
        print(f"[*] Resuming from chunk {resume_from}")
    elif resume_from > 0 and os.path.exists(CHECKPOINT_FILE):
        checkpoint = np.load(CHECKPOINT_FILE, allow_pickle=True)
        embeddings = checkpoint['embeddings'].tolist()
        print(f"[*] Resuming from chunk {resume_from}")
    else:
        embeddings = []
    
    # Initialize API client
    api_client = VNPTAIClient("api-keys.json")
    
    # Embed chunks
    print("[*] Embedding chunks...")
    print(f"[!] Estimated time: {(total - resume_from) / 8 / 60:.1f} minutes")
    
    for i in tqdm(range(resume_from, total), initial=resume_from, total=total):
        chunk = chunks[i]
        
        # Get embedding
        emb = api_client.get_embedding(chunk['text'])
        
        # Detect embedding dimension from first successful embedding
        if len(embeddings) > 0 and emb:
            expected_dim = len(embeddings[0])
        elif emb:
            expected_dim = len(emb)
        else:
            expected_dim = 768  # Default
        
        if not emb or len(emb) == 0:
            print(f"\n[WARN] Failed to embed chunk {i}, using zero vector")
            emb = [0.0] * expected_dim
        elif len(emb) != expected_dim:
            print(f"\n[WARN] Dimension mismatch at chunk {i}: {len(emb)} vs {expected_dim}, padding/truncating")
            if len(emb) < expected_dim:
                emb = emb + [0.0] * (expected_dim - len(emb))
            else:
                emb = emb[:expected_dim]
        
        embeddings.append(emb)
        
        # Rate limit: 500/min = 8.33/sec -> sleep 0.12s
        time.sleep(0.12)
        
        # Save checkpoint every 1000 chunks
        if (i + 1) % 1000 == 0:
            # Save as pickle to avoid numpy shape issues
            with open(CHECKPOINT_FILE.replace('.npz', '.pkl'), 'wb') as f:
                pickle.dump({
                    'embeddings': embeddings,
                    'last_index': i
                }, f)
            print(f"\n[CHECKPOINT] Saved at {i + 1}/{total}")
    
    # Convert to numpy array
    embeddings_array = np.array(embeddings)
    
    # Save final
    np.save(EMBEDDINGS_FILE, embeddings_array)
    print(f"\n[OK] Saved embeddings to {EMBEDDINGS_FILE}")
    print(f"[INFO] Shape: {embeddings_array.shape}")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--resume', type=int, default=0, help='Resume from index')
    args = parser.parse_args()
    
    embed_chunks(resume_from=args.resume)
