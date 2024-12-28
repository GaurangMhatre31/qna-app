from flask import Flask, request, jsonify
import os
import pyttsx3
import pdfplumber
from docx import Document
from transformers import pipeline
from werkzeug.utils import secure_filename
from flask_cors import CORS  # Import CORS
import nest_asyncio

nest_asyncio.apply()

# Initialize Flask app
app = Flask(__name__)

# Enable CORS for all routes
# CORS(app)
# CORS(app, origins=["http://127.0.0.1:5500", "http://127.0.0.1:3000"])
CORS(app, origins="*", methods=["GET", "POST", "OPTIONS"], allow_headers=["Content-Type", "Authorization"])
00

# Configure upload folder
UPLOAD_FOLDER = './uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Initialize text-to-speech engine
engine = pyttsx3.init()

# Function to extract text from PDF
def extract_text_from_pdf(pdf_path):
    print(f"[DEBUG] Extracting text from PDF: {pdf_path}")
    with pdfplumber.open(pdf_path) as pdf:
        text = ''
        for page in pdf.pages:
            text += page.extract_text() + "\n"
    print(f"[DEBUG] Extracted text from PDF: {len(text)} characters")
    return text

# Function to extract text from Word file
def extract_text_from_word(docx_path):
    print(f"[DEBUG] Extracting text from Word file: {docx_path}")
    doc = Document(docx_path)
    text = "\n".join([para.text for para in doc.paragraphs])
    print(f"[DEBUG] Extracted text from Word file: {len(text)} characters")
    return text

# Initialize the question-answering model
qa_pipeline = pipeline("question-answering", model="distilbert-base-cased-distilled-squad")

# Route to upload a file
@app.route('/upload', methods=['POST'])
def upload_file():
    print("[DEBUG] Received file upload request.")
    if 'file' not in request.files:
        print("[DEBUG] No file part in the request.")
        return jsonify({"error": "No file part in the request"}), 400

    file = request.files['file']
    if file.filename == '':
        print("[DEBUG] No file selected.")
        return jsonify({"error": "No file selected"}), 400

    filename = secure_filename(file.filename)
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(file_path)

    # Determine file type and extract text
    print(f"[DEBUG] Processing file: {filename}")
    if filename.lower().endswith('.pdf'):
        context = extract_text_from_pdf(file_path)
    elif filename.lower().endswith('.docx'):
        context = extract_text_from_word(file_path)
    else:
        print("[DEBUG] Invalid file type.")
        return jsonify({"error": "Invalid file type. Please upload a PDF or Word document."}), 400

    if not context.strip():
        print("[DEBUG] No text extracted from the file.")
        return jsonify({"error": "No text was extracted from the file."}), 400

    # Save the context in a temporary location for further processing
    context_path = os.path.join(app.config['UPLOAD_FOLDER'], "context.txt")
    with open(context_path, "w", encoding="utf-8") as f:
        f.write(context)

    print(f"[DEBUG] Text extracted and saved to {context_path}")
    return jsonify({"message": "File uploaded and text extracted successfully."})

# Route to ask questions
@app.route('/ask', methods=['OPTIONS', 'POST'])
def ask_question():
    print("[DEBUG] Received question-asking request.")
    if request.method == 'OPTIONS':
        # Handle the preflight request
        return '', 200  # Respond with 200 status for OPTIONS (preflight) request
    question = request.json.get("question")
    if not question:
        print("[DEBUG] No question provided.")
        return jsonify({"error": "No question provided."}), 400

    # Load the context
    context_path = os.path.join(app.config['UPLOAD_FOLDER'], "context.txt")
    if not os.path.exists(context_path):
        print("[DEBUG] No context available.")
        return jsonify({"error": "No context available. Please upload a file first."}), 400

    with open(context_path, "r", encoding="utf-8") as f:
        context = f.read()
        print(f"[DEBUG] Context loaded: {len(context)} characters")

    # Get the answer from the model
    try:
        print(f"[DEBUG] Asking question: {question}")
        result = qa_pipeline(question=question, context=context)
        answer = result['answer']
        print(f"[DEBUG] Answer: {answer}")
        return jsonify({"answer": answer})
    except Exception as e:
        print(f"[DEBUG] Error during question answering: {str(e)}")
        return jsonify({"error": str(e)}), 500

# Run the app
if __name__ == '__main__':
    print("[DEBUG] Starting the Flask app...")
    app.run(debug=True)
    # Ensure this route is handling the file upload correctly
