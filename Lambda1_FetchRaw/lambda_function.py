# app.py (no external packages)
import json, os, boto3
from urllib.request import urlopen
from datetime import datetime
import ssl

s3 = boto3.client('s3')
API_KEY = os.environ['OWM_API_KEY']
BUCKET = os.environ['BUCKET_NAME']
CITIES = os.environ.get('CITIES', 'Mumbai,London,New York').split(',')

# needed if Python runtime disallows HTTPS without certs
ssl._create_default_https_context = ssl._create_unverified_context

def fetch_json(url):
    with urlopen(url, timeout=10) as resp:
        return json.loads(resp.read().decode('utf-8'))

def lambda_handler(event, context):
    payload = []
    for city in CITIES:
        url = f"http://api.openweathermap.org/data/2.5/weather?q={city.strip()}&appid={API_KEY}&units=metric"
        try:
            data = fetch_json(url)
        except Exception as e:
            print(f"Failed for {city}: {e}")
            continue
        payload.append({
            "city": city.strip(),
            "temp_c": data["main"]["temp"],
            "humidity": data["main"]["humidity"],
            "weather": data["weather"][0]["description"],
            "timestamp": datetime.utcnow().isoformat()
        })

    key = f"weather/raw/weather_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.json"
    s3.put_object(Bucket=BUCKET, Key=key, Body=json.dumps(payload).encode('utf-8'))
    return {"status": "OK", "s3_key": key}
