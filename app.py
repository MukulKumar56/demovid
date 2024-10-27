from flask import Flask, render_template, request, redirect, flash
import yt_dlp

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Needed for flashing messages

@app.route('/', methods=['GET', 'POST'])
def index():
    formats = None
    url = None
    if request.method == 'POST':
        url = request.form['url']
        
        # Get available formats
        ydl_opts = {
            'format': 'bestaudio/best',
            'quiet': True,
            'noplaylist': True,
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            try:
                info_dict = ydl.extract_info(url, download=False)
                formats = [f for f in info_dict.get('formats', []) if f['ext'] in ['mp3', 'mp4', 'opus']]
                print("Available formats:", formats)  # Debugging line
            except Exception as e:
                flash(f'Error extracting video info: {e}')
                formats = []

    return render_template('index.html', formats=formats, url=url)

@app.route('/get_video', methods=['POST'])
def get_video():
    url = request.form['url']
    format_id = request.form['format_id']

    # Prepare the options for extracting info
    ydl_opts = {
        'format': format_id,
        'quiet': True,
        'noplaylist': True,
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        try:
            # Extract video information to get the download link
            info_dict = ydl.extract_info(url, download=False)
            download_url = None

            # Find the direct download link for the selected format
            for format in info_dict.get('formats', []):
                if format['format_id'] == format_id:
                    download_url = format['url']
                    break

            if download_url:
                return redirect(download_url)  # Redirect user to the download link
            else:
                flash('Download link not found.')
                return redirect('/')
        except Exception as e:
            flash(f'Error processing video: {e}')
            return redirect('/')
if __name__ == "__main__":
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)), debug=True)
