# VNPT AI Hackathon - Deployment Guide

## 📋 Prerequisites

Before deploying, ensure you have:

- ✅ **Docker** installed (version 20.10 or later)
- ✅ **Docker Hub account** (free tier is sufficient)
- ✅ **Git** installed
- ✅ **GitHub account**
- ✅ All required files in your project:
  - `main.py` (inference script)
  - `inference.sh` (entry-point script)
  - `api-keys.json` (API credentials)
  - `knowledge_base/` folder (pre-built database)
  - `requirements.txt` (Python dependencies)
  - `Dockerfile`

## 🐳 Step 1: Build Docker Image

### 1.1. Navigate to Project Directory

```bash
cd d:\\FPT\\contest\\vnptaihakathon
```

### 1.2. Build Docker Image

```bash
docker build -t team_submission .
```

**Expected output**: Build process completes successfully without errors.

**Estimated time**: 5-10 minutes (depending on internet speed for downloading base image and packages)

### 1.3. Verify Image Size

```bash
docker images team_submission
```

**Expected**: Image size should be < 2GB as per BTC requirements.

## 🧪 Step 2: Test Docker Image Locally

### 2.1. Create Test Directories

```powershell
# Create output directory
New-Item -ItemType Directory -Force -Path output
```

### 2.2. Run Docker Container with Test Data

```bash
docker run --gpus all -v ${PWD}/test_small_val.csv:/data/public_test.csv -v ${PWD}/output:/output team_submission
```

Or for PowerShell:
```powershell
docker run --gpus all -v ${PWD}/test_small_val.csv:/data/public_test.csv -v ${PWD}/output:/output team_submission
```

**Note**: Remove `--gpus all` if not using GPU.

### 2.3. Verify Output

```bash
# Check if output file exists
ls output/pred.csv

# View first few lines
Get-Content output/pred.csv -Head 10
```

**Expected output format**:
```csv
qid,answer
val_0001,B
val_0002,A
val_0003,B
...
```

## 🚀 Step 3: Push to Docker Hub

### 3.1. Login to Docker Hub

```bash
docker login
```

Enter your Docker Hub username and password when prompted.

### 3.2. Tag Image

Format: `your-dockerhub-username/vnpt-hackathon:v1`

```bash
docker tag team_submission your-dockerhub-username/vnpt-hackathon:v1
```

**Example**:
```bash
docker tag team_submission johndoe/vnpt-hackathon:v1
```

### 3.3. Push to Docker Hub

```bash
docker push your-dockerhub-username/vnpt-hackathon:v1
```

**Estimated time**: 5-15 minutes (depending on internet speed)

### 3.4. Verify on Docker Hub

Visit: `https://hub.docker.com/r/your-dockerhub-username/vnpt-hackathon`

Confirm that the image is publicly accessible.

## 📁 Step 4: Setup GitHub Repository

### 4.1. Initialize Git Repository (if not already done)

```bash
git init
```

### 4.2. Add Remote Repository

```bash
git remote add origin https://github.com/your-username/vnpt-ai-hackathon.git
```

### 4.3. Add Files to Git

```bash
# Add all necessary files (respect .gitignore)
git add .

# Verify what will be committed
git status
```

**Important files to commit**:
- ✅ `main.py`
- ✅ `inference.sh`
- ✅ `api-keys.json`
- ✅ `knowledge_base/`
- ✅ `requirements.txt`
- ✅ `Dockerfile`
- ✅ `.dockerignore`
- ✅ `README.md`

**Files that should be ignored** (per `.gitignore`):
- ❌ `venv/`
- ❌ `test_*.csv`
- ❌ `__pycache__/`
- ❌ `*.log`

### 4.4. Commit Changes

```bash
git commit -m "Initial commit: VNPT AI Hackathon submission"
```

### 4.5. Push to GitHub

```bash
# For first push
git branch -M main
git push -u origin main

# For subsequent pushes
git push
```

### 4.6. Verify on GitHub

Visit: `https://github.com/your-username/vnpt-ai-hackathon`

Confirm that all files are uploaded correctly.

## ✅ Step 5: Submission Checklist

Before submitting to BTC, verify:

- [ ] **Docker Build**: Docker image builds successfully without errors
  ```bash
  docker build -t team_submission .
  ```

- [ ] **Docker Run**: Container executes and produces correct output
  ```bash
  docker run --gpus all -v /path/to/data:/data -v /path/to/output:/output team_submission
  ```

- [ ] **Output Format**: `pred.csv` has correct format (`qid,answer`)
  ```bash
  head output/pred.csv
  ```

- [ ] **Docker Hub**: Image is pushed and publicly accessible
  - Image URL: `your-dockerhub-username/vnpt-hackathon:v1`

- [ ] **GitHub**: Repository is public and contains:
  - [ ] Source code (`main.py`, `inference.sh`)
  - [ ] Configuration files (`Dockerfile`, `requirements.txt`)
  - [ ] Pre-built resources (`knowledge_base/`, `api-keys.json`)
  - [ ] README.md with clear instructions

- [ ] **Submission Deadline**: Before **23:59 (UTC+7) ngày 19/12/2025**

## 📝 Step 6: Submit to BTC

Pada ngày 19/12/2025, BTC sẽ mở PORT để nhận submission. Bạn cần cung cấp:

1. **GitHub Repository URL**
   - Format: `https://github.com/your-username/vnpt-ai-hackathon`
   - Must be public

2. **Docker Hub Image Name**
   - Format: `your-dockerhub-username/vnpt-hackathon:v1`
   - Must follow naming convention from section 1.4 of BTC document

## 🔧 Troubleshooting

### Issue: Docker build fails with "requirements.txt not found"

**Solution**: Ensure `requirements.txt` is in the root directory:
```bash
ls requirements.txt
```

### Issue: Docker image size > 2GB

**Solution**: 
1. Check `.dockerignore` excludes unnecessary files
2. Remove large files from `knowledge_base/` if possible
3. Use `docker images` to verify size

### Issue: Output file not created

**Solution**:
1. Check mount paths are correct
2. Verify `inference.sh` has execute permissions
3. Check container logs: `docker logs <container-id>`

### Issue: "Permission denied" on inference.sh

**Solution**: Make script executable before building Docker image
```bash
# On Linux/Mac
chmod +x inference.sh

# On Windows (Git Bash)
git update-index --chmod=+x inference.sh
```

### Issue: Network error when calling VNPT API

**Solution**:
1. Verify `api-keys.json` is properly loaded
2. Ensure container has network access (default behavior)
3. Test API connectivity outside Docker first

## 📚 Additional Resources

- **VNPT AI API Documentation**: See `document/Tài liệu mô tả APIs LLM_Embedding Track 2.pdf`
- **Submission Guidelines**: See `document/Tài liệu mô tả phương thức nộp bài Track 2 The Builder.pdf`
- **Docker Documentation**: https://docs.docker.com
- **GitHub Documentation**: https://docs.github.com

## 🎯 Quick Reference Commands

```bash
# Build image
docker build -t team_submission .

# Test locally
docker run --gpus all -v ${PWD}/test_small_val.csv:/data/public_test.csv -v ${PWD}/output:/output team_submission

# Tag for Docker Hub
docker tag team_submission your-dockerhub-username/vnpt-hackathon:v1

# Push to Docker Hub
docker push your-dockerhub-username/vnpt-hackathon:v1

# Git commands
git add .
git commit -m "Update submission"
git push
```

---

**Good luck with your submission! 🚀**
