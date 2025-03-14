import os
import re
from pathlib import Path
from typing import Dict, List, Any, Optional

def generate_project_structure(output_base_path: Path, program_name: str) -> Path:
    """
    Generate a Maven project structure for the Java conversion
    
    Args:
        output_base_path: Base path for output
        program_name: Name of the COBOL program
        
    Returns:
        Path to the generated project
    """
    # Convert program name to a valid Java package name
    package_name = cobol_name_to_package_name(program_name)
    
    # Create project directory
    project_dir = output_base_path / f"{program_name.lower()}-java"
    project_dir.mkdir(parents=True, exist_ok=True)
    
    # Create Maven directory structure
    src_main_java = project_dir / "src" / "main" / "java"
    src_main_java.mkdir(parents=True, exist_ok=True)
    
    src_main_resources = project_dir / "src" / "main" / "resources"
    src_main_resources.mkdir(parents=True, exist_ok=True)
    
    src_test_java = project_dir / "src" / "test" / "java"
    src_test_java.mkdir(parents=True, exist_ok=True)
    
    # Create package directory structure
    package_parts = package_name.split('.')
    package_dir = src_main_java
    for part in package_parts:
        package_dir = package_dir / part
        package_dir.mkdir(exist_ok=True)
    
    # Create pom.xml
    create_pom_file(project_dir, program_name, package_name)
    
    return project_dir

def create_pom_file(project_dir: Path, program_name: str, package_name: str) -> None:
    """
    Create a Maven pom.xml file
    
    Args:
        project_dir: Project directory
        program_name: Name of the COBOL program
        package_name: Java package name
    """
    pom_content = f"""<?xml version="1.0" encoding="UTF-8"?>
<project xmlns="http://maven.apache.org/POM/4.0.0"
         xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
         xsi:schemaLocation="http://maven.apache.org/POM/4.0.0 http://maven.apache.org/xsd/maven-4.0.0.xsd">
    <modelVersion>4.0.0</modelVersion>

    <groupId>{package_name}</groupId>
    <artifactId>{program_name.lower()}-java</artifactId>
    <version>1.0-SNAPSHOT</version>

    <properties>
        <maven.compiler.source>11</maven.compiler.source>
        <maven.compiler.target>11</maven.compiler.target>
        <project.build.sourceEncoding>UTF-8</project.build.sourceEncoding>
    </properties>

    <dependencies>
        <!-- JUnit 5 for testing -->
        <dependency>
            <groupId>org.junit.jupiter</groupId>
            <artifactId>junit-jupiter-api</artifactId>
            <version>5.9.2</version>
            <scope>test</scope>
        </dependency>
        <dependency>
            <groupId>org.junit.jupiter</groupId>
            <artifactId>junit-jupiter-engine</artifactId>
            <version>5.9.2</version>
            <scope>test</scope>
        </dependency>
    </dependencies>

    <build>
        <plugins>
            <plugin>
                <groupId>org.apache.maven.plugins</groupId>
                <artifactId>maven-surefire-plugin</artifactId>
                <version>3.0.0</version>
            </plugin>
            <plugin>
                <groupId>org.apache.maven.plugins</groupId>
                <artifactId>maven-jar-plugin</artifactId>
                <version>3.3.0</version>
                <configuration>
                    <archive>
                        <manifest>
                            <addClasspath>true</addClasspath>
                            <mainClass>{package_name}.{cobol_name_to_class_name(program_name)}</mainClass>
                        </manifest>
                    </archive>
                </configuration>
            </plugin>
        </plugins>
    </build>
</project>
"""
    
    pom_path = project_dir / "pom.xml"
    pom_path.write_text(pom_content)

