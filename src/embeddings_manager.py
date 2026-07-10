"""
Embeddings and Vector Store Management using HuggingFace
"""
import os
import warnings
from pathlib import Path
from typing import List

# Suppress TensorFlow warnings and disable oneDNN
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'
warnings.filterwarnings('ignore')

from langchain_core.documents import Document
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from config import EMBEDDINGS_DIR, EMBEDDING_MODEL


class EmbeddingsManager:
    """Manage document embeddings and vector store"""
    
    def __init__(self):
        try:
            # Initialize HuggingFace embeddings (runs locally, no API needed)
            print("Initializing HuggingFace embeddings...")
            self.embeddings = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL)
            print("✓ Embeddings initialized successfully\n")
        except Exception as e:
            print(f"❌ Failed to initialize embeddings: {e}")
            raise
        
        self.vector_store = None
        self.embeddings_path = EMBEDDINGS_DIR / "faiss_index"
    
    def create_vector_store(self, documents: List[Document]) -> FAISS:
        """Create FAISS vector store from documents"""
        if not documents:
            raise ValueError("No documents provided for embedding")
        
        print(f"Creating embeddings for {len(documents)} document chunks...")
        self.vector_store = FAISS.from_documents(
            documents,
            self.embeddings
        )
        print("✓ Vector store created successfully\n")
        return self.vector_store
    
    def save_vector_store(self):
        """Save vector store to disk"""
        if self.vector_store:
            self.vector_store.save_local(str(self.embeddings_path))
            print(f"✓ Vector store saved to {self.embeddings_path}")
    
    def load_vector_store(self) -> FAISS:
        """Load vector store from disk"""
        if self.embeddings_path.exists():
            self.vector_store = FAISS.load_local(
                str(self.embeddings_path),
                self.embeddings
            )
            print("✓ Vector store loaded from disk")
            return self.vector_store
        return None
    
    def get_retriever(self):
        """Get retriever from vector store"""
        if self.vector_store:
            return self.vector_store.as_retriever(search_kwargs={"k": 3})
        return None


def initialize_embeddings(documents: List[Document]) -> EmbeddingsManager:
    """Initialize embeddings manager and create vector store"""
    manager = EmbeddingsManager()
    manager.create_vector_store(documents)
    return manager
