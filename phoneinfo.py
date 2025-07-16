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

USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
REQUEST_TIMEOUT = 15
HEADERS = {'User-Agent': USER_AGENT}

TWILIO_SID = "YOUR_TWILIO_SID"
TWILIO_TOKEN = "YOUR_TWILIO_TOKEN"

EU_COUNTRY_CODES = [
    '43', '32', '359', '385', '357', '420', '45', '372', '358', '33',
    '49', '30', '36', '354', '353', '39', '371', '423', '370', '352',
    '356', '31', '47', '48', '351', '40', '421', '386', '34', '46',
    '41', '44', '383', '389'
]

COUNTRY_CODE_MAP = {
    '43': 'Austria',
    '32': 'Belgium',
    '359': 'Bulgaria',
    '385': 'Croatia',
    '357': 'Cyprus',
    '420': 'Czech Republic',
    '45': 'Denmark',
    '372': 'Estonia',
    '358': 'Finland',
    '33': 'France',
    '49': 'Germany',
    '30': 'Greece',
    '36': 'Hungary',
    '354': 'Iceland',
    '353': 'Ireland',
    '39': 'Italy',
    '371': 'Latvia',
    '423': 'Liechtenstein',
    '370': 'Lithuania',
    '352': 'Luxembourg',
    '356': 'Malta',
    '31': 'Netherlands',
    '47': 'Norway',
    '48': 'Poland',
    '351': 'Portugal',
    '40': 'Romania',
    '421': 'Slovakia',
    '386': 'Slovenia',
    '34': 'Spain',
    '46': 'Sweden',
    '41': 'Switzerland',
    '44': 'United Kingdom',
    '383': 'Kosovo',
    '389': 'North Macedonia',
    '7': 'Russia',
    '380': 'Ukraine',
    '375': 'Belarus',
    '373': 'Moldova',
    '355': 'Albania',
    '387': 'Bosnia and Herzegovina',
    '382': 'Montenegro',
    '381': 'Serbia',
    '90': 'Turkey',
    '995': 'Georgia',
    '994': 'Azerbaijan',
    '372': 'Estonia',
    '370': 'Lithuania',
    '371': 'Latvia',
    '356': 'Malta',
    '357': 'Cyprus',
    '423': 'Liechtenstein',
    '351': 'Portugal',
    '354': 'Iceland',
    '356': 'Malta',
    '357': 'Cyprus',
    '358': 'Finland',
    '359': 'Bulgaria',
    '373': 'Moldova',
    '374': 'Armenia',
    '375': 'Belarus',
    '376': 'Andorra',
    '377': 'Monaco',
    '378': 'San Marino',
    '379': 'Vatican City',
    '380': 'Ukraine',
    '381': 'Serbia',
    '382': 'Montenegro',
    '383': 'Kosovo',
    '385': 'Croatia',
    '386': 'Slovenia',
    '387': 'Bosnia and Herzegovina',
    '389': 'North Macedonia',
    '423': 'Liechtenstein',
}

try:
    with open('europe_countries_cities.json', 'r', encoding='utf-8') as f:
        country_city_data = json.load(f)
except Exception:
    country_city_data = {}

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
        ntype = phonenumbers.number_type(parsed_number)
        # Local mapping of number type integers to human-readable strings
        type_map = {
            0: 'Fixed line',
            1: 'Mobile',
            2: 'Fixed line or Mobile',
            3: 'Toll free',
            4: 'Premium rate',
            5: 'Shared cost',
            6: 'VoIP',
            7: 'Personal number',
            8: 'Pager',
            9: 'UAN',
            10: 'Voicemail',
            99: 'Unknown',
        }
        return type_map.get(ntype, str(ntype))
    except Exception:
        return None

def get_country_name(parsed_number):
    try:
        region_code = phonenumbers.region_code_for_country_code(parsed_number.country_code)
        if region_code:
            country = geocoder.country_name_for_number(parsed_number, 'en')
            if country:
                return country
        # Fallback to manual map
        return COUNTRY_CODE_MAP.get(str(parsed_number.country_code), None)
    except Exception:
        return None

