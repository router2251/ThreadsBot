#!/usr/bin/env python3
"""
Script to fix indentation errors in android_engagement.py
"""

import re

def fix_indentation_errors():
    """Fix common indentation errors in the file."""
    
    # Read the file
    with open('android_engagement.py', 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    fixed_lines = []
    i = 0
    
    while i < len(lines):
        line = lines[i]
        
        # Fix specific indentation issues
        if line.strip().startswith('time.sleep(2)') and i > 0:
            # Check if this line should be indented
            prev_line = lines[i-1].strip()
            if prev_line.endswith('duration=0.5)') or prev_line.endswith('device.click('):
                # This time.sleep should be indented to match the previous line
                indent = len(lines[i-1]) - len(lines[i-1].lstrip())
                line = ' ' * indent + line.lstrip()
        
        # Fix try blocks that are missing indentation
        if line.strip().startswith('try:') and i > 0:
            prev_line = lines[i-1].strip()
            if prev_line.endswith(':') or prev_line.endswith('{'):
                # This try should be indented
                indent = len(lines[i-1]) - len(lines[i-1].lstrip()) + 4
                line = ' ' * indent + line.lstrip()
        
        # Fix else statements that are missing indentation
        if line.strip().startswith('else:') and i > 0:
            prev_line = lines[i-1].strip()
            if prev_line.endswith(']') or prev_line.endswith(')'):
                # This else should be indented
                indent = len(lines[i-1]) - len(lines[i-1].lstrip())
                line = ' ' * indent + line.lstrip()
        
        # Fix for loops that are missing indentation
        if line.strip().startswith('for ') and i > 0:
            prev_line = lines[i-1].strip()
            if prev_line.endswith(':') or prev_line.endswith('{'):
                # This for should be indented
                indent = len(lines[i-1]) - len(lines[i-1].lstrip()) + 4
                line = ' ' * indent + line.lstrip()
        
        fixed_lines.append(line)
        i += 1
    
    # Write the fixed file
    with open('android_engagement_fixed.py', 'w', encoding='utf-8') as f:
        f.writelines(fixed_lines)
    
    print("Fixed indentation errors and saved to android_engagement_fixed.py")

if __name__ == "__main__":
    fix_indentation_errors() 