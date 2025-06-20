# -*- coding: utf-8 -*-
import os
import sys
import json
import time
import logging
import random
import re
import uiautomator2 as u2
from typing import Dict, List, Optional
import requests

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class SimpleThreadsBot:
    def __init__(self, config_file: str = "bot_config.json"):
        """Initialize the simplified Threads bot."""
        self.config_file = config_file
        self.devices = {}
        self.active_devices = {}
        
        # Engagement settings
        self.min_likes_for_viral = 100
        self.min_comments_for_viral = 5
        self.max_posts_to_scan = 20
        self.comment_cooldown = 3600  # 1 hour
        self.follow_cooldown = 7200   # 2 hours
        self.like_cooldown = 300      # 5 minutes
        
        # Track last action times
        self.last_comment_time = {}
        self.last_follow_time = {}
        self.last_like_time = {}
        
        # AI settings
        self.use_ai = True
        self.ai_api_key = "YOUR_GEMINI_API_KEY"  # Replace with your key
        self.ai_api_url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent"
        
        # Load configuration
        self.load_config()
        
        # Predefined responses
        self.comment_templates = [
            "Great post! Really enjoyed this content 🔥",
            "This is amazing! Thanks for sharing 🙌",
            "Love your perspective on this! 💯",
            "Incredible insights! Keep it up 👏",
            "This is exactly what I needed to see today! ✨",
            "Your content is always on point! 🎯",
            "This is so valuable! Thanks for sharing 🌟",
            "Love how you explained this! 💪",
            "This is exactly what I was looking for! 🙏",
            "Your posts are always so insightful! 🎉"
        ]

    def load_config(self):
        """Load device configurations from JSON file."""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r') as f:
                    config = json.load(f)
                    for device in config.get('devices', []):
                        self.devices[device['name']] = device
                logger.info(f"Loaded {len(self.devices)} devices from config")
            else:
                # Create default config if file doesn't exist
                self.create_default_config()
        except Exception as e:
            logger.error(f"Error loading config: {e}")
            self.create_default_config()

    def create_default_config(self):
        """Create a default configuration file."""
        default_config = {
            "devices": [
                {
                    "name": "default_device",
                    "serial": "usb",
                    "description": "Default USB device"
                }
            ]
        }
        
        try:
            with open(self.config_file, 'w') as f:
                json.dump(default_config, f, indent=2)
            logger.info(f"Created default config file: {self.config_file}")
            self.devices = default_config['devices']
        except Exception as e:
            logger.error(f"Error creating default config: {e}")

    def connect_device(self, device_name: str) -> Optional[u2.Device]:
        """Connect to an Android device."""
        if device_name not in self.devices:
            logger.error(f"Device {device_name} not found in config")
            return None

        if device_name in self.active_devices:
            return self.active_devices[device_name]

        device_config = self.devices[device_name]
        try:
            if device_config['serial'] == 'usb':
                device = u2.connect()
            else:
                device = u2.connect(device_config['serial'])
            
            self.active_devices[device_name] = device
            logger.info(f"Connected to device: {device_name}")
            return device
        except Exception as e:
            logger.error(f"Error connecting to device {device_name}: {e}")
            return None

    def open_threads_app(self, device: u2.Device):
        """Open the Threads app on the device."""
        try:
            device.app_start("com.instagram.threadsapp")
            time.sleep(5)
            logger.info("Threads app opened successfully")
        except Exception as e:
            logger.error(f"Error opening Threads app: {e}")

    def can_perform_action(self, device_name: str, action_type: str) -> bool:
        """Check if enough time has passed since last action."""
        last_time_map = {
            'comment': self.last_comment_time,
            'follow': self.last_follow_time,
            'like': self.last_like_time
        }
        
        cooldown_map = {
            'comment': self.comment_cooldown,
            'follow': self.follow_cooldown,
            'like': self.like_cooldown
        }
        
        if device_name not in last_time_map[action_type]:
            return True
        
        time_since_last = time.time() - last_time_map[action_type][device_name]
        return time_since_last >= cooldown_map[action_type]

    def update_action_time(self, device_name: str, action_type: str):
        """Update the last action time for a device."""
        time_map = {
            'comment': self.last_comment_time,
            'follow': self.last_follow_time,
            'like': self.last_like_time
        }
        time_map[action_type][device_name] = time.time()

    def extract_number_from_text(self, text: str) -> int:
        """Extract the first number from text."""
        if not text:
            return 0
        
        # Find numbers (including K for thousands, M for millions)
        numbers = re.findall(r'(\d+(?:\.\d+)?[KMB]?)', text.replace(',', ''))
        
        if numbers:
            num_str = numbers[0].upper()
            if num_str.endswith('K'):
                return int(float(num_str[:-1]) * 1000)
            elif num_str.endswith('M'):
                return int(float(num_str[:-1]) * 1000000)
            elif num_str.endswith('B'):
                return int(float(num_str[:-1]) * 1000000000)
            else:
                return int(float(num_str))
        
        return 0

    def is_usa_user(self, username: str, bio: str = "", comment_text: str = "") -> bool:
        """Check if a user is likely from the USA."""
        text_to_check = f"{username} {bio} {comment_text}".lower()
        
        # USA indicators
        usa_indicators = [
            'usa', 'american', 'united states', 'nyc', 'la', 'chicago', 'miami',
            'texas', 'california', 'florida', 'new york', 'los angeles',
            'y\'all', 'gonna', 'wanna', 'gotta', 'dude', 'bro', 'awesome',
            'super bowl', 'thanksgiving', 'fourth of july', 'football',
            'baseball', 'basketball', 'hockey', 'burger', 'pizza', 'tacos'
        ]
        
        return any(indicator in text_to_check for indicator in usa_indicators)

    def is_male_user(self, username: str, bio: str = "", comment_text: str = "") -> bool:
        """Check if a user is likely male."""
        text_to_check = f"{username} {bio} {comment_text}".lower()
        
        # Male indicators
        male_indicators = [
            'man', 'boy', 'dude', 'guy', 'bro', 'male', 'dad', 'father', 'son',
            'john', 'mike', 'david', 'james', 'robert', 'william', 'chris',
            'football', 'basketball', 'baseball', 'gym', 'lifting', 'cars'
        ]
        
        return any(indicator in text_to_check for indicator in male_indicators)

    def generate_ai_response(self, post_content: str, user_profile: Dict) -> str:
        """Generate an AI-powered response using Gemini API."""
        if not self.use_ai or not self.ai_api_key:
            return random.choice(self.comment_templates)
        
        try:
            prompt = f"""
            Generate a natural, engaging response to this social media post:
            
            Post Content: {post_content}
            User Profile: {user_profile}
            
            Requirements:
            - Keep it under 100 characters
            - Sound natural and conversational
            - Be positive and engaging
            - Include appropriate emojis
            
            Return only the response text.
            """
            
            headers = {"Content-Type": "application/json"}
            data = {
                "contents": [{"parts": [{"text": prompt}]}],
                "generationConfig": {
                    "temperature": 0.7,
                    "maxOutputTokens": 100,
                }
            }
            
            url = f"{self.ai_api_url}?key={self.ai_api_key}"
            response = requests.post(url, headers=headers, json=data, timeout=10)
            
            if response.status_code == 200:
                result = response.json()
                if 'candidates' in result and len(result['candidates']) > 0:
                    text = result['candidates'][0]['content']['parts'][0]['text']
                    return text[:100]  # Ensure it's under 100 characters
            
        except Exception as e:
            logger.error(f"Error generating AI response: {e}")
        
        return random.choice(self.comment_templates)

    def scan_feed_for_viral_posts(self, device: u2.Device) -> List[Dict]:
        """Scan the feed for viral posts."""
        viral_posts = []
        posts_scanned = 0
        
        logger.info(f"Scanning feed for posts with {self.min_likes_for_viral}+ likes and {self.min_comments_for_viral}+ comments")
        
        while posts_scanned < self.max_posts_to_scan:
            try:
                # Find heart icons (like buttons)
                heart_icons = device.xpath('//*[contains(@content-desc, "like") or contains(@resource-id, "like")]').all()
                
                # Find all text elements that might contain numbers
                text_elements = device.xpath('//*[@text]').all()
                
                # Extract numbers from text elements
                elements_with_numbers = []
                for element in text_elements:
                    try:
                        text = element.attrib.get('text', '')
                        if text:
                            num = self.extract_number_from_text(text)
                            if num > 0:
                                elements_with_numbers.append((element, num))
                    except Exception:
                        continue
                
                # Process each heart icon
                for heart_icon in heart_icons:
                    try:
                        heart_center = heart_icon.center()
                        
                        # Find numbers near this heart icon
                        nearby_numbers = []
                        for element, num in elements_with_numbers:
                            try:
                                element_center = element.center()
                                distance = ((heart_center[0] - element_center[0])**2 + 
                                          (heart_center[1] - element_center[1])**2)**0.5
                                
                                if distance <= 500:  # Within 500 pixels
                                    nearby_numbers.append((num, distance))
                            except Exception:
                                continue
                        
                        if len(nearby_numbers) >= 2:
                            # Sort by distance and take the two closest
                            nearby_numbers.sort(key=lambda x: x[1])
                            like_count = nearby_numbers[0][0]
                            comment_count = nearby_numbers[1][0]
                            
                            if like_count >= self.min_likes_for_viral and comment_count >= self.min_comments_for_viral:
                                viral_posts.append({
                                    'heart_icon': heart_icon,
                                    'like_count': like_count,
                                    'comment_count': comment_count,
                                    'position': heart_center
                                })
                                logger.info(f"Found viral post: {like_count} likes, {comment_count} comments")
                    
                    except Exception as e:
                        logger.error(f"Error processing heart icon: {e}")
                        continue
                
                if viral_posts:
                    break
                
                # Scroll down to load more content
                device.swipe(0.5, 0.8, 0.5, 0.2)
                time.sleep(3)
                posts_scanned += 1
                
            except Exception as e:
                logger.error(f"Error in feed scanning: {e}")
                break
        
        logger.info(f"Found {len(viral_posts)} viral posts")
        return viral_posts

    def process_viral_post(self, device: u2.Device, device_name: str, post: Dict):
        """Process a viral post and engage with USA male users."""
        try:
            logger.info(f"Processing viral post: {post['like_count']} likes, {post['comment_count']} comments")
            
            # Click on the post to open comments
            heart_icon = post['heart_icon']
            heart_center = heart_icon.center()
            
            # Click slightly to the right of the heart icon
            click_x = heart_center[0] + 100
            click_y = heart_center[1]
            
            device.click(click_x, click_y)
            time.sleep(3)
            
            # Examine comments for USA male users
            self.examine_comments(device, device_name)
            
            # Go back to feed
            device.press("back")
            time.sleep(2)
            
        except Exception as e:
            logger.error(f"Error processing viral post: {e}")
            try:
                device.press("back")
                time.sleep(2)
            except:
                pass

    def examine_comments(self, device: u2.Device, device_name: str):
        """Examine comments to find and engage with USA male users."""
        try:
            logger.info("Examining comments for USA male users...")
            
            processed_usernames = set()
            comments_scanned = 0
            max_comments = 30
            
            for attempt in range(5):  # 5 scroll attempts
                # Find comment usernames
                comment_elements = device.xpath('//*[contains(@content-desc, "posted")]').all()
                
                for element in comment_elements:
                    if comments_scanned >= max_comments:
                        break
                    
                    try:
                        # Extract username
                        content_desc = element.attrib.get('content-desc', '')
                        username = content_desc.replace(' posted', '').strip()
                        
                        if not username or username in processed_usernames:
                            continue
                        
                        processed_usernames.add(username)
                        comments_scanned += 1
                        
                        # Get comment text
                        comment_text = ""
                        try:
                            username_center = element.center()
                            nearby_text_elements = device.xpath('//*[@text]').all()
                            
                            for text_el in nearby_text_elements:
                                try:
                                    text_center = text_el.center()
                                    distance = ((username_center[0] - text_center[0])**2 + 
                                              (username_center[1] - text_center[1])**2)**0.5
                                    
                                    if distance < 300:
                                        text = text_el.attrib.get('text', '')
                                        if text and len(text) > 5 and not text.isdigit() and text != username:
                                            comment_text = text
                                            break
                                except Exception:
                                    continue
                        except Exception:
                            pass
                        
                        # Click on username to check profile
                        element.click()
                        time.sleep(3)
                        
                        # Get bio
                        bio = ""
                        try:
                            text_elements = device.xpath('//*[@text]').all()
                            for text_el in text_elements[:20]:
                                text = text_el.attrib.get('text', '')
                                if text and len(text) > 10 and len(text) < 200:
                                    if not text.isdigit() and not text.endswith('h') and not text.endswith('d'):
                                        bio = text
                                        break
                        except Exception:
                            pass
                        
                        # Check if user is USA male
                        is_usa = self.is_usa_user(username, bio, comment_text)
                        is_male = self.is_male_user(username, bio, comment_text)
                        
                        if is_usa and is_male:
                            logger.info(f"Found USA male user: {username}")
                            
                            # Generate and post response
                            if self.can_perform_action(device_name, 'comment'):
                                user_profile = {
                                    'username': username,
                                    'bio': bio,
                                    'comment_text': comment_text,
                                    'is_usa': is_usa,
                                    'is_male': is_male
                                }
                                
                                response = self.generate_ai_response("", user_profile)
                                self.post_comment(device, device_name, response)
                        
                        # Go back to comments
                        device.press("back")
                        time.sleep(2)
                        
                    except Exception as e:
                        logger.error(f"Error processing comment: {e}")
                        try:
                            device.press("back")
                            time.sleep(2)
                        except:
                            pass
                
                if comments_scanned >= max_comments:
                    break
                
                # Scroll down for more comments
                device.swipe(0.5, 0.8, 0.5, 0.2)
                time.sleep(2)
            
        except Exception as e:
            logger.error(f"Error examining comments: {e}")
            try:
                device.press("back")
                time.sleep(2)
            except:
                pass

    def post_comment(self, device: u2.Device, device_name: str, comment_text: str):
        """Post a comment on the current post."""
        try:
            # Find reply button
            reply_buttons = device.xpath('//*[contains(@content-desc, "Reply")]').all()
            if not reply_buttons:
                logger.error("Could not find reply button")
                return
            
            reply_buttons[0].click()
            time.sleep(2)
            
            # Find text input field
            text_inputs = device.xpath('//*[@class="android.widget.EditText"]').all()
            if not text_inputs:
                logger.error("Could not find text input field")
                return
            
            text_inputs[0].click()
            time.sleep(1)
            
            # Type the comment
            device.send_keys(comment_text)
            time.sleep(1)
            
            # Find and click post button
            post_buttons = device.xpath('//*[contains(@content-desc, "Post") or contains(@content-desc, "Send")]').all()
            if post_buttons:
                post_buttons[0].click()
                logger.info(f"Posted comment: {comment_text[:50]}...")
                self.update_action_time(device_name, 'comment')
                time.sleep(2)
            else:
                logger.error("Could not find post button")
            
            # Go back
            device.press("back")
            time.sleep(1)
            
        except Exception as e:
            logger.error(f"Error posting comment: {e}")
            try:
                device.press("back")
                time.sleep(1)
            except:
                pass

    def run(self):
        """Main bot loop."""
        logger.info("Starting Simple Threads Bot...")
        
        while True:
            try:
                for device_name in self.devices:
                    logger.info(f"Processing device: {device_name}")
                    
                    device = self.connect_device(device_name)
                    if not device:
                        continue
                    
                    self.open_threads_app(device)
                    
                    # Scan for viral posts
                    viral_posts = self.scan_feed_for_viral_posts(device)
                    
                    # Process each viral post
                    for post in viral_posts:
                        self.process_viral_post(device, device_name, post)
                        time.sleep(random.uniform(5, 10))
                    
                    time.sleep(random.uniform(10, 20))
                
                # Wait before next cycle
                logger.info("Completed cycle, waiting 5 minutes...")
                time.sleep(300)
                
            except Exception as e:
                logger.error(f"Error in main loop: {e}")
                time.sleep(60)

