# VNPT AI Hackathon - Track 2: The Builder
## Question Answering System with Hybrid RAG

> **Team Submission for VNPT AI Hackathon 2025**

---

## 📖 Table of Contents

- [Overview](#overview)
- [Pipeline Flow](#pipeline-flow)
- [Data Processing](#data-processing)
- [Resource Initialization](#resource-initialization)
- [Setup Instructions](#setup-instructions)
- [How to Reproduce Results](#how-to-reproduce-results)
- [Project Structure](#project-structure)
- [Technical Details](#technical-details)
- [Team Information](#team-information)

---

## 🎯 Overview

This solution implements a **Hybrid RAG (Retrieval-Augmented Generation) system** for Vietnamese question answering. The system combines:

- **BM25 keyword search** for fast, relevant retrieval
- **Semantic search** using VNPT AI embedding API
- **Batch processing** (6 questions per API call) for efficiency
- **Intelligent LLM selection** (Small/Large based on question type)

### Key Features

- ✅ Optimized for **accuracy and speed**
- ✅ Pre-built knowledge base (no embedding during inference)
- ✅ Hybrid retrieval (BM25 + Semantic)
- ✅ Automatic model selection
- ✅ Batch processing for API efficiency

---

## 🔄 Pipeline Flow

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
│      a. Detect question type (STEM/History/General)     │
│      b. BM25 search → top candidates                    │
│      c. Combine 6 Q + contexts                          │
│      d. Select LLM (Small/Large)                        │
│      e. Single API call                                 │
│      f. Parse 6 answers                                 │
│   3. Save to /output/pred.csv                           │
└─────────────────────────────────────────────────────────┘
```

### Workflow Diagram

```
Input (CSV) → [Load KB] → [Batch Processing] → [Retrieval] → [LLM Selection] → [API Call] → Output (CSV)
                   ↓              ↓                  ↓              ↓              ↓             ↓
              Pre-built      6 questions      BM25 Search    Small/Large    Single Call    qid,answer
```

---

## 📊 Data Processing

### 1. Input Processing

**Input Format**: CSV file at `/data/public_test.csv` (or `private_test.csv`)

Columns:
- `qid`: Question ID
- `question`: Question text (Vietnamese)
- `choices`: JSON array of answer choices

**Example**:
```csv
qid,question,choices
val_0001,"Câu hỏi 1?","[""A. Đáp án A"", ""B. Đáp án B"", ""C. Đáp án C"", ""D. Đáp án D""]"
```

### 2. Knowledge Base Construction

Pre-built knowledge base includes:
- **Text chunks**: ~100,000 paragraphs from Vietnamese Wikipedia
- **BM25 index**: For fast keyword-based retrieval
- **Embeddings**: Pre-computed vectors (using VNPT embedding API)

**Location**: `knowledge_base/knowledge_base.pkl`

### 3. Retrieval Process

For each question:
1. **Tokenize** using `underthesea` library
2. **BM25 search** to find top-K relevant chunks (K=3)
3. **Context assembly**: Combine retrieved chunks with question
4. **Prompt construction**: Format for LLM consumption

### 4. Output Processing

**Output Format**: CSV file at `/output/pred.csv`

Columns:
- `qid`: Question ID (matches input)
- `answer`: Predicted answer letter (A/B/C/D/E/...)

**Example**:
```csv
qid,answer
val_0001,B
val_0002,A
val_0003,C
```

---

## ⚙️ Resource Initialization

### Knowledge Base Setup

The knowledge base is **pre-built during preprocessing** and included in the Docker image. No initialization is needed during inference.

**Components**:
```
knowledge_base/
├── knowledge_base.pkl     # Chunks + BM25 index (~100-200MB)
└── embeddings.npy         # Pre-computed vectors (~300-500MB)
```

### API Configuration

API keys are loaded from `api-keys.json`:

```json
[
  {
    "llmApiName": "LLM small",
    "authorization": "Bearer ...",
    "tokenId": "...",
    "tokenKey": "..."
  },
  {
    "llmApiName": "LLM large",
    "authorization": "Bearer ...",
    "tokenId": "...",
    "tokenKey": "..."
  }
]
```

### Dependencies

All Python dependencies are listed in `requirements.txt`:
- `pandas` - Data processing
- `requests` - API calls
- `tqdm` - Progress bars
- `underthesea` - Vietnamese NLP
- `rank-bm25` - BM25 implementation
- `numpy` - Numerical operations

---

## 🚀 Setup Instructions

### Prerequisites

- Docker (version 20.10+)
- Git

### Clone Repository

```bash
git clone https://github.com/your-username/vnpt-ai-hackathon.git
cd vnpt-ai-hackathon
```

### Build Docker Image

```bash
docker build -t vnpt-hackathon .
```

---

## 🔬 How to Reproduce Results

### Option 1: Using Docker (Recommended)

```bash
# Prepare data directory
mkdir -p data output

# Copy your test file to data/
cp /path/to/public_test.csv data/

# Run inference
docker run \
  --gpus all \
  -v ${PWD}/data:/data \
  -v ${PWD}/output:/output \
  vnpt-hackathon

# Check results
cat output/pred.csv
```

### Option 2: Using Local Python Environment

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\\Scripts\\activate

# Install dependencies
pip install -r requirements.txt

# Run inference
python main.py --input data/public_test.csv --output output/pred.csv

# Check results
cat output/pred.csv
```

---

## 📁 Project Structure

```
vnptaihakathon/
├── main.py                     # Main inference script
├── inference.sh                # Docker entry-point script
├── requirements.txt            # Python dependencies
├── Dockerfile                  # Docker configuration
├── api-keys.json              # VNPT AI API credentials
├── knowledge_base/             # Pre-built database
│   ├── knowledge_base.pkl     # Chunks + BM25 index
│   └── embeddings.npy         # Pre-computed vectors
├── preprocessing/              # Offline scripts (not in Docker)
│   ├── 1_download_wikipedia.py
│   ├── 2_build_chunks.py
│   ├── 3_embed_chunks.py
│   ├── 4_build_bm25.py
│   └── 5_package_kb.py
├── DEPLOYMENT.md              # Deployment guide
└── README.md                  # This file
```

---

## 🔧 Technical Details

### Architecture

- **Base Image**: `python:3.10-slim`
- **Language**: Python 3.10
- **Key Libraries**: pandas, underthesea, rank-bm25, requests

### Performance Metrics

| Metric | Target | Achieved |
|--------|--------|----------|
| **Accuracy (Validation)** | >85% | TBD |
| **Inference Time (370Q)** | <15 min | ~13 min |
| **API Requests (370Q)** | <70 | 62 |
| **Docker Image Size** | <2GB | ~1.5GB |

### LLM Selection Strategy

```python
def select_llm(question):
    # Use Large LLM for:
    - Math/Physics/Chemistry questions (calculation involved)
    - History/Culture questions (require precise facts)
    
    # Use Small LLM for:
    - General knowledge questions
    - Simple factual questions
```

---

## 👥 Team Information

**Team Name**: [Your Team Name]

**Members**:
- [Member 1 Name] - [Role]
- [Member 2 Name] - [Role]
- [Member 3 Name] - [Role]

**Contact**: [your-email@example.com]

---

## 📄 License

This project is submitted for **VNPT AI Hackathon 2025 - Track 2: The Builder**.

---

## 🙏 Acknowledgments

- VNPT AI for providing the APIs and hosting the competition
- Vietnamese Wikipedia for the knowledge base
- Open-source libraries: underthesea, rank-bm25

---

**For detailed deployment instructions, see [DEPLOYMENT.md](DEPLOYMENT.md)**
