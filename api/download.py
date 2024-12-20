from http.server import BaseHTTPRequestHandler
import json
from pytube import YouTube
import os

class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        data = json.loads(post_data.decode('utf-8'))

        url = data.get('url')
        format = data.get('format')
        quality = data.get('quality')

        try:
            yt = YouTube(url)
            if format == 'mp4':
                if quality == 'high':
                    stream = yt.streams.filter(progressive=True, file_extension='mp4').order_by('resolution').desc().first()
                elif quality == 'medium':
                    stream = yt.streams.filter(progressive=True, file_extension='mp4').order_by('resolution').desc().last()
                else:
                    stream = yt.streams.filter(progressive=True, file_extension='mp4').order_by('resolution').asc().first()
            else:  # mp3
                stream = yt.streams.filter(only_audio=True).first()

            output_path = f"/tmp/{yt.title}.{format}"
            stream.download(output_path=os.path.dirname(output_path), filename=os.path.basename(output_path))

            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            response = {
                'success': True,
                'downloadUrl': f"/tmp/{yt.title}.{format}"
            }
            self.wfile.write(json.dumps(response).encode())
        except Exception as e:
            self.send_response(400)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            response = {
                'success': False,
                'error': str(e)
            }
            self.wfile.write(json.dumps(response).encode())

        return