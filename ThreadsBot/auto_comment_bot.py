import threading
import time
import logging
import random
import uiautomator2 as u2
import requests
from queue import Queue

# AI Integration with Gemini API
GEMINI_API_KEY = "AIzaSyBisaaQ1dsEELVRYKFEIMQId-cR97So_X8"
GEMINI_API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent"

class AutoCommentBot:
    def __init__(self, device_serial='usb', like_threshold=100, comment_threshold=20, ai_api_key=GEMINI_API_KEY, log_callback=None):
        self.device_serial = device_serial
        self.like_threshold = like_threshold
        self.comment_threshold = comment_threshold
        self.ai_api_key = ai_api_key
        self.ai_api_url = GEMINI_API_URL
        self.running = False
        self.thread = None
        self.log_callback = log_callback or (lambda msg: print(msg))
        self.device = None

    def log(self, msg):
        self.log_callback(msg)

    def connect_device(self):
        try:
            self.device = u2.connect(self.device_serial)
            self.log(f"Connected to device: {self.device_serial}")
            return True
        except Exception as e:
            self.log(f"Error connecting to device: {e}")
            return False

    def open_threads_app(self):
        try:
            self.device.app_start("com.instagram.threadsapp")
            time.sleep(5)
            self.log("Threads app opened successfully")
        except Exception as e:
            self.log(f"Error opening Threads app: {e}")

    def extract_number_from_text(self, text):
        import re
        if not text:
            return 0
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

    def generate_ai_comment(self, post_content, user_profile):
        try:
            prompt = f"""
            Generate a natural, engaging response to this social media post:
            Post Content: {post_content}\nUser Profile: {user_profile}\nRequirements:\n- Keep it under 100 characters\n- Sound natural and conversational\n- Be positive and engaging\n- Include appropriate emojis\nReturn only the response text.
            """
            headers = {"Content-Type": "application/json"}
            data = {
                "contents": [{"parts": [{"text": prompt}]}],
                "generationConfig": {"temperature": 0.7, "maxOutputTokens": 100}
            }
            url = f"{self.ai_api_url}?key={self.ai_api_key}"
            response = requests.post(url, headers=headers, json=data, timeout=10)
            if response.status_code == 200:
                result = response.json()
                if 'candidates' in result and len(result['candidates']) > 0:
                    text = result['candidates'][0]['content']['parts'][0]['text']
                    return text[:100]
        except Exception as e:
            self.log(f"Error generating AI response: {e}")
        return random.choice([
            "Great post! Really enjoyed this content 🔥",
            "This is amazing! Thanks for sharing 🙌",
            "Love your perspective on this! 💯",
        ])

    def scan_and_comment(self):
        self.log("Bot started.")
        if not self.connect_device():
            return
        self.open_threads_app()
        while self.running:
            try:
                # Find heart icons (like buttons)
                heart_icons = self.device.xpath('//*[contains(@content-desc, "like") or contains(@resource-id, "like")]').all()
                text_elements = self.device.xpath('//*[@text]').all()
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
                for heart_icon in heart_icons:
                    try:
                        heart_center = heart_icon.center()
                        nearby_numbers = []
                        for element, num in elements_with_numbers:
                            try:
                                element_center = element.center()
                                distance = ((heart_center[0] - element_center[0])**2 + (heart_center[1] - element_center[1])**2)**0.5
                                if distance <= 500:
                                    nearby_numbers.append((num, distance))
                            except Exception:
                                continue
                        if len(nearby_numbers) >= 2:
                            nearby_numbers.sort(key=lambda x: x[1])
                            like_count = nearby_numbers[0][0]
                            comment_count = nearby_numbers[1][0]
                            if like_count >= self.like_threshold and comment_count >= self.comment_threshold:
                                self.log(f"Found post: {like_count} likes, {comment_count} comments")
                                # Click to open post
                                click_x = heart_center[0] + 100
                                click_y = heart_center[1]
                                self.device.click(click_x, click_y)
                                time.sleep(3)
                                # Generate and post comment
                                post_content = ""  # You can add logic to extract post content
                                user_profile = {}  # You can add logic to extract user profile
                                comment = self.generate_ai_comment(post_content, user_profile)
                                self.log(f"Commenting: {comment}")
                                # Find reply button
                                reply_buttons = self.device.xpath('//*[contains(@content-desc, "Reply")]').all()
                                if reply_buttons:
                                    reply_buttons[0].click()
                                    time.sleep(2)
                                    text_inputs = self.device.xpath('//*[@class="android.widget.EditText"]').all()
                                    if text_inputs:
                                        text_inputs[0].click()
                                        time.sleep(1)
                                        self.device.send_keys(comment)
                                        time.sleep(1)
                                        post_buttons = self.device.xpath('//*[contains(@content-desc, "Post") or contains(@content-desc, "Send")]').all()
                                        if post_buttons:
                                            post_buttons[0].click()
                                            self.log("Comment posted!")
                                            time.sleep(2)
                                self.device.press("back")
                                time.sleep(1)
                    except Exception as e:
                        self.log(f"Error processing post: {e}")
                        try:
                            self.device.press("back")
                            time.sleep(1)
                        except:
                            pass
                self.device.swipe(0.5, 0.8, 0.5, 0.2)
                time.sleep(3)
            except Exception as e:
                self.log(f"Error in main loop: {e}")
                time.sleep(5)
        self.log("Bot stopped.")

    def start(self):
        if self.running:
            self.log("Bot is already running.")
            return
        self.running = True
        self.thread = threading.Thread(target=self.scan_and_comment)
        self.thread.start()

    def stop(self):
        self.running = False
        if self.thread:
            self.thread.join()
            self.thread = None 