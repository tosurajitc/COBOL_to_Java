import os
from typing import Dict, Any, List
import logging

from langchain.chains import LLMChain
from agents.base_agent import BaseAgent
from utils.cobol_parser import extract_program_structure
from templates.prompts.analysis_prompts import (
    ANALYZE_COBOL_PROGRAM_PROMPT,
    IDENTIFY_BUSINESS_RULES_PROMPT
)

def remove_thinking_block(text: str) -> str:
    """
    Remove content within <think> tags
    
    Args:
        text: Text that might contain thinking blocks
        
    Returns:
        Cleaned text without thinking blocks
    """
    import re
    # Remove anything between <think> and </think> tags
    cleaned_text = re.sub(r'<think>.*?</think>', '', text, flags=re.DOTALL)
    
    # Also try alternative formats like <thinking> or [thinking]
    cleaned_text = re.sub(r'<thinking>.*?</thinking>', '', cleaned_text, flags=re.DOTALL)
    cleaned_text = re.sub(r'\[thinking\].*?\[/thinking\]', '', cleaned_text, flags=re.DOTALL)
    
    # Remove any empty lines that might be left
    cleaned_text = re.sub(r'\n\s*\n', '\n\n', cleaned_text)
    
    return cleaned_text.strip()

class AnalysisAgent(BaseAgent):
    """Agent responsible for analyzing COBOL programs and extracting business logic"""
    
    def __init__(self, verbose: bool = False):
        super().__init__(
            name="COBOL Analysis Expert",
            description="Analyzes COBOL programs to understand structure, business logic, " +
                        "data flow, and functional requirements.",
            verbose=verbose
        )
        self.logger = logging.getLogger(__name__)
    



    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze COBOL programs to understand their structure and business logic
        
        Args:
            input_data: Dictionary containing extracted COBOL programs and related files
            
        Returns:
            Dictionary containing analysis results
        """
        if not input_data.get('success', False) or not input_data.get('data'):
            return {
                'success': False,
                'error': "Invalid input data or extraction failed",
                'analysis': None
            }
        
        try:
            extracted_data = input_data['data']
            programs = extracted_data['programs']
            copybooks = extracted_data['copybooks']
            program_analyses = []
            
            for program in programs:
                program_path = program['path']
                program_name = program['name']
                program_content = program['content']
                
                # Find related copybooks
                related_copybook_names = program.get('related_copybooks', [])
                related_copybooks = [
                    cp for cp in copybooks
                    if cp['name'] in related_copybook_names
                ]
                
                # Extract program structure
                program_structure = extract_program_structure(
                    program_content,
                    related_copybooks
                )
                
                # Create analysis chain
                analysis_chain = self.create_chain(ANALYZE_COBOL_PROGRAM_PROMPT)
                analysis_result = analysis_chain.run(
                    program_name=program_name,
                    program_content=program_content,
                    copybooks="\n\n".join([
                        f"Copybook {cp['name']}:\n{cp['content']}" 
                        for cp in related_copybooks
                    ]),
                    program_structure=str(program_structure)
                )
                
                # Remove thinking block if present
                analysis_result = remove_thinking_block(analysis_result)
                
                # Use LLM to identify business rules
                business_rules_chain = self.create_chain(IDENTIFY_BUSINESS_RULES_PROMPT)
                
                # Run business rules analysis
                business_rules_result = business_rules_chain.run(
                    program_name=program_name,
                    program_content=program_content,
                    program_analysis=analysis_result
                )
                
                business_rules_result = remove_thinking_block(business_rules_result)
                program_analyses.append({
                    'program_name': program_name,
                    'program_structure': program_structure,
                    'functional_analysis': analysis_result,
                    'business_rules': business_rules_result,
                    'related_copybooks': related_copybook_names
                })
            
            return {
                'success': True,
                'analysis': program_analyses,
                'metadata': {
                    'num_programs_analyzed': len(program_analyses)
                }
            }
            
        except Exception as e:
            self.logger.error(f"Error analyzing COBOL programs: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'analysis': None
            }