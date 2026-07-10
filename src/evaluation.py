"""
Evaluation framework for Medical RAG System responses
"""
from typing import Dict
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from config import GOOGLE_API_KEY, MODEL_NAME, EVALUATION_PROMPT


class RAGEvaluator:
    """Evaluate RAG system responses"""
    
    def __init__(self):
        self.llm = ChatGoogleGenerativeAI(
            google_api_key=GOOGLE_API_KEY,
            model=MODEL_NAME,
            temperature=0.5,
            max_output_tokens=512
        )
    
    def evaluate_response(self, query: str, response: str) -> Dict:
        """
        Evaluate a response based on medical Q&A criteria
        
        Args:
            query: The user's medical question
            response: The system's response
            
        Returns:
            Dictionary with evaluation scores and feedback
        """
        try:
            prompt_template = ChatPromptTemplate.from_messages([
                ("system", "You are an expert medical information evaluator."),
                ("user", f"""{EVALUATION_PROMPT}

Question: {query}

Response to Evaluate:
{response}

Please provide your evaluation in a structured format.""")
            ])
            
            evaluation = self.llm.invoke(
                prompt_template.format_messages()
            )
            
            return {
                "status": "success",
                "evaluation": evaluation.content,
                "query": query,
                "response_length": len(response)
            }
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "query": query
            }
    
    def evaluate_system(self, test_queries: list) -> Dict:
        """
        Evaluate system performance on multiple queries
        
        Args:
            test_queries: List of test queries
            
        Returns:
            Overall evaluation metrics
        """
        results = {
            "total_queries": len(test_queries),
            "successful_evaluations": 0,
            "failed_evaluations": 0,
            "evaluations": []
        }
        
        for query in test_queries:
            eval_result = self.evaluate_response(query, "")
            
            if eval_result.get("status") == "success":
                results["successful_evaluations"] += 1
            else:
                results["failed_evaluations"] += 1
            
            results["evaluations"].append(eval_result)
        
        return results
