import os
from pathlib import Path

# Base directory
BASE_DIR = Path(__file__).parent.absolute()

# Database configuration
DB_PATH = os.path.join(BASE_DIR, "notes.db")
DB_URL = f"sqlite:///{DB_PATH}"

# Model configuration
MODEL_NAME = "all-MiniLM-L6-v2"  # Sentence transformer model
EMBEDDING_DIM = 384  # Dimension of embeddings for the chosen model

# File paths
NOTES_JSON_PATH = os.path.join(BASE_DIR, "notes.json")
FAISS_INDEX_PATH = os.path.join(BASE_DIR, "notes_index.faiss") 