#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Step 5: Package knowledge base - FIXED VERSION
"""

import json
import numpy as np
import pickle
import os

CHUNKS_FILE = "data/chunks.json"
EMBEDDINGS_FILE = "knowledge_base/embeddings.npy"
BM25_FILE = "data/bm25_index.pkl"

OUTPUT_KB = "knowledge_base/knowledge_base.pkl"
OUTPUT_EMB = "knowledge_base/embeddings.npy"

def package_knowledge_base():
    """Package all components into knowledge_base/ folder"""
    
    print("[*] Packaging knowledge base...")
    
    # Create output dir
    os.makedirs("knowledge_base", exist_ok=True)
    
    # Load chunks
    print("  -> Loading chunks...")
    with open(CHUNKS_FILE, 'r', encoding='utf-8') as f:
        chunks = json.load(f)
    
    # Load BM25
    print("  -> Loading BM25 index...")
    with open(BM25_FILE, 'rb') as f:
        bm25_data = pickle.load(f)
    
    # Load embeddings
    print("  -> Loading embeddings...")
    embeddings = np.load(EMBEDDINGS_FILE)
    
    # Verify sizes match
    assert len(chunks) == len(embeddings), f"Chunks ({len(chunks)}) and embeddings ({len(embeddings)}) mismatch!"
    assert len(chunks) == len(bm25_data['tokenized_corpus']), f"Chunks and BM25 mismatch!"
    
    print(f"[OK] All sizes match: {len(chunks)} chunks")
    
    # Package metadata + BM25
    knowledge_base = {
        'chunks': chunks,
        'bm25': bm25_data['bm25'],
        'tokenized_corpus': bm25_data['tokenized_corpus'],
        'version': '1.0',
        'source': 'Vietnamese Wikipedia',
        'num_chunks': len(chunks),
        'embedding_dim': embeddings.shape[1] if len(embeddings.shape) > 1 else len(embeddings[0])
    }
    
    # Save
    with open(OUTPUT_KB, 'wb') as f:
        pickle.dump(knowledge_base, f, protocol=pickle.HIGHEST_PROTOCOL)
    
    # Copy embeddings
    np.save(OUTPUT_EMB, embeddings)
    
    print(f"\n[OK] Packaged successfully!")
    print(f"[*] Knowledge base: {OUTPUT_KB}")
    print(f"[*] Embeddings: {OUTPUT_EMB}")
    
    # Show sizes
    kb_size = os.path.getsize(OUTPUT_KB) / 1e6
    emb_size = os.path.getsize(OUTPUT_EMB) / 1e6
    
    print(f"\n[INFO] File sizes:")
    print(f"  - KB: {kb_size:.1f} MB")
    print(f"  - Embeddings: {emb_size:.1f} MB")
    print(f"  - Total: {kb_size + emb_size:.1f} MB")
    
    print(f"\n[OK] Ready to deploy! Copy knowledge_base/ folder to Docker image.")

if __name__ == "__main__":
    package_knowledge_base()
