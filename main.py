import openai

def analyze_legal_text(text):
    response = openai.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are an AI that extracts key clauses, detects risks, and simplifies legal language from contracts."},
            {"role": "user", "content": f"Extract key clauses, detect risks, and simplify this legal text:\n{text}"}
        ]
    )
    
    return response.choices[0].message.content
