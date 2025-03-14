# COBOL to Java Converter

A GenAI-powered application for converting legacy COBOL programs to modern Java code.

## Overview

This application uses advanced AI techniques to:

1. Analyze COBOL program structure and extract business logic
2. Generate equivalent Java code that preserves the original functionality
3. Organize the converted code into a standard Maven project structure

The conversion process is guided by AI agents that specialize in different aspects of the transformation:

- **Data Agent**: Extracts and processes COBOL files from uploaded ZIP archives
- **Analysis Agent**: Analyzes COBOL programs to understand their structure and business logic
- **Conversion Agent**: Transforms COBOL code into equivalent Java code

## Getting Started

### Prerequisites

- Python 3.9 or higher
- A valid GROQ API key

### Installation

1. Clone this repository:
   ```
   git clone https://github.com/tosurajitc/COBOL_to_Java
   cd cobol-to-java-converter
   ```

2. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

3. Set up your environment variables by creating a `.env` file:
   ```
   GROQ_API_KEY=your_groq_api_key_here
   JAVA_OUTPUT_PATH=./output/java_programs
   MODEL_NAME=llama-3.1-70b-versatile
   ```

### Running the Application

Start the Streamlit application:
```
streamlit run app.py
```

Then navigate to the provided URL (typically http://localhost:8501) in your web browser.

## Usage

1. **Prepare your COBOL code**: Organize your COBOL programs into a ZIP file following the expected directory structure (see below).

2. **Upload and analyze**: Upload your ZIP file in the application and initiate the analysis process.

3. **Review the analysis**: Verify that the AI has correctly understood the program's purpose and business logic.

4. **Convert to Java**: Initiate the conversion process to transform your COBOL code into Java.

5. **Download and use**: The converted Java code will be available as a Maven project that you can build and run.

## Expected ZIP Structure

Your COBOL code should be organized in a ZIP file with the following structure:

```
COBOL_Conversion_Package/
│
├── src/
│   ├── programs/           # Main COBOL programs (.cbl, .cob)
│   │   ├── program1.cbl
│   │   └── program2.cbl
│   │
│   ├── copybooks/          # COBOL copybooks (.cpy)
│   │   ├── common/
│   │   │   ├── constants.cpy
│   │   │   └── structures.cpy
│   │   └── program1/
│   │       └── program1-structs.cpy
│   │
│   └── proc/               # Shared procedures (optional)
│       └── calculations.cbl
│
├── jcl/                    # Job Control Language files (optional)
│   └── program1-job.jcl
│
├── db/                     # Database definitions (optional)
│   └── schemas/
│       └── main-schema.sql
│
└── docs/                   # Documentation (optional)
    └── business-rules.md
```

## Limitations

- **COBOL Dialects**: The converter works best with standard ANSI COBOL but can handle common extensions.
- **Complex Logic**: Very complex COBOL programs with extensive GOTOs may require manual refinement after conversion.
- **External Systems**: Integration with mainframe-specific systems (CICS, IMS, etc.) will require additional customization.
- **Performance**: The converted Java code may have different performance characteristics than the original COBOL.

## Technical Architecture

The application is built using the following components:

- **Streamlit**: For the web user interface
- **CrewAI**: For orchestrating the AI agents
- **GROQ/LangChain**: For accessing large language models
- **Python**: Core application logic and file processing

## License

This project is licensed under the 

## Acknowledgments

- This project uses the [CrewAI](https://github.com/crewai/crewai) framework for agent orchestration
- COBOL parsing techniques were inspired by various open-source COBOL analysis tools