def main():
    """Main entry point."""
    if len(sys.argv) < 2:
        print("Usage: python simple_threads_bot.py <command>")
        print("\nCommands:")
        print("  start - Start the bot")
        print("  config - Show current configuration")
        print("  test - Test device connection")
        return

    bot = SimpleThreadsBot()
    command = sys.argv[1].lower()

    if command == "start":
        print("Starting Simple Threads Bot...")
        bot.run()
    elif command == "config":
        print("\nCurrent Configuration:")
        print(f"Minimum likes for viral: {bot.min_likes_for_viral}")
        print(f"Minimum comments for viral: {bot.min_comments_for_viral}")
        print(f"Maximum posts to scan: {bot.max_posts_to_scan}")
        print(f"Comment cooldown: {bot.comment_cooldown} seconds")
        print(f"Follow cooldown: {bot.follow_cooldown} seconds")
        print(f"Like cooldown: {bot.like_cooldown} seconds")
        print(f"Use AI: {bot.use_ai}")
        print(f"Devices: {list(bot.devices.keys())}")
    elif command == "test":
        print("Testing device connection...")
        device_name = list(bot.devices.keys())[0] if bot.devices else "default_device"
        device = bot.connect_device(device_name)
        if device:
            print(f"Successfully connected to device: {device_name}")
            print(f"Device info: {device.info}")
        else:
            print("Failed to connect to device")
    else:
        print("Unknown command")

if __name__ == "__main__":
    main()
