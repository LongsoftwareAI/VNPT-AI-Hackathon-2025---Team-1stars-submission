#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Step 2: Extract and chunk Wikipedia - SIMPLIFIED VERSION
No wikiextractor needed, direct bz2 parsing
"""

import json
import bz2
import re
from tqdm import tqdm
import xml.etree.ElementTree as ET

INPUT_FILE = "data/viwiki-latest-pages-articles.xml.bz2"
CHUNKS_FILE = "data/chunks.json"

def extract_and_chunk():
    """Extract and chunk Wikipedia articles directly from bz2"""
    
    print("[*] Extracting and chunking Wikipedia articles...")
    print("[!] This may take 10-15 minutes...")
    
    chunks = []
    article_count = 0
    
    # Read compressed XML
    with bz2.open(INPUT_FILE, 'rt', encoding='utf-8') as f:
        current_text = ""
        current_title = ""
        in_text = False
        
        for line in tqdm(f, desc="Processing", unit=" lines"):
            # Simple XML parsing
            if '<title>' in line:
                current_title = line.split('<title>')[1].split('</title>')[0]
            
            elif '<text' in line:
                in_text = True
                current_text = line.split('>', 1)[1] if '>' in line else ""
            
            elif '</text>' in line:
                in_text = False
                current_text += line.split('</text>')[0]
                
                # Process article
                if current_text and len(current_text) > 200:
                    article_count += 1
                    
                    # Clean text
                    text = clean_wiki_text(current_text)
                    
                    # Chunk into paragraphs
                    paras = text.split('\n\n')
                    for para in paras:
                        para = para.strip()
                        if 100 < len(para) < 2000:
                            chunks.append({
                                'text': para,
                                'title': current_title,
                                'length': len(para)
                            })
                    
                    # Limit for faster processing (optional)
                    if article_count >= 50000:  # Process first 50K articles
                        break
                
                current_text = ""
                current_title = ""
            
            elif in_text:
                current_text += line
    
    print(f"[INFO] Processed {article_count} articles")
    print(f"[INFO] Total chunks: {len(chunks)}")
    print(f"[INFO] Avg length: {sum(c['length'] for c in chunks) / len(chunks):.0f} chars")
    
    # Save
    with open(CHUNKS_FILE, 'w', encoding='utf-8') as f:
        json.dump(chunks, f, ensure_ascii=False, indent=2)
    
    print(f"[OK] Saved {len(chunks)} chunks to {CHUNKS_FILE}")

def clean_wiki_text(text):
    """Clean Wikipedia markup"""
    # Remove wiki markup
    text = re.sub(r'\[\[File:.*?\]\]', '', text)
    text = re.sub(r'\[\[Category:.*?\]\]', '', text)
    text = re.sub(r'\{\{.*?\}\}', '', text)
    text = re.sub(r'\[\[([^\|]*?\|)?([^\]]*?)\]\]', r'\2', text)
    text = re.sub(r'==+\s*.*?\s*==+', '', text)
    text = re.sub(r"'''", '', text)
    text = re.sub(r"''", '', text)
    text = re.sub(r'<.*?>', '', text)
    
    # Clean whitespace
    text = re.sub(r'\n\n+', '\n\n', text)
    text = text.strip()
    
    return text

if __name__ == "__main__":
    extract_and_chunk()
