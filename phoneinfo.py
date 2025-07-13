import re
import phonenumbers
from phonenumbers import carrier, geocoder, timezone
import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime
import time
import webbrowser
import socket
import whois
import dns.resolver
import pytz
from twilio.rest import Client  # For Real-Time Caller ID
import threading

# Configuration
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
REQUEST_TIMEOUT = 15
HEADERS = {'User-Agent': USER_AGENT}

# Twilio Config (For Real-Time Caller ID)
TWILIO_SID = "YOUR_TWILIO_SID"
TWILIO_TOKEN = "YOUR_TWILIO_TOKEN"

EU_COUNTRY_CODES = [
    '43', '32', '359', '385', '357', '420', '45', '372', '358', '33',
    '49', '30', '36', '354', '353', '39', '371', '423', '370', '352',
    '356', '31', '47', '48', '351', '40', '421', '386', '34', '46',
    '41', '44', '383', '389'
]

# ==================== HELPER FUNCTIONS (ADDED) ====================
def validate_european_number(phone_number):
    try:
        parsed = phonenumbers.parse(phone_number, None)
        if str(parsed.country_code) in EU_COUNTRY_CODES and phonenumbers.is_valid_number(parsed):
            return parsed
        return None
    except Exception:
        return None

def get_carrier_info(parsed_number):
    try:
        return carrier.name_for_number(parsed_number, 'en')
    except Exception:
        return None

def get_location_info(parsed_number):
    try:
        return geocoder.description_for_number(parsed_number, 'en')
    except Exception:
        return None

def get_timezone_info(parsed_number):
    try:
        return timezone.time_zones_for_number(parsed_number)
    except Exception:
        return None

def check_spam_databases(phone_number):
    # Placeholder: In real use, query spam DBs/APIs
    return "Not checked (demo)"

def check_social_media(phone_number):
    # Placeholder: In real use, query APIs or scrape
    return "Not checked (demo)"

def get_number_type(parsed_number):
    try:
        return phonenumbers.number_type(parsed_number)
    except Exception:
        return None

# ==================== NEW REVERSE LOOKUP FUNCTIONS ====================
def reverse_lookup_public_sources(phone_number):
    """Check public directories and social media for name associations"""
    try:
        formatted_num = phonenumbers.format_number(
            phonenumbers.parse(phone_number),
            phonenumbers.PhoneNumberFormat.E164
        ).replace('+', '')
        
        # Check TruePeopleSearch (US/EU)
        url = f"https://www.truepeoplesearch.com/results?phoneno={formatted_num}"
        response = requests.get(url, headers=HEADERS, timeout=REQUEST_TIMEOUT)
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            name_tag = soup.find("div", class_="h4")
            if name_tag:
                return {"name": name_tag.get_text(strip=True), "source": "truepeoplesearch.com"}
        
        # Fallback to Google search
        google_url = f"https://www.google.com/search?q={phone_number}"
        return {"name": "Not Found (Try manual search)", "source": google_url}
        
    except Exception as e:
        return {"error": str(e)}

def reverse_lookup_social_media(phone_number):
    """Check if number is linked to social profiles"""
    social_profiles = []
    formatted_num = phonenumbers.format_number(
        phonenumbers.parse(phone_number),
        phonenumbers.PhoneNumberFormat.E164
    )
    
    # Facebook
    fb_url = f"https://www.facebook.com/search/people/?q={formatted_num}"
    social_profiles.append({"platform": "Facebook", "url": fb_url})
    
    # LinkedIn
    li_url = f"https://www.linkedin.com/search/results/all/?keywords={formatted_num}"
    social_profiles.append({"platform": "LinkedIn", "url": li_url})
    
    return social_profiles

# ==================== REAL-TIME CALLER ID ====================
def start_live_caller_id_monitor():
    """Monitor incoming calls in real-time using Twilio"""
    def monitor():
        client = Client(TWILIO_SID, TWILIO_TOKEN)
        print("\n🔴 LIVE CALLER ID ACTIVE (Ctrl+C to stop)")
        print("Listening for incoming calls...")
        
        while True:
            calls = client.calls.list(limit=1)
            if calls:
                call = calls[0]
                if call.status == "ringing":
                    print(f"\n🚨 INCOMING CALL FROM: {call.from_}")
                    info = get_phone_info(call.from_)
                    display_results(info)
                    time.sleep(10)  # Prevent duplicate alerts
    
    thread = threading.Thread(target=monitor)
    thread.daemon = True
    thread.start()
    return thread

# ==================== MODIFIED MAIN FUNCTIONS ====================
def get_phone_info(phone_number):
    """Main lookup function now with reverse lookup"""
    start_time = time.time()
    
    parsed_number = validate_european_number(phone_number)
    if not parsed_number:
        return {
            'error': 'Invalid European phone number format',
            'valid': False,
            'lookup_time': time.time() - start_time
        }
    
    formatted_num = phonenumbers.format_number(
        parsed_number,
        phonenumbers.PhoneNumberFormat.INTERNATIONAL
    )
    
    # Get standard info
    result = {
        'number': formatted_num,
        'country_code': parsed_number.country_code,
        'carrier': get_carrier_info(parsed_number),
        'location': get_location_info(parsed_number),
        'timezone': get_timezone_info(parsed_number),
        'spam': check_spam_databases(phone_number),
        'social_media': check_social_media(phone_number),
        'number_type': get_number_type(parsed_number),
        'valid': True,
        'lookup_time': time.time() - start_time
    }
    
    # Add reverse lookup results
    if input("Perform reverse lookup? (y/n): ").lower() == 'y':
        result['reverse_lookup'] = {
            'public_records': reverse_lookup_public_sources(phone_number),
            'social_media': reverse_lookup_social_media(phone_number)
        }
    
    return result

def display_results(info):
    """Enhanced display with reverse lookup results"""
    # ... (keep all your existing display code) ...
    
    # Add reverse lookup section
    if 'reverse_lookup' in info:
        print("\n🕵️‍♂️ REVERSE LOOKUP RESULTS:")
        rl = info['reverse_lookup']
        
        if 'public_records' in rl:
            pr = rl['public_records']
            if 'name' in pr:
                print(f"• Possible Name: {pr['name']} (Source: {pr.get('source', 'Unknown')})")
            elif 'error' in pr:
                print(f"• Public Records Error: {pr['error']}")
        
        if 'social_media' in rl and rl['social_media']:
            print("\n🔍 Social Media Links:")
            for sm in rl['social_media']:
                print(f"  - {sm['platform']}: {sm['url']}")

# ==================== MODIFIED MAIN MENU ====================
def main():
    print("🌍 ULTIMATE EUROPEAN PHONE TRACKER")
    print("=" * 70)
    print("1. Single Number Lookup")
    print("2. Real-Time Caller ID Monitor")
    print("3. Exit")
    
    choice = input("\nSelect mode (1-3): ")
    
    if choice == '1':
        phone_number = input("\nEnter phone number (with country code): ").strip()
        if phone_number:
            info = get_phone_info(phone_number)
            display_results(info)
    elif choice == '2':
        if TWILIO_SID == "YOUR_TWILIO_SID":
            print("\n❌ Twilio not configured. Get SID/Token from twilio.com")
        else:
            monitor = start_live_caller_id_monitor()
            try:
                while True: time.sleep(1)
            except KeyboardInterrupt:
                print("\nStopping monitor...")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n👋 Exiting...")
    except Exception as e:
        print(f"⚠️ Error: {e}")