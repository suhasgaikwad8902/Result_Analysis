import streamlit as st
import PyPDF2


# Function to process the PDF
def process_pdf(pdf_file):
    pdf_reader = PyPDF2.PdfReader(pdf_file)
    num_pages = len(pdf_reader.pages)
    text = ""

    for page_num in range(num_pages):
        page = pdf_reader.pages[page_num]
        text += page.extract_text()

    return text


# Streamlit UI
st.title("PDF Processing App")

# File uploader for PDF files
pdf_file = st.file_uploader("Upload a PDF file", type=["pdf"])

if pdf_file is not None:
    # Process the uploaded PDF
    text = process_pdf(pdf_file)

    # Display a success message
    st.success("PDF processed successfully!")

    # Optionally display the extracted text
    st.write("Extracted Text:")
    st.text_area("Text", value=text, height=200)

    # Allow user to download the extracted text as a file
    st.download_button("Download Text", data=text, file_name="extracted_text.txt")
