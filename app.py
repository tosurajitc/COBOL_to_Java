import os
import tempfile
import time
from pathlib import Path
import streamlit as st
from dotenv import load_dotenv

from agents.data_agent import DataAgent
from agents.analysis_agent import AnalysisAgent
from agents.conversion_agent import ConversionAgent

# Load environment variables
load_dotenv()

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
        
        uploaded_file = st.file_uploader("Upload your COBOL ZIP file", type=["zip"])
        
        if uploaded_file is not None:
            # Save uploaded file to temp directory
            with tempfile.NamedTemporaryFile(delete=False, suffix='.zip') as tmp_file:
                tmp_file.write(uploaded_file.getvalue())
                zip_file_path = tmp_file.name
            
            st.session_state.zip_file_path = zip_file_path
            st.session_state.upload_success = True
            
            st.markdown(
                '<div class="success-box">'
                f"Successfully uploaded: {uploaded_file.name}"
                "</div>",
                unsafe_allow_html=True
            )
            
            if st.button("Process COBOL Files"):
                with st.spinner("Extracting and analyzing COBOL files..."):
                    # Initialize the data agent
                    data_agent = DataAgent(verbose=verbose_mode)
                    
                    # Process the uploaded file
                    extraction_result = data_agent.process({
                        'zip_file_path': zip_file_path
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
                    
                    # User confirmation
                    st.markdown("### Confirm Analysis")
                    
                    if st.button("Confirm and Continue to Conversion"):
                        st.session_state.analysis_confirmed = True
                        st.success("Analysis confirmed! Proceed to Java Conversion tab to convert the program.")
            else:
                st.warning("No programs have been analyzed yet. Please process COBOL files first.")
        else:
            st.info("No analysis available. Please upload and process COBOL files first.")
    
    with tab3:
        st.markdown('<div class="sub-header">Java Conversion</div>', unsafe_allow_html=True)
        
        if 'analysis_result' in st.session_state and st.session_state.analysis_result['success']:
            if st.session_state.get('analysis_confirmed', False):
                program_analyses = st.session_state.analysis_result['analysis']
                program_names = [analysis['program_name'] for analysis in program_analyses]
                
                selected_program = st.selectbox(
                    "Select COBOL Program to Convert", 
                    program_names, 
                    key="conversion_program_selector"
                )
                
                if st.button("Convert to Java"):
                    with st.spinner("Converting COBOL to Java..."):
                        # Initialize the conversion agent
                        conversion_agent = ConversionAgent(verbose=verbose_mode)
                        
                        # Convert the program
                        conversion_result = conversion_agent.process(st.session_state.analysis_result)
                        
                        # Store the conversion result in session state
                        st.session_state.conversion_result = conversion_result
                        
                        if conversion_result['success']:
                            st.success("Conversion to Java complete!")
                            
                            # Find the selected program conversion
                            selected_conversion = next(
                                (conv for conv in conversion_result['conversion'] 
                                 if conv['program_name'] == selected_program),
                                None
                            )
                            
                            if selected_conversion:
                                # Display conversion result
                                st.markdown("### Conversion Summary")
                                st.markdown(f"- Project created at: {selected_conversion['java_project_path']}")
                                st.markdown(f"- Number of Java classes: {len(selected_conversion['java_classes'])}")
                                
                                # List generated classes
                                st.markdown("### Generated Java Classes")
                                for java_class in selected_conversion['java_classes']:
                                    st.markdown(f"- `{java_class['package']}.{java_class['name']}`")
                                
                                # Show output path
                                output_path = conversion_result['output_path']
                                st.markdown(
                                    f"<div class='success-box'>"
                                    f"Java code has been generated at: <code>{output_path}</code>"
                                    f"</div>",
                                    unsafe_allow_html=True
                                )
                        else:
                            st.error(f"Error converting to Java: {conversion_result.get('error', 'Unknown error')}")
            else:
                st.warning(
                    "Please confirm the program analysis in the 'Program Understanding' tab before proceeding to conversion."
                )
        else:
            st.info("No analysis available. Please upload and process COBOL files first.")

if __name__ == "__main__":
    main()