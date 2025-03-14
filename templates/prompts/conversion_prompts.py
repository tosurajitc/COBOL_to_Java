# Conversion Prompt Templates

GENERATE_JAVA_CLASS_STRUCTURE_PROMPT = """
You are an expert in converting COBOL programs to modern Java applications.

TASK: Design a Java class structure that will effectively implement the functionality of the following COBOL program.

COBOL PROGRAM NAME: {program_name}

PROGRAM ANALYSIS:
{program_analysis}

BUSINESS RULES:
{business_rules}

Please create a detailed Java class structure design that:

1. FOLLOWS OBJECT-ORIENTED PRINCIPLES:
   - Proper encapsulation
   - Single responsibility principle
   - Appropriate inheritance where needed
   - Interface-based design where appropriate

2. MAPS COBOL CONCEPTS TO JAVA:
   - Represent COBOL divisions as appropriate Java constructs
   - Map COBOL data structures to Java classes/objects
   - Convert COBOL procedures to Java methods

3. INCLUDES NECESSARY COMPONENTS:
   - Main class with program entry point
   - Data model classes
   - Service/utility classes
   - Exception handling framework

4. MAINTAINS BUSINESS LOGIC:
   - Preserve all business rules
   - Maintain the same processing flow
   - Keep calculation logic equivalent

5. FOLLOWS JAVA BEST PRACTICES:
   - Consistent naming conventions
   - Proper package structure
   - Appropriate access modifiers
   - Documentation with Javadoc

Provide a detailed class diagram in text format, including:
- Class names
- Properties/fields with types
- Methods with parameters and return types
- Relationships between classes
- Package structure

This design will be used as the blueprint for the actual Java code generation, so be thorough and precise.
"""

MAP_DATA_STRUCTURES_PROMPT = """
You are an expert in converting COBOL data structures to Java.

TASK: Create a detailed mapping of COBOL data structures to equivalent Java classes/objects for the following program.

COBOL PROGRAM NAME: {program_name}

PROGRAM STRUCTURE:
{program_structure}

JAVA CLASS STRUCTURE:
{class_structure}

Please create a comprehensive mapping that:

1. MAPS COBOL DATA ITEMS TO JAVA:
   - Convert COBOL record layouts (01 level items) to Java classes
   - Map COBOL elementary items to appropriate Java data types
   - Handle COBOL group items as nested classes or composed objects

2. ADDRESSES COBOL DATA TYPES:
   - PIC X fields → String or char
   - PIC 9 fields → appropriate numeric types (int, long, BigDecimal)
   - PIC S9 fields → signed numeric types
   - COMP fields → appropriate numeric types with consideration for precision
   - COMP-3 fields → BigDecimal or custom decimal handling
   - 88-level condition items → constants, enums, or boolean methods

3. HANDLES SPECIAL CASES:
   - REDEFINES clauses → appropriate Java alternatives (polymorphism, interfaces)
   - OCCURS clauses → arrays, Lists, or other collections
   - INDEXED BY → appropriate indexed access in Java
   - FILLER items → handling strategy (omit or preserve as comments)
   - Sign handling (LEADING/TRAILING) → sign handling in Java

4. INCLUDES DATA VALIDATION:
   - Range checks
   - Required field validation
   - Format validation

5. MAINTAINS BUSINESS MEANING:
   - Preserve field names while converting to Java naming conventions
   - Add descriptive Javadoc to explain business purpose
   - Maintain relationships between data elements

For each COBOL data structure, provide:
- The original COBOL definition
- The equivalent Java class/field definition
- Any necessary conversion methods
- Validation logic where appropriate

This mapping will serve as the foundation for the data model in the converted Java application.
"""

CONVERT_COBOL_TO_JAVA_PROMPT = """
You are an expert COBOL to Java conversion specialist using advanced code transformation techniques.

TASK: Convert the following COBOL program into equivalent Java code that preserves all functionality and business logic.

COBOL PROGRAM NAME: {program_name}

PROGRAM ANALYSIS:
{program_analysis}

JAVA CLASS STRUCTURE:
{class_structure}

DATA MAPPING:
{data_mapping}

BUSINESS RULES:
{business_rules}

Please implement the complete Java code that:

1. FOLLOWS THE PROPOSED CLASS STRUCTURE:
   - Implement all classes as outlined in the class structure
   - Maintain the relationships between classes
   - Use proper package organization

2. IMPLEMENTS ALL DATA STRUCTURES:
   - Create Java classes for all COBOL data records
   - Map all fields according to the data mapping
   - Implement appropriate constructors, getters, and setters

3. CONVERTS PROCEDURAL LOGIC:
   - Transform COBOL paragraphs to Java methods
   - Convert COBOL statements to equivalent Java code
   - Maintain the same processing flow and logic

4. PRESERVES ALL BUSINESS RULES:
   - Implement all validation rules
   - Maintain calculation formulas
   - Preserve conditional processing logic

5. HANDLES COBOL-SPECIFIC FEATURES:
   - Replace COBOL file handling with Java I/O
   - Transform PERFORM statements to method calls or loops
   - Convert COBOL control flow (GOTO, etc.) to structured Java alternatives
   - Implement appropriate replacements for COBOL-specific constructs

6. FOLLOWS JAVA BEST PRACTICES:
   - Use proper exception handling
   - Follow standard Java naming conventions
   - Include appropriate comments and Javadoc
   - Implement proper logging

7. MAINTAINS PROGRAM BEHAVIOR:
   - Ensure the Java code produces the same outputs given the same inputs
   - Preserve side effects where necessary for correctness
   - Handle edge cases consistently with the original COBOL

The resulting Java code should be complete, well-structured, and ready to compile and execute.
Include a main method that demonstrates how to use the converted application.

Organize imports properly and include any necessary utility classes or libraries.
"""