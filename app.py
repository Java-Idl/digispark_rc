from flask import Flask, send_from_directory, abort
import os

app = Flask(__name__)
DOWNLOAD_DIR = 'downloads'  # Folder for your files

@app.route('/download/<filename>')
def download_file(filename):
    if not os.path.exists(os.path.join(DOWNLOAD_DIR, filename)):
        abort(404)
    return send_from_directory(DOWNLOAD_DIR, filename, as_attachment=True)

if __name__ == '__main__':
    os.makedirs(DOWNLOAD_DIR, exist_ok=True)
    app.run(host='0.0.0.0', port=5000, debug=True)
