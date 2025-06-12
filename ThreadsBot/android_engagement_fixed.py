import os
import sys
import json
import time
import logging
import random
import re
import uiautomator2 as u2
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime, timedelta
from dotenv import load_dotenv
import requests

# AI Integration with Gemini API
GEMINI_API_KEY = "AIzaSyA2TYVMt3yzGr5TRtiSnp7mNepGxTaQZJM"  # Replace with your actual Gemini API key from https://makersuite.google.com/app/apikey
GEMINI_API_URL = "https://generativelanguage.googleapis.com/v1/models/gemini-1.5-flash:generateContent"

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AIAnalyzer:
    def __init__(self, api_key: str = GEMINI_API_KEY):
        self.api_key = api_key
        self.api_url = GEMINI_API_URL
        self.logger = logging.getLogger(__name__)
    
    def analyze_user_profile(self, username: str, bio: str, comment_text: str) -> Dict:
        """Analyze a user's profile using AI or fallback."""
        try:
            prompt = f"""
            Analyze the following user profile and comment:
            Username: {username}
            Bio: {bio}
            Comment: {comment_text}
            Return a JSON object with fields:
            - likely_gender (male/female/unknown)
            - likely_age_range (teen/20s/30s/40s/50+/unknown)
            - likely_location (USA/Canada/UK/Australia/other/unknown)
            - is_usa_user (true/false)
            - is_male_user (true/false)
            - interests (list of 3-5 interests based on username/bio/comment)
            - confidence_score (0-100)
            - personality_traits (list of 2-3 personality traits)
            Focus on:
            1. Username patterns that suggest gender (e.g., names ending in -man, -boy, -dude, -guy for male)
            2. USA indicators in username (e.g., city names, state abbreviations, American terms)
            3. Language patterns in comment that suggest American English
            4. Interests and topics that suggest location and demographics
            Return only valid JSON.
            """
            response = self._call_gemini_api(prompt)
            if response:
                return response
            return self._get_fallback_analysis(username, bio, comment_text)
        except Exception as e:
            self.logger.error(f"Error in AI analysis: {e}")
            return self._get_fallback_analysis(username, bio, comment_text)
    
    def generate_female_engagement_response(self, post_content: str, user_profile: Dict, comment_text: str = "") -> str:
        """Generate a female engagement response to a male USA user's comment."""
        try:
            prompt = f"""
            You are a friendly, intelligent woman engaging with a male user's comment on a social media post.
            
            Post Content: {post_content}
            User's Comment: {comment_text}
            User Profile: {user_profile}
            
            Generate a natural, engaging response that:
            1. Shows genuine interest in their comment
            2. Is conversational and friendly
            3. Relates to the post content and their comment
            4. Uses natural female language patterns
            5. Is 1-2 sentences long
            6. Includes appropriate emojis
            7. Feels authentic and not overly flirty
            
            Examples of good responses:
            - "That's such a great point! Love your perspective on this 😊"
            - "Totally agree with you! Thanks for sharing your thoughts"
            - "You always have the best insights! Really appreciate your comment"
            
            Return only the response text, no JSON formatting.
            """
            response = self._call_gemini_api(prompt)
            if response and isinstance(response, str):
                return response
        except Exception as e:
            self.logger.error(f"Error generating female response: {e}")
        return self._get_fallback_female_response(comment_text)
    
    def generate_engagement_response(self, post_content: str, user_profile: Dict) -> str:
        """Generate an AI-powered engagement response based on post content and user profile."""
        try:
            prompt = f"""
            Generate a natural, engaging response to this social media post:
            
            Post Content: {post_content}
            
            Target User Profile:
            - Gender: {user_profile.get('likely_gender', 'unknown')}
            - Age: {user_profile.get('likely_age_range', 'unknown')}
            - Location: {user_profile.get('likely_location', 'unknown')}
            - Interests: {user_profile.get('interests', [])}
            
            Requirements:
            - Keep it under 100 characters
            - Sound natural and conversational
            - Match the user's likely interests and style
            - Be positive and engaging
            - Avoid generic responses
            
            Return only the response text, no additional formatting.
            """
            response = self._call_gemini_api(prompt)
            if response and isinstance(response, str):
                return response[:100]  # Ensure it's under 100 characters
        except Exception as e:
            self.logger.error(f"Error generating AI response: {e}")
        return self._get_fallback_response(post_content)
    
    def _call_gemini_api(self, prompt: str) -> Optional[Dict]:
        """Make API call to Gemini."""
        try:
            headers = {
                "Content-Type": "application/json",
            }
            data = {
                "contents": [{
                    "parts": [{
                        "text": prompt
                    }]
                }],
                "generationConfig": {
                    "temperature": 0.7,
                    "topK": 40,
                    "topP": 0.95,
                    "maxOutputTokens": 1024,
                }
            }
            url = f"{self.api_url}?key={self.api_key}"
            response = requests.post(url, headers=headers, json=data, timeout=10)
            if response.status_code == 200:
                result = response.json()
                if 'candidates' in result and len(result['candidates']) > 0:
                    text = result['candidates'][0]['content']['parts'][0]['text']
                    # Try to parse as JSON if it looks like JSON
                    if text.strip().startswith('{'):
                        try:
                            return json.loads(text)
                        except Exception:
                            return text
                    return text
            self.logger.error(f"Gemini API error: {response.status_code} - {response.text}")
        except Exception as e:
            self.logger.error(f"Error calling Gemini API: {e}")
        return None
    
    def _get_fallback_analysis(self, username: str, bio: str, comment_text: str) -> Dict:
        """Fallback analysis when AI is unavailable."""
        try:
            username_lower = username.lower()
            bio_lower = bio.lower()
            comment_lower = comment_text.lower()
            male_indicators = ['man', 'boy', 'dude', 'guy', 'bro', 'male', 'dad', 'father', 'son']
            is_male = any(indicator in username_lower for indicator in male_indicators)
        # Enhanced USA detection
            is_usa = self._is_usa_user(username_lower) or self._is_usa_user(bio_lower) or self._is_usa_user(comment_lower)
            # Check comment for American English patterns
            if comment_text:
                american_patterns = ['awesome', 'cool', 'yeah', 'yep', 'nope', 'gonna', 'wanna', 'gotta']
                if any(pattern in comment_lower for pattern in american_patterns):
                    is_usa = True
            return {
                'likely_gender': 'male' if is_male else 'unknown',
                'likely_age_range': 'unknown',
                'likely_location': 'USA' if is_usa else 'unknown',
                'is_usa_user': is_usa,
                'is_male_user': is_male,
                'interests': [],
                'confidence_score': 60 if (is_usa or is_male) else 30,
                'personality_traits': []
        }
        except Exception as e:
            self.logger.error(f"Error in fallback analysis: {e}")
            return {
                'likely_gender': 'unknown',
                'likely_age_range': 'unknown',
                'likely_location': 'unknown',
                'is_usa_user': False,
                'is_male_user': False,
                'interests': [],
                'confidence_score': 0,
                'personality_traits': []
        }
    
    def _get_fallback_response(self, post_content: str) -> str:
        """Fallback response when AI is unavailable."""
        fallback_responses = [
            "Great post! 👍",
            "Interesting perspective!",
            "Thanks for sharing!",
            "Love this! ❤️",
            "Amazing content!",
            "Well said! 👏",
            "This is awesome!",
            "Keep it up! 💪",
            "Fantastic! ✨",
            "Brilliant! 🌟"
        ]
        return random.choice(fallback_responses)
    
    def _get_fallback_female_response(self, comment_text: str) -> str:
        """Generate a fallback female response when AI is unavailable."""
        responses = [
            "That's such a great point! Love your perspective on this 😊",
            "Totally agree with you! Thanks for sharing your thoughts",
            "You always have the best insights! Really appreciate your comment",
            "This is exactly what I was thinking too! Great minds think alike",
            "Love how you explained this! Really helpful perspective",
            "Thanks for sharing this! Your comment really adds to the conversation",
            "That's a really interesting take! I hadn't thought of it that way",
            "You make such a good point! Thanks for contributing to the discussion",
            "Love your energy on this topic! Thanks for sharing",
            "This is so well said! Really appreciate your input",
            "You have such a great way of explaining things! Thanks",
            "That's exactly right! Love your perspective",
            "Thanks for this insight! Really helpful",
            "You always have such thoughtful comments! Love it",
            "This is spot on! Thanks for sharing your thoughts"
        ]
        
        # Choose response based on comment content if possible
        if comment_text:
            comment_lower = comment_text.lower()
            if any(word in comment_lower for word in ['agree', 'right', 'true']):
                return "Totally agree with you! Thanks for sharing your thoughts"
            elif any(word in comment_lower for word in ['great', 'amazing', 'awesome']):
                return "That's such a great point! Love your perspective on this 😊"
            elif any(word in comment_lower for word in ['think', 'thought', 'opinion']):
                return "That's a really interesting take! I hadn't thought of it that way"
            elif any(word in comment_lower for word in ['thanks', 'thank']):
                return "You're so welcome! Thanks for your comment"
        
        return random.choice(responses)

