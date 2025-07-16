# 📞 Ultimate European Phone Tracker

A powerful Python-based tool to perform detailed lookups of **European phone numbers**, retrieve information such as **carrier**, **timezone**, **region**, **type**, **latitude/longitude**, and even simulate **real-time caller ID** using Twilio.

> 🔍 Designed for telecom researchers, fraud prevention analysts, and OSINT enthusiasts focused on European territories.

---

## ✅ Features

- 🔎 Validates and parses European numbers using `phonenumbers`
- 🌍 Determines country, city/region, and type (mobile/fixed line/etc.)
- 📡 Retrieves carrier and timezone data
- 🗺️ Finds geolocation coordinates via OpenStreetMap
- 🌐 Performs basic public directory reverse lookup (demo)
- 👤 Links to social media search for cross-reference (e.g., Facebook, LinkedIn)
- 📞 Optional: Live caller ID monitoring using Twilio API
- 📁 Built-in country & city JSON dataset
- 🚀 CLI-based, lightweight, fast, and extendable

---

## 🧰 Requirements

- Python 3.7+
- Required Python packages:
  ```bash
  pip install -r requirements.txt
requirements.txt (example)

phonenumbers
requests
beautifulsoup4
twilio
pytz
dnspython
python-whois

## 🚀 How to Use
🔹 Mode 1: Lookup a Single Number

**python phoneinfo.py**
Choose 1 to enter a number like +4915123456789

View full metadata, including:

**Carrier**

**Timezone(s)**

**Country & city**

**Number type (mobile/fixed, VoIP, etc.)**

**Geolocation (lat/lon)**

Example cities from country JSON

## 🔹 Mode 2: Real-Time Caller ID Monitor (via Twilio)
# 🛑 Twilio credentials required.

Register at Twilio

Replace TWILIO_SID and TWILIO_TOKEN at the top of the script

Run the script and choose 2

Live caller information will be displayed when calls are detected

📦 File Structure

├── phoneinfo.py                # Main script
├── europe_countries_cities.json  # Country -> Cities mapping (optional)
├── requirements.txt            # Dependencies
└── README.md                   # This file
🌍 Supported Regions
Validates phone numbers from all EU and European countries, including:

🇩🇪 Germany

🇫🇷 France

🇬🇧 UK

🇪🇸 Spain

🇮🇹 Italy

🇸🇪 Sweden

🇵🇱 Poland

🇳🇴 Norway

🇧🇪 Belgium

...and more (see COUNTRY_CODE_MAP)

🔐 Disclaimer
This tool is intended for educational and lawful investigative purposes only.

Do not use it for harassment, spamming, or violating data privacy laws (e.g., GDPR).

It uses only publicly available APIs and metadata.

Twilio Caller ID is opt-in and requires explicit integration.

🧠 Author
Threadlinee – GitHub

If you find this project helpful, feel free to star ⭐ the repo or contribute!

📄 License
This project is licensed under the MIT License.

