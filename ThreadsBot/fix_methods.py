# Read the file
with open('android_engagement.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Find the methods outside the class (lines 268-330)
start_line = 268
end_line = 330

# Extract the methods
methods = lines[start_line-1:end_line]

# Find where to insert them in the class (after __init__)
insert_line = 418  # After __init__ method ends

# Remove the methods from outside the class
new_lines = lines[:start_line-1] + lines[end_line:]

# Insert the methods inside the class
new_lines = new_lines[:insert_line-1] + methods + new_lines[insert_line-1:]

# Write the fixed file
with open('android_engagement.py', 'w', encoding='utf-8') as f:
    f.writelines(new_lines)

print("Fixed the file successfully!") 