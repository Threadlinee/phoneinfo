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
from twilio.rest import Client
import threading
import colorama
from colorama import Fore, Style
colorama.init(autoreset=True)

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

# //////////////////////////////////////////////////////////////////////////////////
# //                                                                              //
# //      ███████████  █████                                                      //
# //     ░░███░░░░░███░░███                                                       //
# //      ░███    ░███ ░███████    ██████  ████████    ██████                     //
# //      ░██████████  ░███░░███  ███░░███░░███░░███  ███░░███                    //
# //      ░███░░░░░░   ░███ ░███ ░███ ░███ ░███ ░███ ░███████                     //
# //      ░███         ░███ ░███ ░███ ░███ ░███ ░███ ░███░░░                      //
# //      █████        ████ █████░░██████  ████ █████░░██████                     //
# //     ░░░░░        ░░░░ ░░░░░  ░░░░░░  ░░░░ ░░░░░  ░░░░░░                      //
# //                                            █████                             //
# //                                           ░░███                              //
# //      ████████   █████ ████ █████████████   ░███████   ██████  ████████       //
# //     ░░███░░███ ░░███ ░███ ░░███░░███░░███  ░███░░███ ███░░███░░███░░███      //
# //      ░███ ░███  ░███ ░███  ░███ ░███ ░███  ░███ ░███░███████  ░███ ░░░       //
# //      ░███ ░███  ░███ ░███  ░███ ░███ ░███  ░███ ░███░███░░░   ░███           //
# //      ████ █████ ░░████████ █████░███ █████ ████████ ░░██████  █████          //
# //     ░░░░ ░░░░░   ░░░░░░░░ ░░░░░ ░░░ ░░░░░ ░░░░░░░░   ░░░░░░  ░░░░░           //
# //       ███                ██████                                              //
# //      ░░░                ███░░███                                             //
# //      ████  ████████    ░███ ░░░   ██████                                     //
# //     ░░███ ░░███░░███  ███████    ███░░███                                    //
# //      ░███  ░███ ░███ ░░░███░    ░███ ░███                                    //
# //      ░███  ░███ ░███   ░███     ░███ ░███                                    //
# //      █████ ████ █████  █████    ░░██████                                     //
# //     ░░░░░ ░░░░ ░░░░░  ░░░░░      ░░░░░░                                      //
# //                                   █████     █████                            //
# //                                  ░░███     ░░███                             //
# //       ███████ ████████   ██████   ░███████  ░███████   ██████  ████████      //
# //      ███░░███░░███░░███ ░░░░░███  ░███░░███ ░███░░███ ███░░███░░███░░███     //
# //     ░███ ░███ ░███ ░░░   ███████  ░███ ░███ ░███ ░███░███████  ░███ ░░░      //
# //     ░███ ░███ ░███      ███░░███  ░███ ░███ ░███ ░███░███░░░   ░███          //
# //     ░░███████ █████    ░░████████ ████████  ████████ ░░██████  █████         //
# //      ░░░░░███░░░░░      ░░░░░░░░ ░░░░░░░░  ░░░░░░░░   ░░░░░░  ░░░░░          //
# //      ███ ░███                                                                //
# //     ░░██████                                                                 //
# //      ░░░░░░                                                                  //
# //                                                                              //
# //////////////////////////////////////////////////////////////////////////////////

