from fastapi import FastAPI, UploadFile, File
import openai
import PyPDF2

app = FastAPI()

# OpenAI API Key (Replace with your actual key)
OPENAI_API_KEY = "your_openai_api_key"
openai.api_key = OPENAI_API_KEY

# Function to extract text from PDF
def extract_text_from_pdf(pdf_file):
    reader = PyPDF2.PdfReader(pdf_file.file)
    text = "".join([page.extract_text() for page in reader.pages if page.extract_text()])
    return text

# Function to analyze legal document using OpenAI
def analyze_legal_text(text):
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are an AI that extracts key clauses, detects risks, and simplifies legal language from contracts."},
            {"role": "user", "content": f"Extract key clauses, detect risks, and simplify this legal text:\n{text}"}
        ]
    )
    return response["choices"][0]["message"]["content"]

@app.post("/analyze_legal_document/")
async def analyze_legal_document(file: UploadFile = File(...)):
    try:
        # Extract text from uploaded PDF
        text = extract_text_from_pdf(file)
        
        # Get AI analysis
        analysis = analyze_legal_text(text)
        
        return {"analysis": analysis}
    except Exception as e:
        return {"error": str(e)}
