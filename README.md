# OCR Image to Text Application

A web application that uses Google Drive OCR to extract text from images. Built with Flask and Google Drive API.

## Features

- Multiple image upload support
- Drag and drop interface
- Real-time OCR processing
- Text file download
- Persistent authentication
- Modern UI with Tailwind CSS

## Prerequisites

- Python 3.8 or higher
- Google Cloud Platform account
- Google Drive API enabled
- OAuth 2.0 credentials

## Setup

1. Clone the repository:
```bash
git clone https://github.com/prerakshah3/OCR_app.git
cd OCR_app
```

2. Create and activate virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up Google credentials:
   - Go to Google Cloud Console
   - Enable Google Drive API
   - Create OAuth 2.0 credentials
   - Download credentials JSON file
   - Place it in `credentials/client_secret.json`

5. Create required directories:
```bash
mkdir -p credentials uploads static
```

## Running Locally

1. Start the Flask application:
```bash
python app.py
```

2. Visit `http://localhost:5000` in your browser

## Deployment

### Render.com

1. Fork this repository
2. Create a new Web Service on Render
3. Connect your GitHub repository
4. Configure environment variables:
   - FLASK_ENV=production
   - SECRET_KEY=your-secret-key
   - UPLOAD_FOLDER=uploads
   - MAX_CONTENT_LENGTH=16777216
   - GOOGLE_CREDENTIALS_PATH=credentials/client_secret.json
   - TOKEN_PATH=token.pickle

### PythonAnywhere

1. Create a PythonAnywhere account
2. Upload your code
3. Configure WSGI file
4. Set up virtual environment
5. Configure environment variables

## Project Structure

```
OCR_app/
├── app.py              # Flask application
├── ocr.py             # OCR processing logic
├── requirements.txt    # Python dependencies
├── render.yaml        # Render deployment config
├── wsgi.py           # WSGI configuration
├── credentials/      # Google credentials
├── static/          # Static files
├── templates/       # HTML templates
└── uploads/         # Temporary file storage
```

## Security Notes

- Never commit credentials or tokens
- Keep your Google API credentials secure
- Use environment variables for sensitive data
- Regularly rotate your secret keys

## License

MIT License

## Author

Prerak Shah 