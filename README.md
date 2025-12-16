# VNPT AI Hackathon - Age of AInicorns

## 🏗️ Architecture Overview

```
┌─────────────────────────────────────────────────────────┐
│  PHASE 1: PREPROCESSING (Offline, one-time)            │
│  ─────────────────────────────────────────────────────  │
│  1. Download Vietnamese Wikipedia                       │
│  2. Chunk into paragraphs                               │
│  3. Embed with VNPT API (~3.5 hours)                   │
│  4. Build BM25 index                                    │
│  5. Package → knowledge_base/                           │
└─────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────┐
│  PHASE 2: INFERENCE (Docker, BTC runs)                 │
│  ─────────────────────────────────────────────────────  │
│  main.py:                                               │
│   1. Load knowledge_base/ (pre-built)                   │
│   2. For each batch of 6 questions:                     │
│      a. BM25 search → top candidates                    │
│      b. Combine 6 Q + contexts                          │
│      c. Single LLM API call                             │
│      d. Parse 6 answers                                 │
│   3. Save to /output/pred.csv                           │
└─────────────────────────────────────────────────────────┘
```

## 📂 Project Structure

```
vnptaihakathon/
├── preprocessing/              # Offline scripts (NOT in Docker)
│   ├── 1_download_wikipedia.py
│   ├── 2_build_chunks.py
│   ├── 3_embed_chunks.py
│   ├── 4_build_bm25.py
│   ├── 5_package_kb.py
│   └── README.md
│
├── knowledge_base/             # Pre-built KB (IN Docker)
│   ├── knowledge_base.pkl      # Chunks + BM25 (~100-200MB)
│   └── embeddings.npy          # Vectors (~300-500MB)
│
├── main_optimized.py           # Production inference
├── main.py                     # (Old version)
├── requirements.txt
├── Dockerfile
├── api-keys.json
└── README.md                   # This file
```

## 🚀 Quick Start

### Step 1: Build Knowledge Base (One-time, ~4 hours)

```bash
# Run preprocessing scripts
cd preprocessing

python 1_download_wikipedia.py    # ~15-30 min
python 2_build_chunks.py           # ~10-20 min  
python 3_embed_chunks.py           # ~3-4 hours (uses VNPT API)
python 4_build_bm25.py             # ~5-10 min
python 5_package_kb.py             # ~1 min

# Output: knowledge_base/ folder created
cd ..
```

### Step 2: Test Locally

```bash
# Test with val set
python main_optimized.py \
    --input AInicorns_TheBuilder_public/data/val.json \
    --output val_pred.csv \
    --batch-size 6

# Expected: ~2 minutes for 100 questions
```

### Step 3: Build Docker

```bash
# Build
docker build -t vnpt-ai-hackathon .

# Test
docker run \
    -v $(pwd)/AInicorns_TheBuilder_public/data:/data \
    -v $(pwd)/output:/output \
    vnpt-ai-hackathon
```

### Step 4: Submit

```bash
# Push to Docker Hub
docker tag vnpt-ai-hackathon yourusername/vnpt-ai-hackathon:v1
docker push yourusername/vnpt-ai-hackathon:v1

# Submit Docker image URL + GitHub repo to BTC
```

## 📖 Cách Chạy main_optimized.py

### Cú pháp cơ bản

```bash
python main_optimized.py [OPTIONS]
```

### Các tham số (Arguments)

| Tham số | Mô tả | Giá trị mặc định |
|---------|-------|------------------|
| `--input` | File CSV chứa câu hỏi test | `/data/public_test.csv` |
| `--output` | File CSV kết quả dự đoán | `/output/pred.csv` |
| `--api-keys` | File chứa API keys | `api-keys.json` |
| `--kb` | File knowledge base đã build sẵn | `knowledge_base/knowledge_base.pkl` |
| `--batch-size` | Số câu hỏi xử lý cùng lúc | `6` |
| `--no-rag` | Tắt RAG, chỉ dùng LLM thuần | `False` |

### Ví dụ sử dụng

#### 1. Chạy với file CSV test có sẵn (cơ bản)

```bash
python main_optimized.py --input data/public_test.csv --output output/pred.csv
```

#### 2. Chạy với các tùy chọn đầy đủ

```bash
python main_optimized.py \
  --input data/public_test.csv \
  --output output/predictions.csv \
  --api-keys api-keys.json \
  --kb knowledge_base/knowledge_base.pkl \
  --batch-size 6
```

