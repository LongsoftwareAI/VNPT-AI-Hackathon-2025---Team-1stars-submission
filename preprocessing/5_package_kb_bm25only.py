#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Package BM25-only KB (NO embeddings)
"""

import json
import pickle
import os

CHUNKS_FILE = "data/chunks.json"
BM25_FILE = "data/bm25_index.pkl"
OUTPUT_KB = "knowledge_base/knowledge_base_bm25only.pkl"

def package_bm25_only():
    """Package BM25-only KB"""
    
    print("[*] Packaging BM25-only knowledge base...")
    
    os.makedirs("knowledge_base", exist_ok=True)
    
    # Load chunks
    print("  -> Loading chunks...")
    with open(CHUNKS_FILE, 'r', encoding='utf-8') as f:
        chunks = json.load(f)
    
    # Load BM25
    print("  -> Loading BM25 index...")
    with open(BM25_FILE, 'rb') as f:
        bm25_data = pickle.load(f)
    
    print(f"[OK] Loaded {len(chunks)} chunks")
    
    # Package (NO embeddings)
    kb = {
        'chunks': chunks,
        'bm25': bm25_data['bm25'],
        'tokenized_corpus': bm25_data['tokenized_corpus'],
        'version': '1.0-bm25only',
        'num_chunks': len(chunks)
    }
    
    # Save
    with open(OUTPUT_KB, 'wb') as f:
        pickle.dump(kb, f, protocol=pickle.HIGHEST_PROTOCOL)
    
    size = os.path.getsize(OUTPUT_KB) / 1e6
    print(f"\n[OK] Packaged successfully!")
    print(f"[*] File: {OUTPUT_KB}")
    print(f"[*] Size: {size:.1f} MB")
    print(f"[*] Chunks: {len(chunks)}")
    print(f"\n[OK] Ready to test BM25-only approach!")

if __name__ == "__main__":
    package_bm25_only()
