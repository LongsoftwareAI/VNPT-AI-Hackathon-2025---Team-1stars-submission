#!/bin/bash
# inference.sh - Script to run inference pipeline
# This script will be called by Docker CMD

echo "Starting VNPT AI Hackathon Inference Pipeline..."

# Run main.py with default parameters
# Docker will mount data at /data and expect output at /output
python main.py --input /data/public_test.csv --output /output/pred.csv

echo "Inference completed!"