#### 3. Chạy không dùng knowledge base (LLM only)

```bash
python main_optimized.py \
  --input data/public_test.csv \
  --output output/pred_no_rag.csv \
  --no-rag
```

#### 4. Chạy với batch size khác nhau

```bash
# Batch size nhỏ = an toàn hơn nhưng chậm hơn
python main_optimized.py --input data/test.csv --output output/pred.csv --batch-size 4

# Batch size lớn = nhanh hơn nhưng có thể giảm độ chính xác
python main_optimized.py --input data/test.csv --output output/pred.csv --batch-size 8
```

#### 5. Chạy trong Docker (như BTC sẽ chạy)

```bash
# Build Docker image
docker build -t vnpt-hackathon .

# Run Docker container
docker run \
  -v $(pwd)/data:/data \
  -v $(pwd)/output:/output \
  vnpt-hackathon
```

### Định dạng file input

File CSV input phải có các cột sau:

```csv
qid,question,choices
1,"Câu hỏi 1?","[""A. Đáp án A"", ""B. Đáp án B"", ""C. Đáp án C"", ""D. Đáp án D""]"
2,"Câu hỏi 2?","[""A. Đáp án A"", ""B. Đáp án B"", ""C. Đáp án C""]"
```

- `qid`: ID của câu hỏi
- `question`: Nội dung câu hỏi
- `choices`: Mảng JSON (dạng string) chứa các lựa chọn

### Định dạng file output

File CSV output sẽ có định dạng:

```csv
qid,answer
1,A
2,C
3,B
```

### Lưu ý quan trọng

1. **Knowledge base**: File `knowledge_base/knowledge_base.pkl` phải được build trước bằng các script trong `preprocessing/`
2. **API keys**: File `api-keys.json` phải có trong thư mục gốc với đầy đủ credentials
3. **Tự động chọn model**: Script sẽ tự động chọn LLM Small/Large dựa vào loại câu hỏi:
   - **Large model**: Câu hỏi TOÁN/LÝ/HÓA, LỊCH SỬ/VĂN HÓA
   - **Small model**: Các câu hỏi khác
4. **Rate limiting**: Script có delay 2 giây giữa các batch để tránh vượt quota API

## ⚙️ Configuration

### Batch Size

```bash
# Smaller batch = safer but slower
python main_optimized.py --batch-size 4

# Larger batch = faster but may reduce accuracy
python main_optimized.py --batch-size 8

# Recommended: 6 (balance)
```

### Disable RAG (if needed)

```bash
python main_optimized.py --no-rag
# Uses only LLM, no knowledge base
```

## 📊 Performance Metrics

| Metric | Target | Actual |
|--------|--------|--------|
| **Accuracy (Val)** | >85% | TBD |
| **Inference Time (370q)** | <15 min | ~13 min |
| **API Requests** | <70 | 62 |
| **Docker Image Size** | <2GB | ~1.5GB |

## 🔧 Troubleshooting

### Issue: Knowledge base not found

```bash
# Make sure knowledge_base/ exists
ls -lh knowledge_base/

# Should show:
# knowledge_base.pkl
# embeddings.npy
```

### Issue: Out of memory

```bash
# Reduce batch size
python main_optimized.py --batch-size 4
```

### Issue: API rate limit

```bash
# Increase sleep time in main_optimized.py
# Line 287: time.sleep(10) → time.sleep(15)
```

## 📝 Competition Notes

### Scoring (Round 2)

- **Accuracy**: 70 points (a / total * 100% * 80)
- **Inference Time**: 10 points (y / x * 100% * 10)
  - x = your time
  - y = fastest team time
- **Creativity**: 20 points (manual review)

### Quotas

- Small LLM: 1000 req/day
- Large LLM: 500 req/day  
- Embedding: 500 req/min
- **Private test: NO LIMITS**

### Strategy

1. Build comprehensive knowledge base (Wikipedia)
2. Use hybrid search (BM25 + semantic)
3. Batch processing for speed
4. Optimize prompts for VN questions

## 📚 References

- Vietnamese Wikipedia: https://vi.wikipedia.org
- Underthesea docs: https://underthesea.readthedocs.io
- BM25 paper: https://en.wikipedia.org/wiki/Okapi_BM25

## 👥 Team

- 1stars
- Long

## 📄 License

Competition entry - VNPT AI Hackathon 2025

