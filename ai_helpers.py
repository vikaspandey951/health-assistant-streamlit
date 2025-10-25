# This is the AI helper file
import requests
import json
import pymupdf # fitz
from fpdf import FPDF

# --- AI (Ollama) Function ---
def get_ai_response(symptoms, report_text, user_name):
    # This is your "safe prompt"
    safe_prompt = f"""
    You are a helpful AI Health Assistant. You MUST NOT diagnose or prescribe medicine.
    A user named {user_name} has these symptoms: "{symptoms}"
    They also uploaded a report with this text: "{report_text}"

    Your task is to provide a structured response with:
    1.  **Summary:** A simple summary of the report.
    2.  **Key Terms:** Definitions for any complex terms.
    3.  **Questions for Doctor:** Questions they should ask their real doctor.
    4.  **Disclaimer:** A clear warning that this is not medical advice.
    """
    
    try:
        response = requests.post(
            "http://localhost:11434/api/generate", 
            json={
                "model": "llama3",  # Or your model of choice
                "prompt": safe_prompt,
                "stream": False
            }
        )
        response.raise_for_status() # Raise error for bad responses
        return response.json()["response"]
    except requests.exceptions.RequestException as e:
        return f"Error connecting to AI. Please ensure Ollama is running. {e}"

# --- PDF Parsing Function ---
def extract_text_from_pdf(pdf_file):
    report_text = ""
    try:
        # Open the PDF file from the uploaded byte stream
        doc = pymupdf.open(stream=pdf_file.read(), filetype="pdf")
        for page in doc:
            report_text += page.get_text()
        return report_text
    except Exception as e:
        return f"Error reading PDF: {e}"

# --- PDF Generation Function ---
def create_pdf_report(report_content, user_name):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=16)
    pdf.cell(200, 10, txt=f"Health Report for {user_name}", ln=True, align='C')
    pdf.set_font("Arial", size=12)
    pdf.multi_cell(0, 10, txt=report_content)
    
    # Save PDF to a byte stream to be downloaded
    return bytes(pdf.output(dest='S'))