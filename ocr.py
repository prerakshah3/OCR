from __future__ import print_function
import os
import io
import sys
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload, MediaIoBaseDownload
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import pickle
import json
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/drive']

def authenticate():
    creds = None
    token_path = os.getenv('TOKEN_PATH', 'token.pickle')
    credentials_path = os.getenv('GOOGLE_CREDENTIALS_PATH')
    
    if not credentials_path:
        raise ValueError("GOOGLE_CREDENTIALS_PATH environment variable is not set")
    
    # Load existing credentials if available
    if os.path.exists(token_path):
        try:
            with open(token_path, 'rb') as token:
                creds = pickle.load(token)
        except Exception as e:
            print(f"Error loading credentials: {e}")
            creds = None
    
    # If credentials don't exist or are invalid, get new ones
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            try:
                creds.refresh(Request())
            except Exception as e:
                print(f"Error refreshing credentials: {e}")
                creds = None
        
        # If still no valid credentials, get new ones
        if not creds:
            print("Please authenticate with your Google account.")
            
            # Check if credentials_path is a file path or JSON string
            if os.path.exists(credentials_path):
                # It's a file path
                flow = InstalledAppFlow.from_client_secrets_file(credentials_path, SCOPES)
            else:
                # It's a JSON string from environment variable
                try:
                    client_config = json.loads(credentials_path)
                    flow = InstalledAppFlow.from_client_config(client_config, SCOPES)
                except json.JSONDecodeError:
                    raise ValueError("Invalid JSON in GOOGLE_CREDENTIALS_PATH")
            
            creds = flow.run_local_server(port=0)
            
            # Save the credentials for future use
            try:
                with open(token_path, 'wb') as token:
                    pickle.dump(creds, token)
                print("Credentials saved successfully.")
            except Exception as e:
                print(f"Error saving credentials: {e}")
    
    return creds

def ocr_image(file_path, creds):
    service = build('drive', 'v3', credentials=creds)
    file_metadata = {
        'name': os.path.basename(file_path),
        'mimeType': 'application/vnd.google-apps.document'
    }
    media = MediaFileUpload(file_path, mimetype='image/jpeg')  # Adjust mimetype if needed
    print(f"Uploading and processing {file_path}...")
    file = service.files().create(
        body=file_metadata,
        media_body=media,
        fields='id'
    ).execute()
    file_id = file.get('id')

    # Export the Google Doc as plain text
    request = service.files().export_media(fileId=file_id, mimeType='text/plain')
    fh = io.BytesIO()
    downloader = MediaIoBaseDownload(fh, request)
    done = False
    while not done:
        status, done = downloader.next_chunk()
    text = fh.getvalue().decode('utf-8')

    # Clean up the uploaded file
    service.files().delete(fileId=file_id).execute()

    return text

def main():
    creds = authenticate()
    image_dir = r'D:\study\ocr\tp'
    output_file = 'tp.txt'

    with open(output_file, 'w', encoding='utf-8') as outfile:
        for filename in os.listdir(image_dir):
            if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.tif', '.tiff')):
                image_path = os.path.join(image_dir, filename)
                try:
                    text = ocr_image(image_path, creds)
                    outfile.write(f"--- Text from {filename} ---\n")
                    outfile.write(text)
                    outfile.write("\n\n")
                    print(f"Processed {filename}.")
                except Exception as e:
                    print(f"Failed to process {filename}: {e}")

    print("Extraction complete! The extracted text is saved in 'tp.txt'.")

if __name__ == '__main__':
    main()
