import os
from typing import Dict, Any, List
import logging
from pathlib import Path

from .base_agent import BaseAgent
from utils.java_generator import generate_java_class, generate_project_structure
from templates.prompts.conversion_prompts import (
    CONVERT_COBOL_TO_JAVA_PROMPT,
    GENERATE_JAVA_CLASS_STRUCTURE_PROMPT,
    MAP_DATA_STRUCTURES_PROMPT
)

class ConversionAgent(BaseAgent):
    """Agent responsible for converting COBOL programs to Java"""
    
    def __init__(self, verbose: bool = False):
        super().__init__(
            name="COBOL to Java Conversion Expert",
            description="Converts COBOL programs to equivalent Java code, " +
                        "mapping data structures, business logic, and program flow.",
            verbose=verbose
        )
        self.logger = logging.getLogger(__name__)
        self.output_path = os.getenv("JAVA_OUTPUT_PATH", "./output/java_programs")
    
    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Convert COBOL programs to Java
        
        Args:
            input_data: Dictionary containing analysis results
            
        Returns:
            Dictionary containing conversion results
        """
        if not input_data.get('success', False) or not input_data.get('analysis'):
            return {
                'success': False,
                'error': "Invalid input data or analysis failed",
                'conversion': None
            }
        
        try:
            program_analyses = input_data['analysis']
            conversion_results = []
            
            # Ensure output directory exists
            output_path = Path(self.output_path)
            output_path.mkdir(parents=True, exist_ok=True)
            
            for analysis in program_analyses:
                program_name = analysis['program_name']
                program_structure = analysis['program_structure']
                functional_analysis = analysis['functional_analysis']
                business_rules = analysis['business_rules']
                
                # Create chains for each step
                class_structure_chain = self.create_chain(GENERATE_JAVA_CLASS_STRUCTURE_PROMPT)
                data_mapping_chain = self.create_chain(MAP_DATA_STRUCTURES_PROMPT)
                conversion_chain = self.create_chain(CONVERT_COBOL_TO_JAVA_PROMPT)
                
                # Generate Java class structure
                class_structure_result = class_structure_chain.run(
                    program_name=program_name,
                    program_analysis=functional_analysis,
                    business_rules=business_rules
                )
                
                # Map COBOL data structures to Java
                data_mapping_result = data_mapping_chain.run(
                    program_name=program_name,
                    program_structure=str(program_structure),
                    class_structure=class_structure_result
                )
                
                # Convert COBOL to Java
                conversion_result = conversion_chain.run(
                    program_name=program_name,
                    program_analysis=functional_analysis,
                    class_structure=class_structure_result,
                    data_mapping=data_mapping_result,
                    business_rules=business_rules
                )
                
                # Generate Java class files
                java_project_path = generate_project_structure(
                    output_path, 
                    program_name
                )
                
                java_classes = generate_java_class(
                    java_project_path,
                    program_name,
                    conversion_result,
                    class_structure_result
                )
                
                conversion_results.append({
                    'program_name': program_name,
                    'java_project_path': str(java_project_path),
                    'java_classes': java_classes,
                    'class_structure': class_structure_result,
                    'data_mapping': data_mapping_result,
                    'conversion_result': conversion_result
                })
            
            return {
                'success': True,
                'conversion': conversion_results,
                'output_path': str(output_path),
                'metadata': {
                    'num_programs_converted': len(conversion_results)
                }
            }
            
        except Exception as e:
            self.logger.error(f"Error converting COBOL to Java: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'conversion': None
            }