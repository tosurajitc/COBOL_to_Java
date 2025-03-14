import re
from typing import Dict, List, Any, Optional

def extract_program_structure(program_content: str, copybooks: List[Dict[str, str]]) -> Dict[str, Any]:
    """
    Extract the structure of a COBOL program
    
    Args:
        program_content: Content of the COBOL program
        copybooks: List of copybooks with their content
        
    Returns:
        Dictionary containing the program structure
    """
    structure = {
        'identification': extract_identification_division(program_content),
        'environment': extract_environment_division(program_content),
        'data': extract_data_division(program_content, copybooks),
        'procedure': extract_procedure_division(program_content)
    }
    
    return structure

def extract_identification_division(program_content: str) -> Dict[str, str]:
    """
    Extract information from the IDENTIFICATION DIVISION
    
    Args:
        program_content: Content of the COBOL program
        
    Returns:
        Dictionary containing identification information
    """
    identification = {}
    
    # Extract PROGRAM-ID
    program_id_match = re.search(
        r'PROGRAM-ID\s*\.\s*([A-Za-z0-9-]+)',
        program_content,
        re.IGNORECASE
    )
    if program_id_match:
        identification['program_id'] = program_id_match.group(1).strip()
    
    # Extract AUTHOR
    author_match = re.search(
        r'AUTHOR\s*\.\s*(.+?)\.(?=\s|$|\n)',
        program_content,
        re.IGNORECASE
    )
    if author_match:
        identification['author'] = author_match.group(1).strip()
    
    # Extract DATE-WRITTEN
    date_written_match = re.search(
        r'DATE-WRITTEN\s*\.\s*(.+?)\.(?=\s|$|\n)',
        program_content,
        re.IGNORECASE
    )
    if date_written_match:
        identification['date_written'] = date_written_match.group(1).strip()
    
    return identification

def extract_environment_division(program_content: str) -> Dict[str, Any]:
    """
    Extract information from the ENVIRONMENT DIVISION
    
    Args:
        program_content: Content of the COBOL program
        
    Returns:
        Dictionary containing environment information
    """
    environment = {
        'file_control': [],
        'input_output': {}
    }
    
    # Extract ENVIRONMENT DIVISION section
    env_match = re.search(
        r'ENVIRONMENT\s+DIVISION\s*\.(.+?)(?=DATA\s+DIVISION|PROCEDURE\s+DIVISION|\Z)',
        program_content,
        re.IGNORECASE | re.DOTALL
    )
    
    if not env_match:
        return environment
    
    env_content = env_match.group(1)
    
    # Extract FILE-CONTROL entries
    file_control_match = re.search(
        r'FILE-CONTROL\s*\.(.+?)(?=INPUT-OUTPUT\s+SECTION|\Z)',
        env_content,
        re.IGNORECASE | re.DOTALL
    )
    
    if file_control_match:
        file_control_content = file_control_match.group(1)
        
        # Find SELECT statements
        select_pattern = re.compile(
            r'SELECT\s+([A-Za-z0-9-]+).+?(?=SELECT|\Z)',
            re.IGNORECASE | re.DOTALL
        )
        
        for select_match in select_pattern.finditer(file_control_content):
            select_statement = select_match.group(0)
            file_name = select_match.group(1).strip()
            
            # Extract ASSIGN TO
            assign_match = re.search(
                r'ASSIGN\s+TO\s+([A-Za-z0-9-]+)',
                select_statement,
                re.IGNORECASE
            )
            
            assign_to = assign_match.group(1).strip() if assign_match else ""
            
            # Extract ORGANIZATION
            org_match = re.search(
                r'ORGANIZATION\s+IS\s+([A-Za-z0-9-]+)',
                select_statement,
                re.IGNORECASE
            )
            
            organization = org_match.group(1).strip() if org_match else ""
            
            # Extract ACCESS MODE
            access_match = re.search(
                r'ACCESS\s+MODE\s+IS\s+([A-Za-z0-9-]+)',
                select_statement,
                re.IGNORECASE
            )
            
            access_mode = access_match.group(1).strip() if access_match else ""
            
            file_info = {
                'file_name': file_name,
                'assign_to': assign_to,
                'organization': organization,
                'access_mode': access_mode
            }
            
            environment['file_control'].append(file_info)
    
    return environment

