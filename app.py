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

# Define custom CSS for fonts and colors
st.markdown(
    """
    <style>
    .reportview-container {
        background: url('static/1614776.jpg');
        background-size: cover;
    }
    .title {
        color: #4B0082;  /* Indigo color */
        font-family: 'Comic Sans MS', cursive, sans-serif;
    }
    .button {
        background-color: #FF6347;  /* Tomato color */
        color: white;
    }
    </style>
    """,
    unsafe_allow_html=True
)

st.title('Result Analysis App', help="A tool for analyzing result PDFs")
st.write('Upload your PDF file and process it.')

# Example of a styled button
if st.button('Process PDF', key='process', help="Click to process the uploaded PDF"):
    st.write('Processing...')

# Streamlit UI
# st.title("PDF Processing App")

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
