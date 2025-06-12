#!/usr/bin/env python3
"""
Android Engagement Bot for Threads
Automates engagement on viral posts using UIAutomator2
"""

import uiautomator2 as u2
import time
import json
import logging
import re
from typing import Dict, List, Optional, Any, Tuple
import random

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Gemini API Key (you'll need to set this)
GEMINI_API_KEY = "your_gemini_api_key_here"

class AIAnalyzer:
    def __init__(self, api_key: str = GEMINI_API_KEY):
        self.api_key = api_key
    
    def analyze_user_profile(self, username: str, bio: str, comment_text: str) -> Dict:
        """Analyze user profile to determine gender, interests, and location."""
        try:
            # For now, use fallback analysis
            return self._get_fallback_analysis(username, bio, comment_text)
        except Exception as e:
            logger.warning(f"AI analysis failed: {e}")
            return self._get_fallback_analysis(username, bio, comment_text)
    
    def generate_female_engagement_response(self, post_content: str, user_profile: Dict, comment_text: str = "") -> str:
        """Generate a female engagement response based on user profile."""
        try:
            # For now, use fallback response
            return self._get_fallback_female_response(comment_text)
        except Exception as e:
            logger.warning(f"AI response generation failed: {e}")
            return self._get_fallback_female_response(comment_text)
    
    def _get_fallback_analysis(self, username: str, bio: str, comment_text: str) -> Dict:
        """Fallback analysis when AI is not available."""
        analysis = {
            'username': username,
            'gender': 'unknown',
            'interests': [],
            'is_usa': False,
            'language': 'english',
            'followers': 0
        }
        
        # Simple gender detection
        if any(word in bio.lower() for word in ['he/him', 'guy', 'man', 'dude', 'bro']):
            analysis['gender'] = 'male'
        elif any(word in bio.lower() for word in ['she/her', 'girl', 'woman', 'lady']):
            analysis['gender'] = 'female'
        
        # Simple interest detection
        interests = []
        if any(word in bio.lower() for word in ['crypto', 'bitcoin', 'ethereum']):
            interests.append('crypto')
        if any(word in bio.lower() for word in ['fitness', 'gym', 'workout']):
            interests.append('fitness')
        if any(word in bio.lower() for word in ['business', 'entrepreneur']):
            interests.append('business')
        if any(word in bio.lower() for word in ['tech', 'coding', 'programming']):
            interests.append('tech')
        if any(word in bio.lower() for word in ['travel', 'adventure']):
            interests.append('travel')
        
        analysis['interests'] = interests
        
        # Simple USA detection
        if any(word in bio.lower() for word in ['usa', 'american', 'us_', '_us']):
            analysis['is_usa'] = True
        
        return analysis
    
    def _get_fallback_female_response(self, comment_text: str) -> str:
        """Generate fallback female engagement response."""
        responses = [
            "Love your perspective! 💕",
            "This is so relatable! ✨",
            "You're absolutely right! 🔥",
            "Thanks for sharing this! 💯",
            "This made my day! 🌟",
            "You have such great insights! 💪",
            "This is exactly what I needed to hear! 🙌",
            "Your energy is amazing! 💖",
            "This is spot on! 🎯",
            "Love your authenticity! ✨"
        ]
        return random.choice(responses)

class AndroidEngagement:
    def __init__(self, config_file: str = "android_config.json"):
        """Initialize the Android engagement bot."""
        self.config_file = config_file
        self.devices: Dict[str, Dict] = {}
        self.active_devices: Dict[str, u2.Device] = {}
        self.logger = logging.getLogger(__name__)
        self.ai_analyzer = AIAnalyzer()
        
        # Engagement settings
        self.min_likes_for_viral = 1  # Temporarily lowered for testing
        self.min_comments_for_viral = 1  # Temporarily lowered for testing
        self.max_posts_to_scan = 50
        
        # Load configuration
        self.load_config()
    
    def load_config(self):
        """Load device configurations from JSON file."""
        try:
            with open(self.config_file, 'r') as f:
                config = json.load(f)
                for device in config['devices']:
                    self.devices[device['name']] = device
            logger.info(f"Loaded {len(self.devices)} devices from config")
        except Exception as e:
            logger.error(f"Error loading config: {str(e)}")
            raise
    
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
            logger.error(f"Error connecting to device {device_name}: {str(e)}")
            return None
    
    def open_threads_app(self, device: u2.Device):
        """Open the Threads app on the device."""
        try:
            device.app_start("Threads")
            time.sleep(5)
            logger.info("Threads app opened successfully")
        except Exception as e:
            logger.error(f"Error opening Threads app: {str(e)}")
    
    def scan_feed(self, device: u2.Device) -> list:
        """Scan the feed for viral posts."""
        try:
            logger.info("Scanning feed for viral posts...")
            viral_posts = []
            
            # Find heart icons (like buttons)
            heart_icons = device.xpath('//*[contains(@content-desc, "Like")]').all()
            logger.info(f"Found {len(heart_icons)} heart icons")
            
            for heart_icon in heart_icons:
                try:
                    # Check if this is a viral post
                    viral_post = self.check_if_viral(device, heart_icon)
                    if viral_post:
                        viral_posts.append(viral_post)
                        logger.info("Found viral post!")
                        break  # Process one post at a time
                except Exception as e:
                    logger.error(f"Error checking heart icon: {e}")
                    continue
            
            return viral_posts
        except Exception as e:
            logger.error(f"Error scanning feed: {str(e)}")
            return []
    
    def check_if_viral(self, device: u2.Device, heart_icon) -> Optional[Dict]:
        """Check if a post is viral based on engagement metrics."""
        try:
            # Find numbers near the heart icon
            all_elements = device.xpath('//*').all()
            nearby_numbers = []
            
            heart_center = heart_icon.center()
            
            for element in all_elements:
                try:
                    text = element.attrib.get('text', '')
                    if text and text.isdigit():
                        num = int(text)
                        if num >= self.min_likes_for_viral:
                            element_center = element.center()
                            distance = ((heart_center[0] - element_center[0])**2 + 
                                      (heart_center[1] - element_center[1])**2)**0.5
                            
                            if distance <= 500:  # Within 500 pixels
                                nearby_numbers.append((num, distance))
                except Exception as e:
                    continue
            
            if nearby_numbers:
                # Sort by distance and take the closest number
                nearby_numbers.sort(key=lambda x: x[1])
                like_count = nearby_numbers[0][0]
                
                if like_count >= self.min_likes_for_viral:
                    return {
                        'heart_icon': heart_icon,
                        'like_count': like_count,
                        'comment_count': 0
                    }
            
            return None
        except Exception as e:
            logger.error(f"Error checking if viral: {e}")
            return None
    
    def process_post(self, device: u2.Device, device_name: str, post: Dict):
        """Process a viral post by opening it and engaging with comments."""
        try:
            logger.info(f"Processing viral post with {post['like_count']} likes")
            
            # Click on the post to open it
            heart_icon = post['heart_icon']
            heart_center = heart_icon.center()
            
            # Click above the heart icon to open the post
            click_x = heart_center[0]
            click_y = heart_center[1] - 100  # Click 100 pixels above the heart
            
            device.click(click_x, click_y)
            time.sleep(3)
            
            # Process comments in the post
            self.process_comments_in_post(device, device_name)
            
        except Exception as e:
            logger.error(f"Error processing post: {e}")
    
    def process_comments_in_post(self, device: u2.Device, device_name: str):
        """Process comments in a post to find and engage with users."""
        try:
            logger.info("Processing comments in post...")
            
            # Find usernames in comments
            usernames = self.find_usernames_in_comments(device)
            logger.info(f"Found {len(usernames)} usernames in comments")
            
            # Process each username
            for username in usernames[:3]:  # Process up to 3 usernames
                try:
                    logger.info(f"Processing username: {username}")
                    
                    # Analyze profile
                    profile_info = self.analyze_user_profile(device, username)
                    
                    if profile_info and profile_info.get('gender') == 'male' and profile_info.get('is_usa'):
                        logger.info(f"Found USA male user: {username}")
                        
                        # Generate and post response
                        response = self.generate_ai_response(username, profile_info)
                        if response:
                            self.post_comment_response(device, response, username)
                            time.sleep(3)
                    
                except Exception as e:
                    logger.error(f"Error processing username {username}: {e}")
                    continue
            
        except Exception as e:
            logger.error(f"Error processing comments: {e}")
    
    def find_usernames_in_comments(self, device: u2.Device) -> List[str]:
        """Find usernames in the comment section."""
        try:
            usernames = []
            
            # Look for usernames in text elements
            text_elements = device.xpath('//*[@text]').all()
            
            for element in text_elements:
                try:
                    text = element.attrib.get('text', '').strip()
                    
                    # Check for usernames with @ symbol
                    if (text.startswith('@') and
                        len(text) >= 3 and
                        len(text) < 25 and
                        ' ' not in text):
                        
                        username = text[1:]  # Remove @ symbol
                        if username not in usernames:
                            usernames.append(username)
                            logger.info(f"Found username: {username}")
                    
                    # Check for usernames without @ symbol
                    elif (len(text) >= 3 and
                          len(text) < 25 and
                          ' ' not in text and
                          not text.isdigit()):
                        
                        if text not in usernames:
                            usernames.append(text)
                            logger.info(f"Found potential username: {text}")
                            
                except Exception as e:
                    continue
            
            return usernames
        except Exception as e:
            logger.error(f"Error finding usernames: {e}")
            return []
    
    def analyze_user_profile(self, device: u2.Device, username: str) -> Optional[Dict]:
        """Analyze a user's profile."""
        try:
            logger.info(f"Analyzing profile for username: {username}")
            
            # Click on username to open profile
            if not self.click_username_in_comments(device, username):
                return None
            
            time.sleep(3)
            
            # Extract profile information
            profile_info = {
                'username': username,
                'bio': '',
                'gender': 'unknown',
                'is_usa': False,
                'interests': []
            }
            
            # Look for bio text
            bio_elements = device.xpath('//*[@text]').all()
            for element in bio_elements:
                text = element.attrib.get('text', '')
                if text and len(text) > 10 and len(text) < 200:
                    profile_info['bio'] = text
                    break
            
            # Use AI analyzer to analyze profile
            analysis = self.ai_analyzer.analyze_user_profile(username, profile_info['bio'], '')
            profile_info.update(analysis)
            
            # Go back to the post
            device.press("back")
            time.sleep(2)
            
            return profile_info
            
        except Exception as e:
            logger.error(f"Error analyzing profile for {username}: {e}")
            try:
                device.press("back")
            except:
                pass
            return None
    
    def click_username_in_comments(self, device: u2.Device, username: str) -> bool:
        """Click on a username in the comment section."""
        try:
            # Look for the username in text elements
            text_elements = device.xpath('//*[@text]').all()
            
            for element in text_elements:
                text = element.attrib.get('text', '')
                if username in text:
                    element.click()
                    time.sleep(2)
                    return True
            
            return False
        except Exception as e:
            logger.error(f"Error clicking username {username}: {e}")
            return False
    
    def generate_ai_response(self, username: str, profile_info: Dict) -> str:
        """Generate an AI-powered engagement response."""
        try:
            response = self.ai_analyzer.generate_female_engagement_response("", profile_info, "")
            return response
        except Exception as e:
            logger.error(f"Error generating AI response: {e}")
            return "Great post! 🔥 Love your content!"
    
    def post_comment_response(self, device: u2.Device, response: str, target_username: str = ""):
        """Post a comment response."""
        try:
            logger.info(f"Posting comment response: {response}")
            
            # Look for the comment input field
            input_elements = device.xpath('//*[@content-desc="Add a comment..."]').all()
            if not input_elements:
                input_elements = device.xpath('//*[@text="Add a comment..."]').all()
            
            if input_elements:
                input_element = input_elements[0]
                input_element.click()
                time.sleep(2)
                
                # Type the response
                device.send_keys(response)
                time.sleep(2)
                
                # Look for the post/send button
                post_elements = device.xpath('//*[@content-desc="Post"]').all()
                if not post_elements:
                    post_elements = device.xpath('//*[@text="Post"]').all()
                
                if post_elements:
                    post_elements[0].click()
                    logger.info("Comment posted successfully!")
                else:
                    logger.error("Could not find post button")
            else:
                logger.error("Could not find comment input field")
                
        except Exception as e:
            logger.error(f"Error posting comment response: {e}")
    
    def run(self):
        """Main run method."""
        try:
            logger.info("Starting Android Engagement Bot...")
            
            # Connect to the first device
            device_name = list(self.devices.keys())[0]
            device = self.connect_device(device_name)
            
            if not device:
                logger.error("Failed to connect to device")
                return
            
            # Open Threads app
            self.open_threads_app(device)
            
            # Scan feed for viral posts
            viral_posts = self.scan_feed(device)
            
            if viral_posts:
                logger.info(f"Found {len(viral_posts)} viral posts")
                # Process the first viral post
                self.process_post(device, device_name, viral_posts[0])
            else:
                logger.info("No viral posts found")
            
        except Exception as e:
            logger.error(f"Error in main run: {e}")

def main():
    """Main function to run the bot."""
    try:
        bot = AndroidEngagement()
        bot.run()
    except Exception as e:
        logger.error(f"Error running bot: {e}")

if __name__ == "__main__":
    main() 