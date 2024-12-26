from flask import Flask, request, jsonify
import os
import pyttsx3
import pdfplumber
from docx import Document
import ollama  # Import the Ollama SDK
from werkzeug.utils import secure_filename

# Initialize Flask app
app = Flask(__name__)

# Configure upload folder
UPLOAD_FOLDER = './uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Initialize text-to-speech engine
engine = pyttsx3.init()

# Function for text-to-speech
def speak(text):
    engine.say(text)
    engine.runAndWait()

# Function to extract text from PDF
def extract_text_from_pdf(pdf_path):
    with pdfplumber.open(pdf_path) as pdf:
        text = ''
        for page in pdf.pages:
            text += page.extract_text() + "\n"
    return text

# Function to extract text from Word file
def extract_text_from_word(docx_path):
    doc = Document(docx_path)
    text = "\n".join([para.text for para in doc.paragraphs])
    return text

# Route to upload a file
@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({"error": "No file part in the request"}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No file selected"}), 400
    
    filename = secure_filename(file.filename)
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(file_path)

    # Determine file type and extract text
    if filename.lower().endswith('.pdf'):
        context = extract_text_from_pdf(file_path)
    elif filename.lower().endswith('.docx'):
        context = extract_text_from_word(file_path)
    else:
        return jsonify({"error": "Invalid file type. Please upload a PDF or Word document."}), 400

    if not context.strip():
        return jsonify({"error": "No text was extracted from the file."}), 400

    # Save the context in a temporary location for further processing
    with open(os.path.join(app.config['UPLOAD_FOLDER'], "context.txt"), "w", encoding="utf-8") as f:
        f.write(context)

    return jsonify({"message": "File uploaded and text extracted successfully."})

# Route to ask questions
@app.route('/ask', methods=['POST'])
def ask_question():
    question = request.json.get("question")
    if not question:
        return jsonify({"error": "No question provided."}), 400

    # Load the context
    context_path = os.path.join(app.config['UPLOAD_FOLDER'], "context.txt")
    if not os.path.exists(context_path):
        return jsonify({"error": "No context available. Please upload a file first."}), 400

    with open(context_path, "r", encoding="utf-8") as f:
        context = f.read()

    # Get the answer from Ollama's model
    try:
        # Use the Ollama API to get an answer from the model
        response = ollama.chat(model="llama2", messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": f"Context: {context} Question: {question}"}
        ])
        answer = response['text']
        speak(answer)  # Speak the answer
        return jsonify({"answer": answer})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Run the app
if __name__ == '__main__':
    app.run(debug=True)