def generate_java_class(
    project_dir: Path,
    program_name: str,
    conversion_result: str,
    class_structure: str
) -> List[Dict[str, str]]:
    """
    Generate Java class files from conversion result
    
    Args:
        project_dir: Project directory
        program_name: Name of the COBOL program
        conversion_result: Result of the conversion process
        class_structure: Structure of the Java classes
        
    Returns:
        List of generated Java classes
    """
    # Extract java classes from conversion result
    java_classes = extract_java_classes(conversion_result)
    
    if not java_classes:
        # If no classes were extracted, create a single class from the whole conversion result
        java_classes = [{
            'name': cobol_name_to_class_name(program_name),
            'content': conversion_result
        }]
    
    # Convert program name to a valid Java package name
    package_name = cobol_name_to_package_name(program_name)
    
    # Get the package directory
    package_parts = package_name.split('.')
    package_dir = project_dir / "src" / "main" / "java"
    for part in package_parts:
        package_dir = package_dir / part
    
    # Write each class to a file
    generated_classes = []
    
    for java_class in java_classes:
        class_name = java_class['name']
        class_content = java_class['content']
        
        # Add package declaration if not present
        if not class_content.strip().startswith("package"):
            class_content = f"package {package_name};\n\n{class_content}"
        
        # Write class file
        class_file_path = package_dir / f"{class_name}.java"
        class_file_path.write_text(class_content)
        
        generated_classes.append({
            'name': class_name,
            'path': str(class_file_path),
            'package': package_name
        })
    
    # Generate a README.md file
    generate_readme(project_dir, program_name, generated_classes)
    
    return generated_classes

def extract_java_classes(conversion_result: str) -> List[Dict[str, str]]:
    """
    Extract Java classes from conversion result
    
    Args:
        conversion_result: Result of the conversion process
        
    Returns:
        List of extracted Java classes
    """
    classes = []
    
    # Try to extract classes using regex pattern
    class_pattern = re.compile(
        r'(?:public\s+)?class\s+([A-Za-z0-9_]+)(?:\s+extends\s+[A-Za-z0-9_<>.]+)?(?:\s+implements\s+[A-Za-z0-9_<>.,\s]+)?\s*\{(.+?)(?=(?:public\s+)?class\s+|\Z)',
        re.DOTALL
    )
    
    matches = list(class_pattern.finditer(conversion_result))
    
    if not matches:
        return []
    
    # Process each match
    for i, match in enumerate(matches):
        class_name = match.group(1).strip()
        
        # For the last class, include everything until the end
        if i == len(matches) - 1:
            class_content = conversion_result[match.start():]
        else:
            class_content = match.group(0)
        
        classes.append({
            'name': class_name,
            'content': class_content
        })
    
    return classes

def generate_readme(project_dir: Path, program_name: str, classes: List[Dict[str, str]]) -> None:
    """
    Generate a README.md file for the project
    
    Args:
        project_dir: Project directory
        program_name: Name of the COBOL program
        classes: List of generated Java classes
    """
    readme_content = f"""# {program_name} - Java Conversion

This project contains a Java implementation converted from the COBOL program {program_name}.

## Project Structure

The project is organized as a standard Maven project:

- `src/main/java`: Java source files
- `src/main/resources`: Resource files
- `src/test/java`: Test source files

## Generated Classes

The following classes were generated from the COBOL program:

"""
    
    for java_class in classes:
        readme_content += f"- `{java_class['package']}.{java_class['name']}`: Java class converted from COBOL\n"
    
    readme_content += """
## Building the Project

To build the project, use Maven:

```
mvn clean package
```

## Running the Application

To run the application:

```
java -jar target/*.jar
```

## Notes

This Java code was automatically generated from COBOL source code using a GenAI-powered conversion tool.
Please review the code for accuracy and make any necessary adjustments.
"""
    
    readme_path = project_dir / "README.md"
    readme_path.write_text(readme_content)

def cobol_name_to_package_name(cobol_name: str) -> str:
    """
    Convert a COBOL program name to a valid Java package name
    
    Args:
        cobol_name: COBOL program name
        
    Returns:
        Valid Java package name
    """
    # Remove invalid characters and convert to lowercase
    name = re.sub(r'[^A-Za-z0-9]', '', cobol_name).lower()
    
    # Ensure it doesn't start with a number
    if name and name[0].isdigit():
        name = 'p' + name
    
    # Return a valid package name
    return f"com.conversion.{name}"

def cobol_name_to_class_name(cobol_name: str) -> str:
    """
    Convert a COBOL program name to a valid Java class name
    
    Args:
        cobol_name: COBOL program name
        
    Returns:
        Valid Java class name
    """
    # Remove invalid characters
    name = re.sub(r'[^A-Za-z0-9]', '', cobol_name)
    
    # Ensure it starts with an uppercase letter
    if name:
        name = name[0].upper() + name[1:]
    
    # Ensure it doesn't start with a number
    if name and name[0].isdigit():
        name = 'C' + name
    
    return name