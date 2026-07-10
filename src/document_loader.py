"""
Document loading and preprocessing for Medical RAG System
"""
from pathlib import Path
from typing import List
from langchain_community.document_loaders import TextLoader, PyPDFLoader, CSVLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
from config import DOCUMENTS_DIR, CHUNK_SIZE, CHUNK_OVERLAP


class DocumentLoader:
    """Load and process medical documents"""
    
    def __init__(self, chunk_size: int = CHUNK_SIZE, chunk_overlap: int = CHUNK_OVERLAP):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            separators=["\n\n", "\n", ". ", " ", ""]
        )
    
    def load_documents(self) -> List[Document]:
        """Load all documents from the documents directory"""
        documents = []
        
        if not DOCUMENTS_DIR.exists():
            print(f"Documents directory not found: {DOCUMENTS_DIR}")
            return documents
        
        for file_path in DOCUMENTS_DIR.glob("*"):
            if file_path.suffix.lower() == ".txt":
                print(f"Loading text document: {file_path.name}")
                documents.extend(self._load_text_file(file_path))
            elif file_path.suffix.lower() == ".pdf":
                print(f"Loading PDF document: {file_path.name}")
                documents.extend(self._load_pdf_file(file_path))
            elif file_path.suffix.lower() == ".csv":
                print(f"Loading CSV document: {file_path.name}")
                documents.extend(self._load_csv_file(file_path))
        
        print(f"Loaded {len(documents)} documents from {DOCUMENTS_DIR}")
        return documents
    
    def _load_text_file(self, file_path: Path) -> List[Document]:
        """Load a text file"""
        try:
            loader = TextLoader(str(file_path), encoding="utf-8")
            docs = loader.load()
            return self._split_documents(docs, file_path.name)
        except Exception as e:
            print(f"Error loading text file {file_path}: {e}")
            return []
    
    def _load_pdf_file(self, file_path: Path) -> List[Document]:
        """Load a PDF file"""
        try:
            loader = PyPDFLoader(str(file_path))
            docs = loader.load()
            return self._split_documents(docs, file_path.name)
        except Exception as e:
            print(f"Error loading PDF file {file_path}: {e}")
            return []
    
    def _load_csv_file(self, file_path: Path) -> List[Document]:
        """Load a CSV file"""
        try:
            loader = CSVLoader(
                file_path=str(file_path),
                content_columns=["transcription", "description"],
                metadata_columns=["medical_specialty", "sample_name", "keywords"],
                encoding="utf-8"
            )
            docs = loader.load()
            # Filter out rows where transcription is empty
            docs = [doc for doc in docs if doc.page_content.strip()]
            docs = docs[:500]
            return self._split_documents(docs, file_path.name)
        except Exception as e:
            print(f"Error loading CSV file {file_path}: {e}")
            return []
    
    def _split_documents(self, docs: List[Document], source: str) -> List[Document]:
        """Split documents into chunks"""
        split_docs = self.text_splitter.split_documents(docs)
        
        # Add source metadata
        for doc in split_docs:
            doc.metadata["source"] = source
        
        return split_docs


def prepare_documents() -> List[Document]:
    """Load and prepare all documents"""
    loader = DocumentLoader()
    documents = loader.load_documents()
    
    if not documents:
        print("⚠️  No documents found in documents/ directory")
        return []
    
    print(f"✓ Prepared {len(documents)} document chunks\n")
    return documents
