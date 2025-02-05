# models/classifier.py
import logging
from transformers import pipeline

class ClassifierEngine:
    def __init__(self, candidate_labels, device=0):
        self.candidate_labels = candidate_labels
        self.classifier = pipeline(
            "zero-shot-classification",
            model="facebook/bart-large-mnli",
            device=device
        )

    def classify_text(self, text):
        try:
            result = self.classifier(text, candidate_labels=self.candidate_labels)
            return result["labels"][0], result["scores"][0], result
        except Exception as e:
            logging.error(f"Error classifying text '{text}': {e}")
            return "Unknown", 0.0, None

    def classify_texts(self, texts, batch_size=16):
        try:
            return self.classifier(texts, candidate_labels=self.candidate_labels, batch_size=batch_size)
        except Exception as e:
            logging.error(f"Error classifying texts: {e}")
            return []
