import os 
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import yt_dlp

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

@app.route('/get_video_info', methods=['POST'])
def get_video_info():
    url = request.form.get('url')
    ydl_opts = {
        'format': 'bestaudio/best',
        'quiet': True,
        'noplaylist': True,
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        try:
            info_dict = ydl.extract_info(url, download=False)
            title = info_dict.get('title')
            thumbnail = info_dict.get('thumbnail')
            
            # Filter formats to exclude .m3u8 and keep only mp3 and mp4
            formats = [
                f for f in info_dict.get('formats', [])
                if f.get('url') and f['ext'] in ['mp3', 'mp4'] and not f['url'].endswith('.m3u8')
            ]
            
            return jsonify({'title': title, 'thumbnail': thumbnail, 'formats': formats})
        except Exception as e:
            return jsonify({'error': str(e)}), 400

@app.route('/')
def index():
    return render_template('index.html')
if __name__ == "__main__":
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))


