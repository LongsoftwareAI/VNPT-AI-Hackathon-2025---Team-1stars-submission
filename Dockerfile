# ============================================================================
# VNPT AI Hackathon - Track 2: The Builder
# Dockerfile for Question Answering System
# ============================================================================
# Base: Python 3.10 slim (CPU-only, no GPU required for this solution)
# Note: Sử dụng Python base image vì solution không cần GPU
# ============================================================================

FROM python:3.10-slim

# ============================================================================
# SYSTEM DEPENDENCIES
# Cài đặt các gói hệ thống cần thiết
# ============================================================================
RUN apt-get update && apt-get install -y \
    git \
    && rm -rf /var/lib/apt/lists/*

# ============================================================================
# PROJECT SETUP
# ============================================================================
# Thiết lập thư mục làm việc
WORKDIR /code

# Copy toàn bộ source code vào container
COPY . /code

# ============================================================================
# INSTALL LIBRARIES
# ============================================================================
# Nâng cấp pip và cài đặt các thư viện từ requirements.txt
RUN pip3 install --no-cache-dir --upgrade pip && \
    pip3 install --no-cache-dir -r requirements.txt

# ============================================================================
# METADATA
# ============================================================================
LABEL maintainer="VNPT AI Hackathon Team"
LABEL version="1.0"
LABEL description="Question Answering System with Hybrid RAG"

# ============================================================================
# EXECUTION
# Lệnh chạy mặc định khi container khởi động
# Pipeline sẽ đọc public_test.csv và xuất ra pred.csv
# ============================================================================
CMD ["bash", "inference.sh"]
