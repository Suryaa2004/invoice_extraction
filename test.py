import google.generativeai as genai
import os
from dotenv import load_dotenv

# Load API Key
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Configure Gemini API
genai.configure(api_key=GEMINI_API_KEY)

try:
    model = genai.GenerativeModel('gemini-1.5-pro-latest')  # Ensure correct model
    response = model.generate_content(["Hello! Can you process this request?"])
    print(response.text)  # Should return a valid response
except Exception as e:
    print(f"Error connecting to Gemini API: {e}")

# import google.generativeai as genai
# import os
# from dotenv import load_dotenv

# # Load API Key
# load_dotenv()
# GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# # Configure Gemini API
# genai.configure(api_key=GEMINI_API_KEY)

# try:
#     models = genai.list_models()
#     print("Available Models in Your API Version:")
#     for model in models:
#         print(model.name)
# except Exception as e:
#     print(f"Error fetching models: {e}")