def get_lat_lon_for_location(city, country):
    """Get latitude and longitude for a given city and country using OpenStreetMap Nominatim API."""
    try:
        if not city and not country:
            return None, None
        query = ''
        if city:
            query += city
        if country:
            if query:
                query += ', '
            query += country
        url = f"https://nominatim.openstreetmap.org/search"
        params = {
            'q': query,
            'format': 'json',
            'limit': 1
        }
        response = requests.get(url, params=params, headers={'User-Agent': USER_AGENT}, timeout=REQUEST_TIMEOUT)
        if response.status_code == 200:
            data = response.json()
            if data:
                lat = data[0].get('lat')
                lon = data[0].get('lon')
                return lat, lon
        return None, None
    except Exception:
        return None, None

def reverse_lookup_public_sources(phone_number):
    """Check public directories and social media for name associations"""
    try:
        formatted_num = phonenumbers.format_number(
            phonenumbers.parse(phone_number),
            phonenumbers.PhoneNumberFormat.E164
        ).replace('+', '')
        
        url = f"https://www.truepeoplesearch.com/results?phoneno={formatted_num}"
        response = requests.get(url, headers=HEADERS, timeout=REQUEST_TIMEOUT)
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            name_tag = soup.find("div", class_="h4")
            if name_tag:
                return {"name": name_tag.get_text(strip=True), "source": "truepeoplesearch.com"}
        
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
    
    fb_url = f"https://www.facebook.com/search/people/?q={formatted_num}"
    social_profiles.append({"platform": "Facebook", "url": fb_url})
    
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

def get_phone_info(phone_number):
    """Main lookup function now with always-on info display"""
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
    city = get_location_info(parsed_number)
    country = get_country_name(parsed_number)
    lat, lon = get_lat_lon_for_location(city, country)

    result = {
        'number': formatted_num,
        'country_code': parsed_number.country_code,
        'national_number': parsed_number.national_number,
        'city': city,
        'country': country,
        'latitude': lat,
        'longitude': lon,
        'carrier': get_carrier_info(parsed_number),
        'location': city,  # for backward compatibility
        'timezone': get_timezone_info(parsed_number),
        'number_type': get_number_type(parsed_number),
        'valid': True,
        'lookup_time': time.time() - start_time,
        'parsed_number': parsed_number # Added for display_results
    }
    return result


def display_results(info):
    """Display all key phone info in a user-friendly way, including city, country, and lat/lon"""
    print("\n================ PHONE NUMBER INFO ================")
    if not info.get('valid'):
        print(f"❌ {info.get('error', 'Invalid number')}")
        return
    print(f"• Number: {info.get('number')}")
    print(f"• Country Code: {info.get('country_code')}" )
    print(f"• National Number: {info.get('national_number')}")
    city = info.get('city')
    print(f"• City/Region: {city if city else 'Unknown'}")
    country = info.get('country')
    print(f"• Country: {country if country else 'Unknown'}")
    # Show example cities from JSON if available
    if country and country_city_data:
        cities = country_city_data.get(country)
        if cities:
            print(f"• Example Cities: {', '.join(cities[:5])} ...")
        else:
            print("• No city data found for this country.")
    print(f"• Latitude: {info.get('latitude') if info.get('latitude') else 'Unknown'}")
    print(f"• Longitude: {info.get('longitude') if info.get('longitude') else 'Unknown'}")
    print(f"• Carrier: {info.get('carrier')}")
    tz = info.get('timezone')
    if isinstance(tz, (list, tuple)):
        tz = ', '.join(tz)
    print(f"• Timezone(s): {tz}")
    ntype = info.get('number_type')
    if ntype is not None:
        print(f"• Number Type: {ntype}")
    print(f"• Lookup Time: {info.get('lookup_time'):.2f} seconds")
    print("==================================================\n")

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
