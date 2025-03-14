import os
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional

from langchain_groq import ChatGroq
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from dotenv import load_dotenv

load_dotenv()

class BaseAgent(ABC):
    """Base agent class providing common functionality for all agents"""
    
    def __init__(self, name: str, description: str, verbose: bool = False):
        """
        Initialize a base agent
        
        Args:
            name: The name of the agent
            description: A description of the agent's role and capabilities
            verbose: Whether to enable verbose logging
        """
        self.name = name
        self.description = description
        self.verbose = verbose
        self.model_name = os.getenv("MODEL_NAME", "llama-3.1-70b-versatile")
        self.groq_api_key = os.getenv("GROQ_API_KEY")
        
        if not self.groq_api_key:
            raise ValueError("GROQ_API_KEY is not set in environment variables")
        
        self.llm = ChatGroq(
            api_key=self.groq_api_key,
            model=self.model_name
        )
    
    def create_chain(self, template: str, output_key: str = "result") -> LLMChain:
        """
        Create a LangChain Chain with the given prompt template
        
        Args:
            template: The prompt template string
            output_key: Key to use for the output
            
        Returns:
            An LLMChain instance
        """
        prompt = PromptTemplate(
            input_variables=self._extract_input_variables(template),
            template=template
        )
        return LLMChain(
            llm=self.llm,
            prompt=prompt,
            output_key=output_key,
            verbose=self.verbose
        )
    
    def _extract_input_variables(self, template: str) -> List[str]:
        """
        Extract input variables from a template string
        
        Args:
            template: The prompt template string
            
        Returns:
            List of input variable names
        """
        # Simple regex pattern to find {variable} in the template
        import re
        pattern = r'\{([a-zA-Z0-9_]+)\}'
        return list(set(re.findall(pattern, template)))
    
    @abstractmethod
    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process the input data and return results
        
        Args:
            input_data: The input data to process
            
        Returns:
            The results of processing
        """
        pass