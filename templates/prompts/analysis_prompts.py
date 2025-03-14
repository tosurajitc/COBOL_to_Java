# Analysis Prompt Templates

ANALYZE_COBOL_PROGRAM_PROMPT = """
You are an expert COBOL programmer and analyst responsible for understanding legacy COBOL programs.

TASK: Analyze the following COBOL program and provide a comprehensive understanding of its functionality, structure, and business purpose.

COBOL PROGRAM NAME: {program_name}

COBOL PROGRAM CONTENT:
```cobol
{program_content}
```

RELATED COPYBOOKS:
{copybooks}

PROGRAM STRUCTURE:
{program_structure}

Please provide a detailed analysis covering the following aspects:

1. PROGRAM OVERVIEW:
   - What is the primary purpose of this program?
   - What business function does it serve?
   - What are the main tasks it performs?

2. INPUT/OUTPUT:
   - What files or databases does the program read from?
   - What files or databases does the program write to?
   - What is the format of the input and output data?

3. PROGRAM FLOW:
   - What is the main processing logic of the program?
   - What are the key paragraphs and their functions?
   - How does control flow through the program?

4. DATA STRUCTURES:
   - What are the key data structures used in the program?
   - What do they represent in business terms?

5. SPECIAL FEATURES:
   - Does the program use any special COBOL features (e.g., CICS, SQL, etc.)?
   - Are there any unusual or complex aspects of the program?

6. POTENTIAL CHALLENGES FOR JAVA CONVERSION:
   - What aspects of this program might be challenging to convert to Java?
   - Are there any COBOL-specific features that don't have direct Java equivalents?

Your analysis should be detailed, accurate, and focused on understanding both the technical aspects and business purpose of the program.
"""

IDENTIFY_BUSINESS_RULES_PROMPT = """
You are an expert in business rule extraction from legacy COBOL applications.

TASK: Extract and clearly document all business rules embedded in the following COBOL program.

COBOL PROGRAM NAME: {program_name}

COBOL PROGRAM CONTENT:
```cobol
{program_content}
```

PROGRAM ANALYSIS:
{program_analysis}

Please identify and document all business rules in this program, including:

1. VALIDATION RULES:
   - Input data validation
   - Business data validation
   - Error conditions and handling

2. CALCULATION RULES:
   - Formulas and algorithms
   - Financial calculations
   - Date/time calculations

3. PROCESSING RULES:
   - Conditional processing logic
   - Decision trees and business logic
   - Order of operations

4. DOMAIN-SPECIFIC RULES:
   - Industry-specific logic
   - Regulatory requirements
   - Company policy implementations

5. INTEGRATION RULES:
   - Interactions with other systems
   - Data transformation rules
   - External system dependencies

For each business rule, please provide:
- A clear description of the rule
- Where in the code it appears (paragraph/line reference)
- The business purpose it serves
- Any conditions or exceptions to the rule

Present these rules in a structured format that will help Java developers understand the business logic they need to implement in the converted application.
"""