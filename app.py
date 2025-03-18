import os
import time
import streamlit as st
import re
import json
from dotenv import load_dotenv
from pathlib import Path
# Import the agent classes directly
from agents.data_agent import DataAgent
from agents.analysis_agent import AnalysisAgent
from agents.conversion_agent import ConversionAgent
from utils.java_generator import generate_java_class, generate_project_structure
import tempfile
import zipfile
from collections import OrderedDict
import shutil


# Import utility functions if needed
from utils.file_utils import extract_cobol_files, validate_folder_structure
from utils.java_generator import generate_project_structure

# Load environment variables
load_dotenv()

base_output_path = Path(os.getenv('JAVA_OUTPUT_PATH', r'C:\@Official\Automation\2025 Planning\Agentic AI Handson\Hertz Cobol to Java'))
base_output_path.mkdir(parents=True, exist_ok=True)
java_project_path = base_output_path


# Set page configuration
st.set_page_config(
    page_title="COBOL to Java Converter",
    page_icon="🔄",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        margin-bottom: 1rem;
    }
    .sub-header {
        font-size: 1.5rem;
        font-weight: bold;
        margin-top: 2rem;
        margin-bottom: 1rem;
    }
    .info-box {
        background-color: #f0f2f6;
        border-radius: 0.5rem;
        padding: 1rem;
        margin-bottom: 1rem;
    }
    .success-box {
        background-color: #d1e7dd;
        border-radius: 0.5rem;
        padding: 1rem;
        margin-bottom: 1rem;
    }
    .warning-box {
        background-color: #fff3cd;
        border-radius: 0.5rem;
        padding: 1rem;
        margin-bottom: 1rem;
    }
    .error-box {
        background-color: #f8d7da;
        border-radius: 0.5rem;
        padding: 1rem;
        margin-bottom: 1rem;
    }
