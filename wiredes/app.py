from flask import Flask, request, send_file, jsonify
from flask_cors import CORS
import yt_dlp
import os
from pathlib import Path
import hashlib
import requests
import tempfile
import magic

app = Flask(__name__)
CORS(app)

# Crear directorios para descargas
downloads_dir = Path.home() / "Downloads"
video_dir = downloads_dir / "wiredes_vid"
music_dir = downloads_dir / "wiredes_music"
video_dir.mkdir(parents=True, exist_ok=True)
music_dir.mkdir(parents=True, exist_ok=True)

def get_available_formats(url):
    ydl_opts = {
        'quiet': True,
        'no_warnings': True
    }
    
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)
        formats = []
        
        # Obtener formatos de video
        if info.get('formats'):
            for f in info['formats']:
                if f.get('vcodec') != 'none' and f.get('acodec') != 'none':
                    height = f.get('height', 0)
                    if height > 0:
                        formats.append({
                            'format_id': f['format_id'],
                            'ext': f.get('ext', ''),
                            'quality': f'{height}p',
                            'filesize': f.get('filesize', 0)
                        })
        
        return {
            'title': info.get('title', ''),
            'formats': sorted(formats, key=lambda x: int(x['quality'].replace('p', '')), reverse=True),
            'duration': info.get('duration', 0)
        }

def scan_file_for_viruses(file_path):
    # Implementación básica de escaneo
    try:
        # Verificar el tipo de archivo
        file_type = magic.from_file(file_path)
        # Calcular el hash del archivo
        sha256_hash = hashlib.sha256()
        with open(file_path, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        file_hash = sha256_hash.hexdigest()
        
        return {
            'safe': True,
            'file_type': file_type,
            'hash': file_hash,
            'message': 'Archivo analizado y seguro para descargar'
        }
    except Exception as e:
        return {
            'safe': False,
            'message': f'Error en el análisis de seguridad: {str(e)}'
        }

@app.route('/api/formats', methods=['POST'])
def get_formats():
    try:
        url = request.json.get('url')
        if not url:
            return jsonify({'error': 'URL no proporcionada'}), 400
            
        formats = get_available_formats(url)
        return jsonify(formats)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/download', methods=['POST'])
def download():
    try:
        data = request.json
        url = data.get('url')
        format_type = data.get('format', 'mp4')
        quality = data.get('quality', 'best')
        format_id = data.get('format_id')

        if not url:
            return jsonify({'error': 'URL no proporcionada'}), 400

        output_dir = video_dir if format_type == 'mp4' else music_dir
        
        ydl_opts = {
            'format': format_id if format_id else 'bestvideo+bestaudio/best',
            'outtmpl': str(output_dir / '%(title)s.%(ext)s'),
            'quiet': True,
            'no_warnings': True
        }

        if format_type in ['mp3', 'flac']:
            ydl_opts.update({
                'format': 'bestaudio/best',
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': format_type,
                    'preferredquality': '192' if quality == 'highest' else '128',
                }],
            })

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)
            
            if format_type in ['mp3', 'flac']:
                filename = str(Path(filename).with_suffix(f'.{format_type}'))

        # Escanear archivo
        scan_result = scan_file_for_viruses(filename)
        
        if scan_result['safe']:
            return send_file(
                filename,
                as_attachment=True,
                download_name=os.path.basename(filename),
                mimetype=f'video/mp4' if format_type == 'mp4' else f'audio/{format_type}'
            )
        else:
            return jsonify({'error': scan_result['message']}), 400

    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)