import subprocess
import sys

# Function to install packages programmatically
def install(package):
    subprocess.check_call([sys.executable, "-m", "pip", "install", package])

# Install the necessary packages
required_packages = ['pdfplumber', 'python-docx', 'Pillow', 'pyttsx3', 'SpeechRecognition', 'transformers']

for package in required_packages:
    install(package)

import pyttsx3

# Initialize text-to-speech engine
engine = pyttsx3.init()

# Function for text-to-speech
def speak(text):
    engine.say(text)
    engine.runAndWait()
import pdfplumber
from docx import Document
from PIL import Image

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

# Function to extract text from an image (Placeholder for OCR integration)
def extract_text_from_image(image_path):
    try:
        image = Image.open(image_path)
        image.show()  # Just opens the image for now
        return "Image opened successfully. (Implement OCR here for text extraction)"
    except Exception as e:
        return f"Error loading image: {e}"
 import speech_recognition as sr

# Function to recognize speech and return it as text
def recognize_speech():
    recognizer = sr.Recognizer()
    mic = sr.Microphone()
    with mic as source:
        print("Listening for your voice...")
        audio = recognizer.listen(source)
    try:
        text = recognizer.recognize_google(audio)
        print("You said:", text)
        return text
    except sr.UnknownValueError:
        return "Sorry, I could not understand what you said."
    except sr.RequestError:
        return "Could not request results from the speech recognition service."
    from transformers import pipeline

# Initialize the question-answering model
def initialize_qa_model():
    print("Loading the QA model...")
    qa_pipeline = pipeline("question-answering", model="distilbert-base-cased-distilled-squad")
    print("Model loaded successfully.")
    return qa_pipeline
    # Get answer based on extracted text
def get_answer(qa_pipeline, question, context):
    result = qa_pipeline(question=question, context=context)
    return result['answer']
# Main function to read PDF or Word files and ask questions
def main():
    # Initialize the QA model
    qa_pipeline = initialize_qa_model()

    # Get the file path from the user
    file_path = input("Please enter the file path (PDF or Word document): ")

    # Check the file extension to determine how to read it
    context = ""
    if file_path.lower().endswith('.pdf'):
        context = extract_text_from_pdf(file_path)
    elif file_path.lower().endswith('.docx'):
        context = extract_text_from_word(file_path)
    else:
        print("Invalid file type. Please upload a PDF or Word file.")
        return

    if not context.strip():
        print("No text was extracted from the file.")
        return

    # Loop for user questions
    while True:
        question = input("\nAsk a question (or type 'exit' to quit): ")
        if question.lower() == 'exit':
            print("Exiting question loop.")
            break

        # Get the answer from the model
        answer = get_answer(qa_pipeline, question, context)
        if answer:
            print(f"Answer: {answer}")
            speak(answer)  # Speak the answer
        else:
            print("No answer found.")

if __name__ == "__main__":
    main()