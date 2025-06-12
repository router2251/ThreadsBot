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
import requests  # Added for API calls

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Gemini API Key (you'll need to set this)
GEMINI_API_KEY = "AIzaSyA2TYVMt3yzGr5TRtiSnp7mNepGxTaQZJM"  # Working API key
GEMINI_API_URL = "https://generativelanguage.googleapis.com/v1/models/gemini-1.5-flash:generateContent"

class AIAnalyzer:
    def __init__(self, api_key: str = GEMINI_API_KEY):
        self.api_key = api_key
        self.api_url = GEMINI_API_URL
        self.logger = logging.getLogger(__name__)
    
    def analyze_user_profile(self, username: str, bio: str, comment_text: str) -> Dict:
        """Analyze user profile to determine gender, location, and other attributes."""
        try:
            # Enhanced USA detection - look for common USA indicators
            usa_indicators = [
                'usa', 'america', 'american', 'us', 'united states',
                # Common American surnames that are strong USA indicators
                'wilson', 'johnson', 'williams', 'brown', 'jones', 'garcia', 'miller', 'davis',
                'rodriguez', 'martinez', 'hernandez', 'lopez', 'gonzalez', 'perez', 'taylor',
                'anderson', 'thomas', 'jackson', 'white', 'harris', 'martin', 'thompson',
                'moore', 'young', 'allen', 'king', 'wright', 'scott', 'torres', 'nguyen',
                'hill', 'flores', 'green', 'adams', 'nelson', 'baker', 'hall', 'rivera',
                'campbell', 'mitchell', 'carter', 'roberts', 'gomez', 'phillips', 'evans',
                'turner', 'diaz', 'parker', 'cruz', 'edwards', 'collins', 'reyes', 'stewart',
                'morris', 'morales', 'murphy', 'cook', 'rogers', 'gutierrez', 'ortiz',
                'morgan', 'cooper', 'peterson', 'bailey', 'reed', 'kelly', 'howard', 'ramos',
                'kim', 'cox', 'ward', 'richardson', 'watson', 'brooks', 'chavez', 'wood',
                'james', 'bennett', 'gray', 'mendoza', 'ruiz', 'hughes', 'price', 'alvarez',
                'castillo', 'sanders', 'patel', 'myers', 'long', 'ross', 'foster', 'jimenez',
                'texas', 'california', 'florida', 'new york', 'illinois', 'pennsylvania',
                'ohio', 'georgia', 'north carolina', 'michigan', 'new jersey', 'virginia',
                'washington', 'arizona', 'massachusetts', 'tennessee', 'indiana', 'missouri',
                'maryland', 'wisconsin', 'colorado', 'minnesota', 'south carolina', 'alabama',
                'louisiana', 'kentucky', 'oregon', 'oklahoma', 'connecticut', 'utah', 'iowa',
                'nevada', 'arkansas', 'mississippi', 'kansas', 'new mexico', 'nebraska',
                'west virginia', 'idaho', 'hawaii', 'new hampshire', 'maine', 'montana',
                'rhode island', 'delaware', 'south dakota', 'north dakota', 'alaska', 'vermont',
                'wyoming', 'dc', 'washington dc', 'atlanta', 'chicago', 'houston', 'phoenix',
                'philadelphia', 'san antonio', 'san diego', 'dallas', 'san jose', 'austin',
                'jacksonville', 'fort worth', 'columbus', 'charlotte', 'san francisco',
                'indianapolis', 'seattle', 'denver', 'boston', 'el paso', 'detroit', 'nashville',
                'portland', 'memphis', 'oklahoma city', 'las vegas', 'louisville', 'baltimore',
                'milwaukee', 'albuquerque', 'tucson', 'fresno', 'sacramento', 'mesa', 'kansas city',
                'atlanta', 'long beach', 'colorado springs', 'raleigh', 'miami', 'virginia beach',
                'omaha', 'oakland', 'minneapolis', 'tulsa', 'arlington', 'tampa', 'new orleans',
                'wichita', 'cleveland', 'bakersfield', 'aurora', 'anaheim', 'honolulu', 'santa ana',
                'corpus christi', 'riverside', 'lexington', 'stockton', 'toledo', 'st. paul',
                'newark', 'greensboro', 'plano', 'henderson', 'lincoln', 'buffalo', 'jersey city',
                'chula vista', 'fort wayne', 'orlando', 'st. petersburg', 'chandler', 'laredo',
                'norfolk', 'durham', 'madison', 'lubbock', 'irvine', 'winston-salem', 'glendale',
                'garland', 'hialeah', 'reno', 'chesapeake', 'gilbert', 'baton rouge', 'irving',
                'scottsdale', 'north las vegas', 'fremont', 'boise', 'richmond', 'san bernardino',
                'birmingham', 'spokane', 'rochester', 'des moines', 'modesto', 'fayetteville',
                'tacoma', 'oxnard', 'fontana', 'columbus', 'montgomery', 'moreno valley', 'shreveport',
                'aurora', 'yonkers', 'akron', 'huntington beach', 'little rock', 'augusta',
                'amarillo', 'glendale', 'mobile', 'grand rapids', 'salt lake city', 'tallahassee',
                'huntsville', 'grand prairie', 'knoxville', 'worcester', 'newport news', 'brownsville',
                'santa clarita', 'providence', 'overland park', 'garden grove', 'chattanooga',
                'oceanside', 'jackson', 'fort lauderdale', 'santa rosa', 'rancho cucamonga',
                'port st. lucie', 'tempe', 'ontario', 'vancouver', 'cape coral', 'sioux falls',
                'springfield', 'peoria', 'pembroke pines', 'elk grove', 'salem', 'lancaster',
                'corona', 'eugene', 'palmdale', 'salinas', 'springfield', 'pasadena', 'fort collins',
                'hayward', 'pomona', 'cary', 'rockford', 'alexandria', 'escondido', 'mckinney',
                'kansas city', 'joliet', 'sunnyvale', 'torrance', 'bridgeport', 'lakewood',
                'hollywood', 'paterson', 'naperville', 'syracuse', 'mesquite', 'dayton', 'savannah',
                'clarksville', 'orange', 'pasadena', 'fullerton', 'killeen', 'frisco', 'hampton',
                'mcallen', 'warren', 'west valley city', 'columbia', 'olathe', 'sterling heights',
                'new haven', 'miramar', 'waco', 'thousand oaks', 'cedar rapids', 'charleston',
                'visalia', 'topeka', 'elizabeth', 'gainesville', 'thornton', 'roseville', 'carrollton',
                'coral springs', 'stamford', 'simi valley', 'concord', 'hartford', 'kent', 'lafayette',
                'midland', 'surprise', 'denton', 'victorville', 'evansville', 'santa clara',
                'abilene', 'athens', 'vallejo', 'allentown', 'norman', 'beaumont', 'independence',
                'murfreesboro', 'ann arbor', 'fargo', 'wilmington', 'golden valley', 'pearland',
                'richardson', 'charles town', 'sterling heights', 'west jordan', 'clearwater',
                'westminster', 'arvada', 'carlsbad', 'palm bay', 'miami gardens', 'st. george',
                'san mateo', 'pueblo', 'el monte', 'inglewood', 'high point', 'downey', 'lewisville',
                'centennial', 'billings', 'elgin', 'waterbury', 'clovis', 'lowell', 'richmond',
                'peoria', 'broken arrow', 'miami beach', 'college station', 'pompano beach',
                'odessa', 'west palm beach', 'antioch', 'temecula', 'everett', 'boulder',
                'daly city', 'meridian', 'provo', 'west covina', 'fairfield', 'rochester',
                'yuma', 'burbank', 'fishers', 'sugar land', 'flint', 'tuscaloosa', 'carson',
                'sandy springs', 'edmond', 'renton', 'davenport', 'south bend', 'san angelo',
                'springfield', 'lee\'s summit', 'tyler', 'pearland', 'college station', 'kenosha',
                'sandy', 'clovis', 'lawton', 'gresham', 'green bay', 'san marcos', 'lakeland',
                'pompano beach', 'west valley city', 'norwalk', 'brockton', 'lakewood', 'beaverton',
                'lowell', 'quincy', 'lynn', 'westland', 'avondale', 'dearborn', 'independence',
                'gresham', 'bloomington', 'sioux city', 'warwick', 'hemet', 'longmont', 'troy',
                'baytown', 'pharr', 'albany', 'carmel', 'danbury', 'sandy springs', 'largo',
                'bellingham', 'tustin', 'san leandro', 'rialto', 'davie', 'yuba city', 'las cruces',
                'st. joseph', 'new bedford', 'league city', 'schaumburg', 'tyler', 'eau claire',
                'livonia', 'tracy', 'mansfield', 'sunrise', 'santa monica', 'southfield', 'ventura',
                'allentow', 'orem', 'pueblo', 'reading', 'clifton', 'cambridge', 'old bridge',
                'norman', 'centennial', 'el cajon', 'north charleston', 'dearborn heights',
                'richardson', 'arvada', 'ann arbor', 'rochester hills', 'champaign', 'troy',
                'westminster', 'goodyear', 'laredo', 'gulfport', 'alpharetta', 'woodbridge',
                'white plains', 'new rochelle', 'mount vernon', 'royal oak', 'valdosta',
                'gary', 'lynn', 'alameda', 'lakewood', 'hampton', 'roswell', 'johns creek',
                'hoover', 'redwood city', 'delray beach', 'eagan', 'medford', 'cicero',
                'apple valley', 'gaithersburg', 'bartlett', 'pleasanton', 'kalamazoo'
            ]
            
            # Enhanced male name detection
            male_names = [
                'james', 'robert', 'john', 'michael', 'david', 'william', 'richard', 'charles',
                'joseph', 'thomas', 'christopher', 'daniel', 'paul', 'mark', 'donald', 'steven',
                'kenneth', 'andrew', 'joshua', 'kevin', 'brian', 'george', 'timothy', 'ronald',
                'jason', 'edward', 'jeffrey', 'ryan', 'jacob', 'gary', 'nicholas', 'eric',
                'jonathan', 'stephen', 'larry', 'justin', 'scott', 'brandon', 'benjamin',
                'samuel', 'gregory', 'alexander', 'patrick', 'frank', 'raymond', 'jack',
                'dennis', 'jerry', 'tyler', 'aaron', 'jose', 'henry', 'adam', 'douglas',
                'nathan', 'peter', 'zachary', 'kyle', 'noah', 'alan', 'ethan', 'jeremy',
                'lionel', 'mike', 'bill', 'tom', 'bob', 'jim', 'joe', 'steve', 'dave',
                'chris', 'matt', 'dan', 'rick', 'rob', 'tony', 'andy', 'jeff', 'tim',
                'ken', 'ben', 'sam', 'alex', 'nick', 'josh', 'jake', 'luke', 'mark',
                'paul', 'sean', 'ryan', 'kevin', 'brian', 'jason', 'scott', 'brad',
                'chad', 'derek', 'eric', 'greg', 'jon', 'kyle', 'lance', 'mason',
                'owen', 'quinn', 'reed', 'seth', 'trey', 'wade', 'zach', 'dwayne',
                'wayne', 'wilson', 'jackson', 'mason', 'liam', 'noah', 'oliver',
                'elijah', 'william', 'james', 'benjamin', 'lucas', 'henry', 'alexander',
                'mason', 'michael', 'ethan', 'daniel', 'jacob', 'logan', 'jackson',
                'levi', 'sebastian', 'mateo', 'jack', 'owen', 'theodore', 'aiden',
                'samuel', 'joseph', 'john', 'david', 'wyatt', 'matthew', 'luke',
                'asher', 'carter', 'julian', 'grayson', 'leo', 'jayden', 'gabriel',
                'isaac', 'lincoln', 'anthony', 'hudson', 'dylan', 'ezra', 'thomas',
                'charles', 'christopher', 'jaxon', 'maverick', 'josiah', 'isaiah',
                'andrew', 'elias', 'joshua', 'nathan', 'caleb', 'ryan', 'adrian',
                'miles', 'eli', 'nolan', 'christian', 'aaron', 'cameron', 'ezekiel',
                'colton', 'luca', 'landon', 'hunter', 'jonathan', 'santiago', 'axel',
                'easton', 'cooper', 'jeremiah', 'angel', 'roman', 'connor', 'jameson',
                'robert', 'greyson', 'jordan', 'ian', 'carson', 'jaxson', 'leonardo',
                'nicholas', 'dominic', 'austin', 'everett', 'brooks', 'xavier', 'kai',
                'jose', 'parker', 'adam', 'jace', 'wesley', 'kayden', 'silas'
            ]
            
            # Check for USA indicators in username and bio
            text_to_check = f"{username} {bio}".lower()
            is_usa = any(indicator in text_to_check for indicator in usa_indicators)
            
            # Check for male indicators in username and bio
            is_male = any(name in text_to_check for name in male_names)
            
            # Special case for "dwayne" or "wilson" - clearly male names
            if 'dwayne' in text_to_check or 'wilson' in text_to_check:
                is_male = True
            
            # Check for clear female indicators
            female_indicators = [
                'she/her', 'girl', 'woman', 'lady', 'female', 'mom', 'mother', 'wife', 'girlfriend',
                'daughter', 'sister', 'aunt', 'grandma', 'grandmother', 'queen', 'princess',
                'beauty', 'makeup', 'fashion', 'shopping', 'cute', 'pretty', 'beautiful',
                # Female names - comprehensive list including Ruby
                'sarah', 'jessica', 'jennifer', 'ashley', 'amanda', 'stephanie', 'melissa',
                'nicole', 'elizabeth', 'heather', 'tiffany', 'michelle', 'amber', 'amy',
                'crystal', 'lisa', 'maria', 'anna', 'karen', 'nancy', 'betty', 'helen',
                'sandra', 'donna', 'carol', 'ruth', 'sharon', 'laura', 'kimberly', 'deborah', 
                'dorothy', 'ruby', 'emma', 'olivia', 'sophia', 'isabella', 'ava', 'mia',
                'abigail', 'madison', 'chloe', 'ella', 'avery', 'sofia', 'scarlett', 'grace',
                'lily', 'hannah', 'aria', 'layla', 'zoe', 'penelope', 'riley', 'nora',
                'leah', 'savannah', 'audrey', 'brooklyn', 'bella', 'claire', 'skylar', 'lucy',
                'paisley', 'evelyn', 'caroline', 'nova', 'genesis', 'emilia', 'kennedy', 'maya',
                'willow', 'kinsley', 'naomi', 'aaliyah', 'elena', 'ariana', 'allison', 'gabriella',
                'alice', 'madelyn', 'cora', 'eva', 'serenity', 'autumn', 'adeline', 'hailey',
                'gianna', 'valentina', 'isla', 'eliana', 'quinn', 'nevaeh', 'ivy', 'sadie',
                'piper', 'lydia', 'alexa', 'josephine', 'emery', 'julia', 'delilah', 'arianna',
                'vivian', 'kaylee', 'sophie', 'brielle', 'madeline', 'peyton', 'rylee', 'clara',
                'hadley', 'melanie', 'mackenzie', 'reagan', 'adalynn', 'liliana', 'aubrey', 'jade',
                'katherine', 'isabelle', 'natalie', 'raelynn', 'athena', 'ximena', 'arya', 'leilani',
                'taylor', 'alyssa', 'reese', 'margaret', 'iris', 'parker', 'alayna', 'eden',
                'kamila', 'charlie', 'catherine', 'andrea', 'samantha', 'diana', 'rachel', 'emily',
                # Female emojis and symbols
                '💋', '👄', '💄', '👗', '👠', '💅', '🌸', '🌺', '🦋', '💖', '💕', '💗',
                '👸', '👩', '🤱', '🤰', '💃', '👯', '🙋‍♀️', '🤷‍♀️', '💁‍♀️', '🙅‍♀️'
            ]
            
            # Check for clear non-USA indicators
            non_usa_indicators = [
                'uk', 'england', 'britain', 'british', 'london', 'manchester', 'birmingham',
                'canada', 'canadian', 'toronto', 'vancouver', 'montreal', 'ottawa',
                'australia', 'australian', 'sydney', 'melbourne', 'brisbane', 'perth',
                'india', 'indian', 'mumbai', 'delhi', 'bangalore', 'hyderabad', 'chennai',
                'pakistan', 'pakistani', 'karachi', 'lahore', 'islamabad',
                'bangladesh', 'bangladeshi', 'dhaka', 'chittagong',
                'nigeria', 'nigerian', 'lagos', 'abuja', 'kano',
                'south africa', 'south african', 'johannesburg', 'cape town', 'durban',
                'germany', 'german', 'berlin', 'munich', 'hamburg', 'cologne',
                'france', 'french', 'paris', 'marseille', 'lyon', 'toulouse',
                'italy', 'italian', 'rome', 'milan', 'naples', 'turin',
                'spain', 'spanish', 'madrid', 'barcelona', 'valencia', 'seville',
                'brazil', 'brazilian', 'sao paulo', 'rio de janeiro', 'brasilia',
                'mexico', 'mexican', 'mexico city', 'guadalajara', 'monterrey',
                'china', 'chinese', 'beijing', 'shanghai', 'guangzhou', 'shenzhen',
                'japan', 'japanese', 'tokyo', 'osaka', 'kyoto', 'yokohama',
                'russia', 'russian', 'moscow', 'st petersburg', 'novosibirsk',
                'europe', 'european', 'asia', 'asian', 'africa', 'african'
            ]
            
            # Check for clear indicators
            is_clearly_female = any(indicator in text_to_check for indicator in female_indicators)
            is_clearly_non_usa = any(indicator in text_to_check for indicator in non_usa_indicators)
            
            # Default assumption: male USA user unless clearly indicated otherwise
            final_gender = 'female' if is_clearly_female else 'male'
            final_is_usa = False if is_clearly_non_usa else True
            
            # Enhanced local analysis with detailed logging
            logger.info(f"Analyzing: username='{username}', bio='{bio}'")
            logger.info(f"Text to check: '{text_to_check}'")
            logger.info(f"Positive USA detection: {is_usa}")
            logger.info(f"Positive male detection: {is_male}")
            logger.info(f"Clearly female: {is_clearly_female}")
            logger.info(f"Clearly non-USA: {is_clearly_non_usa}")
            logger.info(f"Final gender (default male): {final_gender}")
            logger.info(f"Final USA (default true): {final_is_usa}")
            
            # Return enhanced detection results with defaults
            result = {
                'gender': final_gender,
                'is_usa': final_is_usa,
                'language': 'english',
                'followers': 0
            }
            
            logger.info(f"Final analysis result: {result}")
            return result
            
        except Exception as e:
            logger.error(f"Error in profile analysis: {e}")
            return self._get_fallback_analysis(username, bio, comment_text)
    
    def generate_female_engagement_response(self, post_content: str, user_profile: Dict, comment_text: str = "") -> str:
        """Generate a female engagement response based on user profile."""
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
            if response and isinstance(response, str) and len(response.strip()) > 10:
                logger.info(f"Generated AI response: {response}")
                return response.strip()
            else:
                logger.warning("AI response was empty or too short, using fallback")
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
    
    def _call_gemini_api(self, prompt: str) -> Optional[str]:
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
                    return text.strip()
            self.logger.error(f"Gemini API error: {response.status_code} - {response.text}")
        except Exception as e:
            self.logger.error(f"Error calling Gemini API: {e}")
        return None

class AndroidEngagement:
    def __init__(self, config_file: str = "android_config.json"):
        """Initialize the Android engagement bot."""
        self.config_file = config_file
        self.devices: Dict[str, Dict] = {}
        self.active_devices: Dict[str, u2.Device] = {}
        self.logger = logging.getLogger(__name__)
        self.ai_analyzer = AIAnalyzer()
        
        # Engagement settings
        self.min_likes_for_viral = 50  # Minimum 50 likes for viral content
        self.min_comments_for_viral = 1  # Lowered for testing
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
            # Try different possible package names for Threads
            threads_packages = [
                "Threads",
                "com.instagram.threads",
                "com.instagram.threadsapp",
                "com.threads.app"
            ]
            
            for package in threads_packages:
                try:
                    device.app_start(package)
                    time.sleep(5)
                    logger.info(f"Threads app opened successfully with package: {package}")
                    return
                except Exception as e:
                    logger.debug(f"Failed to open with package {package}: {e}")
                    continue
            
            # If all packages fail, try to find and click the Threads icon
            try:
                threads_icon = device.xpath('//*[contains(@text, "Threads") or contains(@content-desc, "Threads")]').get()
                if threads_icon:
                    threads_icon.click()
                    time.sleep(5)
                    logger.info("Threads app opened by clicking icon")
                    return
            except Exception as e:
                logger.debug(f"Failed to find Threads icon: {e}")
            
            logger.warning("Could not open Threads app automatically. Please open it manually.")
            
        except Exception as e:
            logger.error(f"Error opening Threads app: {str(e)}")
    
    def extract_number_from_text(self, text: str) -> int:
        """Extract number from text, handling various formats but avoiding timestamps and usernames."""
        try:
            if not text:
                return 0
            
            # Clean the text
            original_text = text
            text = text.strip()
            
            import re
            
            # CRITICAL FIX: Check for ALL time formats first before any other processing
            # This MUST block "4m", "32m", "3m", "1h", "5d", etc. from being interpreted as engagement
            
            # Block all time patterns (seconds, minutes, hours, days, weeks, months, years)
            time_patterns = [
                r'^\d+s$',      # seconds: 30s
                r'^\d+m$',      # minutes: 4m, 32m, 3m - CRITICAL FIX
                r'^\d+h$',      # hours: 1h, 24h
                r'^\d+d$',      # days: 7d, 30d
                r'^\d+w$',      # weeks: 2w
                r'^\d+mo$',     # months: 6mo
                r'^\d+y$',      # years: 1y
                r'^\d+:\d+$',   # clock time: 7:58, 12:30
                r'^\d+/\d+$',   # dates: 04/11, 03/29
                r'^\d+\.\d+$'   # version numbers: 1.5, 2.0
            ]
            
            for pattern in time_patterns:
                if re.match(pattern, text, re.IGNORECASE):
                    logger.info(f"🚫 BLOCKED TIME FORMAT: '{original_text}' (matched pattern: {pattern})")
                    return 0
            
            # Skip if text looks like a username with numbers (e.g., "user123", "digital_warrior_777")
            if re.search(r'[a-zA-Z_]+\d+', text) or re.search(r'\d+[a-zA-Z_]+', text):
                logger.debug(f"Skipping username-like text: {original_text}")
                return 0
            
            # Only look for engagement-related numbers in specific contexts
            engagement_patterns = [
                r'like\s+(\d+)',           # "Like 123"
                r'(\d+)\s+likes?',         # "123 likes"
                r'reply\s+(\d+)',          # "Reply 123"
                r'(\d+)\s+replies',        # "123 replies"
                r'repost\s+(\d+)',         # "Repost 123"
                r'(\d+)\s+reposts?',       # "123 reposts"
                r'share\s+(\d+)',          # "Share 123"
                r'(\d+)\s+shares?',        # "123 shares"
                r'view\s+(\d+)',           # "View 123"
                r'(\d+)\s+views?',         # "123 views"
            ]
            
            for pattern in engagement_patterns:
                match = re.search(pattern, text, re.IGNORECASE)
                if match:
                    num = int(match.group(1))
                    # Only return reasonable engagement numbers
                    if 1 <= num <= 10000000:  # 1 to 10 million max
                        logger.info(f"✅ Found engagement number: '{original_text}' -> {num}")
                        return num
            
            # Convert to uppercase for K/M handling
            text_upper = text.upper()
            
            # Handle K (thousands) - only if it's clearly an engagement number
            if 'K' in text_upper and any(word in text.lower() for word in ['like', 'reply', 'repost', 'share', 'view']):
                text_clean = text_upper.replace('K', '')
                try:
                    num = float(text_clean)
                    result = int(num * 1000)
                    logger.info(f"✅ Converting K to thousands: {original_text} -> {result}")
                    return result
                except:
                    return 0
            
            # Handle M (millions) - but NEVER for standalone timestamps
            if 'M' in text_upper:
                # CRITICAL: Block any standalone number+M pattern (these are timestamps)
                if re.match(r'^\d+M$', text_upper):
                    logger.info(f"🚫 BLOCKED TIMESTAMP: '{original_text}' (standalone number+M is a timestamp)")
                    return 0
                
                # Only proceed if it has clear engagement context words
                if any(word in text.lower() for word in ['like', 'reply', 'repost', 'share', 'view']):
                    text_clean = text_upper.replace('M', '')
                    try:
                        num = float(text_clean)
                        result = int(num * 1000000)
                        logger.info(f"✅ Converting M to millions: {original_text} -> {result}")
                        return result
                    except:
                        return 0
                else:
                    logger.info(f"🚫 BLOCKED: '{original_text}' (M without engagement context)")
                    return 0
            
            # For standalone numbers, only accept them if they're in a reasonable range for engagement
            if text.isdigit():
                num = int(text)
                # Only accept numbers that could reasonably be engagement counts (1-1M)
                if 1 <= num <= 1000000:
                    logger.info(f"✅ Standalone number: '{original_text}' -> {num}")
                    return num
                else:
                    logger.debug(f"Number {num} outside reasonable engagement range: {original_text}")
                    return 0
            
            # Handle numbers with decimal points (but not dates/versions)
            if '.' in text and not re.search(r'[a-zA-Z]', text) and not re.match(r'^\d+\.\d+$', text):
                try:
                    num = float(text)
                    if 1 <= num <= 1000000:
                        result = int(num)
                        logger.info(f"✅ Decimal number: '{original_text}' -> {result}")
                        return result
                    else:
                        logger.debug(f"Decimal number {num} outside reasonable range: {original_text}")
                        return 0
                except:
                    return 0
            
            # Try to extract numbers from mixed text - but be very careful
            numbers = re.findall(r'\d+', text)  # Only extract pure digits
            if numbers:
                try:
                    num = int(numbers[0])
                    # Only accept if it's a reasonable engagement number
                    if 1 <= num <= 1000000:
                        logger.info(f"✅ Extracted number: '{original_text}' -> {num}")
                        return num
                    else:
                        logger.debug(f"Extracted number {num} outside reasonable range: {original_text}")
                        return 0
                except:
                    return 0
            
            return 0
        except Exception as e:
            logger.debug(f"Error extracting number from '{text}': {e}")
            return 0
    
    def scan_feed(self, device: u2.Device) -> list:
        """Scan the feed for viral posts with scrolling to find more posts."""
        try:
            logger.info("Scanning feed for viral posts...")
            viral_posts = []
            scroll_attempts = 0
            max_scrolls = 5  # Scroll up to 5 times to find posts
            
            while len(viral_posts) == 0 and scroll_attempts < max_scrolls:
                logger.info(f"Scanning attempt {scroll_attempts + 1}/{max_scrolls}")
                
                # Find heart icons (like buttons) - try multiple selectors
                heart_selectors = [
                    '//*[contains(@content-desc, "Like")]',
                    '//*[contains(@content-desc, "like")]',
                    '//*[contains(@content-desc, "Heart")]',
                    '//*[contains(@content-desc, "heart")]',
                    '//*[@resource-id="like_button"]',
                    '//*[@resource-id="heart_button"]'
                ]
                
                heart_icons = []
                for selector in heart_selectors:
                    icons = device.xpath(selector).all()
                    if icons:
                        heart_icons.extend(icons)
                        logger.info(f"Found {len(icons)} heart icons with selector: {selector}")
                
                # Remove duplicates
                heart_icons = list(set(heart_icons))
                logger.info(f"Total unique heart icons found: {len(heart_icons)}")
                
                # Debug: Log all elements with engagement numbers (filtered)
                logger.info("=== DEBUGGING: Looking for engagement-related elements ===")
                all_elements = device.xpath('//*').all()
                elements_with_numbers = []
                
                for i, element in enumerate(all_elements[:100]):  # Check first 100 elements
                    try:
                        text = element.attrib.get('text', '')
                        content_desc = element.attrib.get('content-desc', '')
                        
                        # Check if element contains engagement numbers using improved extraction
                        if text:
                            num = self.extract_number_from_text(text)
                            if num > 0:
                                elements_with_numbers.append((element, num, text, "text"))
                                logger.info(f"Element {i}: text='{text}' -> engagement number: {num}")
                        
                        if content_desc:
                            num = self.extract_number_from_text(content_desc)
                            if num > 0:
                                elements_with_numbers.append((element, num, content_desc, "content-desc"))
                                logger.info(f"Element {i}: content-desc='{content_desc}' -> engagement number: {num}")
                                
                    except Exception as e:
                        continue
                
                logger.info(f"Found {len(elements_with_numbers)} elements with valid engagement numbers (filtered out timestamps and usernames)")
                
                for heart_icon in heart_icons:
                    try:
                        # Check if this is a viral post
                        viral_post = self.check_if_viral(device, heart_icon, elements_with_numbers)
                        if viral_post:
                            viral_posts.append(viral_post)
                            logger.info("Found viral post!")
                            break  # Process one post at a time
                    except Exception as e:
                        logger.error(f"Error checking heart icon: {e}")
                        continue
                
                # If no viral posts found, scroll down to load more posts
                if len(viral_posts) == 0:
                    logger.info(f"No viral posts found on attempt {scroll_attempts + 1}, scrolling down...")
                    device.swipe(400, 1200, 400, 400, 0.5)  # Scroll down
                    time.sleep(3)  # Wait for content to load
                    scroll_attempts += 1
                else:
                    break  # Found viral post, stop scrolling
            
            if len(viral_posts) == 0:
                logger.info(f"No viral posts found after {max_scrolls} scroll attempts")
            else:
                logger.info(f"Found {len(viral_posts)} viral posts after {scroll_attempts} scroll attempts")
            
            return viral_posts
        except Exception as e:
            logger.error(f"Error scanning feed: {str(e)}")
            return []
    
    def check_if_viral(self, device: u2.Device, heart_icon, elements_with_numbers) -> Optional[Dict]:
        """Check if a post is viral based on engagement metrics."""
        try:
            heart_center = heart_icon.center()
            logger.info(f"Heart icon center: ({heart_center[0]}, {heart_center[1]})")
            
            # Skip heart icons that are too high on screen (likely in profile/create post area)
            if heart_center[1] < 400:
                logger.info("Heart icon is too high on screen - likely in profile/create post area. Skipping.")
                return None
            
            nearby_numbers = []
            
            for element, num, text, field_type in elements_with_numbers:
                try:
                    element_center = element.center()
                    distance = ((heart_center[0] - element_center[0])**2 + 
                              (heart_center[1] - element_center[1])**2)**0.5
                    
                    if distance <= 800:  # Within 800 pixels
                        nearby_numbers.append((num, distance, text, field_type))
                        logger.info(f"Found number {num} at distance {distance:.1f} (from {field_type}: '{text}')")
                except Exception as e:
                    continue
            
            logger.info(f"Found {len(nearby_numbers)} nearby numbers for this heart icon")
            
            if nearby_numbers:
                # Sort by distance and take the closest number
                nearby_numbers.sort(key=lambda x: x[1])
                like_count = nearby_numbers[0][0]
                
                logger.info(f"Using like count: {like_count} (threshold: {self.min_likes_for_viral})")
                
                if like_count >= self.min_likes_for_viral:
                    return {
                        'heart_icon': heart_icon,
                        'like_count': like_count,
                        'comment_count': 0
                    }
                else:
                    logger.info(f"Like count {like_count} is below threshold {self.min_likes_for_viral}")
            else:
                logger.info("No nearby numbers found for this heart icon")
            
            return None
        except Exception as e:
            logger.error(f"Error checking if viral: {e}")
            return None
    
    def is_in_post_detail(self, device: u2.Device) -> bool:
        """Check if we're currently in a post detail view."""
        try:
            # Look for multiple indicators that we're in a post detail view
            indicators = [
                '//*[contains(@content-desc, "Add a comment")]',
                '//*[contains(@text, "Add a comment")]',
                '//*[contains(@content-desc, "Reply")]',
                '//*[contains(@text, "Reply")]',
                '//*[contains(@content-desc, "Post")]',
                '//*[contains(@text, "Post")]',
                '//*[contains(@content-desc, "Thread")]',
                '//*[contains(@text, "Thread")]',
                '//*[contains(@text, "views")]'  # Post view count indicator
            ]
            
            found_indicators = []
            for indicator in indicators:
                elements = device.xpath(indicator).all()
                if elements:
                    found_indicators.append(indicator)
                    logger.debug(f"Found post indicator: {indicator} ({len(elements)} elements)")
            
            # Need at least 2 indicators to be confident we're in a post
            is_post = len(found_indicators) >= 2
            logger.info(f"Post detail detection: {is_post} (found {len(found_indicators)} indicators)")
            
            # Check for specific post detail indicators that are more reliable
            post_specific_indicators = [
                '//*[contains(@text, "views")]',  # View count
                '//*[contains(@content-desc, "Turn on notifications")]',  # Notification toggle
                '//*[contains(@content-desc, "More options")]'  # Post options menu
            ]
            
            post_specific_count = 0
            for indicator in post_specific_indicators:
                elements = device.xpath(indicator).all()
                if elements:
                    post_specific_count += 1
                    logger.debug(f"Found post-specific indicator: {indicator}")
            
            # If we have post-specific indicators, we're likely in a post
            if post_specific_count >= 1:
                logger.info("Found post-specific indicators - likely in post detail")
                return True
            
            # Additional check: make sure we're not in the main feed (but be less strict)
            feed_indicators = device.xpath('//*[contains(@text, "Feeds") and not(contains(@text, "Thread"))]').all()
            if feed_indicators and len(feed_indicators) > 0 and not is_post:
                logger.info("Detected main feed without post indicators - not in post detail")
                return False
            
            return is_post
            
        except Exception as e:
            logger.error(f"Error checking post detail: {e}")
            return False

    def process_post(self, device: u2.Device, device_name: str, post: Dict):
        """Process a viral post by opening it and engaging with comments."""
        try:
            logger.info(f"Processing viral post with {post['like_count']} likes")
            
            # Click on the post to open it
            heart_icon = post['heart_icon']
            heart_center = heart_icon.center()
            logger.info(f"Heart icon center: ({heart_center[0]}, {heart_center[1]})")
            
            # Try multiple click positions to open the post properly
            # Get screen dimensions to ensure clicks stay within bounds
            screen_width = device.window_size()[0]
            screen_height = device.window_size()[1]
            logger.info(f"Screen dimensions: {screen_width}x{screen_height}")
            
            click_positions = [
                # Click to the left of the heart icon (post content area) - ensure within bounds
                (max(50, heart_center[0] - 100), heart_center[1]),
                # Click above and to the left of the heart icon
                (max(50, heart_center[0] - 80), max(100, heart_center[1] - 150)),
                # Click above the heart icon
                (heart_center[0], max(100, heart_center[1] - 200)),
                # Click on the heart icon itself as fallback
                (heart_center[0], heart_center[1])
            ]
            
            post_opened = False
            for i, (click_x, click_y) in enumerate(click_positions):
                try:
                    logger.info(f"Attempting to click position {i+1}: ({click_x}, {click_y})")
                    device.click(click_x, click_y)
                    time.sleep(3)
                    
                    # Use the new method to check if we're in a post detail view
                    if self.is_in_post_detail(device):
                        logger.info(f"Successfully opened post with click position {i+1}!")
                        post_opened = True
                        break
                    else:
                        logger.info(f"Post not opened with position {i+1}, trying next position...")
                        
                except Exception as e:
                    logger.error(f"Error clicking position {i+1}: {e}")
                    continue
            
            if not post_opened:
                logger.error("Failed to open post after trying all positions")
                return
            
            # Process comments in the post
            self.process_comments_in_post(device, device_name)
            
        except Exception as e:
            logger.error(f"Error processing post: {e}")
    
    def process_comments_in_post(self, device: u2.Device, device_name: str):
        """Process comments in a post to find and engage with users."""
        try:
            logger.info("Processing comments in post...")
            
            # First, identify the post author to exclude them
            post_author = self.get_post_author(device)
            logger.info(f"Post author identified: {post_author}")
            
            # Find usernames in comments
            usernames = self.find_usernames_in_comments(device)
            logger.info(f"Found {len(usernames)} usernames in comments")
            
            # Filter out post author and system accounts
            filtered_usernames = []
            for username in usernames:
                if username.lower() != post_author.lower() and not self.is_system_account(username):
                    filtered_usernames.append(username)
                else:
                    logger.info(f"Filtered out: {username} (post author or system account)")
            
            logger.info(f"After filtering: {len(filtered_usernames)} commenters to process")
            
            # If no commenters found, return to feed to find more posts
            if len(filtered_usernames) == 0:
                logger.info("No commenters found - returning to feed to scan for more viral posts")
                self.return_to_feed(device)
                return
            
            # Process each commenter
            for username in filtered_usernames[:5]:  # Process up to 5 commenters
                try:
                    logger.info(f"Processing commenter: {username}")
                    
                    # Get the comment text for this user before clicking profile
                    comment_text = self.get_user_comment_text(device, username)
                    logger.info(f"Comment from {username}: {comment_text}")
                    
                    # Analyze profile
                    profile_info = self.analyze_user_profile(device, username)
                    
                    if profile_info and profile_info.get('gender') == 'male' and profile_info.get('is_usa'):
                        logger.info(f"Found USA male commenter: {username}")
                        
                        # Return to comments section FIRST
                        self.return_to_comments(device)
                        
                        # Generate topic-relevant response
                        response = self.generate_flirty_response(username, profile_info, comment_text)
                        if response:
                            # Find and reply to their specific comment
                            self.reply_to_user_comment(device, username, response, comment_text)
                            time.sleep(5)  # Wait longer after posting
                            
                            # CRITICAL: Return to the SAME POST to continue processing other commenters
                            # Use top-left arrow to stay in the same post
                            logger.info("Returning to same post to process remaining commenters...")
                            self.return_to_comments(device)
                    else:
                        logger.info(f"Skipping {username}: not male USA user")
                        # Still return to comments for next user
                        self.return_to_comments(device)
                    
                except Exception as e:
                    logger.error(f"Error processing commenter {username}: {e}")
                    # Try to return to comments even if there was an error
                    logger.warning("Error occurred - attempting to return to comments section")
                    self.return_to_comments(device)
                    continue
            
        except Exception as e:
            logger.error(f"Error processing comments: {e}")

    def get_post_author(self, device: u2.Device) -> str:
        """Extract the post author's username."""
        try:
            # Look for elements that indicate the post author
            author_elements = device.xpath('//*[contains(@content-desc, "posted")]').all()
            for element in author_elements:
                content_desc = element.attrib.get('content-desc', '')
                if 'posted' in content_desc:
                    # Extract username from "username posted"
                    author = content_desc.replace(' posted', '').strip()
                    logger.info(f"Found post author: {author}")
                    return author
            
            # Alternative: look for profile elements
            profile_elements = device.xpath('//*[contains(@content-desc, "profile photo")]').all()
            for element in profile_elements:
                content_desc = element.attrib.get('content-desc', '')
                if 'profile photo' in content_desc:
                    # Extract username from "username profile photo"
                    author = content_desc.replace(' profile photo', '').strip()
                    logger.info(f"Found post author from profile photo: {author}")
                    return author
            
            logger.warning("Could not identify post author")
            return ""
            
        except Exception as e:
            logger.error(f"Error getting post author: {e}")
            return ""

    def is_system_account(self, username: str) -> bool:
        """Check if username is a system account or common false positive."""
        system_accounts = {
            'welcome', 'admin', 'moderator', 'support', 'help', 'official', 'verified',
            'system', 'bot', 'automated', 'service', 'notification', 'alert'
        }
        return username.lower() in system_accounts

    def get_user_comment_text(self, device: u2.Device, username: str) -> str:
        """Get the comment text associated with a specific username."""
        try:
            # Look for text elements near username elements
            all_elements = device.xpath('//*').all()
            
            # First, try to find the username element
            username_element_index = -1
            for i, element in enumerate(all_elements):
                try:
                    text = element.attrib.get('text', '').strip()
                    content_desc = element.attrib.get('content-desc', '').strip()
                    
                    # If this element contains the username (exact match preferred)
                    if (username.lower() == text.lower() or username.lower() == content_desc.lower() or
                        (username.lower() in content_desc.lower() and 'profile photo' not in content_desc.lower())):
                        username_element_index = i
                        logger.info(f"Found username element at index {i}: text='{text}', content-desc='{content_desc}'")
                        break
                        
                except Exception as e:
                    continue
            
            if username_element_index >= 0:
                # Look for comment text near the username element (wider search range)
                search_range = 10  # Look 10 elements before and after
                for j in range(max(0, username_element_index - search_range), 
                              min(len(all_elements), username_element_index + search_range)):
                    try:
                        nearby_element = all_elements[j]
                        nearby_text = nearby_element.attrib.get('text', '').strip()
                        
                        # If we find substantial text that's likely a comment
                        if (nearby_text and len(nearby_text) > 15 and 
                            username.lower() not in nearby_text.lower() and
                            not nearby_text.isdigit() and
                            'views' not in nearby_text.lower() and
                            'ago' not in nearby_text.lower() and
                            'Thread' not in nearby_text and
                            'Feeds' not in nearby_text and
                            'Follow' not in nearby_text and
                            'Verified' not in nearby_text and
                            not nearby_text.startswith('$')):  # Exclude stock symbols
                            logger.info(f"Found comment text for {username}: {nearby_text}")
                            return nearby_text
                            
                    except Exception as e:
                        continue
            
            # Fallback: look for any substantial text that might be a comment
            logger.info(f"Fallback search for comment text near {username}")
            for element in all_elements:
                try:
                    text = element.attrib.get('text', '').strip()
                    if (text and len(text) > 20 and len(text) < 300 and
                        not text.isdigit() and
                        'views' not in text.lower() and
                        'ago' not in text.lower() and
                        'Thread' not in text and
                        'Feeds' not in text and
                        username.lower() not in text.lower()):
                        logger.info(f"Found fallback comment text: {text}")
                        return text
                        
                except Exception as e:
                    continue
            
            logger.warning(f"Could not find comment text for {username}")
            return f"Great post about investing!"  # Generic fallback
            
        except Exception as e:
            logger.error(f"Error getting comment text for {username}: {e}")
            return f"Interesting perspective!"  # Generic fallback

    def return_to_comments(self, device: u2.Device):
        """Return to the comments section from a profile."""
        try:
            logger.info("Returning to comments section...")
            
            # First, check if we're still in Threads app
            if not self.is_in_threads_app(device):
                logger.error("Not in Threads app - cannot return to comments")
                return
            
            # Try multiple back button presses to ensure we get back to comments
            max_back_attempts = 3
            for attempt in range(max_back_attempts):
                logger.info(f"Back attempt {attempt + 1}/{max_back_attempts}")
                
                # Check if we're already in post detail (comments section)
                if self.is_in_post_detail(device):
                    logger.info("Successfully in post detail view (comments section)")
                    return
                
                # PRIORITIZE top left arrow navigation button (navigation_bar_back_button)
                try:
                    # Try multiple ways to find the back button
                    back_selectors = [
                        '//*[@resource-id="navigation_bar_back_button"]',
                        '//*[@content-desc="Back"][@resource-id="navigation_bar_back_button"]',
                        '//*[@content-desc="Back"]',
                        '//*[contains(@content-desc, "Back")]'
                    ]
                    
                    back_clicked = False
                    for selector in back_selectors:
                        try:
                            back_elements = device.xpath(selector).all()
                            if back_elements:
                                logger.info(f"Using navigation button: {selector}")
                                back_elements[0].click()
                                time.sleep(4)  # Wait longer for navigation
                                back_clicked = True
                                
                                # Check if we're still in Threads
                                if not self.is_in_threads_app(device):
                                    logger.error("Navigation button left Threads app - stopping navigation")
                                    return
                                
                                # Check if we're back in comments
                                if self.is_in_post_detail(device):
                                    logger.info(f"Successfully returned to comments via {selector}")
                                    return
                                break
                        except Exception as e:
                            logger.debug(f"Navigation selector {selector} failed: {e}")
                            continue
                    
                    if not back_clicked:
                        logger.warning("No navigation buttons found")
                        
                except Exception as e:
                    logger.error(f"Navigation failed on attempt {attempt + 1}: {e}")
                
                # Fallback to other UI back buttons
                back_buttons = [
                    '//*[@content-desc="Back"]',
                    '//*[contains(@content-desc, "Back")][@resource-id="navigation_bar_back_button"]',
                    '//*[contains(@content-desc, "arrow")]',
                    '//*[contains(@content-desc, "left")]',
                    '//*[contains(@content-desc, "←")]'
                ]
                
                back_clicked = False
                for selector in back_buttons:
                    try:
                        back_elements = device.xpath(selector).all()
                        if back_elements:
                            back_elements[0].click()
                            time.sleep(3)
                            logger.info(f"Clicked back button: {selector}")
                            
                            # Check if we're still in Threads
                            if not self.is_in_threads_app(device):
                                logger.error("UI back button left Threads app - stopping navigation")
                                return
                            
                            # Check if we're back in comments
                            if self.is_in_post_detail(device):
                                logger.info("Successfully returned to comments via UI back")
                                return
                            back_clicked = True
                            break
                            
                    except Exception as e:
                        logger.error(f"Error with back button {selector}: {e}")
                        continue
                
                # Only use system back as last resort
                if not back_clicked:
                    try:
                        logger.info("Using system back button as last resort")
                        device.press("back")
                        time.sleep(3)
                        
                        # Check if we're still in Threads
                        if not self.is_in_threads_app(device):
                            logger.error("System back left Threads app - stopping navigation")
                            return
                        
                        # Check if we're back in comments
                        if self.is_in_post_detail(device):
                            logger.info("Successfully returned to comments via system back")
                            return
                            
                    except Exception as e:
                        logger.error(f"System back failed on attempt {attempt + 1}: {e}")
            
            # If we still can't get back to comments after all attempts
            logger.warning(f"Could not return to comments section after {max_back_attempts} attempts")
            
            # Check current state for debugging
            post_detail_result = self.is_in_post_detail(device)
            logger.info(f"Final post detail check result: {post_detail_result}")
            
            # Dump UI elements for debugging
            self.dump_ui_elements(device, 15)
            
        except Exception as e:
            logger.error(f"Error returning to comments: {e}")

    def return_to_feed(self, device: u2.Device):
        """Return to the main feed from a post detail view."""
        try:
            logger.info("Returning to main feed...")
            
            # First, check if we're still in Threads app
            if not self.is_in_threads_app(device):
                logger.error("Not in Threads app - cannot return to feed")
                return
            
            # Try multiple back button presses to get back to feed
            max_back_attempts = 5
            for attempt in range(max_back_attempts):
                logger.info(f"Feed return attempt {attempt + 1}/{max_back_attempts}")
                
                # Check if we're already in the main feed
                feed_indicators = device.xpath('//*[contains(@text, "Feeds") and not(contains(@text, "Thread"))]').all()
                if feed_indicators and len(feed_indicators) > 0:
                    logger.info("Successfully returned to main feed")
                    return
                
                # Try system back button
                try:
                    device.press("back")
                    time.sleep(2)
                    logger.info(f"Used system back button (feed attempt {attempt + 1})")
                    
                    # Check if we're still in Threads
                    if not self.is_in_threads_app(device):
                        logger.error("System back left Threads app - stopping navigation")
                        return
                        
                except Exception as e:
                    logger.error(f"System back failed on feed attempt {attempt + 1}: {e}")
                    
                    # Try UI back buttons - prioritize top left arrow
                    back_buttons = [
                        '//*[@resource-id="navigation_bar_back_button"]',  # Top left arrow - PRIORITY
                        '//*[@content-desc="Back"]',
                        '//*[contains(@content-desc, "arrow")]',
                        '//*[contains(@content-desc, "left")]',
                        '//*[contains(@content-desc, "←")]'
                    ]
                    
                    for selector in back_buttons:
                        try:
                            back_elements = device.xpath(selector).all()
                            if back_elements:
                                back_elements[0].click()
                                time.sleep(2)
                                logger.info(f"Clicked back button for feed: {selector}")
                                
                                # Check if we're still in Threads
                                if not self.is_in_threads_app(device):
                                    logger.error("UI back button left Threads app - stopping navigation")
                                    return
                                break
                                
                        except Exception as e:
                            logger.error(f"Error with back button {selector}: {e}")
                            continue
            
            # Final check
            feed_indicators = device.xpath('//*[contains(@text, "Feeds") and not(contains(@text, "Thread"))]').all()
            if feed_indicators and len(feed_indicators) > 0:
                logger.info("Successfully returned to main feed after multiple attempts")
            else:
                logger.warning(f"Could not return to main feed after {max_back_attempts} attempts")
                # Dump UI elements for debugging
                self.dump_ui_elements(device, 10)
            
        except Exception as e:
            logger.error(f"Error returning to feed: {e}")

    def generate_flirty_response(self, username: str, profile_info: Dict, comment_text: str) -> str:
        """Generate a flirty female response that stays on topic."""
        try:
            logger.info(f"Generating flirty response for {username} about: {comment_text}")
            
            # Create a more specific prompt for flirty responses
            flirty_prompt = f"""
            You are a 25-year-old flirty female responding to a comment on social media.
            
            User: {username}
            Their comment: {comment_text}
            Their profile: {profile_info.get('bio', 'No bio available')}
            
            Generate a flirty but tasteful response that:
            1. Stays on topic with their comment
            2. Shows interest in them personally
            3. Is playful and engaging
            4. Uses emojis appropriately
            5. Keeps it under 100 characters
            6. Sounds natural and conversational
            
            Examples of tone:
            - "Totally agree! You seem really smart about this 😊 What got you into [topic]?"
            - "Love this perspective! You're clearly passionate about it 💭 Tell me more?"
            - "So true! I'd love to hear more of your thoughts on this 😉"
            
            Response:
            """
            
            # Use AI to generate response
            response = self.ai_analyzer.generate_female_engagement_response(flirty_prompt, profile_info, comment_text)
            
            # Fallback flirty responses if AI fails
            if not response or len(response) < 10:
                fallback_responses = [
                    f"Love your take on this! You seem really thoughtful 😊",
                    f"Totally agree with you! What else do you think about this? 💭",
                    f"Great point! You clearly know what you're talking about 😉",
                    f"This is so interesting! I'd love to hear more of your thoughts 💫",
                    f"You make such good points! What got you interested in this? 😊"
                ]
                import random
                response = random.choice(fallback_responses)
            
            logger.info(f"Generated flirty response: {response}")
            return response
            
        except Exception as e:
            logger.error(f"Error generating flirty response: {e}")
            return "Great point! 😊"

    def reply_to_user_comment(self, device: u2.Device, username: str, response: str, comment_text: str):
        """Find and reply to a specific user's comment."""
        try:
            logger.info(f"Replying to {username}'s comment with: {response}")
            
            # First, try to find the user's comment on screen
            comment_found = False
            all_elements = device.xpath('//*').all()
            
            for i, element in enumerate(all_elements):
                try:
                    text = element.attrib.get('text', '').strip()
                    content_desc = element.attrib.get('content-desc', '').strip()
                    
                    # If we find the username or their comment text
                    if (username.lower() in text.lower() or username.lower() in content_desc.lower() or
                        (comment_text and len(comment_text) > 10 and comment_text.lower() in text.lower())):
                        
                        # Look for nearby reply button
                        for j in range(max(0, i-2), min(len(all_elements), i+3)):
                            nearby_element = all_elements[j]
                            nearby_desc = nearby_element.attrib.get('content-desc', '')
                            
                            if 'reply' in nearby_desc.lower():
                                logger.info(f"Found reply button for {username}")
                                nearby_element.click()
                                time.sleep(2)
                                comment_found = True
                                break
                        
                        if comment_found:
                            break
                            
                except Exception as e:
                    continue
            
            if not comment_found:
                # Fallback: use reply/comment icons from the logs
                logger.info("Using general comment input as fallback")
                reply_selectors = [
                    '//*[@resource-id="feed_post_ufi_reply_button"]',  # Main reply button from logs
                    '//*[contains(@content-desc, "Reply")]',  # Reply buttons
                    '//*[contains(@content-desc, "Add a comment")]',
                    '//*[contains(@text, "Add a comment")]',
                    '//*[contains(@content-desc, "Write a comment")]',
                    '//*[contains(@text, "Write a comment")]',
                    '//*[contains(@content-desc, "Comment")]',
                    '//*[@resource-id="comment_input"]',
                    '//*[@class="android.widget.EditText"]'
                ]
                
                input_found = False
                for selector in reply_selectors:
                    try:
                        reply_elements = device.xpath(selector).all()
                        if reply_elements:
                            reply_elements[0].click()
                            time.sleep(3)  # Wait longer for comment input to appear
                            logger.info(f"Clicked reply/comment button with selector: {selector}")
                            input_found = True
                            break
                    except Exception as e:
                        logger.warning(f"Reply selector failed: {selector} - {e}")
                        continue
                
                if not input_found:
                    logger.error("Could not find any reply/comment button")
                    return
            
            # Type the response using different methods
            try:
                # Try to find and click on text input field first
                input_fields = device.xpath('//*[@class="android.widget.EditText"]').all()
                if input_fields:
                    input_fields[0].click()
                    time.sleep(1)
                    input_fields[0].set_text(response)
                    time.sleep(2)
                    logger.info("Used EditText field to type response")
                else:
                    # Try focused element
                    device(focused=True).set_text(response)
                    time.sleep(2)
                    logger.info("Used focused element to type response")
            except Exception as e:
                logger.warning(f"Text input failed: {e}, trying send_keys")
                try:
                    device.send_keys(response)
                    time.sleep(2)
                    logger.info("Used send_keys to type response")
                except Exception as e2:
                    logger.error(f"All typing methods failed: {e2}")
                    return
            
            # Look for post/send button with multiple selectors
            post_selectors = [
                '//*[@content-desc="Post"]',
                '//*[contains(@content-desc, "Post")]',
                '//*[contains(@content-desc, "Send")]',
                '//*[contains(@text, "Post")]',
                '//*[contains(@text, "Send")]',
                '//*[contains(@text, "Reply")]',
                '//*[@resource-id="post_button"]',
                '//*[@resource-id="send_button"]',
                '//*[@class="android.widget.Button"]'
            ]
            
            post_found = False
            for selector in post_selectors:
                try:
                    post_buttons = device.xpath(selector).all()
                    if post_buttons:
                        post_buttons[0].click()
                        logger.info(f"Successfully posted reply to {username} using {selector}: {response}")
                        time.sleep(3)
                        post_found = True
                        break
                except Exception as e:
                    continue
            
            if not post_found:
                # Try pressing Enter as primary fallback
                try:
                    device.press("enter")
                    logger.info(f"Used Enter key to post reply to {username}: {response}")
                    time.sleep(3)
                    post_found = True
                except Exception as e:
                    logger.warning(f"Enter key failed: {e}")
                    
                    # Try clicking anywhere on screen as last resort
                    try:
                        device.click(600, 1500)  # Bottom right area where post buttons usually are
                        logger.info(f"Used screen click to post reply to {username}: {response}")
                        time.sleep(3)
                        post_found = True
                    except Exception as e2:
                        logger.error(f"All post methods failed for {username}: {e2}")
                
        except Exception as e:
            logger.error(f"Error replying to {username}: {e}")

    def find_usernames_in_comments(self, device: u2.Device) -> List[str]:
        """Find usernames in the comment section, scrolling if needed, and log skipped candidates for debugging."""
        try:
            usernames = set()
            ui_words = set([
                'reply', 'views', 'top', 'like', 'comment', 'share', 'post', 'feeds', 'thread', 'view',
                'following', 'follow', 'message', 'minutes', 'hours', 'days', 'weeks', 'months', 'years',
                'just now', 'now', 'today', 'yesterday', 'ago', 'original', 'author', 'see translation',
                'translated', 'verified', 'replied', 'liked', 'reposted', 'shared', 'send', 'add', 'edit', 'delete',
                'hide', 'report', 'block', 'unblock', 'mute', 'unmute', 'remove', 'cancel', 'save', 'unsave', 'copy',
                'more', 'less', 'expand', 'collapse', 'show', 'hide', 'all', 'none', 'done', 'back', 'close', 'open',
                'search', 'filter', 'sort', 'settings', 'options', 'help', 'info', 'about', 'terms', 'privacy', 'policy',
                'logout', 'login', 'sign up', 'register', 'create', 'new', 'old', 'recent', 'popular', 'trending', 'hot',
                'cold', 'random', 'suggested', 'recommended', 'for you', 'you', 'me', 'my', 'mine', 'your', 'yours',
                'his', 'her', 'hers', 'its', 'our', 'ours', 'their', 'theirs', 'everyone', 'everybody', 'someone',
                'somebody', 'anyone', 'anybody', 'no one', 'nobody', 'user', 'users', 'account', 'accounts', 'profile',
                'profiles', 'bio', 'bios', 'story', 'stories', 'highlight', 'highlights', 'archive', 'archives', 'activity',
                'activities', 'notification', 'notifications', 'update', 'updates', 'news', 'feed', 'feeds', 'explore',
                'discover', 'search', 'find', 'browse', 'watch', 'view', 'see', 'look', 'read', 'write', 'type', 'input',
                'output', 'send', 'receive', 'sent', 'received', 'draft', 'drafts', 'pending', 'approved', 'rejected',
                'flagged', 'banned', 'suspended', 'active', 'inactive', 'online', 'offline', 'available', 'unavailable',
                'busy', 'away', 'do not disturb', 'dnd', 'status', 'state', 'mode', 'level', 'rank', 'score', 'points',
                'badges', 'rewards', 'achievements', 'goals', 'milestones', 'progress', 'completed', 'incomplete',
                'failed', 'success', 'win', 'lose', 'lost', 'found', 'missing', 'error', 'warning', 'info', 'tip', 'hint',
                'guide', 'tutorial', 'faq', 'support', 'contact', 'feedback', 'bug', 'bugs', 'issue', 'issues', 'problem',
                'problems', 'solution', 'solutions', 'fix', 'fixed', 'update', 'updated', 'upgrade', 'upgraded', 'install',
                'installed', 'uninstall', 'uninstalled', 'download', 'downloaded', 'upload', 'uploaded', 'sync', 'synced',
                'connect', 'connected', 'disconnect', 'disconnected', 'link', 'linked', 'unlink', 'unlinked', 'pair',
                'paired', 'unpair', 'unpaired', 'share', 'shared', 'unshare', 'unshared', 'invite', 'invited', 'join',
                'joined', 'leave', 'left', 'exit', 'quit', 'start', 'started', 'stop', 'stopped', 'pause', 'paused',
                'resume', 'resumed', 'restart', 'restarted', 'reset', 'resetting', 'restore', 'restored', 'backup',
                'backed up', 'restore', 'restored', 'import', 'imported', 'export', 'exported', 'sync', 'synced',
            ])
            import re
            scroll_attempts = 0
            max_scrolls = 5  # Increased scroll attempts
            
            logger.info("=== STARTING USERNAME DETECTION IN COMMENTS ===")
            
            # First, check if we're actually in a comment section
            comment_indicators = device.xpath('//*[contains(@content-desc, "Add a comment")]').all()
            if not comment_indicators:
                comment_indicators = device.xpath('//*[contains(@text, "Add a comment")]').all()
            if not comment_indicators:
                # Look for reply buttons which indicate we're in a post with comments
                comment_indicators = device.xpath('//*[contains(@content-desc, "Reply")]').all()
            if not comment_indicators:
                # Look for comment-related elements
                comment_indicators = device.xpath('//*[contains(@resource-id, "comment")]').all()
            
            if comment_indicators:
                logger.info("✅ Comment section detected - found comment-related elements")
            else:
                logger.warning("⚠️ Comment section not detected - may not be in a post")
                # Dump UI elements to see what's actually on screen
                self.dump_ui_elements(device)
            
            while len(usernames) < 5 and scroll_attempts < max_scrolls:  # Increased target to 5 usernames
                logger.info(f"Scanning for usernames (attempt {scroll_attempts + 1}/{max_scrolls})")
                
                # Check both text and content-desc attributes
                text_elements = device.xpath('//*[@text]').all()
                content_desc_elements = device.xpath('//*[@content-desc]').all()
                
                logger.info(f"Found {len(text_elements)} text elements and {len(content_desc_elements)} content-desc elements")
                
                # Process text elements
                for i, element in enumerate(text_elements):
                    try:
                        text = element.attrib.get('text', '').strip()
                        
                        # Log all text elements for debugging (but limit to first 20)
                        if text and len(text) > 0 and i < 20:
                            logger.info(f"Text element {i}: '{text}'")
                        
                        # More lenient username detection
                        if self._is_valid_username(text, ui_words):
                            candidate = text.lstrip('@')
                            if candidate.lower() not in usernames:
                                usernames.add(candidate.lower())
                                logger.info(f"✅ Found username from text: {candidate}")
                        
                    except Exception as e:
                        continue
                
                # Process content-desc elements (usernames often appear here without @)
                for i, element in enumerate(content_desc_elements):
                    try:
                        content_desc = element.attrib.get('content-desc', '').strip()
                        
                        # Log content-desc elements for debugging (but limit to first 20)
                        if content_desc and len(content_desc) > 0 and i < 20:
                            logger.info(f"Content-desc element {i}: '{content_desc}'")
                        
                        # More lenient username detection for content-desc
                        if self._is_valid_username(content_desc, ui_words):
                            candidate = content_desc.lstrip('@')
                            if candidate.lower() not in usernames:
                                usernames.add(candidate.lower())
                                logger.info(f"✅ Found username from content-desc: {candidate}")
                        
                    except Exception as e:
                        continue
                
                logger.info(f"After scan {scroll_attempts + 1}: Found {len(usernames)} usernames")
                
                # If we found no usernames and this is the first attempt, dump UI elements
                if len(usernames) == 0 and scroll_attempts == 0:
                    logger.warning("No usernames found on first attempt - dumping UI elements for debugging")
                    self.dump_ui_elements(device)
                
                if len(usernames) < 5:  # Increased target
                    logger.info(f"Scrolling comments to find more usernames (attempt {scroll_attempts+1})...")
                    
                    # Check current screen state before scrolling
                    before_elements = len(device.xpath('//*[@text]').all())
                    logger.info(f"Text elements before scroll: {before_elements}")
                    
                    # Try different scroll directions and coordinates
                    if scroll_attempts == 0:
                        # Scroll down in comment section
                        device.swipe(400, 1200, 400, 600, 0.5)
                        logger.info("Scrolled down (attempt 1)")
                    elif scroll_attempts == 1:
                        # Scroll down more aggressively
                        device.swipe(400, 1400, 400, 400, 0.5)
                        logger.info("Scrolled down aggressively (attempt 2)")
                    elif scroll_attempts == 2:
                        # Scroll up to see if there are comments above
                        device.swipe(400, 600, 400, 1200, 0.5)
                        logger.info("Scrolled up (attempt 3)")
                    else:
                        # Alternate scroll directions
                        if scroll_attempts % 2 == 0:
                            device.swipe(400, 1200, 400, 600, 0.5)
                            logger.info(f"Scrolled down (attempt {scroll_attempts + 1})")
                        else:
                            device.swipe(400, 600, 400, 1200, 0.5)
                            logger.info(f"Scrolled up (attempt {scroll_attempts + 1})")
                    
                    time.sleep(3)  # Wait longer for content to load
                    
                    # Check if scroll changed anything
                    after_elements = len(device.xpath('//*[@text]').all())
                    logger.info(f"Text elements after scroll: {after_elements}")
                    
                    if after_elements == before_elements:
                        logger.warning("Scroll did not change the number of text elements - may not be working")
                    else:
                        logger.info(f"Scroll successful - element count changed from {before_elements} to {after_elements}")
                    
                    scroll_attempts += 1
                else:
                    break
            
            logger.info(f"=== USERNAME DETECTION COMPLETE: Found {len(usernames)} usernames ===")
            return list(usernames)
        except Exception as e:
            logger.error(f"Error finding usernames: {e}")
            return []

    def _is_valid_username(self, text: str, ui_words: set) -> bool:
        """Helper method to check if text is a valid username with more lenient rules and a hardened exclusion list."""
        import re
        
        # Hardened exclusion list for common false positives and system labels
        hardened_exclusions = {
            'overview', 'home', 'gallery', 'gif', 'back', 'follow', 'following', 'repost', 'like', 'reply',
            'send', 'post', 'comment', 'share', 'feeds', 'thread', 'view', 'edit', 'delete', 'add', 'remove',
            'save', 'unsave', 'copy', 'more', 'less', 'expand', 'collapse', 'show', 'hide', 'all', 'none',
            'done', 'close', 'open', 'search', 'filter', 'sort', 'settings', 'options', 'help', 'info',
            'about', 'terms', 'privacy', 'policy', 'logout', 'login', 'sign up', 'register', 'create',
            'new', 'old', 'recent', 'popular', 'trending', 'hot', 'cold', 'random', 'suggested',
            'recommended', 'for you', 'you', 'me', 'my', 'mine', 'your', 'yours', 'his', 'her', 'hers',
            'its', 'our', 'ours', 'their', 'theirs', 'everyone', 'everybody', 'someone', 'somebody',
            'anyone', 'anybody', 'no one', 'nobody', 'user', 'users', 'account', 'accounts', 'profile',
            'profiles', 'bio', 'bios', 'story', 'stories', 'highlight', 'highlights', 'archive', 'archives',
            'activity', 'activities', 'notification', 'notifications', 'update', 'updates', 'news', 'feed',
            'explore', 'discover', 'find', 'browse', 'watch', 'see', 'look', 'read', 'write', 'type',
            'input', 'output', 'receive', 'sent', 'received', 'draft', 'drafts', 'pending', 'approved',
            'rejected', 'flagged', 'banned', 'suspended', 'active', 'inactive', 'online', 'offline',
            'available', 'unavailable', 'busy', 'away', 'do not disturb', 'dnd', 'status', 'state',
            'mode', 'level', 'rank', 'score', 'points', 'badges', 'rewards', 'achievements', 'goals',
            'milestones', 'progress', 'completed', 'incomplete', 'failed', 'success', 'win', 'lose',
            'lost', 'found', 'missing', 'error', 'warning', 'tip', 'hint', 'guide', 'tutorial', 'faq',
            'support', 'contact', 'feedback', 'bug', 'bugs', 'issue', 'issues', 'problem', 'problems',
            'solution', 'solutions', 'fix', 'fixed', 'upgrade', 'upgraded', 'install', 'installed',
            'uninstall', 'uninstalled', 'download', 'downloaded', 'upload', 'uploaded', 'sync', 'synced',
            'connect', 'connected', 'disconnect', 'disconnected', 'link', 'linked', 'unlink', 'unlinked',
            'pair', 'paired', 'unpair', 'unpaired', 'invite', 'invited', 'join', 'joined', 'leave', 'left',
            'exit', 'quit', 'start', 'started', 'stop', 'stopped', 'pause', 'paused', 'resume', 'resumed',
            'restart', 'restarted', 'reset', 'resetting', 'restore', 'restored', 'backup', 'backed up',
            'import', 'imported', 'export', 'exported', 'send', 'shared', 'unshare', 'unshared',
            'minutes', 'hours', 'days', 'weeks', 'months', 'years', 'just now', 'now', 'today',
            'yesterday', 'ago', 'original', 'author', 'see translation', 'translated', 'verified',
            'replied', 'liked', 'reposted', 'shared', 'add a comment', 'turn on notifications',
            'more options', 'profile photo', 'posted', 'feed_post_ufi_like_button', 'feed_post_ufi_reply_button',
            # CRITICAL: Threads-specific system elements that are being detected as usernames
            'threads', 'replies', 'media', 'reposts', 'pinned', 'insights', 'instagram', 'gorkha', 'gorkhalanda',
            'hotbpoison', 'navalsarchive', 'chriswillx', '48lawsofpowerrr', 'views', 'turn', 'notifications',
            'thread', 'hours', 'enable', 'profile', 'menu', 'weekly', 'recap', 'ready', 'activity',
            'hi', 'hello', 'hey', 'thanks', 'thank', 'you', 'welcome', 'please', 'sorry', 'excuse',
            'pardon', 'yes', 'no', 'ok', 'okay', 'sure', 'maybe', 'perhaps', 'probably', 'definitely',
            'absolutely', 'certainly', 'exactly', 'precisely', 'indeed', 'really', 'truly', 'actually',
            'basically', 'essentially', 'generally', 'usually', 'normally', 'typically', 'commonly',
            'frequently', 'often', 'sometimes', 'occasionally', 'rarely', 'seldom', 'never', 'always',
            'forever', 'constantly', 'continuously', 'regularly', 'daily', 'weekly', 'monthly', 'yearly',
            # Additional system elements found in logs
            'camera', 'voice', 'poll', 'gif', 'gallery', 'withregram', 'lennieboy', 'refreshing',
            'cancel', 'switch', 'input', 'method', 'public', 'settings', 'edit', 'share', 'add',
            'interests', 'followers', 'picture', 'posted', 'reposted', 'shared', 'liked', 'replied',
            'commented', 'followed', 'unfollowed', 'blocked', 'unblocked', 'muted', 'unmuted',
        }
        
        # Exclude empty or too long
        if not text or len(text) < 2 or len(text) > 35:
            return False
        
        # Exclude time strings (e.g., 6:14, 9h, 1d)
        if re.match(r'\d{1,2}:\d{2}$', text) or re.match(r'\d+h$', text) or re.match(r'\d+d$', text):
            return False
        
        # Exclude UI words (case-insensitive, exact match)
        if text.lower() in ui_words:
            return False
        
        # Exclude hardened exclusions (case-insensitive)
        if text.lower() in hardened_exclusions:
            return False
        
        # Exclude if contains spaces
        if ' ' in text:
            return False
        
        # Exclude pure numbers
        if text.isdigit():
            return False
        
        # Exclude very short numbers (like "1", "2", etc.)
        if len(text) <= 2 and text.isdigit():
            return False
        
        # Allow usernames with @, letters, numbers, underscores, dots, hyphens
        candidate = text.lstrip('@')
        if re.match(r'^[A-Za-z0-9_.-]{2,35}$', candidate):
            # Additional checks for valid usernames
            # Must contain at least one letter
            if not re.search(r'[A-Za-z]', candidate):
                return False
            # Must not be all numbers
            if candidate.isdigit():
                return False
            # Must not be time format (like "2m", "3h", "5d")
            if re.match(r'^\d+[mhd]$', candidate):
                return False
            # Must not be just "no" or other common words
            if candidate.lower() in ['no', 'hi', 'ok']:
                return False
            return True
        
        return False

    def dump_ui_elements(self, device: u2.Device, max_elements: int = 50):
        """Dump all UI elements for debugging purposes."""
        try:
            logger.info("=== DUMPING ALL UI ELEMENTS FOR DEBUGGING ===")
            
            # Get all elements with text
            text_elements = device.xpath('//*[@text]').all()
            logger.info(f"Found {len(text_elements)} elements with text")
            
            for i, element in enumerate(text_elements[:max_elements]):
                try:
                    text = element.attrib.get('text', '').strip()
                    content_desc = element.attrib.get('content-desc', '').strip()
                    resource_id = element.attrib.get('resource-id', '').strip()
                    class_name = element.attrib.get('class', '').strip()
                    
                    if text or content_desc:
                        logger.info(f"Element {i}: text='{text}' | content-desc='{content_desc}' | resource-id='{resource_id}' | class='{class_name}'")
                        
                except Exception as e:
                    continue
            
            # Get all elements with content-desc
            content_desc_elements = device.xpath('//*[@content-desc]').all()
            logger.info(f"Found {len(content_desc_elements)} elements with content-desc")
            
            for i, element in enumerate(content_desc_elements[:max_elements]):
                try:
                    text = element.attrib.get('text', '').strip()
                    content_desc = element.attrib.get('content-desc', '').strip()
                    resource_id = element.attrib.get('resource-id', '').strip()
                    class_name = element.attrib.get('class', '').strip()
                    
                    if content_desc and not text:  # Only log if content-desc exists and text doesn't
                        logger.info(f"Content-desc element {i}: text='{text}' | content-desc='{content_desc}' | resource-id='{resource_id}' | class='{class_name}'")
                        
                except Exception as e:
                    continue
            
            logger.info("=== END UI ELEMENT DUMP ===")
            
        except Exception as e:
            logger.error(f"Error dumping UI elements: {e}")

    def check_available_apps(self, device: u2.Device):
        """Check what apps are available on the device and look for Threads."""
        try:
            logger.info("=== CHECKING AVAILABLE APPS ===")
            
            # Get list of installed apps
            apps = device.app_list()
            logger.info(f"Found {len(apps)} installed apps")
            
            # Look for Threads-related apps
            threads_apps = []
            for app in apps:
                if 'threads' in app.lower() or 'barcelona' in app.lower():
                    threads_apps.append(app)
            
            if threads_apps:
                logger.info(f"Found {len(threads_apps)} Threads-related apps:")
                for app in threads_apps:
                    logger.info(f"  - {app}")
            else:
                logger.info("No Threads-related apps found in app list")
            
            # Also check for Threads UI elements on current screen
            threads_elements = device.xpath('//*[contains(@text, "Threads") or contains(@content-desc, "Threads")]').all()
            if threads_elements:
                logger.info(f"Found {len(threads_elements)} Threads-related UI elements")
                for i, element in enumerate(threads_elements):
                    text = element.attrib.get('text', '')
                    content_desc = element.attrib.get('content-desc', '')
                    logger.info(f"Threads element {i+1}: text='{text}', content-desc='{content_desc}'")
            else:
                logger.info("No Threads-related UI elements found on current screen")
                
        except Exception as e:
            logger.error(f"Error checking available apps: {e}")

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
            
            logger.info(f"Profile analysis for {username}: {profile_info}")
            return profile_info
            
        except Exception as e:
            logger.error(f"Error analyzing profile for {username}: {e}")
            return None

    def click_username_in_comments(self, device: u2.Device, username: str) -> bool:
        """Click on a username in the comments to open their profile."""
        try:
            logger.info(f"Looking for username {username} to click")
            
            # Look for elements containing the username
            all_elements = device.xpath('//*').all()
            
            for element in all_elements:
                try:
                    text = element.attrib.get('text', '').strip()
                    content_desc = element.attrib.get('content-desc', '').strip()
                    
                    # Check if this element contains the username
                    if (username.lower() in text.lower() or username.lower() in content_desc.lower()):
                        # Make sure it's not a system element
                        if ('profile photo' not in content_desc.lower() and 
                            'posted' not in content_desc.lower() and
                            text != 'views' and text != 'ago'):
                            
                            logger.info(f"Found username element: text='{text}', content-desc='{content_desc}'")
                            element.click()
                            time.sleep(2)
                            logger.info(f"Clicked on username: {username}")
                            return True
                            
                except Exception as e:
                    continue
            
            logger.warning(f"Could not find clickable element for username: {username}")
            return False
            
        except Exception as e:
            logger.error(f"Error clicking username {username}: {e}")
            return False

    def is_in_threads_app(self, device: u2.Device) -> bool:
        """Check if we're still in the Threads app."""
        try:
            # Look for Threads-specific elements
            threads_indicators = [
                '//*[@resource-id="com.instagram.barcelona:id/action_bar_root"]',
                '//*[contains(@text, "Thread")]',
                '//*[contains(@text, "Feeds")]',
                '//*[contains(@content-desc, "Threads")]'
            ]
            
            for indicator in threads_indicators:
                elements = device.xpath(indicator).all()
                if elements:
                    logger.debug(f"Found Threads indicator: {indicator}")
                    return True
            
            logger.warning("Not in Threads app - may have navigated away")
            return False
            
        except Exception as e:
            logger.error(f"Error checking Threads app: {e}")
            return False

    def run(self):
        """Main bot execution loop."""
        try:
            logger.info("Starting Android Engagement Bot...")
            
            # Connect to devices
            for device_name in self.devices:
                device = self.connect_device(device_name)
                if not device:
                    continue
                
                try:
                    # Check available apps
                    self.check_available_apps(device)
                    
                    # Open Threads app
                    self.open_threads_app(device)
                    time.sleep(3)
                    
                    # Debug: Check screen content
                    logger.info("=== DEBUGGING: Checking screen content ===")
                    all_elements = device.xpath('//*').all()
                    logger.info(f"Total elements on screen: {len(all_elements)}")
                    
                    for i in range(min(20, len(all_elements))):
                        element = all_elements[i]
                        text = element.attrib.get('text', '')
                        content_desc = element.attrib.get('content-desc', '')
                        resource_id = element.attrib.get('resource-id', '')
                        logger.info(f"Element {i+1}: text='{text}', content-desc='{content_desc}', resource-id='{resource_id}'")
                    
                    # Continuous scanning loop
                    while True:
                        try:
                            # Scan for viral posts
                            viral_posts = self.scan_feed(device)
                            logger.info(f"Found {len(viral_posts)} viral posts")
                            
                            # Process viral posts
                            if viral_posts:
                                for post in viral_posts:
                                    self.process_post(device, device_name, post)
                                    break  # Process one post at a time, then scan for more
                            else:
                                logger.info("No viral posts found, waiting 30 seconds before next scan...")
                                time.sleep(30)
                                
                        except Exception as e:
                            logger.error(f"Error in scanning loop: {e}")
                            time.sleep(10)  # Wait before retrying
                            continue
                    
                except Exception as e:
                    logger.error(f"Error processing device {device_name}: {e}")
                    continue
                
        except Exception as e:
            logger.error(f"Error in main execution: {e}")

def main():
    """Main entry point for the bot."""
    try:
        # Set up logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        
        # Create and run the bot
        bot = AndroidEngagement()
        bot.run()
        
    except Exception as e:
        logger.error(f"Error in main: {e}")

if __name__ == "__main__":
    main()
