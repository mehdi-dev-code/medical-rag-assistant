"""
Main application entry point for Medical RAG System
"""
import sys
import os

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from config import GOOGLE_API_KEY
from document_loader import prepare_documents
from embeddings_manager import initialize_embeddings
from rag_pipeline import create_rag_pipeline
from evaluation import RAGEvaluator


def main():
    """Main application loop"""
    
    # Validate API key
    if not GOOGLE_API_KEY:
        print("❌ Error: GOOGLE_API_KEY not found in .env file")
        print("Please set your GOOGLE_API_KEY in the .env file")
        return
    
    print("=" * 60)
    print("🏥 Medical RAG System - Powered by Gemini")
    print("=" * 60)
    
    # Step 1: Load documents
    print("\n📚 Step 1: Loading medical documents...")
    documents = prepare_documents()
    
    if not documents:
        print("❌ No documents found. Please add .txt or .pdf files to documents/ directory")
        return
    
    # Step 2: Initialize embeddings
    print("🧠 Step 2: Initializing embeddings and vector store...")
    try:
        embeddings_manager = initialize_embeddings(documents)
    except Exception as e:
        print(f"❌ Error initializing embeddings: {e}")
        return
    
    # Step 3: Create RAG pipeline
    print("⚙️  Step 3: Creating RAG pipeline...")
    try:
        rag_pipeline = create_rag_pipeline(embeddings_manager)
        print("✓ RAG pipeline ready\n")
    except Exception as e:
        print(f"❌ Error creating RAG pipeline: {e}")
        return
    
    # Step 4: Interactive Q&A
    print("=" * 60)
    print("💬 Starting Medical Q&A System")
    print("=" * 60)
    print("Commands:")
    print("  - Type your medical question and press Enter")
    print("  - Type 'eval' to evaluate system")
    print("  - Type 'history' to see conversation history")
    print("  - Type 'exit' to quit")
    print("=" * 60 + "\n")
    
    while True:
        try:
            user_input = input("\n👤 You: ").strip()
            
            if not user_input:
                continue
            
            if user_input.lower() == 'exit':
                print("\n👋 Thank you for using Medical RAG System. Goodbye!")
                break
            
            elif user_input.lower() == 'history':
                history = rag_pipeline.get_conversation_history()
                if not history:
                    print("📭 No conversation history yet")
                else:
                    print("\n📋 Conversation History:")
                    print("-" * 60)
                    for i, entry in enumerate(history, 1):
                        print(f"\n[{i}] Query: {entry['query']}")
                        print(f"    Sources: {', '.join(entry['sources'])}")
                        print(f"    Response Preview: {entry['response'][:100]}...")
                continue
            
            elif user_input.lower() == 'eval':
                print("\n🔬 Evaluating system...")
                evaluator = RAGEvaluator()
                
                # Evaluate last response if exists
                if rag_pipeline.get_conversation_history():
                    last_entry = rag_pipeline.get_conversation_history()[-1]
                    eval_result = evaluator.evaluate_response(
                        query=last_entry['query'],
                        response=last_entry['response']
                    )
                    print("\n📊 Evaluation Result:")
                    print(eval_result.get('evaluation', 'No evaluation available'))
                else:
                    print("❌ No responses to evaluate yet")
                continue
            
            # Process normal query
            print("\n🔄 Processing...\n")
            result = rag_pipeline.generate_response(user_input)
            
            print(f"\n🤖 Assistant: {result['response']}")
            print(f"\n📌 Sources ({len(result['sources'])} chunks retrieved):")
            for i, source in enumerate(result['sources'], 1):
                print(f"   {i}. {source}")
        
        except KeyboardInterrupt:
            print("\n\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"\n❌ Error processing query: {e}")
            print("Please try again with a different question.")


if __name__ == "__main__":
    main()
