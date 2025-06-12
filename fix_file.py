import re

# Read the file
with open('android_engagement.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Find the methods outside the class
pattern = r'def _is_usa_user\(self, text: str\) -> bool:.*?return False\n\n    def analyze_user_profile\(self, device: u2\.Device, username: str\) -> Optional\[Dict\]:.*?return None\n\nclass AndroidEngagement:'
match = re.search(pattern, content, re.DOTALL)

if match:
    # Extract the methods
    methods_text = match.group(0)
    methods_text = methods_text.replace('class AndroidEngagement:', '')
    
    # Find where to insert the methods in the class
    init_end_pattern = r'# Connect to devices as needed.*?def load_config\(self\):'
    init_end_match = re.search(init_end_pattern, content, re.DOTALL)
    
    if init_end_match:
        # Remove the methods from outside the class
        content = re.sub(pattern, 'class AndroidEngagement:', content, flags=re.DOTALL)
        
        # Insert the methods after __init__
        insert_pos = init_end_match.end() - len('def load_config(self):')
        content = content[:insert_pos] + methods_text + '\n    ' + content[insert_pos:]
        
        # Write the fixed content
        with open('android_engagement.py', 'w', encoding='utf-8') as f:
            f.write(content)
        print('Fixed the file successfully!')
    else:
        print('Could not find __init__ end position')
else:
    print('Could not find the methods outside the class') 