class AndroidEngagement:
    def __init__(self, config_file: str = "android_config.json"):
        """Initialize the Android engagement bot."""
        self.config_file = config_file
        self.devices: Dict[str, Dict] = {}
        self.active_devices: Dict[str, u2.Device] = {}
        self.logger = logging.getLogger(__name__)
        self.ai_analyzer = AIAnalyzer()  # Initialize AI analyzer
        
        # Engagement settings
        self.min_likes_for_viral = 1  # Temporarily lowered for testing
        self.min_comments_for_viral = 1  # Temporarily lowered for testing
        self.max_posts_to_scan = 50
        self.comment_cooldown = 3600
        self.follow_cooldown = 7200  # 2 hours between follows
        self.like_cooldown = 300  # 5 minutes between likes
        self.last_comment_time = {}
        self.last_follow_time = {}
        self.last_like_time = {}
        
        # USA Language Patterns
        self.usa_language_patterns = {
            'common_phrases': [
                r'\b(awesome|cool|yeah|yep|nope|gonna|wanna|gotta)\b',
                r'\b(like|literally|actually|basically|totally)\b',
                r'\b(omg|lol|tbh|idk|imo|fyi)\b',
                r'\b(thanks|thx|ty|np|yw)\b',
                r'\b(hey|hi|hello|yo|sup)\b'
            ],
            'american_spelling': [
                r'\b(color|center|theater|traveler|program)\b',
                r'\b(analyze|organize|realize|specialize)\b',
                r'\b(behavior|humor|labor|favor)\b',
                r'\b(license|defense|offense|pretense)\b'
            ],
            'american_expressions': [
                r'\b(awesome sauce|my bad|no worries|for real)\b',
                r'\b(that\'s cool|sounds good|you bet|sure thing)\b',
                r'\b(heck yeah|heck no|darn|shoot)\b',
                r'\b(awesome|epic|sick|rad|dope)\b'
            ],
            'punctuation_patterns': [
                r'\.{3,}',  # Multiple dots
                r'!{2,}',   # Multiple exclamation marks
                r'\?{2,}',  # Multiple question marks
                r'[A-Z]{2,}'  # ALL CAPS words
            ],
            'emoji_patterns': [
                r'[🔥💯🙌👏✨🎯🌟💪🙏🎉]',
                r'[👍👎❤️💔😊😎🤔]',
                r'[😂🤣😅😆😉]'
            ]
        }
        
        # Response templates
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

        # Load configuration
        self.load_config()
        
        # Connect to devices as needed (not all at once)
        # Devices will be connected when needed in connect_device method

    def _is_usa_user(self, text: str) -> bool:
        """Enhanced USA detection using keywords, state names, cities, and American English spelling."""
        text = text.lower()
        usa_keywords = [
            'usa', 'united states', 'american', 'us citizen', 'us_', '_us', '🇺🇸', 'nyc', 'la', 'sf', 'dallas', 'miami', 'texas', 'california', 'chicago', 'atlanta', 'boston', 'seattle', 'vegas', 'florida', 'houston', 'philly', 'washington', 'dc', 'new york', 'los angeles', 'san francisco', 'phoenix', 'denver', 'detroit', 'minneapolis', 'portland', 'baltimore', 'cleveland', 'nashville', 'austin', 'orlando', 'pittsburgh', 'cincinnati', 'charlotte', 'indianapolis', 'columbus', 'milwaukee', 'kansas city', 'salt lake', 'st louis', 'oklahoma', 'albuquerque', 'tucson', 'fresno', 'sacramento', 'mesa', 'omaha', 'colorado', 'carolina', 'jersey', 'browns', 'bronx', 'queens', 'brooklyn', 'manhattan', 'long island', 'midwest', 'bay area', 'silicon valley', 'hollywood'
        ]
        us_states = [
            'alabama', 'alaska', 'arizona', 'arkansas', 'california', 'colorado', 'connecticut', 'delaware', 'florida', 'georgia', 'hawaii', 'idaho', 'illinois', 'indiana', 'iowa', 'kansas', 'kentucky', 'louisiana', 'maine', 'maryland', 'massachusetts', 'michigan', 'minnesota', 'mississippi', 'missouri', 'montana', 'nebraska', 'nevada', 'new hampshire', 'new jersey', 'new mexico', 'new york', 'north carolina', 'north dakota', 'ohio', 'oklahoma', 'oregon', 'pennsylvania', 'rhode island', 'south carolina', 'south dakota', 'tennessee', 'texas', 'utah', 'vermont', 'virginia', 'washington', 'west virginia', 'wisconsin', 'wyoming'
        ]
        american_spelling = ['color', 'center', 'theater', 'traveler', 'analyze', 'organize', 'realize', 'specialize', 'behavior', 'humor', 'labor', 'favor', 'license', 'defense', 'offense', 'pretense']
        for word in usa_keywords + us_states + american_spelling:
            if word in text:
                return True
        return False

    def analyze_user_profile(self, device: u2.Device, username: str) -> Optional[Dict]:
        """Analyze a user's profile by clicking on their username and extracting information."""
        try:
            logger.info(f"Analyzing profile for username: {username}")
            if not self.click_username_in_comments(device, username):
                logger.error(f"Failed to click on username: {username}")
                return None
            time.sleep(3)
            profile_info = {
                'username': username,
                'bio': '',
                'followers': 0,
                'following': 0,
                'posts': 0,
                'is_verified': False,
                'is_private': False,
                'location': '',
                'website': '',
                'gender': 'unknown',
                'age_group': 'unknown',
                'interests': [],
                'language': 'unknown',
                'is_usa': False
            }
            # Look for bio text
            try:
                bio_elements = device.xpath('//*[contains(@text, "bio") or contains(@content-desc, "bio")]').all()
                if not bio_elements:
                    all_text_elements = device.xpath('//*[@text]').all()
                    for element in all_text_elements:
                        text = element.attrib.get('text', '')
                        if text and len(text) > 10 and len(text) < 200:
                            profile_info['bio'] = text
                            logger.info(f"Found bio: {text}")
                            break
                else:
                    bio_text = bio_elements[0].attrib.get('text', '') or bio_elements[0].attrib.get('content-desc', '')
                    if bio_text:
                        profile_info['bio'] = bio_text
                        logger.info(f"Found bio: {bio_text}")
            except Exception as e:
                logger.debug(f"Error extracting bio: {e}")
            
            # Enhanced USA detection
            combined_text = f"{username} {profile_info['bio']}"
            profile_info['is_usa'] = self._is_usa_user(combined_text)
            
            # Go back to the post
            logger.info("Going back to post from profile...")
            self.click_back_to_post(device)
            time.sleep(2)
            
            logger.info(f"Profile analysis complete for {username}: {profile_info}")
            return profile_info
            
        except Exception as e:
            logger.error(f"Error analyzing profile for {username}: {e}")
            # Try to go back to post
            try:
                self.click_back_to_post(device)
            except:
                pass
            return None

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
            # Handle USB connection
            if device_config['serial'] == 'usb':
                device = u2.connect()  # Connect to first available USB device
            else:
                device = u2.connect(device_config['serial'])
            
            # Test the connection with a simple operation
            try:
                device.info
                logger.info(f"Successfully connected to device: {device_name}")
            except Exception as test_error:
                logger.error(f"Device connection test failed for {device_name}: {test_error}")
                return None
            
            self.active_devices[device_name] = device
            logger.info(f"Connected to device: {device_name}")
            return device
        except Exception as e:
            logger.error(f"Error connecting to device {device_name}: {str(e)}")
            return None

    def open_threads_app(self, device: u2.Device):
        """Open the Threads app on the device."""
        try:
            # Try to open Threads using the app name directly
            try:
                device.app_start("Threads")
                time.sleep(5)
                logger.info("Threads app opened successfully by name")
                return
            except Exception as e:
                logger.debug(f"Failed to open Threads by name: {str(e)}")
            
            # If that fails, try to find and click the Threads app icon
            try:
                # Look for Threads app icon on home screen
                threads_icon = device.xpath('//*[contains(@text, "Threads") or contains(@content-desc, "Threads")]').get()
                if threads_icon:
                    threads_icon.click()
                    time.sleep(5)
                    logger.info("Threads app opened by clicking icon")
                    return
            except Exception as e:
                logger.debug(f"Failed to find Threads icon: {str(e)}")
            
            # If all else fails, just assume we're already in Threads
            logger.info("Assuming Threads app is already open or will be opened manually")
                
        except Exception as e:
            logger.error(f"Error opening Threads app: {str(e)}")
            # Try alternative method - click on Threads icon
            try:
                threads_icon = device.xpath('//*[contains(@content-desc, "Threads")]').first()
                if threads_icon:
                    threads_icon.click()
                    time.sleep(3)
                    logger.info("Threads app opened by clicking icon")
                    else:
                    logger.info("Assuming Threads app is already open or will be opened manually")
            except Exception as icon_error:
                logger.error(f"Error clicking Threads icon: {icon_error}")
                logger.info("Assuming Threads app is already open or will be opened manually")

    def scan_feed(self, device: u2.Device) -> list:
        """Minimal working example for linter: scan the feed and return an empty list."""
        try:
            logger.info("Scanning feed (minimal example)...")
            # Simulate scanning logic
            return []
        except Exception as e:
            logger.error(f"Error scanning feed: {str(e)}")
            return []

    def scan_feed_unfiltered(self, device: u2.Device, device_name: str) -> List[Dict]:
        """Scan feed for viral posts using unfiltered element search."""
        try:
            logger.info("Scanning feed for viral posts (unfiltered search)...")
            viral_posts = []
            
            for scroll_attempt in range(self.max_posts_to_scan):
                try:
                    logger.info(f"Scan attempt {scroll_attempt + 1}/{self.max_posts_to_scan}")
                    
                    # Find heart icons (like buttons)
                    heart_icons = self.safe_find_elements(device, '//*[contains(@content-desc, "Like") or contains(@content-desc, "like")]')
                    logger.info(f"Found {len(heart_icons)} heart icons")
                    
                    if not heart_icons:
                        logger.info("No heart icons found, scrolling down...")
                        device.swipe(0.5, 0.8, 0.5, 0.2)
                        time.sleep(3)
                        continue
                    
                    # Find all elements with numbers - use unfiltered search to ensure we don't miss any
                    elements_with_numbers = []
                    logger.info("Searching for numbers in all elements (unfiltered)...")
                    
                    # Use unfiltered search for number detection
                    all_elements_unfiltered = device.xpath('//*').all()
                    logger.info(f"Found {len(all_elements_unfiltered)} total elements (unfiltered)")
                    
                    for i, element in enumerate(all_elements_unfiltered):
                        try:
                            # Check text attribute
                            text = element.attrib.get('text', '')
                            if text:
                                logger.debug(f"Checking text: '{text}'")
                                num = self.extract_number_from_text(text)
                                if num > 0:
                                    elements_with_numbers.append((element, num, text, "text"))
                                    logger.info(f"Element {i}: text='{text}' -> number: {num}")
                            
                            # Check content description
                            content_desc = element.attrib.get('content-desc', '')
                            if content_desc:
                                logger.debug(f"Checking content-desc: '{content_desc}'")
                                num = self.extract_number_from_text(content_desc)
                                if num > 0:
                                    elements_with_numbers.append((element, num, content_desc, "content-desc"))
                                    logger.info(f"Element {i}: content-desc='{content_desc}' -> number: {num}")
                            
                            # Check resource ID
                            resource_id = element.attrib.get('resource-id', '')
                            if resource_id:
                                logger.debug(f"Checking resource-id: '{resource_id}'")
                                num = self.extract_number_from_text(resource_id)
                                if num > 0:
                                    elements_with_numbers.append((element, num, resource_id, "resource-id"))
                                    logger.info(f"Element {i}: resource-id='{resource_id}' -> number: {num}")
                                    
                        except Exception as e:
                            logger.debug(f"Error processing element {i}: {e}")
                            continue
                    
                    logger.info(f"Found {len(elements_with_numbers)} elements with numbers on screen")
                    
                    # Process each heart icon
                    for i, heart_icon in enumerate(heart_icons):
                        try:
                            heart_center = heart_icon.center()
                            logger.info(f"Heart icon {i}: center at ({heart_center[0]}, {heart_center[1]})")
                            
                            # Skip heart icons that are too high on screen (likely in profile/create post area)
                            if heart_center[1] < 400:  # Much more restrictive - avoid top 400 pixels
                                logger.error("Heart icon is too high on screen - likely in profile/create post area. Skipping this post.")
                                continue
                            
                            # Find numbers near this heart icon
                            nearby_numbers = []
                            for element, num, text, field_type in elements_with_numbers:
                                try:
                                    element_center = element.center()
                                    distance = ((heart_center[0] - element_center[0])**2 + 
                                              (heart_center[1] - element_center[1])**2)**0.5
                                    
                                    # Increase distance threshold to 800 pixels to catch more numbers
                                    if distance <= 800:  # Increased from 500 to 800
                                        nearby_numbers.append((num, distance, text, field_type))
                                        logger.info(f"  Found number {num} at distance {distance:.1f} (from {field_type}: '{text}')")
                                        else:
                                        logger.debug(f"  Number {num} too far at distance {distance:.1f} (from {field_type}: '{text}')")
                                except Exception as e:
                                    logger.debug(f"  Error calculating distance for number {num}: {e}")
                                    continue
                            
                            logger.info(f"Heart icon {i}: found {len(nearby_numbers)} nearby numbers")
                            
                            # Simplified viral post detection - look for any post with sufficient engagement
                            if len(nearby_numbers) >= 1:  # Changed from 2 to 1
                                # Sort by distance and take the closest numbers
                                nearby_numbers.sort(key=lambda x: x[1])
                                
                                # Use the first number as like count, second as comment count if available
                                like_count = nearby_numbers[0][0]
                                comment_count = nearby_numbers[1][0] if len(nearby_numbers) > 1 else 0
                                
                                logger.info(f"  Using like count: {like_count}, comment count: {comment_count}")
                                logger.info(f"  Viral thresholds: min_likes={self.min_likes_for_viral}, min_comments={self.min_comments_for_viral}")
                                
                                # Verify this is actually a post by checking if it has a heart icon
                                if like_count >= self.min_likes_for_viral and comment_count >= self.min_comments_for_viral:
                                    # Double-check that this heart icon is actually a like button (not in profile area)
                                    try:
                                        # Check if the heart icon has a "Like" or "Unlike" content description
                                        heart_content_desc = heart_icon.attrib.get('content-desc', '')
                                        if 'like' in heart_content_desc.lower() or 'unlike' in heart_content_desc.lower():
                                            logger.info(f"=== FOUND VIRAL POST ===")
                                            logger.info(f"Like count: {like_count}")
                                            logger.info(f"Comment count: {comment_count}")
                                            logger.info(f"Heart element: {heart_icon}")
                                            logger.info(f"Number element: {nearby_numbers[0][2]}")
                                            
                                            viral_post = {
                                                'heart_icon': heart_icon,
                                                'like_count': like_count,
                                                'comment_count': comment_count,
                                                'number_element': nearby_numbers[0][2],
                                                'distance': nearby_numbers[0][1]
                                            }
                                            viral_posts.append(viral_post)
                                            logger.info(f"Added viral post to list. Total found: {len(viral_posts)}")
                                            
                                            # Process this post immediately
                                            logger.info("Processing viral post immediately...")
                                            self.process_post(device, device_name, viral_post)
                                            break  # Process one post at a time
                                        else:
                                            logger.info(f"  Heart icon does not have like/unlike content: '{heart_content_desc}' - skipping")
                                    except Exception as e:
                                        logger.error(f"  Error checking heart icon content: {e}")
                                        # If we can't verify, skip this post to be safe
                                        continue
                                else:
                                    logger.info(f"  Post doesn't meet viral criteria: {like_count} likes, {comment_count} comments")
                                    else:
                                logger.info(f"Heart icon {i}: no nearby numbers found, checking all numbers on screen...")
                                
                                # If no nearby numbers, check if there are any numbers on screen at all
                                if elements_with_numbers:
                                    logger.info(f"  Found {len(elements_with_numbers)} numbers on screen but none near heart icon")
                                    # Use the first number as a fallback
                                    first_number = elements_with_numbers[0]
                                    logger.info(f"  Using fallback number: {first_number[1]} from {first_number[3]}: '{first_number[2]}'")
                                    
                                    if first_number[1] >= self.min_likes_for_viral:
                                        logger.info(f"=== FOUND VIRAL POST (fallback) ===")
                                        viral_post = {
                                            'heart_icon': heart_icon,
                                            'like_count': first_number[1],
                                            'comment_count': 0,
                                            'number_element': first_number[2],
                                            'distance': 999  # Unknown distance
                                        }
                                        viral_posts.append(viral_post)
                                        logger.info(f"Added viral post to list (fallback). Total found: {len(viral_posts)}")
                                        
                                        # Process this post immediately
                                        logger.info("Processing viral post immediately (fallback)...")
                                        self.process_post(device, device_name, viral_post)
                                        break  # Process one post at a time
                                else:
                                    logger.info(f"  No numbers found on screen at all")
                        
                        except Exception as e:
                            logger.error(f"Error processing heart icon {i}: {e}")
                            continue
                    
                    # If we found a viral post, break out of the scroll loop
                    if viral_posts:
                        break
                    
                    # If no viral posts found, scroll down and try again
                    logger.info("No viral posts found in this view, scrolling down...")
                    device.swipe(0.5, 0.8, 0.5, 0.2)
                    time.sleep(3)
                    
                except Exception as e:
                    logger.error(f"Error in scan attempt {scroll_attempt + 1}: {e}")
                    # Try to scroll and continue
                    try:
                        device.swipe(0.5, 0.8, 0.5, 0.2)
                        time.sleep(3)
                    except:
                        pass
                    continue
            
            logger.info(f"Scan complete. Found {len(viral_posts)} viral posts.")
            return viral_posts
            
        except Exception as e:
            logger.error(f"Error in scan_feed_unfiltered: {e}")
            return []

    def debug_unfiltered_number_search(self, device: u2.Device) -> List[Tuple[Any, int, str, str]]:
        # Implementation of debug_unfiltered_number_search method
        pass

    def debug_clickable_usernames(self, device: u2.Device) -> bool:
        # Implementation of debug_clickable_usernames method
        pass

    def simple_username_click_test(self, device: u2.Device) -> bool:
        # Implementation of simple_username_click_test method
        pass

    def detect_usernames_in_feed(self, device: u2.Device) -> List[Tuple[Any, str, str]]:
        # Implementation of detect_usernames_in_feed method
        pass

    def simple_heart_icon_detection(self, device: u2.Device) -> bool:
        # Implementation of simple_heart_icon_detection method
        pass

    def detect_nearby_numbers(self, device: u2.Device) -> List[Tuple[int, float, str, str]]:
        # Implementation of detect_nearby_numbers method
        pass

    def extract_number_from_text(self, text: str) -> int:
        """Extract a number from a string, handling K/M/B suffixes."""
        try:
            import re
            match = re.search(r"(\d+[\.,]?\d*)([KMB]?)", text.replace(",", ""))
            if not match:
                logger.debug(f"No numbers found in '{text}'")
                return 0
            num_str, suffix = match.groups()
            num_str = num_str.replace(',', '').replace(' ', '')
            result = 0
            if suffix == 'K':
                result = int(float(num_str) * 1000)
            elif suffix == 'M':
                result = int(float(num_str) * 1000000)
            elif suffix == 'B':
                result = int(float(num_str) * 1000000000)
                else:
                result = int(float(num_str))
            logger.debug(f"Extracted number from '{text}': {result}")
            return result
        except Exception as e:
            logger.debug(f"Error extracting number from text '{text}': {str(e)}")
            return 0

    def safe_find_elements(self, device: u2.Device, xpath: str) -> List[Any]:
        """Safely find elements using xpath, filtering out system UI elements."""
        try:
            elements = device.xpath(xpath).all()
            filtered_elements = []
            for element in elements:
                try:
                    # Filter out system UI elements
                    resource_id = element.attrib.get('resource-id', '')
                    package = element.attrib.get('package', '')
                    # Skip system UI elements
                    if (resource_id.startswith('com.android.systemui') or 
                        resource_id.startswith('android:id/') or
                        package == 'com.android.systemui'):
                        continue
                    filtered_elements.append(element)
                except Exception as e:
                    logger.debug(f"Error filtering element: {e}")
                    continue
            return filtered_elements
        except Exception as e:
            logger.error(f"Error finding elements with xpath '{xpath}': {e}")
            return []

    def safe_get_text(self, element) -> str:
        """Safely get text from an element."""
        try:
            return element.attrib.get('text', '') or element.attrib.get('content-desc', '')
        except Exception as e:
            logger.debug(f"Error getting text from element: {e}")
            return ""

    def run(self):
        """Main method to run the engagement bot."""
        try:
            logger.info("Starting Android engagement bot...")
            for device_name in self.devices:
                try:
                    logger.info(f"Starting engagement on device: {device_name}")
                    device = self.connect_device(device_name)
                    if not device:
                        logger.error(f"Failed to connect to device: {device_name}")
                        continue
                    # Open Threads app
                    self.open_threads_app(device)
                    time.sleep(5)
                    # Scan for viral posts using the unfiltered method
                    viral_posts = self.scan_feed_unfiltered(device, device_name)
                    logger.info(f"Scan completed. Found {len(viral_posts)} viral posts")
                    if not viral_posts:
                        logger.info("No viral posts found, continuing to next scan...")
                        continue
                    logger.info("Processing viral posts...")
                    # Process each viral post
                    for i, post in enumerate(viral_posts):
                        try:
                            logger.info(f"Processing viral post {i+1}/{len(viral_posts)}")
                            logger.info(f"Post details: {post['like_count']} likes, {post['comment_count']} comments")
                            self.process_post(device, device_name, post)
                        except Exception as e:
                            logger.error(f"Error processing post: {e}")
                            continue
                except Exception as e:
                    logger.error(f"Error with device {device_name}: {e}")
                    continue
        except Exception as e:
            logger.error(f"Error in main run method: {e}")

    def process_post(self, device: u2.Device, device_name: str, post: Dict):
        """Process a viral post by opening it and looking for usernames in comments."""
        try:
            logger.info(f"=== PROCESSING POST: {post} ===")
            # Get the heart icon element
            heart_element = post.get('heart_icon')
            if not heart_element:
                logger.error("No heart element found in post")
                return
            # Get heart icon position
            try:
                heart_bounds = heart_element.attrib.get('bounds', '')
                logger.info(f"Heart icon bounds: {heart_bounds}")
                # Parse bounds to get coordinates
                if heart_bounds:
                    # Format: "[left,top][right,bottom]"
                    # Remove the outer brackets and split by "]["
                    bounds_clean = heart_bounds.strip('[]')
                    bounds_parts = bounds_clean.split('][')
                    if len(bounds_parts) == 2:
                        # Parse left,top
                        left_top = bounds_parts[0].split(',')
                        # Parse right,bottom  
                        right_bottom = bounds_parts[1].split(',')
                        if len(left_top) == 2 and len(right_bottom) == 2:
                            left, top = map(int, left_top)
                            right, bottom = map(int, right_bottom)
                            heart_x = (left + right) // 2
                            heart_y = (top + bottom) // 2
                            logger.info(f"Heart icon center: ({heart_x}, {heart_y})")
                            else:
                            logger.error(f"Invalid coordinate format in bounds: {heart_bounds}")
                            return
                    else:
                        logger.error(f"Invalid coordinate format in bounds: {heart_bounds}")
                        return
                else:
                    logger.error(f"Invalid bounds format: {heart_bounds}")
                    return
            except Exception as e:
                logger.error(f"Error parsing heart bounds: {e}")
                return
            # Try to click on the post content area (to the left and above the heart)
            click_positions = [
                (heart_x - 200, heart_y - 50),  # Left and above
                (heart_x - 150, heart_y - 30),  # Closer to heart
                (heart_x - 100, heart_y - 20),  # Even closer
                (heart_x, heart_y),  # On the heart itself as fallback
            ]
            post_opened = False
            for i, (click_x, click_y) in enumerate(click_positions):
                try:
                    logger.info(f"Attempting to click position {i+1}: ({click_x}, {click_y})")
                    device.click(click_x, click_y)
                    time.sleep(3)
                    # Check if comment section is open
                    if self.is_comment_section_open(device):
                        logger.info(f"Successfully opened post with click position {i+1}")
                        post_opened = True
                        break
                    else:
                        logger.info(f"Click position {i+1} did not open comment section")
                except Exception as e:
                    logger.error(f"Error clicking position {i+1}: {e}")
                    continue
            if not post_opened:
                logger.error("Failed to open post comment section after all attempts")
                return
            # Now look for usernames in comments
            logger.info("=== LOOKING FOR USERNAMES IN COMMENTS ===")
            # First, scroll through comments to load actual commenters
            logger.info("=== SCROLLING COMMENTS TO LOAD COMMENTERS ===")
            self.scroll_comments(device)
            # Now look for usernames in the comment section
            usernames = self.find_usernames_in_comments(device)
            if usernames:
                logger.info(f"Found {len(usernames)} usernames: {usernames}")
                # Process each username
                for username in usernames[:3]:  # Limit to first 3 usernames
                    logger.info(f"Processing username: {username}")
                    # Analyze user profile
                    logger.info(f"=== ANALYZING PROFILE FOR: {username} ===")
                    profile_info = self.analyze_user_profile(device, username)
                    if profile_info:
                        logger.info(f"Profile analysis for {username}: {profile_info}")
                        # Generate engagement response
                        logger.info(f"=== GENERATING ENGAGEMENT RESPONSE FOR: {username} ===")
                        response = self.generate_ai_response(username, profile_info)
                        if response:
                            logger.info(f"Generated response for {username}: {response}")
                            # Post the response
                            logger.info(f"=== POSTING RESPONSE FOR: {username} ===")
                            self.post_comment_response(device, response, username)
                            # Add cooldown between comments
                            time.sleep(5)
                            else:
                            logger.warning(f"Failed to generate response for {username}")
                            else:
                        logger.warning(f"Failed to analyze profile for {username}")
                        else:
                logger.warning("No usernames found in comments")
            # Go back to feed
            logger.info("Going back to feed...")
            self.click_back_to_post(device)
            time.sleep(2)
        except Exception as e:
            logger.error(f"Error processing post: {e}")
            # Try to go back to feed
            try:
                self.click_back_to_post(device)
            except:
                pass

    def process_comments_in_post(self, device: u2.Device, device_name: str):
        """Process comments in the opened post to find and engage with USA male users."""
        try:
            logger.info("=== STARTING COMMENT PROCESSING ===")
            
            # First check if we're actually in the comment section
            if not self.is_comment_section_open(device):
                logger.error("Comment section is not open! Cannot process comments.")
                return
            
            logger.info("Comment section is open, starting to process comments...")
            
            # Track processed usernames to avoid duplicates
            processed_usernames = set()
            engagement_count = 0
            max_engagements_per_post = 5  # Limit engagements per post
            
            # Initial scroll to load comments (reduced from 10 to 3 scrolls)
            logger.info("Starting initial comment scrolling to find commenters...")
            self.scroll_comments_initial(device)
            
            # Main engagement loop
            for engagement_round in range(3):  # Try up to 3 rounds of engagement per post
                logger.info(f"=== ENGAGEMENT ROUND {engagement_round + 1}/3 ===")
                
                # Find usernames in current view
                usernames = self.find_usernames_in_comments(device)
                logger.info(f"Found {len(usernames)} usernames in current view")
                
                # Filter out already processed usernames
                new_usernames = [u for u in usernames if u not in processed_usernames]
                logger.info(f"Found {len(new_usernames)} new usernames to process")
                
                if not new_usernames:
                    logger.info("No new usernames found, scrolling up to look for more...")
                    # Scroll up to find more usernames
                    self.scroll_comments_up(device)
                    time.sleep(2)
                    
                    # Check again after scrolling up
                    usernames = self.find_usernames_in_comments(device)
                    new_usernames = [u for u in usernames if u not in processed_usernames]
                    logger.info(f"After scrolling up, found {len(new_usernames)} new usernames")
                
                if not new_usernames:
                    logger.info("No more new usernames found, ending engagement round")
                    break
                
                # Process each new username
                for username in new_usernames[:3]:  # Process up to 3 usernames per round
                    if engagement_count >= max_engagements_per_post:
                        logger.info(f"Reached max engagements per post ({max_engagements_per_post})")
                        break
                        
                    try:
                        logger.info(f"Processing username: {username}")
                        
                        # Click on username to open profile
                        if self.click_username_in_comments(device, username):
                            logger.info(f"Successfully clicked on username: {username}")
                            time.sleep(3)
                            
                            # Analyze profile
                            profile_info = self.analyze_user_profile(device, username)
                            
                            if profile_info and profile_info.get('is_male') and profile_info.get('is_usa'):
                                logger.info(f"Found USA male user: {username}")
                                
                                # Click back to return to post
                                if self.click_back_to_post(device):
                                    logger.info("Successfully returned to post")
                                    time.sleep(2)
                                    
                                    # Generate AI response and post it
                                    response = self.generate_ai_response(username, profile_info)
                                    if response:
                                        logger.info(f"Posting AI response to {username}: {response}")
                                        self.post_comment_response(device, response, username)
                                        engagement_count += 1
                                        time.sleep(3)  # Wait after posting
                                        
                                        # After posting, scroll up efficiently to find more usernames
                                        logger.info("Scrolling up after posting comment to find more usernames...")
                                        self.scroll_comments_up(device)
                                        time.sleep(2)
                                        else:
                                        logger.warning("Failed to generate response")
                                        else:
                                    logger.warning("Failed to return to post")
                                    else:
                                logger.info(f"User {username} is not a USA male, skipping")
                                # Click back anyway to return to post
                                self.click_back_to_post(device)
                                time.sleep(2)
                                else:
                            logger.warning(f"Failed to click on username: {username}")
                            
                    except Exception as e:
                        logger.error(f"Error processing username {username}: {e}")
                        # Try to click back to post if we're stuck on a profile
                        try:
                            self.click_back_to_post(device)
                            time.sleep(2)
                        except:
                            pass
                        continue
                    
                    # Mark username as processed
                    processed_usernames.add(username)
                
                # If we've reached max engagements, break
                if engagement_count >= max_engagements_per_post:
                    logger.info(f"Reached max engagements per post ({max_engagements_per_post})")
                    break
            
            logger.info(f"=== FINISHED COMMENT PROCESSING - Total engagements: {engagement_count} ===")
                    
        except Exception as e:
            logger.error(f"Error processing comments in post: {e}")

    def scroll_comments_initial(self, device: u2.Device):
        """Initial scroll down in comments to load content (reduced from 10 to 3 scrolls)."""
        try:
            logger.info("=== STARTING INITIAL COMMENT SCROLLING ===")
            screen_width, screen_height = device.window_size()
            logger.info(f"Screen size: {screen_width} x {screen_height}")
            # Reduced initial scrolling from 10 to 3 scrolls
            for i in range(3):
                start_y = int(screen_height * 0.8)
                end_y = int(screen_height * 0.2)
                start_x = screen_width // 2
                logger.info(f"Initial scrolling (attempt {i+1}/3) from ({start_x}, {start_y}) to ({start_x}, {end_y})")
                device.swipe(start_x, start_y, start_x, end_y, duration=0.5)
                time.sleep(2)
                usernames = self.find_usernames_in_comments(device)
                logger.info(f"Found {len(usernames)} usernames after initial scroll {i+1}")
                if usernames:
                    logger.info(f"Sample usernames: {usernames[:3]}")
            logger.info("=== FINISHED INITIAL COMMENT SCROLLING ===")
        except Exception as e:
            logger.error(f"Error in initial comment scrolling: {e}")

    def scroll_comments_up(self, device: u2.Device):
        """Scroll up in comments to find more usernames (efficient scrolling)."""
        try:
            logger.info("=== SCROLLING UP TO FIND MORE USERNAMES ===")
            screen_width, screen_height = device.window_size()
            # Scroll up efficiently (only 1-2 scrolls)
            for i in range(2):
                start_y = int(screen_height * 0.3)  # Start from middle
                end_y = int(screen_height * 0.9)    # Scroll up
                start_x = screen_width // 2
                logger.info(f"Scrolling up (attempt {i+1}/2) from ({start_x}, {start_y}) to ({start_x}, {end_y})")
                device.swipe(start_x, start_y, start_x, end_y, duration=0.5)
                time.sleep(1.5)  # Shorter wait time
                usernames = self.find_usernames_in_comments(device)
                logger.info(f"Found {len(usernames)} usernames after scroll up {i+1}")
                if usernames:
                    logger.info(f"Sample usernames: {usernames[:3]}")
                break  # If we found usernames, stop scrolling
            logger.info("=== FINISHED SCROLLING UP ===")
        except Exception as e:
            logger.error(f"Error scrolling up: {e}")

    def scroll_comments(self, device: u2.Device):
        """Scroll down in comments to load more content (legacy method, kept for compatibility)."""
        try:
            logger.info("=== STARTING COMMENT SCROLLING ===")
            screen_width, screen_height = device.window_size()
            logger.info(f"Screen size: {screen_width} x {screen_height}")
            # Scroll down more extensively to load many more comments
            for i in range(5):  # Reduced from 10 to 5 scrolls
                start_y = int(screen_height * 0.8)
                end_y = int(screen_height * 0.2)
                start_x = screen_width // 2
                logger.info(f"Scrolling comments (attempt {i+1}/5) from ({start_x}, {start_y}) to ({start_x}, {end_y})")
                device.swipe(start_x, start_y, start_x, end_y, duration=0.5)
                time.sleep(2)
                # After each scroll, check if we're finding new usernames
                if i % 2 == 0:  # Check every 2nd scroll
                    usernames = self.find_usernames_in_comments(device)
                    logger.info(f"Found {len(usernames)} usernames after scroll {i+1}")
                    if usernames:
                        logger.info(f"Sample usernames: {usernames[:3]}")
            logger.info("=== FINISHED COMMENT SCROLLING ===")
        except Exception as e:
            logger.error(f"Error scrolling comments: {e}")

    def click_back_to_post(self, device: u2.Device) -> bool:
        """Click back button to return to the post from a user profile."""
        try:
            # Try system back button first
            device.press("back")
            time.sleep(1)
            return True
            
        except Exception as e:
            logger.error(f"Error clicking back to post: {e}")
            return False

    def generate_ai_response(self, username: str, profile_info: Dict) -> str:
        """Generate an AI-powered engagement response based on user profile analysis."""
        try:
            logger.info(f"Generating AI response for {username} based on profile: {profile_info}")
            
            # Extract profile information
            bio = profile_info.get('bio', '')
            gender = profile_info.get('gender', 'unknown')
            interests = profile_info.get('interests', [])
            followers = profile_info.get('followers', 0)
            language = profile_info.get('language', 'english')
            
            # Use AI analyzer to generate response
            try:
                response = self.ai_analyzer.generate_female_engagement_response(
                    post_content="",  # We don't have the original post content here
                    user_profile=profile_info,
                    comment_text=""
                )
                
                if response and len(response.strip()) > 0:
                    logger.info(f"AI generated response: {response}")
                    return response
                    
            except Exception as e:
                logger.warning(f"AI response generation failed: {e}")
            
            # Fallback to template-based responses
            logger.info("Using fallback template-based response")
            
            # Choose response based on interests
            if interests:
                primary_interest = interests[0]
                
                if primary_interest == 'crypto':
                    responses = [
                        "Love your crypto insights! 🚀 What's your take on the current market?",
                        "Great crypto perspective! 💎 Any tips for a fellow trader?",
                        "Your crypto analysis is spot on! 📈 What's your next move?",
                        "Awesome crypto content! 🔥 Keep sharing those insights!"
                    ]
                elif primary_interest == 'fitness':
                    responses = [
                        "Your fitness journey is inspiring! 💪 What's your favorite workout?",
                        "Love your fitness content! 🏋️‍♀️ Any tips for staying motivated?",
                        "Your dedication to fitness is amazing! 🔥 Keep crushing those goals!",
                        "Great fitness vibes! 💯 What's your go-to exercise routine?"
                    ]
                elif primary_interest == 'business':
                    responses = [
                        "Your business insights are valuable! 💼 What's your biggest lesson learned?",
                        "Love your entrepreneurial spirit! 🚀 Any advice for aspiring founders?",
                        "Your business content is gold! 💎 Keep sharing that wisdom!",
                        "Amazing business perspective! 🔥 What's your next big move?"
                    ]
                elif primary_interest == 'tech':
                    responses = [
                        "Your tech insights are on point! 💻 What's the most exciting tech trend?",
                        "Love your tech content! 🚀 Any coding tips to share?",
                        "Your tech knowledge is impressive! 🔥 What's your favorite programming language?",
                        "Great tech perspective! 💯 Keep sharing that innovation!"
                    ]
                elif primary_interest == 'travel':
                    responses = [
                        "Your travel adventures look amazing! ✈️ What's your favorite destination?",
                        "Love your travel content! 🌍 Any hidden gems you've discovered?",
                        "Your wanderlust is contagious! 🔥 Where's your next adventure?",
                        "Amazing travel vibes! 💫 What's your most memorable trip?"
                    ]
                    else:
                    # Generic responses for other interests
                    responses = [
                        "Love your content! 🔥 Keep sharing your passion!",
                        "Your perspective is so valuable! 💯 Thanks for sharing!",
                        "Amazing insights! 🙌 Keep up the great work!",
                        "Your content always inspires! ✨ Love your energy!"
                    ]
                    else:
                # No specific interests detected, use general responses
                responses = [
                    "Great post! 🔥 Love your content!",
                    "Your perspective is so valuable! 💯",
                    "Amazing insights! 🙌 Keep sharing!",
                    "Love your energy! ✨ Thanks for the inspiration!",
                    "Your content is always on point! 🎯",
                    "Great vibes! 💫 Keep up the amazing work!",
                    "Your posts are so relatable! 💕",
                    "Love your authenticity! 🔥 Keep being you!"
                ]
            
            # Choose a random response
            import random
            response = random.choice(responses)
            
            # Add emoji based on gender (for female engagement)
            if gender == 'male':
                # Add flirty/friendly emojis for male profiles
                flirty_emojis = ['😊', '💕', '✨', '🌸', '💖', '😍', '💫', '🌹']
                response += f" {random.choice(flirty_emojis)}"
            
            logger.info(f"Generated fallback response: {response}")
            return response
            
        except Exception as e:
            logger.error(f"Error generating AI response: {e}")
            # Ultimate fallback
            return "Great post! 🔥 Love your content!"

    def post_comment_response(self, device: u2.Device, response: str, target_username: str = ""):
        """Post a comment response by clicking on the target comment first."""
        try:
            logger.info(f"Attempting to post comment response to {target_username}: {response}")
            
            # First, make sure we're in the comment section
            if not self.is_comment_section_open(device):
                logger.error("Not in comment section, cannot post comment")
                return
            
            # Find and click on the target comment to open reply interface
            comment_clicked = False
            
            # First, try to find the Reply button associated with the target username
            reply_elements = device.xpath('//*[contains(@content-desc, "Reply") or contains(@text, "Reply")]').all()
            logger.info(f"Found {len(reply_elements)} reply elements")
            
            for reply_element in reply_elements:
                try:
                    reply_text = reply_element.attrib.get('text', '')
                    reply_content_desc = reply_element.attrib.get('content-desc', '')
                    
                    # Check if this reply button is associated with our target username
                    if target_username in reply_text or target_username in reply_content_desc:
                        logger.info(f"Found reply button for {target_username}: text='{reply_text}', content-desc='{reply_content_desc}'")
                        reply_center = reply_element.center()
                        logger.info(f"Clicking on reply button at ({reply_center[0]}, {reply_center[1]})")
                        device.click(reply_center[0], reply_center[1])
                    time.sleep(2)
                        comment_clicked = True
                    break
            except Exception as e:
                    logger.debug(f"Error checking reply element: {e}")
                    continue
            
            # If no specific reply button found, try clicking on the comment text
            if not comment_clicked:
                logger.info("No specific reply button found, trying to click on comment text")
                all_elements = device.xpath('//*').all()
                for element in all_elements:
                    try:
                    text = element.attrib.get('text', '')
                        content_desc = element.attrib.get('content-desc', '')
                        
                        # Check if this element contains the target username
                        if target_username and (target_username in text or target_username in content_desc):
                            logger.info(f"Found target username '{target_username}' in element: text='{text}', content-desc='{content_desc}'")
                            
                            # Instead of clicking on the username element, look for the comment text
                            # The comment text is usually a longer text element near the username
                        if text and len(text) > 10:  # This is likely the comment text
                                element_center = element.center()
                                logger.info(f"Clicking on comment text at ({element_center[0]}, {element_center[1]})")
                                device.click(element_center[0], element_center[1])
                            time.sleep(2)
                                comment_clicked = True
                            break
                        else:
                                # If this element doesn't have the comment text, look for nearby text elements
                                element_center = element.center()
                                nearby_text_elements = device.xpath('//*[@text]').all()
                                
                                for text_element in nearby_text_elements:
                                    try:
                                        text_element_center = text_element.center()
                                        # Check if this text element is near the username element
                                        distance = ((element_center[0] - text_element_center[0])**2 + 
                                                  (element_center[1] - text_element_center[1])**2)**0.5
                                        
                                        if distance < 200:  # Within 200 pixels
                                            text_content = text_element.attrib.get('text', '')
                                            if text_content and len(text_content) > 10 and target_username not in text_content:
                                                # This is likely the comment text (not the username)
                                                logger.info(f"Found nearby comment text: '{text_content}' at ({text_element_center[0]}, {text_element_center[1]})")
                                                device.click(text_element_center[0], text_element_center[1])
                                            time.sleep(2)
                                                comment_clicked = True
                                            break
                                except Exception as e:
                                        logger.debug(f"Error checking nearby text element: {e}")
                                        continue
                                
                                if comment_clicked:
                                break
                            
                except Exception as e:
                        logger.debug(f"Error checking element for username: {e}")
                        continue
            
            if not comment_clicked:
                logger.error("Failed to click on any comment")
                return
            
            # Debug: Log all elements after clicking to see what's available
            logger.info("=== DEBUGGING REPLY INTERFACE ===")
            all_elements_after_click = device.xpath('//*').all()
            logger.info(f"Total elements after clicking comment: {len(all_elements_after_click)}")
            
            # Log first 30 elements to see what's available
            for i, elem in enumerate(all_elements_after_click[:30]):
                try:
                    text = elem.attrib.get('text', '')
                    content_desc = elem.attrib.get('content-desc', '')
                    if text or content_desc:
                        logger.info(f"Element {i+1}: text='{text}', content-desc='{content_desc}'")
            except Exception as e:
                    logger.debug(f"Error getting element {i+1} info: {e}")
            
            # Now look for the reply input field - it's the same icon as comment count
            input_elements = []
            input_selectors = [
                '//*[contains(@content-desc, "Reply")]',
                '//*[contains(@text, "Reply")]',
                '//*[contains(@content-desc, "comment")]',
                '//*[contains(@text, "comment")]',
                '//*[contains(@content-desc, "reply")]',
                '//*[contains(@text, "reply")]'
            ]
            
            for selector in input_selectors:
                elements = device.xpath(selector).all()
                if elements:
                    # Filter out elements that are too high on screen (likely main post elements)
                    for element in elements:
                        try:
                            center = element.center()
                            # Only consider elements in the lower part of the screen (comment area)
                            if center[1] > 200:  # Below the top area
                                input_elements.append(element)
                    except Exception as e:
                            logger.debug(f"Error checking element position: {e}")
                            continue
                    
                    if input_elements:
                        logger.info(f"Found reply icon using selector: {selector}")
                    break
            
            if not input_elements:
                logger.error("Could not find reply icon")
                return
            
            # Use the first reply icon found
            input_element = input_elements[0]
            input_center = input_element.center()
            logger.info(f"Found reply icon at ({input_center[0]}, {input_center[1]})")
            
            # Click on reply icon to open reply interface
            device.click(input_center[0], input_center[1])
        time.sleep(2)  # Wait for reply interface to open
            
            # Now look for the actual text input field
            text_input_elements = []
            text_input_selectors = [
                '//*[@content-desc="Add a comment..."]',
                '//*[@text="Add a comment..."]',
                '//*[@content-desc="Write a comment..."]',
                '//*[@text="Write a comment..."]',
                '//*[@content-desc="Reply..."]',
                '//*[@text="Reply..."]',
                '//*[contains(@content-desc, "comment")]',
                '//*[contains(@text, "comment")]',
                '//*[contains(@content-desc, "reply")]',
                '//*[contains(@text, "reply")]'
            ]
            
            for selector in text_input_selectors:
                elements = device.xpath(selector).all()
                if elements:
                    text_input_elements = elements
                    logger.info(f"Found text input using selector: {selector}")
                break
            
            if not text_input_elements:
                logger.error("Could not find text input field after clicking reply icon")
                return
            
            # Use the first text input element found
            text_input_element = text_input_elements[0]
            text_input_center = text_input_element.center()
            logger.info(f"Found text input at ({text_input_center[0]}, {text_input_center[1]})")
            
            # Click on text input field
            device.click(text_input_center[0], text_input_center[1])
        time.sleep(2)  # Wait longer for keyboard to appear
            
            # Type the response
            logger.info("Typing reply response...")
            device.send_keys(response)
            time.sleep(1)
            
            # Look for the post/send button
            post_elements = []
            post_selectors = [
                '//*[@content-desc="Post"]',
                '//*[@text="Post"]',
                '//*[@content-desc="Send"]',
                '//*[@text="Send"]',
                '//*[@content-desc="Reply"]',
                '//*[@text="Reply"]'
            ]
            
            for selector in post_selectors:
                elements = device.xpath(selector).all()
                if elements:
                    # Filter out elements that might be the main post button (usually at top)
                    for element in elements:
                        try:
                            center = element.center()
                            # Avoid clicking on buttons that are too high on screen (likely main post button)
                            if center[1] > 100:  # Only consider buttons below the top area
                                post_elements.append(element)
                    except Exception as e:
                            logger.debug(f"Error checking element position: {e}")
                            continue
                    
                    if post_elements:
                        logger.info(f"Found post button using selector: {selector}")
                    break
            
            if post_elements:
                post_element = post_elements[0]
                post_center = post_element.center()
                logger.info(f"Found post button at ({post_center[0]}, {post_center[1]})")
                
                # Double-check we're not clicking on the main post button
                if post_center[1] > 100:  # Should be below the top area
                    device.click(post_center[0], post_center[1])
                    logger.info(f"Posted reply to {target_username}: {response}")
                    else:
                    logger.error("Post button is too high on screen, might be main post button")
                    else:
                logger.error("Could not find appropriate post button")
                
        except Exception as e:
            logger.error(f"Error posting comment response: {e}")

    def find_usernames_in_comments(self, device: u2.Device) -> List[str]:
        """Find usernames in the comment section, excluding post author and quoted accounts."""
        try:
            usernames = []
            
            # Enhanced list of UI elements and common comment words to exclude
            ui_elements_to_exclude = [
                # Engagement metrics
                'like', 'reply', 'repost', 'share', 'follow', 'following', 'unfollow', 'unlike',
                'views', 'view', 'show', 'replies', 'comments', 'comment',
                
                # Navigation and UI
                'home', 'back', 'top', 'recent', 'overview', 'feeds', 'create feed', 'edit feeds',
                'verified', 'gallery', 'gif', 'feed', 'search', 'create', 'activity', 'profile',
                'add', 'send', 'post', 'all', 'thread', 'sell', 'bookmark', 'more', 'options', 
                'menu', 'settings', 'notifications', 'messages', 'explore', 'trending', 
                'popular', 'new', 'hot', 'latest', 'viral', 'featured', 'recommended', 'suggested',
                
                # Media and attachments
                'photo', 'image', 'picture', 'preview', 'media', 'video', 'gif', 'attachment',
                'see all', 'photo preview',
                
                # Post content indicators (to avoid detecting post author)
                'posted', 'regram', 'repost', 'quote', 'shared', 'withregram',
                
                # Common comment words (not usernames)
                'amen', 'thanks', 'thank', 'great', 'awesome', 'amazing', 'love', 'loved', 'cool',
                'nice', 'good', 'bad', 'wow', 'omg', 'lol', 'haha', 'yes', 'no', 'maybe', 'ok',
                'okay', 'sure', 'right', 'wrong', 'true', 'false', 'agree', 'disagree', 'facts',
                'fact', 'real', 'fake', 'best', 'worst', 'perfect', 'exactly', 'literally',
                'actually', 'basically', 'totally', 'absolutely', 'definitely', 'probably',
                'maybe', 'perhaps', 'possibly', 'hopefully', 'unfortunately', 'fortunately',
                'sadly', 'happily', 'luckily', 'unluckily', 'obviously', 'clearly', 'apparently',
                'supposedly', 'allegedly', 'reportedly', 'accordingly', 'consequently', 'therefore',
                'however', 'nevertheless', 'nonetheless', 'meanwhile', 'furthermore', 'moreover',
                'additionally', 'besides', 'also', 'too', 'as', 'well', 'either', 'neither',
                'both', 'all', 'none', 'some', 'any', 'every', 'each', 'other', 'another',
                'same', 'different', 'similar', 'various', 'several', 'many', 'few', 'much',
                'little', 'more', 'less', 'most', 'least', 'better', 'worse', 'best', 'worst',
                'first', 'last', 'next', 'previous', 'current', 'recent', 'old', 'new', 'young',
                'big', 'small', 'large', 'tiny', 'huge', 'enormous', 'massive', 'giant', 'mini',
                'micro', 'macro', 'high', 'low', 'tall', 'short', 'long', 'wide', 'narrow',
                'thick', 'thin', 'fat', 'skinny', 'heavy', 'light', 'dark', 'bright', 'dull',
                'sharp', 'blunt', 'smooth', 'rough', 'soft', 'hard', 'easy', 'difficult',
                'simple', 'complex', 'basic', 'advanced', 'beginner', 'expert', 'professional',
                'amateur', 'novice', 'veteran', 'experienced', 'inexperienced', 'skilled',
                'unskilled', 'talented', 'untalented', 'gifted', 'average', 'normal', 'special',
                'unique', 'common', 'rare', 'usual', 'unusual', 'typical', 'atypical',
                'standard', 'nonstandard', 'regular', 'irregular', 'formal', 'informal',
                'official', 'unofficial', 'public', 'private', 'personal', 'professional',
                'business', 'commercial', 'residential', 'urban', 'rural', 'suburban',
                'domestic', 'international', 'local', 'global', 'national', 'regional',
                'state', 'city', 'town', 'village', 'neighborhood', 'community', 'society',
                'culture', 'tradition', 'custom', 'habit', 'routine', 'schedule', 'plan',
                'strategy', 'tactic', 'method', 'approach', 'technique', 'skill', 'ability',
                'talent', 'gift', 'strength', 'weakness', 'advantage', 'disadvantage',
                'benefit', 'drawback', 'pro', 'con', 'positive', 'negative', 'good', 'bad',
                'right', 'wrong', 'correct', 'incorrect', 'accurate', 'inaccurate', 'true',
                'false', 'real', 'fake', 'genuine', 'fake', 'authentic', 'fake', 'original',
                'copy', 'duplicate', 'replica', 'imitation', 'genuine', 'fake', 'legitimate',
                'illegitimate', 'legal', 'illegal', 'lawful', 'unlawful', 'permitted',
                'forbidden', 'allowed', 'prohibited', 'acceptable', 'unacceptable', 'appropriate',
                'inappropriate', 'suitable', 'unsuitable', 'proper', 'improper', 'correct',
                'incorrect', 'right', 'wrong', 'true', 'false', 'accurate', 'inaccurate',
                'precise', 'imprecise', 'exact', 'inexact', 'specific', 'general', 'detailed',
                'brief', 'comprehensive', 'limited', 'complete', 'incomplete', 'full', 'empty',
                'filled', 'unfilled', 'occupied', 'unoccupied', 'busy', 'free', 'available',
                'unavailable', 'accessible', 'inaccessible', 'reachable', 'unreachable',
                'possible', 'impossible', 'feasible', 'infeasible', 'practical', 'impractical',
                'realistic', 'unrealistic', 'reasonable', 'unreasonable', 'logical', 'illogical',
                'rational', 'irrational', 'sensible', 'nonsensical', 'meaningful', 'meaningless',
                'significant', 'insignificant', 'important', 'unimportant', 'essential',
                'nonessential', 'necessary', 'unnecessary', 'required', 'optional', 'mandatory',
                'voluntary', 'compulsory', 'elective', 'automatic', 'manual', 'automatic',
                'manual', 'automatic', 'manual', 'automatic', 'manual', 'automatic', 'manual'
            ]
            
            logger.info("=== SEARCHING FOR USERNAMES IN COMMENTS ===")
            
            # Look for usernames in text elements
            text_elements = device.xpath('//*[@text]').all()
            logger.info(f"Checking {len(text_elements)} text elements for usernames")
            
            # Print first 30 text elements to see what's there
            logger.info("First 30 text elements:")
            for i, element in enumerate(text_elements[:30]):
                try:
                text = element.attrib.get('text', '')
                    if text and len(text) > 0:
                        logger.info(f"  Text {i+1}: '{text}'")
            except Exception as e:
                    logger.debug(f"Error getting text element {i+1}: {e}")
            
            # Look for usernames in different formats - more restrictive
            for element in text_elements:
                try:
                text = element.attrib.get('text', '')
                    
                    # Skip if this text contains post content indicators
                    if any(indicator in text.lower() for indicator in ['posted', 'regram', 'repost', 'quote', 'shared', 'withregram']):
                        logger.debug(f"Skipping post content: '{text}'")
                        continue
                    
                    # Check for usernames with @ symbol
                    clean_text = text.strip()
                    if (clean_text.startswith('@') and
                        len(clean_text) >= 3 and
                        len(clean_text) < 25 and
                        not clean_text[1:].isspace() and
                        any(c.isalnum() for c in clean_text[1:]) and
                        clean_text.lower() not in ui_elements_to_exclude and
                        ' ' not in clean_text and
                        clean_text.count('_') <= 3 and
                        clean_text.count('.') <= 2 and
                        not clean_text[1:].isdigit() and  # Don't allow pure numbers
                        not any(word in clean_text.lower() for word in ['http', 'www', '.com', '.org', '.net', '.io', 'spotify', 'youtube', 'instagram', 'twitter', 'tiktok', 'facebook'])):
                        
                        username = clean_text[1:]  # Remove @ symbol
                        if username not in usernames:
                            usernames.append(username)
                            logger.info(f"Found username with @: {username}")
                    
                    # Check for usernames without @ symbol (more restrictive)
                    elif (len(clean_text) >= 3 and
                          len(clean_text) < 25 and
                          not clean_text.isspace() and
                          any(c.isalnum() for c in clean_text) and
                          clean_text.lower() not in ui_elements_to_exclude and
                          ' ' not in clean_text and
                          clean_text.count('_') <= 3 and
                          clean_text.count('.') <= 2 and
                          not clean_text.isdigit() and  # Don't allow pure numbers
                          not any(word in clean_text.lower() for word in ['http', 'www', '.com', '.org', '.net', '.io', 'spotify', 'youtube', 'instagram', 'twitter', 'tiktok', 'facebook']) and
                          not any(char in clean_text for char in ['@', '#', '$', '%', '&', '*', '(', ')', '+', '=', '[', ']', '{', '}', '|', '\\', ':', ';', '"', "'", '<', '>', ',', '?', '/']) and
                          clean_text.lower() not in ['amen', 'thanks', 'thank', 'great', 'awesome', 'amazing', 'love', 'loved', 'cool', 'nice', 'good', 'bad', 'wow', 'omg', 'lol', 'haha', 'yes', 'no', 'maybe', 'ok', 'okay', 'sure', 'right', 'wrong', 'true', 'false', 'agree', 'disagree', 'facts', 'fact', 'real', 'fake', 'best', 'worst', 'perfect', 'exactly', 'literally', 'actually', 'basically', 'totally', 'absolutely', 'definitely', 'probably', 'maybe', 'perhaps', 'possibly', 'hopefully', 'unfortunately', 'fortunately', 'sadly', 'happily', 'luckily', 'unluckily', 'obviously', 'clearly', 'apparently', 'supposedly', 'allegedly', 'reportedly', 'accordingly', 'consequently', 'therefore', 'however', 'nevertheless', 'nonetheless', 'meanwhile', 'furthermore', 'moreover', 'additionally', 'besides', 'also', 'too', 'as', 'well', 'either', 'neither', 'both', 'all', 'none', 'some', 'any', 'every', 'each', 'other', 'another', 'same', 'different', 'similar', 'various', 'several', 'many', 'few', 'much', 'little', 'more', 'less', 'most', 'least', 'better', 'worse', 'best', 'worst', 'first', 'last', 'next', 'previous', 'current', 'recent', 'old', 'new', 'young', 'big', 'small', 'large', 'tiny', 'huge', 'enormous', 'massive', 'giant', 'mini', 'micro', 'macro', 'high', 'low', 'tall', 'short', 'long', 'wide', 'narrow', 'thick', 'thin', 'fat', 'skinny', 'heavy', 'light', 'dark', 'bright', 'dull', 'sharp', 'blunt', 'smooth', 'rough', 'soft', 'hard', 'easy', 'difficult', 'simple', 'complex', 'basic', 'advanced', 'beginner', 'expert', 'professional', 'amateur', 'novice', 'veteran', 'experienced', 'inexperienced', 'skilled', 'unskilled', 'talented', 'untalented', 'gifted', 'average', 'normal', 'special', 'unique', 'common', 'rare', 'usual', 'unusual', 'typical', 'atypical', 'standard', 'nonstandard', 'regular', 'irregular', 'formal', 'informal', 'official', 'unofficial', 'public', 'private', 'personal', 'professional', 'business', 'commercial', 'residential', 'urban', 'rural', 'suburban', 'domestic', 'international', 'local', 'global', 'national', 'regional', 'state', 'city', 'town', 'village', 'neighborhood', 'community', 'society', 'culture', 'tradition', 'custom', 'habit', 'routine', 'schedule', 'plan', 'strategy', 'tactic', 'method', 'approach', 'technique', 'skill', 'ability', 'talent', 'gift', 'strength', 'weakness', 'advantage', 'disadvantage', 'benefit', 'drawback', 'pro', 'con', 'positive', 'negative', 'good', 'bad', 'right', 'wrong', 'correct', 'incorrect', 'accurate', 'inaccurate', 'true', 'false', 'real', 'fake', 'genuine', 'fake', 'authentic', 'fake', 'original', 'copy', 'duplicate', 'replica', 'imitation', 'genuine', 'fake', 'legitimate', 'illegitimate', 'legal', 'illegal', 'lawful', 'unlawful', 'permitted', 'forbidden', 'allowed', 'prohibited', 'acceptable', 'unacceptable', 'appropriate', 'inappropriate', 'suitable', 'unsuitable', 'proper', 'improper', 'correct', 'incorrect', 'right', 'wrong', 'true', 'false', 'accurate', 'inaccurate', 'precise', 'imprecise', 'exact', 'inexact', 'specific', 'general', 'detailed', 'brief', 'comprehensive', 'limited', 'complete', 'incomplete', 'full', 'empty', 'filled', 'unfilled', 'occupied', 'unoccupied', 'busy', 'free', 'available', 'unavailable', 'accessible', 'inaccessible', 'reachable', 'unreachable', 'possible', 'impossible', 'feasible', 'infeasible', 'practical', 'impractical', 'realistic', 'unrealistic', 'reasonable', 'unreasonable', 'logical', 'illogical', 'rational', 'irrational', 'sensible', 'nonsensical', 'meaningful', 'meaningless', 'significant', 'insignificant', 'important', 'unimportant', 'essential', 'nonessential', 'necessary', 'unnecessary', 'required', 'optional', 'mandatory', 'voluntary', 'compulsory', 'elective', 'automatic', 'manual', 'automatic', 'manual', 'automatic', 'manual', 'automatic', 'manual', 'automatic', 'manual', 'automatic', 'manual']):
                        
                        if clean_text not in usernames:
                            usernames.append(clean_text)
                            logger.info(f"Found potential username (no @): {clean_text}")
                            
            except Exception as e:
                    logger.debug(f"Error checking text element: {e}")
                    continue
            
            # Look for usernames in content-desc elements
            content_desc_elements = device.xpath('//*[@content-desc]').all()
            logger.info(f"Checking {len(content_desc_elements)} content-desc elements for usernames")
            
            # Print first 30 content-desc elements to see what's there
            logger.info("First 30 content-desc elements:")
            for i, element in enumerate(content_desc_elements[:30]):
                try:
                    content_desc = element.attrib.get('content-desc', '')
                    if content_desc and len(content_desc) > 0:
                        logger.info(f"  Content-desc {i+1}: '{content_desc}'")
            except Exception as e:
                    logger.debug(f"Error getting content-desc element {i+1}: {e}")
            
            for element in content_desc_elements:
                try:
                    content_desc = element.attrib.get('content-desc', '')
                    clean_content_desc = content_desc.strip()
                    
                    # Skip if this content-desc contains post content indicators
                    if any(indicator in clean_content_desc.lower() for indicator in ['posted', 'regram', 'repost', 'quote', 'shared', 'withregram']):
                        logger.debug(f"Skipping post content: '{clean_content_desc}'")
                        continue
                    
                    # Check for usernames in content-desc (more restrictive)
                    if (len(clean_content_desc) >= 3 and
                        len(clean_content_desc) < 25 and
                        not clean_content_desc.isspace() and
                        any(c.isalnum() for c in clean_content_desc) and
                        clean_content_desc.lower() not in ui_elements_to_exclude and
                        ' ' not in clean_content_desc and
                        clean_content_desc.count('_') <= 3 and
                        clean_content_desc.count('.') <= 2 and
                        not clean_content_desc.isdigit() and  # Don't allow pure numbers
                        not any(word in clean_content_desc.lower() for word in ['http', 'www', '.com', '.org', '.net', '.io', 'spotify', 'youtube', 'instagram', 'twitter', 'tiktok', 'facebook']) and
                        not any(char in clean_content_desc for char in ['@', '#', '$', '%', '&', '*', '(', ')', '+', '=', '[', ']', '{', '}', '|', '\\', ':', ';', '"', "'", '<', '>', ',', '?', '/']) and
                        clean_content_desc.lower() not in ['amen', 'thanks', 'thank', 'great', 'awesome', 'amazing', 'love', 'loved', 'cool', 'nice', 'good', 'bad', 'wow', 'omg', 'lol', 'haha', 'yes', 'no', 'maybe', 'ok', 'okay', 'sure', 'right', 'wrong', 'true', 'false', 'agree', 'disagree', 'facts', 'fact', 'real', 'fake', 'best', 'worst', 'perfect', 'exactly', 'literally', 'actually', 'basically', 'totally', 'absolutely', 'definitely', 'probably', 'maybe', 'perhaps', 'possibly', 'hopefully', 'unfortunately', 'fortunately', 'sadly', 'happily', 'luckily', 'unluckily', 'obviously', 'clearly', 'apparently', 'supposedly', 'allegedly', 'reportedly', 'accordingly', 'consequently', 'therefore', 'however', 'nevertheless', 'nonetheless', 'meanwhile', 'furthermore', 'moreover', 'additionally', 'besides', 'also', 'too', 'as', 'well', 'either', 'neither', 'both', 'all', 'none', 'some', 'any', 'every', 'each', 'other', 'another', 'same', 'different', 'similar', 'various', 'several', 'many', 'few', 'much', 'little', 'more', 'less', 'most', 'least', 'better', 'worse', 'best', 'worst', 'first', 'last', 'next', 'previous', 'current', 'recent', 'old', 'new', 'young', 'big', 'small', 'large', 'tiny', 'huge', 'enormous', 'massive', 'giant', 'mini', 'micro', 'macro', 'high', 'low', 'tall', 'short', 'long', 'wide', 'narrow', 'thick', 'thin', 'fat', 'skinny', 'heavy', 'light', 'dark', 'bright', 'dull', 'sharp', 'blunt', 'smooth', 'rough', 'soft', 'hard', 'easy', 'difficult', 'simple', 'complex', 'basic', 'advanced', 'beginner', 'expert', 'professional', 'amateur', 'novice', 'veteran', 'experienced', 'inexperienced', 'skilled', 'unskilled', 'talented', 'untalented', 'gifted', 'average', 'normal', 'special', 'unique', 'common', 'rare', 'usual', 'unusual', 'typical', 'atypical', 'standard', 'nonstandard', 'regular', 'irregular', 'formal', 'informal', 'official', 'unofficial', 'public', 'private', 'personal', 'professional', 'business', 'commercial', 'residential', 'urban', 'rural', 'suburban', 'domestic', 'international', 'local', 'global', 'national', 'regional', 'state', 'city', 'town', 'village', 'neighborhood', 'community', 'society', 'culture', 'tradition', 'custom', 'habit', 'routine', 'schedule', 'plan', 'strategy', 'tactic', 'method', 'approach', 'technique', 'skill', 'ability', 'talent', 'gift', 'strength', 'weakness', 'advantage', 'disadvantage', 'benefit', 'drawback', 'pro', 'con', 'positive', 'negative', 'good', 'bad', 'right', 'wrong', 'correct', 'incorrect', 'accurate', 'inaccurate', 'true', 'false', 'real', 'fake', 'genuine', 'fake', 'authentic', 'fake', 'original', 'copy', 'duplicate', 'replica', 'imitation', 'genuine', 'fake', 'legitimate', 'illegitimate', 'legal', 'illegal', 'lawful', 'unlawful', 'permitted', 'forbidden', 'allowed', 'prohibited', 'acceptable', 'unacceptable', 'appropriate', 'inappropriate', 'suitable', 'unsuitable', 'proper', 'improper', 'correct', 'incorrect', 'right', 'wrong', 'true', 'false', 'accurate', 'inaccurate', 'precise', 'imprecise', 'exact', 'inexact', 'specific', 'general', 'detailed', 'brief', 'comprehensive', 'limited', 'complete', 'incomplete', 'full', 'empty', 'filled', 'unfilled', 'occupied', 'unoccupied', 'busy', 'free', 'available', 'unavailable', 'accessible', 'inaccessible', 'reachable', 'unreachable', 'possible', 'impossible', 'feasible', 'infeasible', 'practical', 'impractical', 'realistic', 'unrealistic', 'reasonable', 'unreasonable', 'logical', 'illogical', 'rational', 'irrational', 'sensible', 'nonsensical', 'meaningful', 'meaningless', 'significant', 'insignificant', 'important', 'unimportant', 'essential', 'nonessential', 'necessary', 'unnecessary', 'required', 'optional', 'mandatory', 'voluntary', 'compulsory', 'elective', 'automatic', 'manual', 'automatic', 'manual', 'automatic', 'manual', 'automatic', 'manual', 'automatic', 'manual', 'automatic', 'manual']):
                        
                        if clean_content_desc not in usernames:
                            usernames.append(clean_content_desc)
                            logger.info(f"Found username in content-desc: '{clean_content_desc}' (from '{content_desc}')")
                            
            except Exception as e:
                    logger.debug(f"Error checking content-desc element: {e}")
                    continue
            
            # Look for comment-related text to help identify actual comments
            logger.info("Looking for comment-related text:")
            for element in text_elements:
                try:
                text = element.attrib.get('text', '')
                if text and len(text) > 10 and any(word in text.lower() for word in ['reply', 'comment', 'view', 'like', 'share']):
                        logger.info(f"Found comment-related text: '{text}'")
            except Exception as e:
                    logger.debug(f"Error checking comment-related text: {e}")
                    continue
            
            logger.info(f"Total usernames found: {len(usernames)}")
            logger.info(f"Usernames found: {usernames}")
            
            return usernames
            
        except Exception as e:
            logger.error(f"Error finding usernames in comments: {e}")
            return []

    def is_comment_section_open(self, device: u2.Device) -> bool:
        """Check if the comment section is open by looking for comment-related UI elements."""
        try:
            logger.info("=== CHECKING IF COMMENT SECTION IS OPEN ===")
            
            # First, let's see what elements are actually on the screen
            all_elements = device.xpath('//*').all()
            logger.info(f"Total elements on screen: {len(all_elements)}")
            
            # Look for the most reliable indicator: "Reply X" pattern in content-desc
            reply_elements = device.xpath('//*[contains(@content-desc, "Reply")]').all()
            if reply_elements:
                for element in reply_elements:
                    try:
                        content_desc = element.attrib.get('content-desc', '')
                        logger.info(f"Found Reply element: '{content_desc}'")
                        if 'Reply' in content_desc:
                            logger.info("Comment section detected by Reply element")
                            logger.info("=== COMMENT SECTION IS OPEN ===")
                            return True
                except Exception as e:
                        logger.debug(f"Error getting Reply element info: {e}")
            
            # Look for any elements that might indicate we're in a comment section
            comment_indicators = [
                '//*[@content-desc="Add a comment..."]',
                '//*[@text="Add a comment..."]',
                '//*[@content-desc="Reply"]',
                '//*[@text="Reply"]',
                '//*[@content-desc="Post"]',
                '//*[@text="Post"]',
                '//*[@content-desc="Send"]',
                '//*[@text="Send"]',
                '//*[contains(@content-desc, "comment")]',
                '//*[contains(@text, "comment")]',
                '//*[contains(@content-desc, "reply")]',
                '//*[contains(@text, "reply")]'
            ]
            
            found_indicators = []
            for xpath in comment_indicators:
                elements = device.xpath(xpath).all()
                if elements:
                    for element in elements:
                        try:
                        text = element.attrib.get('text', '')
                            content_desc = element.attrib.get('content-desc', '')
                            logger.info(f"Found comment indicator: {xpath} -> text: '{text}', content-desc: '{content_desc}'")
                            found_indicators.append(xpath)
                    except Exception as e:
                            logger.debug(f"Error getting element info: {e}")
            
            # Also check for any text elements that might be usernames (indicating comments)
            username_elements = device.xpath('//*[starts-with(@text, "@")]').all()
            if username_elements:
                logger.info(f"Found {len(username_elements)} potential username elements")
                for i, element in enumerate(username_elements[:5]):  # Show first 5
                try:
                    text = element.attrib.get('text', '')
                        logger.info(f"Username element {i+1}: '{text}'")
                except Exception as e:
                        logger.debug(f"Error getting username element info: {e}")
            
            # Check for any elements with "comment" in their attributes
            for i, element in enumerate(all_elements[:20]):  # Check first 20 elements
            try:
                text = element.attrib.get('text', '')
                    content_desc = element.attrib.get('content-desc', '')
                    resource_id = element.attrib.get('resource-id', '')
                    
                    if any(word in text.lower() for word in ['comment', 'reply', 'post', 'send']) or \
                       any(word in content_desc.lower() for word in ['comment', 'reply', 'post', 'send']) or \
                       any(word in resource_id.lower() for word in ['comment', 'reply', 'post', 'send']):
                        logger.info(f"Element {i+1}: text='{text}', content-desc='{content_desc}', resource-id='{resource_id}'")
            except Exception as e:
                    logger.debug(f"Error checking element {i+1}: {e}")
            
            # More flexible detection: if we found any comment indicators, consider the section open
            if found_indicators:
                logger.info(f"Comment section detected by indicators: {found_indicators}")
                logger.info("=== COMMENT SECTION IS OPEN ===")
                return True
            
            # If we found username elements, that's also a good sign
            if username_elements:
                logger.info("Comment section detected by presence of username elements")
                logger.info("=== COMMENT SECTION IS OPEN ===")
                return True
            
            # Check if we're in a post detail view by looking for post-related elements
            post_indicators = [
                '//*[contains(@content-desc, "Unlike")]',
                '//*[contains(@content-desc, "Like")]',
                '//*[contains(@text, "Unlike")]',
                '//*[contains(@text, "Like")]'
            ]
            
            for xpath in post_indicators:
                elements = device.xpath(xpath).all()
                if elements:
                    logger.info(f"Found post indicator: {xpath}")
                    logger.info("Assuming we're in post detail view (comment section should be accessible)")
                    logger.info("=== COMMENT SECTION IS OPEN ===")
                    return True
            
            logger.info("=== COMMENT SECTION IS NOT OPEN ===")
            return False
            
        except Exception as e:
            logger.error(f"Error checking if comment section is open: {e}")
            return False

    def click_username_in_comments(self, device: u2.Device, username: str) -> bool:
        """Click on a specific username in the comment section."""
        try:
            logger.info(f"Attempting to click on username: {username}")
            
            # Try to find the username element in content-desc (the format we found)
            username_elements = device.xpath(f'//*[@content-desc="{username} "]').all()
            
            if not username_elements:
                # Try without the trailing space
                username_elements = device.xpath(f'//*[@content-desc="{username}"]').all()
            
            if not username_elements:
                # Try with @ symbol
                username_elements = device.xpath(f'//*[@content-desc="@{username}"]').all()
            
            if not username_elements:
                # Try in text attribute
                username_elements = device.xpath(f'//*[@text="@{username}"]').all()
            
            if username_elements:
                element = username_elements[0]
                center = element.center()
                logger.info(f"Found username element for {username} at ({center[0]}, {center[1]})")
                device.click(center[0], center[1])
                return True
        else:
                logger.warning(f"Could not find username element for: {username}")
                return False
                
        except Exception as e:
            logger.error(f"Error clicking username {username}: {e}")
            return False

