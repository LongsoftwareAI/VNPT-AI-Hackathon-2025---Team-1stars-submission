# PREPROCESSING SCRIPTS

Scripts trong folder này chỉ chạy MỘT LẦN ở local để build knowledge base.
**KHÔNG submit vào Docker!**

## Workflow

```bash
# 1. Download Wikipedia (~15-30 phút)
python 1_download_wikipedia.py

# 2. Extract & chunk (~10-20 phút)
python 2_build_chunks.py

# 3. Embed chunks (~3-4 giờ, dùng VNPT API)
python 3_embed_chunks.py

# 4. Build BM25 index (~5-10 phút)
python 4_build_bm25.py

# 5. Package for Docker (~1 phút)
python 5_package_kb.py
```

## Output

```
knowledge_base/
├── knowledge_base.pkl  (chunks + BM25, ~100-200MB)
└── embeddings.npy      (vectors, ~300-500MB)
```

## Submit

Copy `knowledge_base/` folder vào Docker image.
`main.py` sẽ load knowledge base này khi inference.
