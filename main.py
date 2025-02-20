import os
from fastapi import FastAPI, UploadFile, File
from fastapi.responses import JSONResponse
from dotenv import load_dotenv
import openai
import PyPDF2
from openai import OpenAIError, AuthenticationError, RateLimitError

# Load environment variables from .env file
load_dotenv()

# Ensure OpenAI API key is loaded
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise ValueError("Missing OpenAI API key. Please set OPENAI_API_KEY in the .env file.")

# Initialize OpenAI client
client = openai.OpenAI(api_key=api_key)

app = FastAPI()

@app.get("/")
def home():
    return {"message": "Welcome to the Legal Analysis API. Use /docs to test the API."}

def extract_text_from_pdf(pdf_file):
    reader = PyPDF2.PdfReader(pdf_file.file)
    extracted_text = []

    for page in reader.pages:
        page_text = page.extract_text()
        if page_text:
            extracted_text.append(page_text.strip())

    return "\n".join(extracted_text) if extracted_text else "No text found in the document."

MAX_TOKENS = 4000  # Adjust based on OpenAI model limits

def analyze_legal_text(text):
    # Truncate text if too long
    if len(text) > MAX_TOKENS:
        text = text[:MAX_TOKENS] + " [Text truncated due to token limits.]"

    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are an AI that extracts key clauses, detects risks, and simplifies legal language from contracts."},
            {"role": "user", "content": f"Extract key clauses, detect risks, and simplify this legal text:\n{text}"}
        ]
    )
    return response.choices[0].message["content"]

@app.post("/analyze_legal_document/")
async def analyze_legal_document(file: UploadFile = File(...)):
    try:
        text = extract_text_from_pdf(file)
        if text == "No text found in the document.":
            return JSONResponse(content={"error": "The uploaded PDF has no readable text."}, status_code=400)
        
        analysis = analyze_legal_text(text)
        return {"analysis": analysis}

    except AuthenticationError:
        return JSONResponse(content={"error": "Invalid OpenAI API key."}, status_code=401)

    except RateLimitError:
        return JSONResponse(content={"error": "OpenAI API rate limit exceeded. Please try again later."}, status_code=429)

    except OpenAIError as api_error:
        return JSONResponse(content={"error": f"OpenAI API error: {str(api_error)}"}, status_code=500)

    except Exception as e:
        return JSONResponse(content={"error": f"Internal server error: {str(e)}"}, status_code=500)
