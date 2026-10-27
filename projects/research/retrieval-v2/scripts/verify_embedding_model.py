"""Verify paraphrase-multilingual-MiniLM-L12-v2 loads."""
from sentence_transformers import SentenceTransformer
import numpy as np

model = SentenceTransformer("sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2")
print(f"Model loaded: {model.get_sentence_embedding_dimension()} dims")
pl = model.encode("Jakie sa metody kompresji sesji agentow?")
en = model.encode("What are the methods for compressing AI agent sessions?")
sim = np.dot(pl, en) / (np.linalg.norm(pl) * np.linalg.norm(en))
print(f"PL-EN cosine similarity: {sim:.3f}")
print("OK" if sim > 0.7 else "WARN: low similarity")
