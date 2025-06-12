# Read the file
with open('android_engagement.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Find and fix the analyze_user_profile method indentation
fixed_lines = []
for i, line in enumerate(lines):
    # Check if this is the analyze_user_profile method definition
    if line.strip().startswith('def analyze_user_profile(self, device: u2.Device, username: str) -> Optional[Dict]:'):
        # Fix indentation from 8 spaces to 4 spaces
        if line.startswith('        def '):
            fixed_lines.append('    ' + line[8:])  # Replace 8 spaces with 4
        else:
            fixed_lines.append(line)
    elif (line.strip().startswith('"""Analyze a user\'s profile') or
          line.strip().startswith('try:') or
          line.strip().startswith('logger.info(f"Analyzing profile') or
          line.strip().startswith('if not self.click_username_in_comments') or
          line.strip().startswith('time.sleep(3)') or
          line.strip().startswith('profile_info = {') or
          line.strip().startswith('username: username,') or
          line.strip().startswith('bio: \'\',') or
          line.strip().startswith('followers: 0,') or
          line.strip().startswith('following: 0,') or
          line.strip().startswith('posts: 0,') or
          line.strip().startswith('is_verified: False,') or
          line.strip().startswith('is_private: False,') or
          line.strip().startswith('location: \'\',') or
          line.strip().startswith('website: \'\',') or
          line.strip().startswith('gender: \'unknown\',') or
          line.strip().startswith('age_group: \'unknown\',') or
          line.strip().startswith('interests: [],') or
          line.strip().startswith('language: \'unknown\',') or
          line.strip().startswith('is_usa: False') or
          line.strip().startswith('}') or
          line.strip().startswith('# Look for bio text') or
          line.strip().startswith('try:') or
          line.strip().startswith('bio_elements = device.xpath') or
          line.strip().startswith('if not bio_elements:') or
          line.strip().startswith('all_text_elements = device.xpath') or
          line.strip().startswith('for element in all_text_elements:') or
          line.strip().startswith('text = element.attrib.get') or
          line.strip().startswith('if text and len(text) > 10') or
          line.strip().startswith('profile_info[\'bio\'] = text') or
          line.strip().startswith('logger.info(f"Found bio: {text}")') or
          line.strip().startswith('break') or
          line.strip().startswith('else:') or
          line.strip().startswith('bio_text = bio_elements[0].attrib.get') or
          line.strip().startswith('if bio_text:') or
          line.strip().startswith('profile_info[\'bio\'] = bio_text') or
          line.strip().startswith('logger.info(f"Found bio: {bio_text}")') or
          line.strip().startswith('except Exception as e:') or
          line.strip().startswith('logger.debug(f"Error extracting bio: {e}")') or
          line.strip().startswith('# Enhanced USA detection') or
          line.strip().startswith('combined_text = f"{username} {profile_info[\'bio\']}"') or
          line.strip().startswith('profile_info[\'is_usa\'] = self._is_usa_user(combined_text)') or
          line.strip().startswith('# Go back to the post') or
          line.strip().startswith('logger.info("Going back to post from profile...")') or
          line.strip().startswith('self.click_back_to_post(device)') or
          line.strip().startswith('time.sleep(2)') or
          line.strip().startswith('logger.info(f"Profile analysis complete for {username}: {profile_info}")') or
          line.strip().startswith('return profile_info') or
          line.strip().startswith('except Exception as e:') or
          line.strip().startswith('logger.error(f"Error analyzing profile for {username}: {e}")') or
          line.strip().startswith('# Try to go back to post') or
          line.strip().startswith('try:') or
          line.strip().startswith('self.click_back_to_post(device)') or
          line.strip().startswith('except:') or
          line.strip().startswith('pass') or
          line.strip().startswith('return None')):
        # Fix indentation for method content
        if line.startswith('            '):
            fixed_lines.append('        ' + line[12:])  # Replace 12 spaces with 8
        elif line.startswith('                '):
            fixed_lines.append('            ' + line[16:])  # Replace 16 spaces with 12
        elif line.startswith('                    '):
            fixed_lines.append('                ' + line[20:])  # Replace 20 spaces with 16
        else:
            fixed_lines.append(line)
    else:
        fixed_lines.append(line)

# Write the fixed file
with open('android_engagement.py', 'w', encoding='utf-8') as f:
    f.writelines(fixed_lines)

print("Fixed indentation successfully!") 