def main():
    import sys
    if len(sys.argv) < 2:
        print("Usage: python android_engagement.py <command>")
        print("\nCommands:")
        print("  start - Start automated engagement")
        print("  config - Show current configuration")
        print("  list-devices - List connected Android devices")
        return

    engagement = AndroidEngagement()
    command = sys.argv[1].lower()

    if command == "start":
        print("Starting automated engagement...")
        engagement.run()
    elif command == "config":
        print("\nCurrent Configuration:")
        print(f"Minimum likes for viral: {engagement.min_likes_for_viral}")
        print(f"Minimum comments for viral: {engagement.min_comments_for_viral}")
        print(f"Maximum posts to scan: {engagement.max_posts_to_scan}")
        print(f"Comment cooldown: {engagement.comment_cooldown} seconds")
        print(f"Follow cooldown: {engagement.follow_cooldown} seconds")
        print(f"Like cooldown: {engagement.like_cooldown} seconds")
    elif command == "list-devices":
        print("\nConnected Devices:")
        for device_name, device in engagement.active_devices.items():
            print(f"\nDevice: {device_name}")
            print(f"Serial: {device.serial}")
            print(f"Model: {device.info.get('model', 'Unknown')}")
            else:
        print("Unknown command")

if __name__ == "__main__":
    main() 