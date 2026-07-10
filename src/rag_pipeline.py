"""
RAG (Retrieval-Augmented Generation) Pipeline
"""
from typing import List, Dict
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.documents import Document
from langchain_core.prompts import ChatPromptTemplate
from config import GOOGLE_API_KEY, MODEL_NAME, SYSTEM_PROMPT, TOP_K


class RAGPipeline:
    """Complete RAG pipeline for medical Q&A"""
    
    def __init__(self, retriever):
        """
        Initialize RAG pipeline
        
        Args:
            retriever: FAISS retriever for document retrieval
        """
        self.retriever = retriever
        self.llm = ChatGoogleGenerativeAI(
            google_api_key=GOOGLE_API_KEY,
            model=MODEL_NAME,
            temperature=0.3,  # Lower temperature for consistent medical info
            max_output_tokens=1024
        )
        self.conversation_history = []
    
    def retrieve_documents(self, query: str, k: int = TOP_K) -> List[Document]:
        """Retrieve relevant documents"""
        try:
            docs = self.retriever.invoke(query)
            return docs[:k]
        except Exception as e:
            print(f"Error retrieving documents: {e}")
            return []
    
    def format_context(self, documents: List[Document]) -> str:
        """Format retrieved documents into context"""
        if not documents:
            return "No relevant medical documents found."
        
        context = "Relevant Medical Information:\n"
        context += "=" * 50 + "\n"
        
        for i, doc in enumerate(documents, 1):
            source = doc.metadata.get("source", "Unknown")
            context += f"\n[Document {i}: {source}]\n"
            context += doc.page_content[:500] + "...\n"
        
        return context
    
    def generate_response(self, query: str) -> Dict:
        """Generate response using RAG pipeline"""
        # Step 1: Retrieve relevant documents
        retrieved_docs = self.retrieve_documents(query)
        
        # Step 2: Format context
        context = self.format_context(retrieved_docs)
        
        # Step 3: Create prompt
        prompt_template = ChatPromptTemplate.from_messages([
            ("system", SYSTEM_PROMPT),
            ("user", "Medical Context:\n{context}\n\nQuestion: {query}")
        ])
        
        # Step 4: Generate response
        try:
            response = self.llm.invoke(
                prompt_template.format_messages(context=context, query=query)
            )
            response_text = response.content
        except Exception as e:
            response_text = f"Error generating response: {e}"

        # Step 4b: Parse the MODE tag the model was instructed to prefix its answer with.
        # Defaults to "grounded" if the model didn't follow the format, so behavior
        # degrades gracefully rather than silently hiding real sources.
        mode = "grounded"
        cleaned_text = response_text.strip()
        first_line, _, rest = cleaned_text.partition("\n")
        first_line_upper = first_line.strip().upper()
        if first_line_upper in ("MODE: GROUNDED", "MODE:GROUNDED", "MODE: GENERAL", "MODE:GENERAL"):
            mode = "general" if "GENERAL" in first_line_upper else "grounded"
            response_text = rest.lstrip("\n").lstrip()

        # In general mode, the retrieved chunks weren't actually relevant - don't
        # present them to the user as if they were the basis for the answer.
        effective_docs = retrieved_docs if mode == "grounded" else []

        # Step 5: Extract sources
        sources = [doc.metadata.get("source", "Unknown") for doc in effective_docs]

        # Step 6: Store in history
        history_entry = {
            "query": query,
            "response": response_text,
            "sources": sources,
            "mode": mode
        }
        self.conversation_history.append(history_entry)

        return {
            "response": response_text,
            "sources": sources,
            "context": context,
            "documents": effective_docs,
            "mode": mode
        }
    
    def get_conversation_history(self) -> List[Dict]:
        """Get conversation history"""
        return self.conversation_history


def create_rag_pipeline(embeddings_manager) -> RAGPipeline:
    """Create RAG pipeline from embeddings manager"""
    retriever = embeddings_manager.get_retriever()
    
    if not retriever:
        raise ValueError("Failed to create retriever from embeddings manager")
    
    return RAGPipeline(retriever)