</style>
""", unsafe_allow_html=True)




def remove_thinking_block(text):
    """Remove thinking blocks from LLM responses more aggressively"""
    # Try multiple patterns for thinking blocks
    patterns = [
        r'<think>.*?</think>',
        r'<thinking>.*?</thinking>',
        r'\[thinking\].*?\[/thinking\]',
        r'<thought>.*?</thought>',
        r'<reasoning>.*?</reasoning>'
    ]
    
    for pattern in patterns:
        text = re.sub(pattern, '', text, flags=re.DOTALL)
    
    # Also check for thinking blocks in Java code comments
    text = re.sub(r'/\*\s*<think>.*?</think>\s*\*/', '', text, flags=re.DOTALL)
    text = re.sub(r'//\s*<think>.*?', '', text, flags=re.MULTILINE)
    
    # Remove empty lines that might be left
    text = re.sub(r'\n\s*\n', '\n\n', text)
    
    return text.strip()

def extract_json_from_llm_response(response_text):
    """Extract JSON from LLM response"""
    # Remove thinking blocks first
    response_text = remove_thinking_block(response_text)
    
    # Find JSON between code blocks
    json_match = re.search(r'```json\s*([\s\S]*?)```', response_text)
    if json_match:
        return json_match.group(1).strip()
    
    # Try to find any code block
    code_match = re.search(r'```\s*([\s\S]*?)```', response_text)
    if code_match and '"file_name"' in code_match.group(1) and '"content"' in code_match.group(1):
        return code_match.group(1).strip()
    
    # Try to find a JSON object
    json_obj_match = re.search(r'\{\s*"file_name"[\s\S]*"content"[\s\S]*\}', response_text)
    if json_obj_match:
        return json_obj_match.group(0)
    
    return None

def extract_java_from_response(response_text):
    """Extract Java code directly from a response"""
    # Remove thinking blocks first
    response_text = remove_thinking_block(response_text)
    
    # Look for Java code block
    java_match = re.search(r'```java\s*(.*?)```', response_text, re.DOTALL)
    if not java_match:
        # Try without the java tag
        java_match = re.search(r'```\s*(.*?)```', response_text, re.DOTALL)
    
    if java_match:
        java_code = java_match.group(1).strip()
        
        # Extract package name
        package_match = re.search(r'package\s+([\w.]+);', java_code)
        package_name = package_match.group(1) if package_match else "com.conversion.generated"
        
        # Extract class name
        class_match = re.search(r'class\s+(\w+)', java_code)
        class_name = class_match.group(1) if class_match else "GeneratedClass"
        
        # Look for description in the text
        description_match = re.search(r'(We\'ll create a |I\'ll create a |This class )([^.]+)', response_text)
        description = description_match.group(0) if description_match else "Generated Java class"
        
        return {
            "file_name": class_name,
            "package": package_name,
            "content": java_code,
            "description": description
        }
    
    return None

def parse_java_json(json_str):
    """
    More forgiving JSON parser that can handle common formatting issues
    """
    if not json_str:
        raise ValueError("Empty JSON string provided")
    
    # Keep original for error reporting
    original_json = json_str
    
    # Remove markdown code block markers
    json_str = re.sub(r'```(json)?|```', '', json_str).strip()
    
    # Log the JSON for debugging
    with open('raw_json.txt', 'w', encoding='utf-8') as f:
        f.write(json_str)
    
    # Try direct parsing first
    try:
        return json.loads(json_str)
    except:
        pass  # Continue with cleanup attempts
    
    # Try to extract just the content value directly
    try:
        # Find file name
        file_name_match = re.search(r'"file_name"\s*:\s*"([^"]+)"', json_str)
        file_name = file_name_match.group(1) if file_name_match else "GeneratedClass"
        
        # Find package name
        package_match = re.search(r'"package"\s*:\s*"([^"]+)"', json_str)
        package = package_match.group(1) if package_match else "com.conversion.generated"
        
        # Extract content by finding open and close quotes around it
        content_start = json_str.find('"content"') 
        if content_start > 0:
            # Find the opening quote of the content
            quote_start = json_str.find('"', content_start + 10)
            if quote_start > 0:
                # Find the closing quote of the content (accounting for escaped quotes)
                quote_end = -1
                pos = quote_start + 1
                while pos < len(json_str):
                    if json_str[pos] == '"' and json_str[pos-1] != '\\':
                        quote_end = pos
                        break
                    pos += 1
                
                if quote_end > 0:
                    content = json_str[quote_start+1:quote_end]
                    
                    # Unescape any escaped quotes
                    content = content.replace('\\"', '"')
                    
                    # Find description if present
                    description_match = re.search(r'"description"\s*:\s*"([^"]+)"', json_str)
                    description = description_match.group(1) if description_match else "Generated Java class"
                    
                    # Create a properly structured JSON
                    return {
                        "file_name": file_name,
                        "package": package,
                        "content": content,
                        "description": description
                    }
        
        # If direct extraction failed, try a more aggressive approach
        # Extract Java code
        java_match = re.search(r'public\s+class\s+(\w+)', json_str, re.DOTALL)
        if java_match:
            class_name = java_match.group(1)
            
            # Find package statement if present
            package_stmt_match = re.search(r'package\s+([\w.]+);', json_str)
            package_name = package_stmt_match.group(1) if package_stmt_match else "com.conversion.generated"
            
            return {
                "file_name": class_name,
                "package": package_name,
                "content": json_str,  # Use the entire text as content
                "description": "Generated Java class"
            }
    except Exception as e:
        # Log error
        with open('extraction_error.txt', 'w', encoding='utf-8') as f:
            f.write(f"Original JSON:\n{original_json}\n\n")
            f.write(f"Error: {str(e)}")
        
        # Last resort: create a default Java class
        raise ValueError(f"Failed to parse JSON or extract Java code: {str(e)}")


def process_github_repository(repo_url, branch=None, token=None):
    """
    Clone a GitHub repository and prepare it for COBOL processing
    
    Args:
        repo_url: URL of the GitHub repository
        branch: Branch to clone (None for default branch)
        token: GitHub Personal Access Token for private repositories
        
    Returns:
        Path to the processed ZIP file or None if failed
    """
    import tempfile
    import zipfile
    import os
    import subprocess
    import shutil
    from pathlib import Path
    import re
    
    # Extract owner and repo name from URL
    # Example: https://github.com/username/repository
    match = re.match(r'https?://github\.com/([^/]+)/([^/]+)', repo_url)
    if not match:
        st.error("Invalid GitHub repository URL format")
        return None
    
    owner, repo_name = match.groups()
    repo_name = repo_name.strip('/')
    
    try:
        # Create temporary directory for cloning
        temp_dir = tempfile.mkdtemp()
        
        # Prepare git clone command
        if token:
            # Use token for authentication
            auth_url = f"https://{token}@github.com/{owner}/{repo_name}.git"
        else:
            # Public repository
            auth_url = f"https://github.com/{owner}/{repo_name}.git"
        
        # Clone the repository
        clone_cmd = ["git", "clone"]
        
        # Add branch if specified
        if branch:
            clone_cmd.extend(["-b", branch])
        
        # Add depth to speed up cloning
        clone_cmd.extend(["--depth", "1"])
        
        # Add repository URL and target directory
        clone_cmd.extend([auth_url, temp_dir])
        
        # Execute git clone
        subprocess.run(clone_cmd, check=True, capture_output=True)
        
        # Create a zip file of the repository
        zip_path = tempfile.mktemp(suffix='.zip')
        
        # Check if there's a src directory, if not, create one and move COBOL files
        src_dir = Path(temp_dir) / "src"
        if not src_dir.exists():
            # Create proper directory structure for processing
            src_dir.mkdir()
            programs_dir = src_dir / "programs"
            copybooks_dir = src_dir / "copybooks"
            programs_dir.mkdir()
            copybooks_dir.mkdir()
            
            # Find COBOL files in repository
            repo_path = Path(temp_dir)
            cobol_files = list(repo_path.glob('**/*.cbl')) + list(repo_path.glob('**/*.cob'))
            copybook_files = list(repo_path.glob('**/*.cpy'))
            jcl_files = list(repo_path.glob('**/*.jcl'))
            
            # Move COBOL programs to programs directory
            for file in cobol_files:
                shutil.copy2(file, programs_dir / file.name)
            
            # Move copybooks to copybooks directory
            for file in copybook_files:
                shutil.copy2(file, copybooks_dir / file.name)
            
            # Create JCL directory if needed
            if jcl_files:
                jcl_dir = Path(temp_dir) / "jcl"
                jcl_dir.mkdir(exist_ok=True)
                for file in jcl_files:
                    shutil.copy2(file, jcl_dir / file.name)
        
        # Create a ZIP file with the contents
        shutil.make_archive(zip_path[:-4], 'zip', temp_dir)
        
        # Clean up the temp directory
        shutil.rmtree(temp_dir)
        
        return zip_path
    
    except Exception as e:
        import traceback
        st.error(f"Error processing GitHub repository: {str(e)}")
        st.code(traceback.format_exc())
        
        # Clean up on failure
        if 'temp_dir' in locals() and os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)
        
        return None



def main():
    # Header
    st.markdown('<div class="main-header">COBOL to Java Converter</div>', unsafe_allow_html=True)
    st.markdown(
        "Transform your legacy COBOL applications into modern Java code using advanced AI techniques."
    )
    
    # Sidebar
    with st.sidebar:
        st.markdown("## About")
        st.markdown(
            "This application uses GenAI to convert legacy COBOL programs to Java. "
            "Upload your COBOL programs in a structured ZIP file to get started."
        )
        
        st.markdown("## Settings")
        verbose_mode = st.checkbox("Verbose Mode", value=False, help="Show detailed processing information")
        
        st.markdown("## Process Steps")
        st.markdown("1. Upload COBOL ZIP file")
        st.markdown("2. Analyze COBOL program structure")
        st.markdown("3. Extract business logic")
        st.markdown("4. Convert to Java")
        st.markdown("5. Download converted code")
    
    # Main content
    tab1, tab2, tab3 = st.tabs(["Upload & Analyze", "Program Understanding", "Java Conversion"])
    
    with tab1:
        st.markdown('<div class="sub-header">Upload Your COBOL Program</div>', unsafe_allow_html=True)
        
        # Define helper functions
        def process_github_repository(repo_url, branch=None, token=None):
            """
            Clone a GitHub repository and prepare it for COBOL processing
            
            Args:
                repo_url: URL of the GitHub repository
                branch: Branch to clone (None for default branch)
                token: GitHub Personal Access Token for private repositories
                
            Returns:
                Path to the processed ZIP file or None if failed
            """
            import tempfile
            import zipfile
            import os
            import subprocess
            import shutil
            from pathlib import Path
            import re
            
            # Extract owner and repo name from URL
            # Example: https://github.com/username/repository
            match = re.match(r'https?://github\.com/([^/]+)/([^/]+)', repo_url)
            if not match:
                st.error("Invalid GitHub repository URL format")
                return None
            
            owner, repo_name = match.groups()
            repo_name = repo_name.strip('/')
            
            try:
                # Create temporary directory for cloning
                temp_dir = tempfile.mkdtemp()
                
                # Prepare git clone command
                if token:
                    # Use token for authentication
                    auth_url = f"https://{token}@github.com/{owner}/{repo_name}.git"
                else:
                    # Public repository
                    auth_url = f"https://github.com/{owner}/{repo_name}.git"
                
                # Clone the repository
                clone_cmd = ["git", "clone"]
                
                # Add branch if specified
                if branch:
                    clone_cmd.extend(["-b", branch])
                
                # Add depth to speed up cloning
                clone_cmd.extend(["--depth", "1"])
                
                # Add repository URL and target directory
                clone_cmd.extend([auth_url, temp_dir])
                
                # Execute git clone
                subprocess.run(clone_cmd, check=True, capture_output=True)
                
                # Create a zip file of the repository
                zip_path = tempfile.mktemp(suffix='.zip')
                
                # Check if there's a src directory, if not, create one and move COBOL files
                src_dir = Path(temp_dir) / "src"
                if not src_dir.exists():
                    # Create proper directory structure for processing
                    src_dir.mkdir()
                    programs_dir = src_dir / "programs"
                    copybooks_dir = src_dir / "copybooks"
                    programs_dir.mkdir()
                    copybooks_dir.mkdir()
                    
                    # Find COBOL files in repository
                    repo_path = Path(temp_dir)
                    cobol_files = list(repo_path.glob('**/*.cbl')) + list(repo_path.glob('**/*.cob'))
                    copybook_files = list(repo_path.glob('**/*.cpy'))
                    jcl_files = list(repo_path.glob('**/*.jcl'))
                    
                    # Move COBOL programs to programs directory
                    for file in cobol_files:
                        shutil.copy2(file, programs_dir / file.name)
                    
                    # Move copybooks to copybooks directory
                    for file in copybook_files:
                        shutil.copy2(file, copybooks_dir / file.name)
                    
                    # Create JCL directory if needed
                    if jcl_files:
                        jcl_dir = Path(temp_dir) / "jcl"
                        jcl_dir.mkdir(exist_ok=True)
                        for file in jcl_files:
                            shutil.copy2(file, jcl_dir / file.name)
                
                # Create a ZIP file with the contents
                shutil.make_archive(zip_path[:-4], 'zip', temp_dir)
                
                # Clean up the temp directory
                shutil.rmtree(temp_dir)
                
                return zip_path
            
            except Exception as e:
                import traceback
                st.error(f"Error processing GitHub repository: {str(e)}")
                st.code(traceback.format_exc())
                
                # Clean up on failure
                if 'temp_dir' in locals() and os.path.exists(temp_dir):
                    shutil.rmtree(temp_dir)
                
                return None

        def process_single_program_file(zip_file_path):
            """
            Process a ZIP file containing a single COBOL program with dependencies
            
            Args:
                zip_file_path: Path to the uploaded ZIP file
                
            Returns:
                Dictionary containing extraction results
            """
            import tempfile
            import zipfile
            import os
            import shutil
            from pathlib import Path
            
            try:
                # Create temporary directory for structured content
                temp_dir = tempfile.mkdtemp()
                
                # Create the expected directory structure
                structured_dir = Path(temp_dir)
                src_dir = structured_dir / "src"
                src_dir.mkdir(exist_ok=True)
                
                programs_dir = src_dir / "programs"
                programs_dir.mkdir(exist_ok=True)
                
                copybooks_dir = src_dir / "copybooks"
                copybooks_dir.mkdir(exist_ok=True)
                
                # Extract and process the original ZIP file
                with zipfile.ZipFile(zip_file_path, 'r') as zip_ref:
                    # Get list of all files in the ZIP
                    all_files = zip_ref.namelist()
                    
                    # Process each file based on extension
                    for file_path in all_files:
                        file_name = os.path.basename(file_path)
                        
                        # Skip directories
                        if file_name == '' or file_path.endswith('/'):
                            continue
                        
                        # Extract file content
                        file_content = zip_ref.read(file_path)
                        
                        # Determine file type by extension
                        if file_name.lower().endswith(('.cbl', '.cob')):
                            # COBOL program file
                            with open(os.path.join(programs_dir, file_name), 'wb') as f:
                                f.write(file_content)
                                
                        elif file_name.lower().endswith('.cpy'):
                            # Copybook file
                            with open(os.path.join(copybooks_dir, file_name), 'wb') as f:
                                f.write(file_content)
                                
                        elif file_name.lower().endswith('.jcl'):
                            # JCL file - create JCL directory if needed
                            jcl_dir = structured_dir / "jcl"
                            jcl_dir.mkdir(exist_ok=True)
                            
                            with open(os.path.join(jcl_dir, file_name), 'wb') as f:
                                f.write(file_content)
                
                # Create the new structured ZIP file
                structured_zip_path = tempfile.mktemp(suffix='.zip')
                
                with zipfile.ZipFile(structured_zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                    # Recursively add all files from the structured directory
                    for root, _, files in os.walk(structured_dir):
                        for file in files:
                            file_path = os.path.join(root, file)
                            # Calculate relative path (to maintain directory structure)
                            rel_path = os.path.relpath(file_path, structured_dir)
                            zipf.write(file_path, rel_path)
                
                # Skip the DataAgent validation and manually create the expected structure
                extraction_result = {
                    'success': True,
                    'extraction_path': temp_dir,
                    'data': {
                        'programs': [],
                        'copybooks': [],
                        'other_files': [],
                        'file_relationships': {},
                        'metadata': {
                            'num_programs': 0,
                            'num_copybooks': 0,
                            'extraction_path': temp_dir
                        }
                    }
                }
                
                # Find all COBOL programs and add them to the result
                for file_path in programs_dir.glob('*.cbl'):
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                    
                    program_info = {
                        'name': file_path.stem,
                        'path': str(file_path),
                        'content': content,
                        'related_copybooks': []  # We'll populate this later
                    }
                    
                    extraction_result['data']['programs'].append(program_info)
                    extraction_result['data']['metadata']['num_programs'] += 1
                
                # Also check for .cob files
                for file_path in programs_dir.glob('*.cob'):
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                    
                    program_info = {
                        'name': file_path.stem,
                        'path': str(file_path),
                        'content': content,
                        'related_copybooks': []  # We'll populate this later
                    }
                    
                    extraction_result['data']['programs'].append(program_info)
                    extraction_result['data']['metadata']['num_programs'] += 1
                    
                # Find all copybooks and add them to the result
                for file_path in copybooks_dir.glob('*.cpy'):
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                    
                    copybook_info = {
                        'name': file_path.stem,
                        'path': str(file_path),
                        'content': content
                    }
                    
                    extraction_result['data']['copybooks'].append(copybook_info)
                    extraction_result['data']['metadata']['num_copybooks'] += 1
                
                # For each program, try to find referenced copybooks
                for program in extraction_result['data']['programs']:
                    # Look for "COPY" statements in the program content
                    import re
                    copybook_refs = re.findall(r'COPY\s+([A-Za-z0-9-]+)', program['content'], re.IGNORECASE)
                    program['related_copybooks'] = list(set(copybook_refs))
                    
                    # Add to file relationships
                    extraction_result['data']['file_relationships'][program['name']] = program['related_copybooks']
                
                return extraction_result
                    
            except Exception as e:
                import traceback
                st.error(f"Error processing single program: {str(e)}")
                st.code(traceback.format_exc())
                
                # Clean up temporary directory
                if 'temp_dir' in locals() and os.path.exists(temp_dir):
                    shutil.rmtree(temp_dir)
                
                return {
                    'success': False,
                    'error': str(e),
                    'data': None
                }
        
        # Add upload options
        upload_option = st.radio(
            "Select Source",
            ["Upload ZIP File", "Connect to GitHub Repository", "Single COBOL Program"],
            index=0
        )
        
        # ZIP File Upload Option
        if upload_option == "Upload ZIP File":
            st.markdown(
                '<div class="info-box">'
                "<b>Expected ZIP structure:</b><br>"
                "Your ZIP file should follow this structure:<br><br>"
                "```<br>"
                "COBOL_Conversion_Package/<br>"
                "├── src/<br>"
                "│   ├── programs/        # Main COBOL programs (.cbl, .cob)<br>"
                "│   ├── copybooks/       # COBOL copybooks (.cpy)<br>"
                "│   └── proc/            # Procedure division code<br>"
                "├── jcl/                 # Job Control Language files<br>"
                "├── db/                  # Database definitions<br>"
                "└── docs/                # Documentation<br>"
                "```"
                "</div>",
                unsafe_allow_html=True
            )
            
            uploaded_file = st.file_uploader("Upload your COBOL ZIP file", type=["zip"], key="zip_upload")
            
            if uploaded_file is not None:
                # Save uploaded file to temp directory
                with tempfile.NamedTemporaryFile(delete=False, suffix='.zip') as tmp_file:
                    tmp_file.write(uploaded_file.getvalue())
                    zip_file_path = tmp_file.name
                
                st.session_state.zip_file_path = zip_file_path
                st.session_state.upload_source = "zip"
                st.session_state.upload_success = True
                
                st.markdown(
                    '<div class="success-box">'
                    f"Successfully uploaded: {uploaded_file.name}"
                    "</div>",
                    unsafe_allow_html=True
                )
        
        # GitHub Repository Option
        elif upload_option == "Connect to GitHub Repository":
            st.markdown(
                '<div class="info-box">'
                "<b>GitHub Repository Connection:</b><br>"
                "Enter a GitHub repository URL containing COBOL code.<br>"
                "The repository should contain COBOL programs (.cbl, .cob) and related files.<br>"
                "For private repositories, you'll need to provide a personal access token."
                "</div>",
                unsafe_allow_html=True
            )
            
            # GitHub repository URL input
            repo_url = st.text_input("GitHub Repository URL", 
                                placeholder="https://github.com/username/repository")
            
            # Branch selection
            branch = st.text_input("Branch (leave empty for default branch)", 
                            placeholder="main")
            
            # Optional: Personal access token for private repositories
            use_token = st.checkbox("Use Personal Access Token (for private repositories)")
            
            token = None
            if use_token:
                token = st.text_input("GitHub Personal Access Token", type="password")
            
            if st.button("Connect to Repository") and repo_url:
                with st.spinner("Connecting to GitHub repository..."):
                    try:
                        # Process GitHub repository
                        repo_path = process_github_repository(repo_url, branch, token)
                        
                        if repo_path:
                            st.session_state.zip_file_path = repo_path
                            st.session_state.upload_source = "github"
                            st.session_state.upload_success = True
                            
                            st.markdown(
                                '<div class="success-box">'
                                f"Successfully connected to repository: {repo_url}"
                                "</div>",
                                unsafe_allow_html=True
                            )
                        else:
                            st.error("Failed to process GitHub repository")
                    except Exception as e:
                        st.error(f"Error connecting to GitHub: {str(e)}")
        
        # Single COBOL Program Option
        elif upload_option == "Single COBOL Program":
            st.markdown(
                '<div class="info-box">'
                "<b>Single COBOL Program Upload:</b><br>"
                "Please upload a ZIP file containing:<br><br>"
                "```<br>"
                "- Your main COBOL program (.cbl or .cob file)<br>"
                "- Any copybooks (.cpy files) referenced by the program<br>"
                "- Optional JCL files (.jcl) if available<br>"
                "```<br><br>"
                "The files can be in a flat structure - no specific folders required."
                "</div>",
                unsafe_allow_html=True
            )
            
            uploaded_file = st.file_uploader("Upload your COBOL files as ZIP", type=["zip"], key="single_upload")
            
            if uploaded_file is not None:
                # Save uploaded file to temp directory
                with tempfile.NamedTemporaryFile(delete=False, suffix='.zip') as tmp_file:
                    tmp_file.write(uploaded_file.getvalue())
                    zip_file_path = tmp_file.name
                
                st.session_state.zip_file_path = zip_file_path
                st.session_state.upload_source = "single"
                st.session_state.upload_success = True
                
                st.markdown(
                    '<div class="success-box">'
                    f"Successfully uploaded: {uploaded_file.name}"
                    "</div>",
                    unsafe_allow_html=True
                )
        
        # Common process button for all upload options
        if 'upload_success' in st.session_state and st.session_state.upload_success:
            if st.button("Process COBOL Files"):
                with st.spinner("Extracting and analyzing COBOL files..."):
                    # Initialize the data agent
                    data_agent = DataAgent(verbose=verbose_mode)
                    
                    # Process based on upload source
                    upload_source = st.session_state.get('upload_source', 'zip')
                    
                    if upload_source == "github" or upload_source == "single":
                        # For GitHub or single program sources, use special processing
                        if upload_source == "single":
                            extraction_result = process_single_program_file(st.session_state.zip_file_path)
                        else:  # github
                            extraction_result = data_agent.process({
                                'zip_file_path': st.session_state.zip_file_path
                            })
                    else:  # Regular ZIP upload
                        extraction_result = data_agent.process({
                            'zip_file_path': st.session_state.zip_file_path
                        })
                    
                    # Store the extraction result in session state
                    st.session_state.extraction_result = extraction_result
                    
                    if extraction_result['success']:
                        st.success("COBOL files successfully processed!")
                        
                        # Display metadata
                        metadata = extraction_result['data']['metadata']
                        st.markdown("### Program Summary")
                        st.markdown(f"- Number of COBOL programs: {metadata['num_programs']}")
                        st.markdown(f"- Number of copybooks: {metadata['num_copybooks']}")
                        
                        # Store programs in session state for display
                        st.session_state.programs = extraction_result['data']['programs']
                        
                        # Analyze programs if automated analysis is enabled
                        with st.spinner("Analyzing COBOL programs..."):
                            analysis_agent = AnalysisAgent(verbose=verbose_mode)
                            analysis_result = analysis_agent.process(extraction_result)
                            
                            # Store the analysis result in session state
                            st.session_state.analysis_result = analysis_result
                            
                            if analysis_result['success']:
                                st.success("Program analysis complete!")
                            else:
                                st.error(f"Error analyzing programs: {analysis_result.get('error', 'Unknown error')}")
                    else:
                        st.error(f"Error processing COBOL files: {extraction_result.get('error', 'Unknown error')}")
    
    with tab2:
        st.markdown('<div class="sub-header">Program Understanding</div>', unsafe_allow_html=True)
        
        if 'analysis_result' in st.session_state and st.session_state.analysis_result['success']:
            program_analyses = st.session_state.analysis_result['analysis']
            
            # Program selector
            if len(program_analyses) > 0:
                program_names = [analysis['program_name'] for analysis in program_analyses]
                selected_program = st.selectbox("Select COBOL Program", program_names)
                
                # Find the selected program analysis
                selected_analysis = next(
                    (analysis for analysis in program_analyses if analysis['program_name'] == selected_program),
                    None
                )
                
                if selected_analysis:
                    st.markdown("### Program Overview")
                    st.markdown(selected_analysis['functional_analysis'])
                    
                    st.markdown("### Business Rules")
                    st.markdown(selected_analysis['business_rules'])
                    
                    # User confirmation - Add unique key here
                    st.markdown("### Confirm Analysis")
                    
                    if st.button("Confirm and Continue", key="tab2_analysis_confirm_unique"):
                        st.session_state.analysis_confirmed = True
                        st.success("Analysis confirmed! Proceed to Java Conversion tab to convert the program.")
            else:
                st.warning("No programs have been analyzed yet. Please process COBOL files first.")
        else:
            st.info("No analysis available. Please upload and process COBOL files first.")

    with tab3:
        try:
            st.markdown('<div class="sub-header">Java Conversion</div>', unsafe_allow_html=True)

            def get_standard_package(program_name):
                """Generate a standardized package name for a given program"""
                # Convert to lowercase and remove any special characters
                safe_name = ''.join(c.lower() if c.isalnum() else '' for c in program_name)
                return f"com.conversion.{safe_name}"
            
            def display_java_structure(java_classes):
                """
                Display the Java project folder structure in a tree-like format
                
                Args:
                    java_classes: List of generated Java classes with package information
                """

                
                if not java_classes:
                    return "No Java classes generated yet."
                
                # Group classes by package and deduplicate
                packages = {}
                class_tracker = set()  # Track classes that have already been added
                
                for java_class in java_classes:
                    package = java_class.get("package", "default")
                    class_name = java_class["name"]
                    
                    # Create a unique key for this class
                    class_key = f"{package}.{class_name}"
                    
                    # Skip if we've already processed this class
                    if class_key in class_tracker:
                        continue
                    
                    # Add to tracker and packages
                    class_tracker.add(class_key)
                    if package not in packages:
                        packages[package] = []
                    packages[package].append(class_name)
                
                # Build folder structure representation
                structure = ["📁 src", "  📁 main", "    📁 java"]
                
                for package, classes in sorted(packages.items()):
                    # Split package into folder hierarchy
                    folders = package.split(".")
                    indent = "      "
                    
                    # Add package folders with proper indentation
                    for i, folder in enumerate(folders):
                        structure.append(f"{indent}📁 {folder}")
                        indent += "  "
                    
                    # Add classes under the package
                    for class_name in sorted(classes):
                        structure.append(f"{indent}📄 {class_name}.java")
                
                return "\n".join(structure)
            
            # Check if analysis is confirmed
            if 'analysis_confirmed' not in st.session_state:
                st.info("Please complete the analysis in the 'Program Understanding' tab first.")
            else:
                # Initialize conversion progress if not already done
                if 'conversion_progress' not in st.session_state:
                    st.session_state.conversion_progress = {
                        "steps_completed": 0,
                        "total_steps": 0,
                        "results": {},
                        "java_classes": [],
                        "step_status": {}  # Track status of each step
                    }
                    st.session_state.current_step = 0
                
                # Check if we have analysis data
                if 'analysis_result' in st.session_state and st.session_state.analysis_result['success']:
                    # Get program data
                    program_analyses = st.session_state.analysis_result['analysis']
                    
                    # Program selector
                    if len(program_analyses) > 0:
                        program_names = [analysis['program_name'] for analysis in program_analyses]
                        selected_program = st.selectbox("Select COBOL Program to Convert", 
                                                    program_names, 
                                                    key="tab3_program_selector")
                        
                        # Find the selected program analysis
                        selected_analysis = next(
                            (analysis for analysis in program_analyses if analysis['program_name'] == selected_program),
                            None
                        )
                        
                        if selected_analysis:
                            # Define conversion steps
                            conversion_steps = [
                                "Generate main Java class",
                                "Generate supporting classes",
                                "Generate data models",
                                "Generate utility functions",
                                "Generate package structure"
                            ]
                            
                            # Initialize conversion state if new program selected
                            if ('current_program' not in st.session_state or 
                                st.session_state.current_program != selected_program):
                                
                                st.session_state.current_program = selected_program
                                st.session_state.conversion_progress = {
                                    "steps_completed": 0,
                                    "total_steps": len(conversion_steps),
                                    "results": {},
                                    "java_classes": [],
                                    "step_status": {}
                                }
                                st.session_state.current_step = 0
                            
                            # Display progress
                            progress_value = st.session_state.conversion_progress["steps_completed"] / len(conversion_steps)
                            st.progress(progress_value)
                            
                            # Display step status overview
                            st.markdown("### Conversion Steps Status")
                            status_cols = st.columns(len(conversion_steps))
                            
                            for idx, col in enumerate(status_cols):
                                step_status = st.session_state.conversion_progress["step_status"].get(idx, {"status": "pending"})
                                status = step_status.get("status", "pending")
                                
                                if status == "success":
                                    col.success(f"Step {idx+1}")
                                elif status == "error":
                                    col.error(f"Step {idx+1}")
                                else:
                                    col.info(f"Step {idx+1}")
                            
                            # Process current step
                            current_step = st.session_state.current_step
                            if current_step < len(conversion_steps):
                                current_step_text = conversion_steps[current_step]
                                
                                st.markdown(f"### Current Step: {current_step_text}")
                                
                                # Only show action button if not already converting
                                if 'is_converting' not in st.session_state or not st.session_state.is_converting:
                                    execute_btn = st.button(f"Execute Step {current_step + 1}: {current_step_text}")
                                    
                                    if execute_btn:
                                        st.session_state.is_converting = True
                                        
                                        # Create a progress indicator
                                        progress_bar = st.progress(0)
                                        status_text = st.empty()
                                        
                                        try:
                                            # Update status
                                            status_text.info("Preparing conversion...")
                                            progress_bar.progress(10)
                                            
                                            # Get inputs for conversion
                                            cobol_code = selected_analysis.get('cobol_code', '')
                                            business_rules = selected_analysis.get('business_rules', '')
                                            functional_analysis = selected_analysis.get('functional_analysis', '')
                                            
                                            # Update status
                                            status_text.info("Building prompt...")
                                            progress_bar.progress(20)
                                            
                                            # Build step prompt

                                            # Build step prompt
                                            step_prompt = f"""
                                            You are an expert COBOL to Java conversion specialist. 
                                            Convert the following COBOL program to a well-structured Java class:

                                            Program Name: {selected_program}

                                            Business Rules:
                                            {business_rules}

                                            Functional Analysis:
                                            {functional_analysis}

                                            Current Step: {current_step_text}

                                            IMPORTANT: Use the package name "{get_standard_package(selected_program)}" for all generated code.

                                            The output should be a JSON object with the following structure:
                                            {{
                                                "file_name": "ClassName",
                                                "package": "{get_standard_package(selected_program)}",
                                                "content": "Full Java source code",
                                                "description": "Brief description of the class"
                                            }}

                                            Focus on modern Java practices, maintain clean code, and follow Java naming conventions.
                                            """

                                            
                                            # Initialize agent
                                            status_text.info("Initializing conversion agent...")
                                            progress_bar.progress(30)
                                            
                                            conversion_agent = ConversionAgent(verbose=False)
                                            
                                            # Invoke agent
                                            status_text.info("Generating Java code (this may take a minute)...")
                                            progress_bar.progress(40)
                                            
                                            step_result = conversion_agent.invoke(step_prompt)
                                            
                                            # Process results
                                            status_text.info("Processing response...")
                                            progress_bar.progress(60)
                                            
                                            clean_result = remove_thinking_block(step_result)
                                            
                                            # Extract JSON from response
                                            json_str = extract_json_from_llm_response(clean_result)
                                            
                                            # If no JSON found, try to extract Java code directly
                                            if not json_str:
                                                status_text.warning("JSON extraction failed, trying direct Java extraction...")
                                                file_info = extract_java_from_response(clean_result)
                                                
                                                if not file_info:
                                                    # Save response for debugging
                                                    debug_file = f'response_debug_{time.strftime("%Y%m%d%H%M%S")}.txt'
                                                    with open(debug_file, 'w', encoding='utf-8') as f:
                                                        f.write(clean_result)
                                                    
                                                    # Update step status
                                                    st.session_state.conversion_progress["step_status"][current_step] = {
                                                        "status": "error",
                                                        "message": "Could not extract valid data from response",
                                                        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
                                                    }
                                                    
                                                    status_text.error("Could not extract valid data from response")
                                                    st.error("Could not extract valid data from the response. Check debug file.")
                                                    st.session_state.is_converting = False
                                                    return
                                            else:
                                                # Parse JSON
                                                status_text.info("Parsing JSON...")
                                                file_info = parse_java_json(json_str)
                                                
                                                # Enforce standard package name
                                                if file_info and "package" in file_info:
                                                    file_info["package"] = get_standard_package(selected_program)
                                            
                                            # Create Java file
                                            status_text.info("Creating Java file...")
                                            progress_bar.progress(80)
                                            
                                            # Create directory structure
                                            package_path = file_info.get("package", "com.generated").replace(".", "/")
                                            file_dir = java_project_path / "src" / "main" / "java" / package_path
                                            file_dir.mkdir(parents=True, exist_ok=True)
                                            
                                            # Write the Java file
                                            file_path = file_dir / f"{file_info['file_name']}.java"
                                            
                                            # Ensure content has package declaration
                                            content = file_info["content"]
                                            if not content.startswith("package"):
                                                content = f"package {file_info['package']};\n\n{content}"
                                            
                                            with open(file_path, "w", encoding='utf-8') as f:
                                                f.write(content)
                                            
                                            # Update progress
                                            progress_bar.progress(100)
                                            status_text.success("Step completed successfully!")
                                            
                                            # Update conversion progress
                                            st.session_state.conversion_progress["results"][current_step] = {
                                                "step": current_step_text,
                                                "output": f"Created {file_info['file_name']}.java in package {file_info['package']}",
                                                "description": file_info.get("description", ""),
                                                "file_path": str(file_path)
                                            }
                                            
                                            # Track Java class
                                            st.session_state.conversion_progress["java_classes"].append({
                                                "name": file_info["file_name"],
                                                "path": str(file_path),
                                                "package": file_info["package"],
                                                "step_index": current_step
                                            })
                                            
                                            # Update step status
                                            st.session_state.conversion_progress["step_status"][current_step] = {
                                                "status": "success",
                                                "message": f"Created {file_info['file_name']}.java in package {file_info['package']}",
                                                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
                                            }
                                            
                                            # Update progress counters
                                            st.session_state.conversion_progress["steps_completed"] += 1
                                            st.session_state.current_step += 1
                                            
                                            st.success(f"Step {current_step + 1} completed: Created {file_info['file_name']}.java")
                                            
                                        except Exception as e:
                                            import traceback
                                            error_details = traceback.format_exc()
                                            
                                            # Log error to file
                                            error_file = f'error_{time.strftime("%Y%m%d%H%M%S")}.txt'
                                            with open(error_file, 'w', encoding='utf-8') as f:
                                                f.write(f"Error: {str(e)}\n\n")
                                                f.write(f"Stack trace:\n{error_details}\n\n")
                                                if 'step_result' in locals():
                                                    f.write(f"Response:\n{step_result}")
                                            
                                            # Update step status
                                            st.session_state.conversion_progress["step_status"][current_step] = {
                                                "status": "error",
                                                "message": str(e),
                                                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                                                "error_file": error_file
                                            }
                                            
                                            # Show error in UI
                                            status_text.error(f"Error: {str(e)}")
                                            st.error(f"Error in Step {current_step + 1}: {str(e)}")
                                            st.info(f"Error details saved to {error_file}")
                                            
                                        finally:
                                            # Always reset the conversion flag
                                            st.session_state.is_converting = False
                                            st.rerun()
                                else:
                                    st.info("Conversion in progress...")
                            
                            # Display detailed step status
                            st.markdown("### Steps Details")
                            if st.session_state.conversion_progress["java_classes"]:
                                st.markdown("### Current Java Project Structure")
                                structure = display_java_structure(st.session_state.conversion_progress["java_classes"])
                                st.code(structure, language="")
                            for step_idx in range(len(conversion_steps)):
                                step_text = conversion_steps[step_idx]
                                
                                # Get step status
                                step_status = st.session_state.conversion_progress["step_status"].get(step_idx, {"status": "pending"})
                                status = step_status.get("status", "pending")
                                
                                if status == "success":
                                    with st.expander(f"✅ Step {step_idx + 1}: {step_text} - Completed"):
                                        st.success(step_status.get("message", "Step completed successfully"))
                                        st.markdown(f"**Completed at:** {step_status.get('timestamp', 'Unknown')}")
                                        
                                        # Display result details if available
                                        if str(step_idx) in st.session_state.conversion_progress["results"]:
                                            result = st.session_state.conversion_progress["results"][str(step_idx)]
                                            st.markdown(f"**Output:** {result['output']}")
                                            st.markdown(f"**Description:** {result['description']}")
                                            
                                            # Show code if available
                                            file_path = result.get("file_path")
                                            if file_path and os.path.exists(file_path):
                                                with open(file_path, "r", encoding="utf-8") as f:
                                                    java_code = f.read()
                                                st.markdown("**Generated Java Code:**")
                                                st.code(java_code, language="java")
                                
                                elif status == "error":
                                    with st.expander(f"❌ Step {step_idx + 1}: {step_text} - Failed"):
                                        st.error(step_status.get("message", "Step failed"))
                                        st.markdown(f"**Failed at:** {step_status.get('timestamp', 'Unknown')}")
                                        
                                        # Show error file link if available
                                        error_file = step_status.get("error_file")
                                        if error_file and os.path.exists(error_file):
                                            st.markdown(f"**Error details:** {error_file}")
                                
                                elif step_idx < st.session_state.current_step:
                                    with st.expander(f"⏳ Step {step_idx + 1}: {step_text} - In Progress"):
                                        st.info("This step is currently in progress")
                                
                                else:
                                    with st.expander(f"⏳ Step {step_idx + 1}: {step_text} - Pending"):
                                        st.info("This step has not been started yet")
                            
                            # Display download section if all steps complete
                            if st.session_state.conversion_progress["steps_completed"] == len(conversion_steps):
                                st.markdown("### Java Conversion Complete!")
                                if st.session_state.conversion_progress["steps_completed"] == len(conversion_steps):
                                    st.markdown("### Java Conversion Complete!")
                                    st.success(f"All {len(conversion_steps)} steps completed successfully. You can now download the converted Java code.")
                                    
                                    # Add this new section to display the Java structure
                                    st.markdown("### Java Project Structure")
                                    structure = display_java_structure(st.session_state.conversion_progress["java_classes"])
                                    st.code(structure, language="")
                                    
                                    st.info("""
                                    This is the folder structure of your converted Java project. 
                                    The structure follows standard Maven/Gradle conventions with:
                                    - Source code under src/main/java
                                    - Packages organized by domain
                                    - Each Java class in its corresponding package folder
                                    """)
                                st.success(f"All {len(conversion_steps)} steps completed successfully. You can now download the converted Java code.")
                                
                                try:
                                    import io
                                    
                                    # Create a buffer for the ZIP file
                                    zip_buffer = io.BytesIO()
                                    
                                    # Write files to the ZIP
                                  # Write files to the ZIP
                                    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zipf:
                                        # Add all Java files (deduplicating by class name)
                                        added_files = set()
                                        for java_class in st.session_state.conversion_progress["java_classes"]:
                                            if os.path.exists(java_class["path"]):
                                                class_key = f"{java_class['package']}.{java_class['name']}"
                                                
                                                # Skip if already added
                                                if class_key in added_files:
                                                    continue
                                                    
                                                added_files.add(class_key)
                                                zipf.write(
                                                    java_class["path"],
                                                    arcname=f"java/{java_class['package'].replace('.', '/')}/{java_class['name']}.java"
                                                )
                                        
                                        # Add README file
                                        # (Keep your existing README code)
                                        # Add README file
                                        readme_content = f"""# Converted Java Project: {selected_program}

    This project was automatically converted from COBOL to Java.

    ## Generated Classes:
    """
                                        for java_class in st.session_state.conversion_progress["java_classes"]:
                                            readme_content += f"- {java_class['package']}.{java_class['name']}\n"
                                        
                                        zipf.writestr("README.md", readme_content)
                                    
                                    # Reset buffer position and create download button
                                    zip_buffer.seek(0)
                                    
                                    # Provide download button
                                    st.download_button(
                                        label="Download Java Project",
                                        data=zip_buffer.getvalue(),
                                        file_name=f"{selected_program}_java.zip",
                                        mime="application/zip"
                                    )
                                    
                                except Exception as e:
                                    import traceback
                                    st.error(f"Error creating download file: {str(e)}")
                                    st.code(traceback.format_exc())
                                    st.info("Try refreshing the page and completing the conversion again.")
                        else:
                            st.warning("Could not find the selected program analysis. Please try again.")
                    else:
                        st.warning("No programs have been analyzed yet. Please process COBOL files first.")
                else:
                    st.info("No analysis available. Please upload and process COBOL files first.")
                    
        except Exception as e:
            import traceback
            
            # Log the full error
            error_file = f'critical_error_{time.strftime("%Y%m%d%H%M%S")}.txt'
            with open(error_file, 'w', encoding='utf-8') as f:
                f.write(f"Critical Error: {str(e)}\n\n")
                f.write(traceback.format_exc())
            
            # Show error in UI
            st.error(f"A critical error occurred: {str(e)}")
            st.error(f"Error details saved to {error_file}")
            st.code(traceback.format_exc(), language="python")

if __name__ == "__main__":
    main()