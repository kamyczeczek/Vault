"""Verify polish cross-encoder loads and scores correctly."""
import torch.nn as nn
from sentence_transformers import CrossEncoder

model = CrossEncoder(
    "sdadas/polish-reranker-large-ranknet",
    default_activation_function=nn.Identity(),
    max_length=512,
)

query = "Jakie sa metody kompresji sesji agentow?"
answers = [
    "Kompresja sesji agentow polega na streszczaniu kontekstu.",
    "Przepis na pierogi ruskie.",
]
scores = model.predict([[query, a] for a in answers])
print(f"Scores: {scores.tolist()}")
print("OK" if scores[0] > scores[1] else "WARN: ranking inverted")
