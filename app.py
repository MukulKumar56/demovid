# from flask import Flask, render_template, request, redirect, flash
# import yt_dlp

# app = Flask(__name__)
# app.secret_key = 'your_secret_key'  # Needed for flashing messages

# @app.route('/', methods=['GET', 'POST'])
# def index():
#     formats, url = None, None
#     if request.method == 'POST':
#         url = request.form['url']
#         ydl_opts = {'format': 'bestaudio/best', 'quiet': True, 'noplaylist': True}

#         with yt_dlp.YoutubeDL(ydl_opts) as ydl:
#             try:
#                 info_dict = ydl.extract_info(url, download=False)
#                 formats = [f for f in info_dict.get('formats', []) 
#                            if f['ext'] in ['mp3', 'mp4'] and 'm3u8' not in f['url']]
#             except Exception as e:
#                 flash(f'Error extracting video info: {e}')

#     return render_template('index.html', formats=formats, url=url)

# @app.route('/get_video', methods=['POST'])
# def get_video():
#     url, format_id = request.form['url'], request.form['format_id']
#     ydl_opts = {'format': format_id, 'quiet': True, 'noplaylist': True, 'outtmpl': '%(title)s.%(ext)s'}

#     with yt_dlp.YoutubeDL(ydl_opts) as ydl:
#         try:
#             info_dict = ydl.extract_info(url, download=True)
#             download_url = next((f['url'] for f in info_dict.get('formats', []) if f['format_id'] == format_id), None)

#             if download_url:
#                 return redirect(download_url)
#             else:
#                 flash('Download link not found.')
#         except Exception as e:
#             flash(f'Error processing video: {e}')

#     return redirect('/')

# if __name__ == '__main__':
#     app.run(debug=True)

import os
from flask import Flask, render_template, request, redirect, flash, session
import yt_dlp

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Needed for flashing messages

# OAuth token storage
OAUTH_TOKEN = None

@app.route('/', methods=['GET', 'POST'])
def index():
    formats, url = None, None
    if request.method == 'POST':
        url = request.form['url']
        ydl_opts = {
            'format': 'bestaudio/best',
            'quiet': True,
            'noplaylist': True,
            'extract_flat': True,  # This allows you to get the download link without downloading
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }]
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            try:
                info_dict = ydl.extract_info(url, download=False)
                formats = [f for f in info_dict.get('formats', [])
                           if f['ext'] in ['mp3', 'mp4'] and 'm3u8' not in f['url']]
            except Exception as e:
                flash(f'Error extracting video info: {e}')

    return render_template('index.html', formats=formats, url=url)

@app.route('/authorize')
def authorize():
    global OAUTH_TOKEN
    # Start the OAuth flow
    os.system('yt-dlp --username=oauth --password=""')  # This will prompt for authorization in the terminal
    # After successful authorization, you should have the token saved in the cache
    # You can fetch it or set it to a global variable here if needed
    # For simplicity, we assume the token is saved by yt-dlp
    OAUTH_TOKEN = 'your_oauth_token'  # Replace with actual token retrieval logic
    flash('Authorization successful! You can now download videos.')
    return redirect('/')

@app.route('/get_video', methods=['POST'])
def get_video():
    url, format_id = request.form['url'], request.form['format_id']
    ydl_opts = {
        'format': format_id,
        'quiet': True,
        'noplaylist': True,
        'outtmpl': '%(title)s.%(ext)s',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'username': 'oauth',
        'password': ''  # Leave this empty
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        try:
            info_dict = ydl.extract_info(url, download=True)
            download_url = next((f['url'] for f in info_dict.get('formats', []) if f['format_id'] == format_id), None)

            if download_url:
                flash('Video downloaded successfully.')
                return redirect(download_url)
            else:
                flash('Download link not found.')
        except Exception as e:
            flash(f'Error processing video: {e}')

    return redirect('/')



if __name__ == "__main__":
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))
