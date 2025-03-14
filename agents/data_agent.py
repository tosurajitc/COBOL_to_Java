import os
import tempfile
from typing import Dict, Any, List, Optional
from zipfile import ZipFile
from pathlib import Path
import logging

from .base_agent import BaseAgent
from utils.file_utils import extract_cobol_files, validate_folder_structure

class DataAgent(BaseAgent):
    """Agent responsible for extracting and processing COBOL files"""
    
    def __init__(self, verbose: bool = False):
        super().__init__(
            name="COBOL Data Extraction Specialist",
            description="Extracts and processes COBOL source files from zip archives, " + 
                        "validates folder structure, and prepares data for analysis.",
            verbose=verbose
        )
        self.logger = logging.getLogger(__name__)
    
    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process the zip file and extract COBOL programs
        
        Args:
            input_data: Dictionary containing the zip file path
            
        Returns:
            Dictionary containing extracted data
        """
        zip_file_path = input_data.get('zip_file_path')
        if not zip_file_path:
            raise ValueError("No zip file path provided")
        
        # Create a temporary directory for extraction
        with tempfile.TemporaryDirectory() as temp_dir:
            try:
                # Extract all files from the zip
                with ZipFile(zip_file_path, 'r') as zip_ref:
                    zip_ref.extractall(temp_dir)
                
                # Validate folder structure
                validation_result = validate_folder_structure(temp_dir)
                if not validation_result['valid']:
                    return {
                        'success': False,
                        'error': f"Invalid folder structure: {validation_result['reason']}",
                        'data': None
                    }
                
                # Extract COBOL files and organize them
                extracted_data = extract_cobol_files(temp_dir)
                
                # Process based on extraction results
                return {
                    'success': True,
                    'extraction_path': temp_dir,
                    'data': {
                        'programs': extracted_data['programs'],
                        'copybooks': extracted_data['copybooks'],
                        'other_files': extracted_data['other_files'],
                        'file_relationships': extracted_data['file_relationships'],
                        'metadata': {
                            'num_programs': len(extracted_data['programs']),
                            'num_copybooks': len(extracted_data['copybooks']),
                            'extraction_path': temp_dir
                        }
                    }
                }
                
            except Exception as e:
                self.logger.error(f"Error processing zip file: {str(e)}")
                return {
                    'success': False,
                    'error': str(e),
                    'data': None
                }