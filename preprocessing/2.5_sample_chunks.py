#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Sample chunks to reduce embedding time
"""

import json

print("[*] Sampling chunks to reduce size...")

# Load all chunks
with open('data/chunks.json', 'r', encoding='utf-8') as f:
    chunks = json.load(f)

print(f"[INFO] Original: {len(chunks)} chunks")

# Sample strategy: keep longer, more informative chunks
# Sort by length and keep top 80K
chunks_sorted = sorted(chunks, key=lambda x: x['length'], reverse=True)
sampled_chunks = chunks_sorted[:80000]

print(f"[INFO] Sampled: {len(sampled_chunks)} chunks")
print(f"[INFO] Avg length: {sum(c['length'] for c in sampled_chunks) / len(sampled_chunks):.0f} chars")

# Save
with open('data/chunks_sampled.json', 'w', encoding='utf-8') as f:
    json.dump(sampled_chunks, f, ensure_ascii=False, indent=2)

# Replace original
with open('data/chunks.json', 'w', encoding='utf-8') as f:
    json.dump(sampled_chunks, f, ensure_ascii=False, indent=2)

print("[OK] Sampled chunks saved")
print(f"[!] New embedding time: ~{80000 / 8 / 60:.1f} minutes (~{80000 / 8 / 60 / 60:.1f} hours)")
