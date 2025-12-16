#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Step 3: PARALLEL Embedding - FAST VERSION!
Uses ThreadPoolExecutor to max out 500 req/min quota
"""

import json
import numpy as np
import time
from tqdm import tqdm
import sys
import os
import pickle
from concurrent.futures import ThreadPoolExecutor, as_completed
from threading import Lock

# Add parent to path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from main import VNPTAIClient

CHUNKS_FILE = "data/chunks.json"
EMBEDDINGS_FILE = "data/embeddings.npy"
CHECKPOINT_FILE = "data/embeddings_checkpoint.pkl"

# Thread-safe lock for embeddings list
embeddings_lock = Lock()

def embed_single_chunk(api_client, chunk_text, chunk_idx):
    """Embed a single chunk - thread-safe"""
    try:
        emb = api_client.get_embedding(chunk_text)
        
        if not emb or len(emb) == 0:
            # Use default dimension
            emb = [0.0] * 768
        
        return chunk_idx, emb, None
    except Exception as e:
        return chunk_idx, None, str(e)

def embed_chunks_parallel(resume_from: int = 0, max_workers: int = 50):
    """
    Embed chunks in PARALLEL using ThreadPoolExecutor
    
    With 500 req/min quota:
    - 50 workers can achieve ~400-450 req/min
    - Time: 80K chunks / 400 req/min = 200 min = 3.3 hours!
    """
    
    # Load chunks
    print("[*] Loading chunks...")
    with open(CHUNKS_FILE, 'r', encoding='utf-8') as f:
        chunks = json.load(f)
    
    total = len(chunks)
    print(f"[INFO] Total chunks to embed: {total}")
    
    # Load checkpoint if exists
    if resume_from > 0 and os.path.exists(CHECKPOINT_FILE):
        with open(CHECKPOINT_FILE, 'rb') as f:
            checkpoint = pickle.load(f)
        embeddings = checkpoint['embeddings']
        print(f"[*] Resuming from chunk {resume_from}")
    else:
        embeddings = [None] * total  # Pre-allocate
    
    # Initialize API client (will be shared across threads)
    api_client = VNPTAIClient("api-keys.json")
    
    print(f"[*] Embedding with {max_workers} parallel workers...")
    print(f"[!] Target: ~{500 * 60 / 3600:.0f} chunks/sec = ~{500} req/min")
    print(f"[!] Estimated time: {(total - resume_from) / (500 / 60):.1f} minutes = {(total - resume_from) / (500):.1f} hours")
    
    completed = resume_from
    failed = 0
    
    # Process in batches to save checkpoints
    batch_size = 1000
    
    for batch_start in range(resume_from, total, batch_size):
        batch_end = min(batch_start + batch_size, total)
        batch_chunks = chunks[batch_start:batch_end]
        
        print(f"\n[*] Processing batch {batch_start}-{batch_end}...")
        
        # Submit all chunks in batch to thread pool
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = {
                executor.submit(
                    embed_single_chunk, 
                    api_client, 
                    chunk['text'], 
                    batch_start + i
                ): i for i, chunk in enumerate(batch_chunks)
            }
            
            # Collect results with progress bar
            with tqdm(total=len(futures), desc=f"Batch {batch_start//1000}") as pbar:
                for future in as_completed(futures):
                    chunk_idx, emb, error = future.result()
                    
                    if error:
                        print(f"\n[WARN] Failed chunk {chunk_idx}: {error}")
                        emb = [0.0] * 768
                        failed += 1
                    
                    embeddings[chunk_idx] = emb
                    completed += 1
                    pbar.update(1)
        
        # Save checkpoint after each batch
        print(f"[CHECKPOINT] Saving at {batch_end}/{total}...")
        with open(CHECKPOINT_FILE, 'wb') as f:
            pickle.dump({
                'embeddings': embeddings,
                'last_index': batch_end - 1
            }, f)
    
    print(f"\n[INFO] Completed: {completed}/{total}, Failed: {failed}")
    
    # Filter out None values and convert to numpy
    embeddings_clean = [e for e in embeddings if e is not None]
    embeddings_array = np.array(embeddings_clean)
    
    # Save final
    np.save(EMBEDDINGS_FILE, embeddings_array)
    print(f"[OK] Saved {len(embeddings_clean)} embeddings to {EMBEDDINGS_FILE}")
    print(f"[INFO] Shape: {embeddings_array.shape}")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--resume', type=int, default=0, help='Resume from index')
    parser.add_argument('--workers', type=int, default=50, help='Number of parallel workers')
    args = parser.parse_args()
    
    embed_chunks_parallel(resume_from=args.resume, max_workers=args.workers)