def extract_data_division(program_content: str, copybooks: List[Dict[str, str]]) -> Dict[str, Any]:
    """
    Extract information from the DATA DIVISION
    
    Args:
        program_content: Content of the COBOL program
        copybooks: List of copybooks with their content
        
    Returns:
        Dictionary containing data division information
    """
    data_division = {
        'file_section': [],
        'working_storage': [],
        'linkage_section': []
    }
    
    # Extract DATA DIVISION section
    data_match = re.search(
        r'DATA\s+DIVISION\s*\.(.+?)(?=PROCEDURE\s+DIVISION|\Z)',
        program_content,
        re.IGNORECASE | re.DOTALL
    )
    
    if not data_match:
        return data_division
    
    data_content = data_match.group(1)
    
    # Extract FILE SECTION
    file_section_match = re.search(
        r'FILE\s+SECTION\s*\.(.+?)(?=WORKING-STORAGE\s+SECTION|LINKAGE\s+SECTION|\Z)',
        data_content,
        re.IGNORECASE | re.DOTALL
    )
    
    if file_section_match:
        file_section_content = file_section_match.group(1)
        data_division['file_section'] = extract_data_items(file_section_content, copybooks)
    
    # Extract WORKING-STORAGE SECTION
    ws_match = re.search(
        r'WORKING-STORAGE\s+SECTION\s*\.(.+?)(?=FILE\s+SECTION|LINKAGE\s+SECTION|\Z)',
        data_content,
        re.IGNORECASE | re.DOTALL
    )
    
    if ws_match:
        ws_content = ws_match.group(1)
        data_division['working_storage'] = extract_data_items(ws_content, copybooks)
    
    # Extract LINKAGE SECTION
    linkage_match = re.search(
        r'LINKAGE\s+SECTION\s*\.(.+?)(?=FILE\s+SECTION|WORKING-STORAGE\s+SECTION|\Z)',
        data_content,
        re.IGNORECASE | re.DOTALL
    )
    
    if linkage_match:
        linkage_content = linkage_match.group(1)
        data_division['linkage_section'] = extract_data_items(linkage_content, copybooks)
    
    return data_division

def extract_data_items(section_content: str, copybooks: List[Dict[str, str]]) -> List[Dict[str, Any]]:
    """
    Extract data items from a DATA DIVISION section
    
    Args:
        section_content: Content of the section
        copybooks: List of copybooks with their content
        
    Returns:
        List of data items
    """
    data_items = []
    
    # Handle COPY statements first
    for copybook in copybooks:
        copy_pattern = re.compile(
            r'COPY\s+' + re.escape(copybook['name']) + r'\s*\.',
            re.IGNORECASE
        )
        
        section_content = copy_pattern.sub(copybook['content'], section_content)
    
    # Parse data items
    # Pattern to match level numbers and data names
    data_item_pattern = re.compile(
        r'^\s*(\d{2})\s+([A-Za-z0-9-]+)(.+?)(?=^\s*\d{2}|\Z)',
        re.IGNORECASE | re.MULTILINE | re.DOTALL
    )
    
    for item_match in data_item_pattern.finditer(section_content):
        level = item_match.group(1).strip()
        name = item_match.group(2).strip()
        definition = item_match.group(3).strip()
        
        # Extract PIC clause if present
        pic_match = re.search(
            r'PIC\s+([XS9()/V.]+)',
            definition,
            re.IGNORECASE
        )
        
        pic_clause = pic_match.group(1).strip() if pic_match else ""
        
        # Extract USAGE clause if present
        usage_match = re.search(
            r'USAGE\s+(?:IS\s+)?([A-Za-z0-9-]+)',
            definition,
            re.IGNORECASE
        )
        
        usage = usage_match.group(1).strip() if usage_match else ""
        
        # Extract VALUE clause if present
        value_match = re.search(
            r'VALUE\s+(?:IS\s+)?([^\s\.]+)',
            definition,
            re.IGNORECASE
        )
        
        value = value_match.group(1).strip() if value_match else ""
        
        data_item = {
            'level': level,
            'name': name,
            'pic': pic_clause,
            'usage': usage,
            'value': value,
            'definition': definition
        }
        
        data_items.append(data_item)
    
    return data_items

