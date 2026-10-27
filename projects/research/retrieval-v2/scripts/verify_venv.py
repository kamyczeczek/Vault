"""Verify venv has all required packages."""
import sys
import attune_rag
import sentence_transformers
import torch
import numpy
print(f"python: {sys.executable}")
print(f"attune-rag: {attune_rag.__version__}")
print(f"sentence-transformers: {sentence_transformers.__version__}")
print(f"torch: {torch.__version__}")
print(f"numpy: {numpy.__version__}")
print("VENV_OK")
