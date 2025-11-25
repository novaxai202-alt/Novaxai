from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
import io
import tempfile
import os

class GoogleDriveService:
    def __init__(self, access_token):
        self.credentials = Credentials(token=access_token)
        self.service = build('drive', 'v3', credentials=self.credentials)
    
    async def download_file_content(self, file_id):
        """Download file content temporarily for AI analysis"""
        try:
            # Get file metadata
            file_metadata = self.service.files().get(fileId=file_id).execute()
            
            # Download file content
            request = self.service.files().get_media(fileId=file_id)
            file_content = io.BytesIO()
            downloader = MediaIoBaseDownload(file_content, request)
            
            done = False
            while done is False:
                status, done = downloader.next_chunk()
            
            file_content.seek(0)
            content_bytes = file_content.read()
            
            # Extract text based on file type
            mime_type = file_metadata.get('mimeType', '')
            
            if mime_type.startswith('text/') or file_metadata['name'].endswith(('.txt', '.md', '.py', '.js', '.html')):
                return {
                    'content': content_bytes.decode('utf-8')[:10000],
                    'type': 'text',
                    'name': file_metadata['name']
                }
            elif mime_type.startswith('image/'):
                import base64
                return {
                    'content': f"[Image: {file_metadata['name']}]",
                    'base64': base64.b64encode(content_bytes).decode('utf-8')[:50000],
                    'type': 'image',
                    'name': file_metadata['name']
                }
            else:
                return {
                    'content': f"[File: {file_metadata['name']} - {len(content_bytes)} bytes]",
                    'type': 'binary',
                    'name': file_metadata['name']
                }
                
        except Exception as e:
            return {
                'content': f"[Error reading file: {str(e)}]",
                'type': 'error',
                'name': 'unknown'
            }