import os
from pathlib import Path
from typing import Dict, List, Any
import re

def validate_folder_structure(extract_path: str) -> Dict[str, Any]:
    """
    Validate the folder structure of the extracted zip file
    
    Args:
        extract_path: Path to the extracted files
        
    Returns:
        Dictionary with validation result
    """
    extract_dir = Path(extract_path)
    
    # Check for src directory
    src_dir = extract_dir / 'src'
    if not src_dir.exists() or not src_dir.is_dir():
        return {
            'valid': False,
            'reason': "Missing 'src' directory in the zip file"
        }
    
    # Check for programs directory
    programs_dir = src_dir / 'programs'
    if not programs_dir.exists() or not programs_dir.is_dir():
        return {
            'valid': False,
            'reason': "Missing 'src/programs' directory for COBOL programs"
        }
    
    # Check for at least one COBOL program
    cobol_files = list(programs_dir.glob('*.cbl')) + list(programs_dir.glob('*.cob'))
    if not cobol_files:
        return {
            'valid': False,
            'reason': "No COBOL programs (.cbl or .cob files) found in 'src/programs'"
        }
    
    # Check for copybooks directory (optional but recommended)
    copybooks_dir = src_dir / 'copybooks'
    if not copybooks_dir.exists() or not copybooks_dir.is_dir():
        return {
            'valid': True,
            'warning': "No 'src/copybooks' directory found. Copybooks may be missing."
        }
    
    return {'valid': True}

def extract_cobol_files(extract_path: str) -> Dict[str, Any]:
    """
    Extract and organize COBOL files from the extracted directory
    
    Args:
        extract_path: Path to the extracted files
        
    Returns:
        Dictionary containing organized COBOL files
    """
    extract_dir = Path(extract_path)
    result = {
        'programs': [],
        'copybooks': [],
        'other_files': [],
        'file_relationships': {}
    }
    
    # Extract COBOL programs
    programs_dir = extract_dir / 'src' / 'programs'
    for file_ext in ['.cbl', '.cob']:
        for file_path in programs_dir.glob(f'*{file_ext}'):
            program_content = file_path.read_text(encoding='utf-8')
            program_name = file_path.stem
            
            # Find copybook references in the program
            copybook_refs = find_copybook_references(program_content)
            
            program_info = {
                'name': program_name,
                'path': str(file_path),
                'content': program_content,
                'related_copybooks': copybook_refs
            }
            
            result['programs'].append(program_info)
            result['file_relationships'][program_name] = copybook_refs
    
    # Extract copybooks
    copybooks_dir = extract_dir / 'src' / 'copybooks'
    if copybooks_dir.exists():
        for copybook_dir in [copybooks_dir] + list(copybooks_dir.glob('*/')):
            for file_path in copybook_dir.glob('*.cpy'):
                copybook_content = file_path.read_text(encoding='utf-8')
                copybook_name = file_path.stem
                
                copybook_info = {
                    'name': copybook_name,
                    'path': str(file_path),
                    'content': copybook_content
                }
                
                result['copybooks'].append(copybook_info)
    
    # Extract other relevant files (JCL, etc.)
    jcl_dir = extract_dir / 'jcl'
    if jcl_dir.exists():
        for file_path in jcl_dir.glob('*.jcl'):
            file_content = file_path.read_text(encoding='utf-8')
            file_name = file_path.stem
            
            file_info = {
                'name': file_name,
                'path': str(file_path),
                'content': file_content,
                'type': 'jcl'
            }
            
            result['other_files'].append(file_info)
    
    # Extract documentation if available
    docs_dir = extract_dir / 'docs'
    if docs_dir.exists():
        for file_path in docs_dir.glob('*.*'):
            if file_path.suffix.lower() in ['.txt', '.md', '.pdf']:
                try:
                    # For text files, read content
                    if file_path.suffix.lower() in ['.txt', '.md']:
                        file_content = file_path.read_text(encoding='utf-8')
                    else:
                        file_content = f"Binary file: {file_path.name}"
                    
                    file_info = {
                        'name': file_path.stem,
                        'path': str(file_path),
                        'content': file_content,
                        'type': 'documentation'
                    }
                    
                    result['other_files'].append(file_info)
                except Exception as e:
                    # Skip files that can't be read
                    pass
    
    return result

def find_copybook_references(program_content: str) -> List[str]:
    """
    Find copybook references in a COBOL program
    
    Args:
        program_content: Content of the COBOL program
        
    Returns:
        List of copybook names referenced in the program
    """
    # Pattern to match COPY statements in COBOL
    copy_pattern = re.compile(r'COPY\s+([A-Za-z0-9-]+)', re.IGNORECASE)
    
    matches = copy_pattern.findall(program_content)
    return list(set(matches))  # Remove duplicates