#!/usr/bin/env python3
"""
Script to convert prompt injection payloads to XML format
Reads prompts from text file and generates basic keywords
"""

import xml.etree.ElementTree as ET
import re
import argparse
import sys
from typing import List

def extract_basic_keywords(prompt: str) -> str:
    """
    Extract basic keywords from a prompt injection payload.
    Simple approach - just looks for key terms.
    """
    # Basic prompt injection indicators
    basic_keywords = [
        'ignore', 'forget', 'override', 'bypass', 'system prompt', 'debug mode',
        'unrestricted', 'godmode', 'dan', 'jailbreak', 'admin', 'roleplay', 
        'simulation', 'red team', 'training', 'uncensored', 'safety', 'ethical'
    ]
    
    prompt_lower = prompt.lower()
    found_keywords = []
    
    # Simple keyword matching
    for keyword in basic_keywords:
        if keyword in prompt_lower:
            found_keywords.append(keyword)
    
    # If no specific keywords found, extract first few meaningful words
    if not found_keywords:
        words = re.findall(r'\b[a-zA-Z]{4,}\b', prompt)
        found_keywords = words[:3] if words else ['prompt injection']
    
    # Clean up and limit to 5 keywords max
    keywords = list(set(found_keywords))[:5]
    return ', '.join(keywords)

def parse_prompts_from_file(file_path: str) -> List[str]:
    """
    Parse prompts from a text file. Handles YAML-like format:
    prompts:
      - "prompt 1"
      - "prompt 2"
    """
    prompts = []
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Extract quoted strings that appear after "- " (YAML list format)
        # Use non-greedy matching and handle both quote types separately
        double_quote_pattern = r'^\s*-\s*"([^"]+)"'
        single_quote_pattern = r"^\s*-\s*'([^']+)'"
        
        # Try double quotes first
        double_matches = re.findall(double_quote_pattern, content, re.MULTILINE)
        single_matches = re.findall(single_quote_pattern, content, re.MULTILINE)
        
        prompts = double_matches + single_matches
        
        if not prompts:
            # Fallback: try to extract any quoted strings (at least 20 chars)
            fallback_pattern = r'["\']([^"\']{20,})["\']'
            prompts = re.findall(fallback_pattern, content)
        
        print(f"Extracted {len(prompts)} prompts from {file_path}")
        
    except FileNotFoundError:
        print(f"Error: File '{file_path}' not found")
        sys.exit(1)
    except Exception as e:
        print(f"Error reading file: {e}")
        sys.exit(1)
    
    return prompts

def create_xml_payload(prompt: str) -> ET.Element:
    """Create a single payload XML element with proper escaping"""
    payload_elem = ET.Element('payload')
    
    # Create inject element
    inject_elem = ET.SubElement(payload_elem, 'inject')
    inject_elem.text = prompt  # ET handles XML escaping automatically
    
    # Create keywords element
    keywords_elem = ET.SubElement(payload_elem, 'keywords')
    keywords_elem.text = extract_basic_keywords(prompt)
    
    return payload_elem

def prompts_to_xml(prompts: List[str], output_file: str = None) -> str:
    """
    Convert list of prompts to XML format matching the existing structure.
    Returns XML as string and optionally writes to file.
    """
    # Create root element
    root = ET.Element('payloads')
    
    # Add each prompt as a payload
    for prompt in prompts:
        if prompt.strip():  # Skip empty prompts
            payload = create_xml_payload(prompt.strip())
            root.append(payload)
    
    # Create tree and format
    tree = ET.ElementTree(root)
    ET.indent(tree, space="  ", level=0)  # Pretty print with 2-space indentation
    
    # Convert to string with XML declaration
    xml_str = '<?xml version="1.0" encoding="UTF-8"?>\n'
    xml_str += ET.tostring(root, encoding='unicode', method='xml')
    
    # Write to file if specified
    if output_file:
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(xml_str)
        print(f"XML written to: {output_file}")
    
    return xml_str

def main():
    """Main function with command line argument support"""
    parser = argparse.ArgumentParser(
        description='Convert prompt injection payloads from text file to XML format',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python3 convert_prompts_to_xml.py prompts.txt
  python3 convert_prompts_to_xml.py prompts.txt -o output.xml
  python3 convert_prompts_to_xml.py prompts.txt --output /path/to/output.xml
        """
    )
    
    parser.add_argument('input_file', help='Text file containing prompts to convert')
    parser.add_argument('-o', '--output', 
                       help='Output XML file (default: input_file_name_injection.xml)')
    
    args = parser.parse_args()
    
    # Parse prompts from input file
    prompts = parse_prompts_from_file(args.input_file)
    
    if not prompts:
        print("No prompts found in input file!")
        sys.exit(1)
    
    # Determine output file name
    if args.output:
        output_file = args.output
    else:
        # Auto-generate output filename
        base_name = args.input_file.rsplit('.', 1)[0]
        output_file = f"{base_name}_injection.xml"
    
    # Generate XML
    xml_content = prompts_to_xml(prompts, output_file)
    
    print(f"✅ Converted {len(prompts)} prompts to XML format")
    print(f"📄 Output saved to: {output_file}")
    
    # Display first few lines as preview
    lines = xml_content.split('\n')
    print("\n📋 Preview (first 15 lines):")
    print('\n'.join(lines[:15]))
    if len(lines) > 15:
        print("...")

if __name__ == "__main__":
    main()