ASCII_ART = f"""
{Fore.CYAN}
//////////////////////////////////////////////////////////////////////////////////
//                                                                              //
//      ███████████  █████                                                      //
//     ░░███░░░░░███░░███                                                       //
//      ░███    ░███ ░███████    ██████  ████████    ██████                     //
//      ░██████████  ░███░░███  ███░░███░░███░░███  ███░░███                    //
//      ░███░░░░░░   ░███ ░███ ░███ ░███ ░███ ░███ ░███████                     //
//      ░███         ░███ ░███ ░███ ░███ ░███ ░███ ░███░░░                      //
//      █████        ████ █████░░██████  ████ █████░░██████                     //
//     ░░░░░        ░░░░ ░░░░░  ░░░░░░  ░░░░ ░░░░░  ░░░░░░                      //
//                                            █████                             //
//                                           ░░███                              //
//      ████████   █████ ████ █████████████   ░███████   ██████  ████████       //
//     ░░███░░███ ░░███ ░███ ░░███░░███░░███  ░███░░███ ███░░███░░███░░███      //
//      ░███ ░███  ░███ ░███  ░███ ░███ ░███  ░███ ░███░███████  ░███ ░░░       //
//      ░███ ░███  ░███ ░███  ░███ ░███ ░███  ░███ ░███░███░░░   ░███           //
//      ████ █████ ░░████████ █████░███ █████ ████████ ░░██████  █████          //
//     ░░░░ ░░░░░   ░░░░░░░░ ░░░░░ ░░░ ░░░░░ ░░░░░░░░   ░░░░░░  ░░░░░           //
//       ███                ██████                                              //
//      ░░░                ███░░███                                             //
//      ████  ████████    ░███ ░░░   ██████                                     //
//     ░░███ ░░███░░███  ███████    ███░░███                                    //
//      ░███  ░███ ░███ ░░░███░    ░███ ░███                                    //
//      ░███  ░███ ░███   ░███     ░███ ░███                                    //
//      █████ ████ █████  █████    ░░██████                                     //
//     ░░░░░ ░░░░ ░░░░░  ░░░░░      ░░░░░░                                      //
//                                   █████     █████                            //
//                                  ░░███     ░░███                             //
//       ███████ ████████   ██████   ░███████  ░███████   ██████  ████████      //
//      ███░░███░░███░░███ ░░░░░███  ░███░░███ ░███░░███ ███░░███░░███░░███     //
//     ░███ ░███ ░███ ░░░   ███████  ░███ ░███ ░███ ░███░███████  ░███ ░░░      //
//     ░███ ░███ ░███      ███░░███  ░███ ░███ ░███ ░███░███░░░   ░███          //
//     ░░███████ █████    ░░████████ ████████  ████████ ░░██████  █████         //
//      ░░░░░███░░░░░      ░░░░░░░░ ░░░░░░░░  ░░░░░░░░   ░░░░░░  ░░░░░          //
//      ███ ░███                                                                //
//     ░░██████                                                                 //
//      ░░░░░░                                                                  //
//                                                                              //
//////////////////////////////////////////////////////////////////////////////////
{Style.RESET_ALL}
"""

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
    return "Not checked (demo)"

def check_social_media(phone_number):
    return "Not checked (demo)"

