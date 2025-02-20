import os
from fastapi import FastAPI, UploadFile, File
from dotenv import load_dotenv
import openai
import PyPDF2

# Load environment variables from .env file
load_dotenv()

# Retrieve the API key from environment variables
openai.api_key = os.getenv("OPENAI_API_KEY")

app = FastAPI()

@app.get("/")
def home():
    return {"message": "Welcome to the Legal Analysis API. Use /docs to test the API."}

def extract_text_from_pdf(pdf_file):
    reader = PyPDF2.PdfReader(pdf_file.file)
    text = "".join([page.extract_text() for page in reader.pages if page.extract_text()])
    return text

def analyze_legal_text(text):
    response = openai.ChatCompletion.create(
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
        analysis = analyze_legal_text(text)
        return {"analysis": analysis}
    except Exception as e:
        return {"error": str(e)}
