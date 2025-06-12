# Read the file
with open('android_engagement.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Find the methods outside the class
methods_start = content.find('    def _is_usa_user(self, text: str) -> bool:')
methods_end = content.find('class AndroidEngagement:')

# Extract the methods
methods = content[methods_start:methods_end]

# Remove the methods from outside the class
content_without_methods = content[:methods_start] + content[methods_end:]

# Find where to insert them in the class (after __init__ method ends)
init_end = content_without_methods.find('        # Connect to devices as needed (not all at once)')
init_end = content_without_methods.find('\n    def load_config(self):', init_end)

# Insert the methods with proper indentation
indented_methods = '\n'.join('    ' + line if line.strip() else line for line in methods.split('\n'))

# Insert after __init__ method
new_content = content_without_methods[:init_end] + '\n' + indented_methods + '\n' + content_without_methods[init_end:]

# Write the fixed file
with open('android_engagement.py', 'w', encoding='utf-8') as f:
    f.write(new_content)

print("Fixed the file successfully!") 