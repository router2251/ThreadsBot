#!/usr/bin/env python3
"""
Test script to verify timestamp detection is working correctly.
This ensures the bot doesn't interpret timestamps as massive like counts.
"""

import re

def extract_number_from_text(text: str) -> int:
    """Extract number from text, handling various formats but avoiding timestamps and usernames."""
    try:
        if not text:
            return 0
        
        # Clean the text
        original_text = text
        text = text.strip()
        
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
                print(f"🚫 BLOCKED TIME FORMAT: '{original_text}' (matched pattern: {pattern})")
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
                    print(f"✅ Found engagement number: '{original_text}' -> {num}")
                    return num
        
        # For standalone numbers, only accept them if they're in a reasonable range for engagement
        if text.isdigit():
            num = int(text)
            # Only accept numbers that could reasonably be engagement counts (1-1M)
            if 1 <= num <= 1000000:
                print(f"✅ Standalone number: '{original_text}' -> {num}")
                return num
            else:
                print(f"Number {num} outside reasonable engagement range: {original_text}")
                return 0
        
        return 0
    except Exception as e:
        print(f"Error extracting number from '{text}': {e}")
        return 0

def test_timestamp_detection():
    """Test cases to verify timestamp detection works correctly."""
    print("=== TESTING TIMESTAMP DETECTION ===")
    
    # Test cases that should be BLOCKED (return 0)
    blocked_cases = [
        "4m",      # 4 minutes - should NOT be 4 million
        "32m",     # 32 minutes - should NOT be 32 million  
        "3m",      # 3 minutes - should NOT be 3 million
        "1h",      # 1 hour
        "24h",     # 24 hours
        "7d",      # 7 days
        "2w",      # 2 weeks
        "6mo",     # 6 months
        "1y",      # 1 year
        "7:58",    # clock time
        "12:30",   # clock time
        "04/11",   # date
        "03/29",   # date
        "1.5",     # version number
        "2.0"      # version number
    ]
    
    print("\n--- Testing BLOCKED cases (should return 0) ---")
    for case in blocked_cases:
        result = extract_number_from_text(case)
        status = "✅ PASS" if result == 0 else f"❌ FAIL (returned {result})"
        print(f"{case:10} -> {result:10} {status}")
    
    # Test cases that should be ALLOWED (return actual numbers)
    allowed_cases = [
        ("Like 123", 123),
        ("Reply 45", 45),
        ("Repost 67", 67),
        ("123 likes", 123),
        ("45 replies", 45),
        ("67 reposts", 67),
        ("100", 100),
        ("50", 50),
        ("1000", 1000)
    ]
    
    print("\n--- Testing ALLOWED cases (should return numbers) ---")
    for case, expected in allowed_cases:
        result = extract_number_from_text(case)
        status = "✅ PASS" if result == expected else f"❌ FAIL (expected {expected}, got {result})"
        print(f"{case:15} -> {result:10} {status}")

if __name__ == "__main__":
    test_timestamp_detection()
    print("\n=== TEST COMPLETE ===") 