def extract_procedure_division(program_content: str) -> Dict[str, Any]:
    """
    Extract information from the PROCEDURE DIVISION
    
    Args:
        program_content: Content of the COBOL program
        
    Returns:
        Dictionary containing procedure division information
    """
    procedure = {
        'paragraphs': []
    }
    
    # Extract PROCEDURE DIVISION section
    proc_match = re.search(
        r'PROCEDURE\s+DIVISION(?:\s+[^\.]+)?\s*\.(.+)',
        program_content,
        re.IGNORECASE | re.DOTALL
    )
    
    if not proc_match:
        return procedure
    
    proc_content = proc_match.group(1)
    
    # Extract paragraphs
    paragraph_pattern = re.compile(
        r'([A-Za-z0-9-]+)\s*\.\s*(.+?)(?=\s+[A-Za-z0-9-]+\s*\.|$)',
        re.IGNORECASE | re.DOTALL
    )
    
    for para_match in paragraph_pattern.finditer(proc_content):
        name = para_match.group(1).strip()
        content = para_match.group(2).strip()
        
        # Skip if this is a section header
        if "SECTION" in name.upper():
            continue
        
        paragraph = {
            'name': name,
            'content': content,
            'statements': extract_statements(content)
        }
        
        procedure['paragraphs'].append(paragraph)
    
    return procedure

def extract_statements(paragraph_content: str) -> List[Dict[str, str]]:
    """
    Extract COBOL statements from paragraph content
    
    Args:
        paragraph_content: Content of the paragraph
        
    Returns:
        List of statements
    """
    statements = []
    
    # Common COBOL statements to look for
    statement_patterns = [
        (r'IF\s+(.+?)\s+THEN(.+?)(?:ELSE(.+?))?END-IF', 'IF'),
        (r'PERFORM\s+(.+?)(?:UNTIL|VARYING|TIMES|\s*\Z)', 'PERFORM'),
        (r'MOVE\s+(.+?)\s+TO\s+(.+?)(?:\s|\.|\Z)', 'MOVE'),
        (r'OPEN\s+(.+?)(?:\s|\.|\Z)', 'OPEN'),
        (r'CLOSE\s+(.+?)(?:\s|\.|\Z)', 'CLOSE'),
        (r'READ\s+(.+?)(?:NEXT|END-READ|\s|\.|\Z)', 'READ'),
        (r'WRITE\s+(.+?)(?:FROM|END-WRITE|\s|\.|\Z)', 'WRITE'),
        (r'COMPUTE\s+(.+?)(?:\s|\.|\Z)', 'COMPUTE'),
        (r'DISPLAY\s+(.+?)(?:\s|\.|\Z)', 'DISPLAY'),
        (r'CALL\s+(.+?)(?:USING|END-CALL|\s|\.|\Z)', 'CALL')
    ]
    
    for pattern, stmt_type in statement_patterns:
        stmt_regex = re.compile(pattern, re.IGNORECASE | re.DOTALL)
        
        for stmt_match in stmt_regex.finditer(paragraph_content):
            full_stmt = stmt_match.group(0).strip()
            
            statement = {
                'type': stmt_type,
                'content': full_stmt
            }
            
            statements.append(statement)
    
    return statements