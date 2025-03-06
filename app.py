from flask import Flask, request, jsonify
import requests
import os
import gzip
import json
import re

app = Flask(__name__)

# Enable compression for all responses (Flask-Compress is recommended for more advanced compression)
@app.after_request
def after_request(response):
    if response.mimetype == 'application/json':
        response.headers['Content-Encoding'] = 'gzip'
        response.set_data(gzip.compress(response.get_data()))
    return response

# Path to the cache file
cache_file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'cache.json.gz')

# Helper function: Load cache from gzip file
def load_cache():
    if not os.path.exists(cache_file_path):
        return {}
    with gzip.open(cache_file_path, 'rt', encoding='utf-8') as f:
        return json.load(f)

# Helper function: Save cache to gzip file with compression level 9
def save_cache(cache):
    with gzip.open(cache_file_path, 'wt', encoding='utf-8', compresslevel=9) as f:
        json.dump(cache, f)

# API keys and rotation logic
api_keys = [
    'db751b0a05msh95365b14dcde368p12dbd9jsn440b1b8ae7cb',
    '0649dc83c2msh88ac949854b30c2p1f2fe8jsn871589450eb3',
    '0e88d5d689msh145371e9bc7d2d8p17eebejsn8ff825d6291f',
    'ea7a66dfaemshecacaabadeedebbp17b247jsn7966d78a3945',
]
current_key_index = 0

def get_next_api_key():
    global current_key_index
    current_key_index = (current_key_index + 1) % len(api_keys)
    return api_keys[current_key_index]

def youtube_parser(url):
    url = url.replace(r'\?si=.*', '')
    regExp = r'^.*((youtu.be\/)|(v\/)|(\/u\/\w\/)|(embed\/)|(watch\?))\??v?=?([^#&?]*).*'
    match = re.match(regExp, url)
    return match.group(7) if match and len(match.group(7)) == 11 else False

# Download route
@app.route('/dl', methods=['GET'])
def download():
    url = request.args.get('url')

    if not url or not isinstance(url, str):
        return jsonify({'error': 'Missing YouTube URL'}), 400

    video_id = youtube_parser(url)
    if not video_id:
        return jsonify({'error': 'Invalid YouTube URL'}), 400

    # Load cache
    cache = load_cache()

    # Check cache
    if video_id in cache:
        return jsonify({'link': cache[video_id]})

    retries = 3
    success = False
    mp3_link = ''

    while retries > 0 and not success:
        api_key = get_next_api_key()
        headers = {
            'x-rapidapi-key': api_key,
            'x-rapidapi-host': 'youtube-mp36.p.rapidapi.com',
        }
        params = {'id': video_id}

        try:
            response = requests.get(
                'https://youtube-mp36.p.rapidapi.com/dl',
                headers=headers,
                params=params,
                timeout=5
            )
            response.raise_for_status() # Raise HTTPError for bad responses (4xx or 5xx)
            data = response.json()
            if data and data.get('link'):
                success = True
                mp3_link = data['link']

                # Save to cache
                cache[video_id] = mp3_link
                save_cache(cache)
                break
            else:
                raise ValueError('No MP3 link found in response.')
        except (requests.exceptions.RequestException, ValueError) as e:
            print(f"Attempt failed with API key: {api_key} - {e}")
            retries -= 1

    if success:
        return jsonify({'link': mp3_link})
    else:
        return jsonify({'error': 'Failed to fetch MP3 after multiple attempts.'}), 500

# Handle undefined routes
@app.errorhandler(404)
def not_found(error):
    return "Not Found", 404

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3000, debug=True)
