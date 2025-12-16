#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Step 1: Download Vietnamese Wikipedia
Preprocessing script - RUN ONCE OFFLINE
"""

import os
import requests
from tqdm import tqdm

WIKI_DUMP_URL = "https://dumps.wikimedia.org/viwiki/latest/viwiki-latest-pages-articles.xml.bz2"
OUTPUT_FILE = "data/viwiki-latest-pages-articles.xml.bz2"

def download_wikipedia():
    """Download Vietnamese Wikipedia dump"""
    
    os.makedirs("data", exist_ok=True)
    
    print(f"[*] Downloading Vietnamese Wikipedia from {WIKI_DUMP_URL}")
    print(f"[!] This will take ~15-30 minutes (file size ~1-2GB)")
    
    response = requests.get(WIKI_DUMP_URL, stream=True)
    total_size = int(response.headers.get('content-length', 0))
    
    with open(OUTPUT_FILE, 'wb') as f:
        with tqdm(total=total_size, unit='B', unit_scale=True) as pbar:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
                pbar.update(len(chunk))
    
    print(f"[OK] Downloaded to {OUTPUT_FILE}")
    print(f"[INFO] File size: {os.path.getsize(OUTPUT_FILE) / 1e9:.2f} GB")

if __name__ == "__main__":
    download_wikipedia()
