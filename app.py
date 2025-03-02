import os
import dotenv
from flask import Flask, request, jsonify, render_template
from werkzeug.utils import secure_filename
import google.generativeai as genai
from flask_cors import CORS

# Load environment variables
dotenv.load_dotenv()
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')

# Initialize Flask app
app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB limit

# Configure Google Gemini
genai.configure(api_key=GEMINI_API_KEY)

# Home page
@app.route('/')
def index():
    return render_template('index.html')

# Handle file upload and send to GPT model
@app.route('/upload', methods=['POST'])
def upload_file():
    print("📩 Received file upload request")

    if 'file' not in request.files:
        print("❌ No file found in request!")
        return jsonify({'error': 'No file uploaded'}), 400

    file = request.files['file']
    if file.filename == '':
        print("❌ No selected file!")
        return jsonify({'error': 'No selected file'}), 400

    filename = secure_filename(file.filename)
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)

    try:
        file.save(file_path)
        print(f"✅ File uploaded successfully: {file_path}")
        print(f"📏 File size: {os.path.getsize(file_path)} bytes")
    except Exception as e:
        print(f"❌ Error saving file: {e}")
        return jsonify({'error': 'Failed to save file'}), 500

    # Confirm file exists before sending it to Gemini
    if not os.path.exists(file_path):
        print("❌ File does not exist after saving!")
        return jsonify({'error': 'File save failed'}), 500

    # Send the file to Gemini AI for extraction
    extracted_data = extract_data_with_gemini(file_path, filename)
    
    print("📤 Extracted Data Sent to Client:", extracted_data)
    return jsonify({'extracted_data': extracted_data})


# Function to extract data using Google Gemini AI
# def extract_data_with_gemini(file_path, filename):
#     model = genai.GenerativeModel('gemini-1.5-pro-latest')  # ✅ Ensure correct model

#     print("🚀 Starting Gemini Processing")
#     print(f"📂 File Path: {file_path}")

#     try:
#         # Confirm the file exists
#         if not os.path.exists(file_path):
#             print("❌ File not found for Gemini processing!")
#             return {'error': 'File not found'}

#         print("✅ File exists, proceeding to read...")

#         # Read the file
#         with open(file_path, "rb") as file:
#             file_data = file.read()
#             print(f"📖 Reading file: {file_path}, Bytes read: {len(file_data)}")

#             if len(file_data) == 0:
#                 print("❌ File is empty!")
#                 return {'error': 'Empty file'}

#         print("📡 Sending file to Gemini API...")

#         # Set MIME type dynamically
#         file_extension = filename.split('.')[-1].lower()
#         if file_extension in ['pdf']:
#             mime_type = "application/pdf"
#         elif file_extension in ['png', 'jpg', 'jpeg', 'webp']:
#             mime_type = "image/png"
#         else:
#             print("❌ Unsupported file format!")
#             return {'error': 'Unsupported file format'}

#         print(f"📌 Using MIME Type: {mime_type}")

#         # Send the file directly to Gemini API
#         response = model.generate_content(
#             [
#                 "Extract structured key-value pairs from this document, including labels and values. Provide output in JSON format.",
#                 {"mime_type": mime_type, "data": file_data}  # ✅ Correct format
#             ]
#         )

#         print("🤖 Gemini API Response:", response)  # ✅ Debugging output

#         if hasattr(response, "text"):
#             return response.text  # ✅ Return structured JSON
#         else:
#             print("❌ Gemini API did not return a valid response.")
#             return {'error': 'Invalid response from AI model'}

#     except Exception as e:
#         print(f"❌ Error extracting data from Gemini API: {e}")
#         return {'error': f'Failed to process file with AI model: {str(e)}'}

import json  # Import JSON module

import json
import re
import google.generativeai as genai
import os

def extract_data_with_gemini(file_path, filename):
    model = genai.GenerativeModel('gemini-1.5-pro-latest')  # ✅ Ensure correct model

    print("🚀 Starting Gemini Processing")
    print(f"📂 File Path: {file_path}")

    try:
        # Confirm the file exists
        if not os.path.exists(file_path):
            print("❌ File not found for Gemini processing!")
            return {'error': 'File not found'}

        print("✅ File exists, proceeding to read...")

        # Read the file
        with open(file_path, "rb") as file:
            file_data = file.read()
            print(f"📖 Reading file: {file_path}, Bytes read: {len(file_data)}")

            if len(file_data) == 0:
                print("❌ File is empty!")
                return {'error': 'Empty file'}

        print("📡 Sending file to Gemini API...")

        # Set MIME type dynamically
        file_extension = filename.split('.')[-1].lower()
        if file_extension == "pdf":
            mime_type = "application/pdf"
        elif file_extension in ["png", "jpg", "jpeg", "webp"]:
            mime_type = "image/png"
        else:
            print("❌ Unsupported file format!")
            return {'error': 'Unsupported file format'}

        print(f"📌 Using MIME Type: {mime_type}")

        # Send file to Gemini API
        response = model.generate_content(
            [
                "Extract structured key-value pairs from this document. "
                "Ensure the response is a valid JSON object without any extra explanations. "
                "Return only JSON, without Markdown formatting or extra text.",
                {"mime_type": mime_type, "data": file_data}  # ✅ Correct format
            ]
        )

        print("🤖 Raw Gemini API Response:", response)

        # Extract response text
        if hasattr(response, "text"):
            response_text = response.text.strip()
            print("🔍 Extracted Response:", response_text)

            # Remove Markdown code block formatting if present (```json ... ```)
            cleaned_text = re.sub(r"```json\n(.*?)\n```", r"\1", response_text, flags=re.DOTALL).strip()

            # Try parsing the cleaned response as JSON
            try:
                extracted_json = json.loads(cleaned_text)
                return extracted_json
            except json.JSONDecodeError:
                print("❌ Failed to parse JSON. Response received:", cleaned_text)
                return {'error': 'Invalid JSON format from AI model'}
        else:
            print("❌ Gemini API did not return a valid response.")
            return {'error': 'Invalid response from AI model'}

    except Exception as e:
        print(f"❌ Error extracting data from Gemini API: {e}")
        return {'error': f'Failed to process file with AI model: {str(e)}'}


# Run the app
if __name__ == '__main__':
    if not os.path.exists('uploads'):
        os.makedirs('uploads')
    app.run(host='0.0.0.0', port=8000, debug=True)
