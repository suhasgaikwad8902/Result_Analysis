import base64, os
import streamlit as st


def set_background():
    def get_base64(bin_file):
        with open(bin_file, 'rb') as f:
            data = f.read()
            return base64.b64encode(data).decode()

    def set_background(png_file):
        bin_str = get_base64(png_file)
        page_bg_img = '''
        <style>
        .stApp {
        background-image: url("data:image/png;base64,%s");
        background-size: cover;
        }
        </style>
        ''' % bin_str
        st.markdown(page_bg_img, unsafe_allow_html=True)

    # Determine the correct path for the image
    current_dir = os.path.dirname(os.path.abspath(__file__))
    image_path = os.path.join(current_dir, "static", "wall.png")
    set_background(image_path)
    st.markdown("<div style='margin-top: 50px;'></div>", unsafe_allow_html=True)  # Adds vertical space
    st.title('Result Analysis App', help="A tool for analyzing result PDFs")
    # File uploader for PDF files
    pdf_file = st.file_uploader("Upload a PDF file(2019 Pattern) SPPU", type=["pdf"])
    # Example of a styled button
    st.write('Upload your PDF file and process it.')
    return st, pdf_file