def get_number_type(parsed_number):
    try:
        ntype = phonenumbers.number_type(parsed_number)
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
    """Check public directories and social media for name associations and personal info."""
    try:
        formatted_num = phonenumbers.format_number(
            phonenumbers.parse(phone_number),
            phonenumbers.PhoneNumberFormat.E164
        ).replace('+', '')
        result = {}
        url = f"https://www.truepeoplesearch.com/results?phoneno={formatted_num}"
        response = requests.get(url, headers=HEADERS, timeout=REQUEST_TIMEOUT)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            name_tag = soup.find("div", class_="h4")
            address_tag = soup.find("div", class_="content-value")
            if name_tag:
                result["name"] = name_tag.get_text(strip=True)
            if address_tag:
                result["address"] = address_tag.get_text(strip=True)
            email_tag = soup.find("a", href=lambda x: isinstance(x, str) and x.startswith("mailto:"))
            if email_tag:
                result["email"] = email_tag.get_text(strip=True)
            if result:
                result["source"] = url
                return result
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
    lat = lon = None
    latlon_note = ''
    city_source = ''
    if city and city != 'Unknown':
        lat, lon = get_lat_lon_for_location(city, country)
        city_source = city
        if lat and lon:
            latlon_note = ''
        else:
            capital_map = {
                'France': 'Paris', 'Germany': 'Berlin', 'Italy': 'Rome', 'Spain': 'Madrid', 'United Kingdom': 'London',
                'Kosovo': 'Pristina', 'Austria': 'Vienna', 'Belgium': 'Brussels', 'Bulgaria': 'Sofia', 'Croatia': 'Zagreb',
                'Czech Republic': 'Prague', 'Denmark': 'Copenhagen', 'Estonia': 'Tallinn', 'Finland': 'Helsinki',
                'Greece': 'Athens', 'Hungary': 'Budapest', 'Iceland': 'Reykjavik', 'Ireland': 'Dublin', 'Latvia': 'Riga',
                'Liechtenstein': 'Vaduz', 'Lithuania': 'Vilnius', 'Luxembourg': 'Luxembourg', 'Malta': 'Valletta',
                'Netherlands': 'Amsterdam', 'Norway': 'Oslo', 'Poland': 'Warsaw', 'Portugal': 'Lisbon', 'Romania': 'Bucharest',
                'Slovakia': 'Bratislava', 'Slovenia': 'Ljubljana', 'Sweden': 'Stockholm', 'Switzerland': 'Bern',
                'North Macedonia': 'Skopje', 'Ukraine': 'Kyiv', 'Belarus': 'Minsk', 'Moldova': 'Chisinau', 'Albania': 'Tirana',
                'Bosnia and Herzegovina': 'Sarajevo', 'Montenegro': 'Podgorica', 'Serbia': 'Belgrade', 'Turkey': 'Ankara',
                'Georgia': 'Tbilisi', 'Azerbaijan': 'Baku', 'Armenia': 'Yerevan', 'Andorra': 'Andorra la Vella',
                'Monaco': 'Monaco', 'San Marino': 'San Marino', 'Vatican City': 'Vatican City'
            }
            capital = capital_map.get(country)
            if capital:
                lat, lon = get_lat_lon_for_location(capital, country)
                latlon_note = f" (Approximate, capital: {capital})"
                city_source = f"Capital: {capital}"
    else:
        capital_map = {
            'France': 'Paris', 'Germany': 'Berlin', 'Italy': 'Rome', 'Spain': 'Madrid', 'United Kingdom': 'London',
            'Kosovo': 'Pristina', 'Austria': 'Vienna', 'Belgium': 'Brussels', 'Bulgaria': 'Sofia', 'Croatia': 'Zagreb',
            'Czech Republic': 'Prague', 'Denmark': 'Copenhagen', 'Estonia': 'Tallinn', 'Finland': 'Helsinki',
            'Greece': 'Athens', 'Hungary': 'Budapest', 'Iceland': 'Reykjavik', 'Ireland': 'Dublin', 'Latvia': 'Riga',
            'Liechtenstein': 'Vaduz', 'Lithuania': 'Vilnius', 'Luxembourg': 'Luxembourg', 'Malta': 'Valletta',
            'Netherlands': 'Amsterdam', 'Norway': 'Oslo', 'Poland': 'Warsaw', 'Portugal': 'Lisbon', 'Romania': 'Bucharest',
            'Slovakia': 'Bratislava', 'Slovenia': 'Ljubljana', 'Sweden': 'Stockholm', 'Switzerland': 'Bern',
            'North Macedonia': 'Skopje', 'Ukraine': 'Kyiv', 'Belarus': 'Minsk', 'Moldova': 'Chisinau', 'Albania': 'Tirana',
            'Bosnia and Herzegovina': 'Sarajevo', 'Montenegro': 'Podgorica', 'Serbia': 'Belgrade', 'Turkey': 'Ankara',
            'Georgia': 'Tbilisi', 'Azerbaijan': 'Baku', 'Armenia': 'Yerevan', 'Andorra': 'Andorra la Vella',
            'Monaco': 'Monaco', 'San Marino': 'San Marino', 'Vatican City': 'Vatican City'
        }
        capital = capital_map.get(country)
        if capital:
            lat, lon = get_lat_lon_for_location(capital, country)
            latlon_note = f" (Approximate, capital: {capital})"
            city_source = f"Capital: {capital}"
        else:
            city_source = 'Unknown'
    result = {
        'number': formatted_num,
        'country_code': parsed_number.country_code,
        'national_number': parsed_number.national_number,
        'city': city if city and city != 'Unknown' else city_source,
        'city_source': city_source,
        'country': country,
        'latitude': lat,
        'longitude': lon,
        'latlon_note': latlon_note,
        'carrier': get_carrier_info(parsed_number),
        'location': city if city and city != 'Unknown' else city_source, 
        'timezone': get_timezone_info(parsed_number),
        'number_type': get_number_type(parsed_number),
        'valid': True,
        'lookup_time': time.time() - start_time,
        'parsed_number': parsed_number
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
    city_source = info.get('city_source', '')
    if city_source and city_source != city:
        print(f"• City/Region: {city} ({city_source})")
    else:
        print(f"• City/Region: {city if city else 'Unknown'}")
    country = info.get('country')
    print(f"• Country: {country if country else 'Unknown'}")
    if country_city_data:
        key = country if isinstance(country, str) and country not in (None, "Unknown") else ""
        cities = country_city_data.get(key)
        if not cities:
            cities = []
        if cities:
            print(f"• Example Cities: {', '.join(cities[:5])} ...")
        else:
            print("• No city data found for this country.")
    lat = info.get('latitude')
    lon = info.get('longitude')
    latlon_note = info.get('latlon_note', '')
    print(f"• Latitude: {lat if lat else 'Unknown'}{latlon_note}")
    print(f"• Longitude: {lon if lon else 'Unknown'}{latlon_note}")
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


def comprehensive_lookup_report(phone_number):
    """Comprehensive, structured report for a phone number lookup."""
    info = get_phone_info(phone_number)
    print(Fore.CYAN + "\n================= PHONE NUMBER ANALYSIS REPORT =================" + Style.RESET_ALL)
    print(Fore.BLUE + "\n--- Number Validation & Formatting ---" + Style.RESET_ALL)
    if not info.get('valid'):
        print(Fore.RED + f"❌  Number Validation: {info.get('error', 'Invalid number')}" + Style.RESET_ALL)
        print(Fore.CYAN + "==============================================================\n" + Style.RESET_ALL)
        return
    print(Fore.GREEN + f"✔️  Number Validation: Valid European number" + Style.RESET_ALL)
    print(f"• Formatted Number: {Fore.YELLOW}{info.get('number')}{Style.RESET_ALL}")
    print(f"• Country Code: {Fore.YELLOW}{info.get('country_code')}{Style.RESET_ALL}")
    print(f"• National Number: {Fore.YELLOW}{info.get('national_number')}{Style.RESET_ALL}")

    print(Fore.BLUE + "\n--- Carrier Information ---" + Style.RESET_ALL)
    print(f"• Carrier: {Fore.YELLOW}{info.get('carrier') if info.get('carrier') else 'Unknown'}{Style.RESET_ALL}")

    print(Fore.BLUE + "\n--- Geographical Location ---" + Style.RESET_ALL)
    city = info.get('city')
    city_source = info.get('city_source', '')
    lat = info.get('latitude')
    lon = info.get('longitude')
    latlon_note = info.get('latlon_note', '')
    if city_source and city_source != city:
        print(f"• City/Region: {Fore.YELLOW}{city}{Style.RESET_ALL} ({Fore.CYAN}{city_source}{Style.RESET_ALL})")
    else:
        print(f"• City/Region: {Fore.YELLOW}{city if city else 'Unknown'}{Style.RESET_ALL}")
    country = info.get('country')
    print(f"• Country: {Fore.YELLOW}{country if country else 'Unknown'}{Style.RESET_ALL}")
    print(f"• Latitude: {Fore.YELLOW}{lat if lat else 'Unknown'}{latlon_note}{Style.RESET_ALL}")
    print(f"• Longitude: {Fore.YELLOW}{lon if lon else 'Unknown'}{latlon_note}{Style.RESET_ALL}")

    print(Fore.BLUE + "\n--- Timezone Details ---" + Style.RESET_ALL)
    tz = info.get('timezone')
    if isinstance(tz, (list, tuple)):
        tz = ', '.join(tz)
    print(f"• Timezone(s): {Fore.YELLOW}{tz if tz else 'Unknown'}{Style.RESET_ALL}")

    print(Fore.BLUE + "\n--- Number Type ---" + Style.RESET_ALL)
    ntype = info.get('number_type')
    print(f"• Number Type: {Fore.YELLOW}{ntype if ntype else 'Unknown'}{Style.RESET_ALL}")

    print(Fore.BLUE + "\n--- Social Media Profiles ---" + Style.RESET_ALL)
    try:
        social_links = reverse_lookup_social_media(phone_number)
        if social_links:
            for profile in social_links:
                print(f"  - {Fore.GREEN}{profile['platform']}{Style.RESET_ALL}: {Fore.YELLOW}{profile['url']}{Style.RESET_ALL}")
        else:
            print(Fore.RED + "  No social media profiles found." + Style.RESET_ALL)
    except Exception as e:
        print(Fore.RED + f"  Error checking social media: {e}" + Style.RESET_ALL)

    print(Fore.BLUE + "\n--- Public Directory & Reverse Lookup ---" + Style.RESET_ALL)
    try:
        public_info = reverse_lookup_public_sources(phone_number)
        print(f"  Name: {Fore.YELLOW}{public_info.get('name', 'Not found')}{Style.RESET_ALL}")
        print(f"  Address: {Fore.YELLOW}{public_info.get('address', 'Not found')}{Style.RESET_ALL}")
        print(f"  Email: {Fore.YELLOW}{public_info.get('email', 'Not found')}{Style.RESET_ALL}")
        print(f"  Source: {Fore.YELLOW}{public_info.get('source', 'Not found')}{Style.RESET_ALL}")
        if public_info.get('error'):
            print(Fore.RED + f"  Error: {public_info['error']}" + Style.RESET_ALL)
    except Exception as e:
        print(Fore.RED + f"  Error checking public directories: {e}" + Style.RESET_ALL)

    print(Fore.BLUE + "\n--- Spam Database Check ---" + Style.RESET_ALL)
    try:
        spam_status = check_spam_databases(phone_number)
        print(f"  Spam Status: {Fore.YELLOW}{spam_status}{Style.RESET_ALL}")
    except Exception as e:
        print(Fore.RED + f"  Error checking spam databases: {e}" + Style.RESET_ALL)

    print(Fore.CYAN + "\n==============================================================\n" + Style.RESET_ALL)

def main():
    print(ASCII_ART)
    print(Fore.GREEN + Style.BRIGHT + "🌍 ULTIMATE EUROPEAN PHONE TRACKER" + Style.RESET_ALL)
    print(Fore.MAGENTA + "=" * 70 + Style.RESET_ALL)
    print(Fore.YELLOW + "1. Single Number Lookup" + Style.RESET_ALL)
    print(Fore.YELLOW + "2. Real-Time Caller ID Monitor" + Style.RESET_ALL)
    print(Fore.YELLOW + "3. Exit" + Style.RESET_ALL)
    
    choice = input(Fore.CYAN + "\nSelect mode (1-3): " + Style.RESET_ALL)
    
    if choice == '1':
        phone_number = input(Fore.CYAN + "\nEnter phone number (with country code): " + Style.RESET_ALL).strip()
        if phone_number:
            comprehensive_lookup_report(phone_number)
    elif choice == '2':
        if TWILIO_SID == "YOUR_TWILIO_SID":
            print(Fore.RED + "\n❌ Twilio not configured. Get SID/Token from twilio.com" + Style.RESET_ALL)
        else:
            monitor = start_live_caller_id_monitor()
            try:
                while True: time.sleep(1)
            except KeyboardInterrupt:
                print(Fore.YELLOW + "\nStopping monitor..." + Style.RESET_ALL)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n👋 Exiting...")
    except Exception as e:
        print(f"⚠️ Error: {e}")
