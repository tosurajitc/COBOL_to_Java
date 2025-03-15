import os
import logging
import re
import groq
import json
from typing import Dict, Any, List
from pathlib import Path
from dotenv import load_dotenv
from utils.java_generator import generate_java_class, generate_project_structure
from templates.prompts.conversion_prompts import (
    CONVERT_COBOL_TO_JAVA_PROMPT,
    GENERATE_JAVA_CLASS_STRUCTURE_PROMPT,
    MAP_DATA_STRUCTURES_PROMPT
)
import sys

# Add the project root to the Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.insert(0, project_root)


load_dotenv()

class ConversionAgent:
    """Agent responsible for converting COBOL programs to Java"""
    
    def __init__(self, verbose: bool = False):
        """
        Initialize a Conversion Agent
        
        Args:
            verbose: Whether to enable verbose logging
        """
        self.name = "COBOL to Java Conversion Expert"
        self.description = "Converts COBOL programs to equivalent Java code"
        self.verbose = verbose
        self.model_name = os.getenv("MODEL_NAME", "llama-3.1-70b-versatile")
        self.groq_api_key = os.getenv("GROQ_API_KEY")
        self.logger = logging.getLogger(__name__)
        self.output_path = os.getenv("JAVA_OUTPUT_PATH", "./output/java_programs")
        
        if not self.groq_api_key:
            raise ValueError("GROQ_API_KEY is not set in environment variables")
        
        # Initialize Groq client directly
        self.client = groq.Client(api_key=self.groq_api_key)
    
    def run_with_template(self, template: str, **kwargs) -> str:
        """
        Fill a template with variables and run it through the LLM
        
        Args:
            template: The prompt template string
            **kwargs: Variables to fill in the template
            
        Returns:
            The LLM's response
        """
        # Fill template with variables
        filled_prompt = template
        for key, value in kwargs.items():
            placeholder = "{" + key + "}"
            if placeholder in filled_prompt:
                filled_prompt = filled_prompt.replace(placeholder, str(value))
        
        # Call the LLM
        try:
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {"role": "system", "content": f"You are {self.name}, an AI assistant that {self.description}"},
                    {"role": "user", "content": filled_prompt}
                ],
                temperature=0.1,
                max_tokens=4000,
                top_p=1
            )
            
            if self.verbose:
                print(f"Prompt: {filled_prompt}")
                print(f"Response: {response.choices[0].message.content}")
            
            return response.choices[0].message.content
        except Exception as e:
            self.logger.error(f"Error invoking LLM: {str(e)}")
            raise e
    
    def invoke(self, prompt: str, max_retries: int = 3, **kwargs) -> str:
        """
        Invoke the LLM with a prompt and retry on failure
        
        Args:
            prompt: The prompt to send to the LLM
            max_retries: Maximum number of retry attempts
            **kwargs: Additional parameters for the API call
            
        Returns:
            The LLM's response
        """
        retries = 0
        while retries <= max_retries:
            try:
                # Call the Groq API directly
                response = self.client.chat.completions.create(
                    model=self.model_name,
                    messages=[
                        {"role": "system", "content": f"You are {self.name}, an AI assistant that {self.description}"},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.1,
                    max_tokens=4000,
                    top_p=1,
                    **kwargs
                )
                
                if self.verbose:
                    print(f"Prompt: {prompt}")
                    print(f"Response: {response.choices[0].message.content}")
                
                return response.choices[0].message.content
                
            except Exception as e:
                retries += 1
                if retries > max_retries:
                    raise e
                
                wait_time = 2 ** retries  # Exponential backoff
                self.logger.warning(f"API error: {str(e)}. Retrying in {wait_time} seconds...")
                import time
                time.sleep(wait_time)
    
    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Modify the process method to handle potential edge cases
        and improve error handling
        """
        try:
            # Existing validation
            if not input_data.get('success', False) or not input_data.get('analysis'):
                return {
                    'success': False,
                    'error': "Invalid input data or analysis failed",
                    'conversion': None
                }
            
            # Existing conversion logic
            program_analyses = input_data['analysis']
            conversion_results = []
            
            # More robust error handling and logging
            for analysis in program_analyses:
                try:
                    # Existing conversion steps
                    conversion_result = self.run_with_template(
                        CONVERT_COBOL_TO_JAVA_PROMPT,
                        program_name=analysis['program_name'],
                        # ... other parameters
                    )
                except Exception as sub_error:
                    # Log individual program conversion errors
                    self.logger.error(f"Error converting program {analysis['program_name']}: {sub_error}")
                    # Continue with next program instead of failing entire process
                    continue
            
            return {
                'success': True,
                'conversion': conversion_results,
                # ... other metadata
            }
        
        except Exception as e:
            # Comprehensive error handling
            self.logger.error(f"Conversion process failed: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'conversion': None
            }