from flask import Flask, render_template, request
import os
from dotenv import load_dotenv
from google import genai
from pypdf import PdfReader
import markdown

load_dotenv()
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
app = Flask(__name__)

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/analyze", methods=["POST"])
def analyze():
    file = request.files["resume"]

    # extract text from the PDF
    reader = PdfReader(file)
    resume_text = ""
    for page in reader.pages:
        resume_text += page.extract_text()

    # build the prompt for Gemini
    prompt = f"""
    You are a resume reviewer. Analyze this resume and give feedback in this format:
    
    1. Grammar issues (if any)
    2. Estimated ATS compatibility score out of 100
    3. Missing skills (based on what's typical for the field this resume seems to target)
    4. Suggestions to improve it

    Resume text:
    {resume_text}
    """

    response = client.models.generate_content(
    model="gemini-3.5-flash",
    contents=prompt
)

    feedback_html = markdown.markdown(response.text)
    return render_template("results.html", feedback=feedback_html)

if __name__ == "__main__":
    app.run(debug=True)
    