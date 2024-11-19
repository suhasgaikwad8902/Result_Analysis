import streamlit as st
import PyPDF2
import numpy as np
import pandas as pd
import seaborn as sns
from matplotlib import pyplot as plt
import os, time, shutil,io,zipfile, base64
import smtplib
import ssl
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email import encoders

from Web_app.pre_processing_dictionary_to_dataframe import convert_dict_to_dataframe
from Web_app.create_excel_sheets import create_excel
from Web_app.pre_processing_pdf_to_dictionary import convert_pdf_to_dict


# Function to process the PDF
def process_pdf(pdf_file):
    list_dict, pdfdoc = convert_pdf_to_dict(pdf_file)
    "pdf to dict successfull"
    #
    # '''**************************RECORDS SAVED IN DICTIONARY********************************'''
    sub_list,list_subdf,multiindex_df, df_students= convert_dict_to_dataframe(list_dict)
    "dict to dataframe  successfull"


    # save subwise dataframe in excel sheet
    sub_analy_list, output,failed_students,bins = create_excel(sub_list, list_subdf, multiindex_df, pdfdoc, df_students)
    data = ['MARKS ABOVE 90', 'MARKS [ 80-90]', 'MARKS [70-80]', 'MARKS [60-70]', 'MARKS [50-60]', 'MARKS [40-50]',
            'FAIL', 'ABSENT']
    zip_stream = io.BytesIO()
    col1, col2, col3, col4,col5 = st.columns(5)
    with zipfile.ZipFile(zip_stream, mode='w', compression=zipfile.ZIP_DEFLATED) as zip_file:

        for sub in sub_analy_list:
            cmap = sns.color_palette("magma", len(data))
            sns.set_style("whitegrid")
            plt.figure(figsize=(8, 6))
            x_data = sub['range_marks'] + [sub['failed'], sub['absent']]
            ax = sns.barplot(x=x_data, y=data, orient='h', palette=cmap)
            ax.set_title('AVERAGE MARKS  [{}%]'.format(round(sub['avg'], 2)), fontsize=14, fontweight='bold')
            ax.set_xlabel('NO OF STUDENTS  \n[TOTAL {}]'.format(sub['opted']), fontsize=15, fontweight='bold')
            ax.set_ylabel('MARKS RANGE (%)', fontsize=15, fontweight='bold')
            for i in ax.containers:
                ax.bar_label(i, fontsize=12, fontweight='bold')
            plt.xticks(fontweight='bold', fontsize=14)
            plt.yticks(fontweight='bold', fontsize=14)
            plt.suptitle('{}'.format(sub['subname']), fontsize=14, fontweight='bold')
            plt.tight_layout()  # Adjusts the spacing and margins
            plot_buffer = io.BytesIO()
            plt.savefig(plot_buffer, format='png')
            plot_buffer.seek(0)  # Move the buffer cursor to the beginnin
            image_name = f"{sub['subname'].replace('/', '-')}.png"
            st.image(plot_buffer, caption=image_name, use_column_width=True)
            zip_file.writestr(f"{image_name}.png", plot_buffer.read())
        # '''Overall result plots'''
        sgpa_y = ['SGPA ABOVE 9', 'SGPA[ 8-9]', 'SGPA [7-8]', 'SGPA [6-7]', 'SGPA[5-6]', 'SGPA[4-5]', 'FAILED']
        sgpa = pd.to_numeric(df_students['SGPA'], errors='coerce').dropna()
        sgpa_bin = list(map(lambda x: x / 10, bins))
        sgpa_x = pd.cut(sgpa, sgpa_bin).value_counts(sort=False).tolist()[-1::-1]

        cmap = sns.color_palette("viridis", len(sgpa_y))
        sns.set_style("whitegrid")
        plt.figure(figsize=(8, 6))
        sgpa_x.append(failed_students)
        ax = sns.barplot(x=sgpa_x, y=sgpa_y, orient='h', palette=cmap)
        ax.set_title('AVERAGE SGPA [{}]'.format(round(sgpa.mean(), 2)), fontsize=15, fontweight='bold')
        ax.set_xlabel('NO OF STUDENTS', fontsize=15, fontweight='bold')
        ax.set_ylabel('SGPA RANGE ', fontsize=15, fontweight='bold')
        for i in ax.containers:
            ax.bar_label(i, fontsize=12, fontweight='bold')
        plt.xticks(fontweight='bold', fontsize=14)
        plt.yticks(fontweight='bold', fontsize=14)
        plt.tight_layout()
        plot_buffer = io.BytesIO()
        plt.savefig(plot_buffer, format='png')
        plot_buffer.seek(0)  # Move the buffer cursor to the beginnin
        image_name = "SGPA"
        st.image(plot_buffer, caption=image_name, use_column_width=True)
        zip_file.writestr(f"{image_name}.png", plot_buffer.read())
        # '''**********************ALL SUB PASS FAIL %***********************'''

        data_y = [i['subname'] + '[{}]'.format(i['opted']) for i in sub_analy_list]
        data_x = [i['failed'] for i in sub_analy_list]
        cmap = sns.color_palette("magma", len(data_x))
        sns.set_style("whitegrid")
        plt.figure(figsize=(16, 20))
        data_x, data_y = zip(*sorted(zip(data_x, data_y)))
        ax = sns.barplot(x=list(data_x), y=list(data_y), orient='h', palette=cmap)
        ax.set_title('SUBJECT WISE RESULT', fontsize=15, fontweight='bold')
        ax.set_xlabel('FAILED STUDENTS NO.', fontsize=15, fontweight='bold')
        ax.set_ylabel('SUBJECT NAME ', fontsize=20, fontweight='bold')
        for i in ax.containers:
            ax.bar_label(i, fontsize=12, fontweight='bold')
        plt.xticks(fontweight='bold', fontsize=14)
        plt.yticks(fontweight='bold', fontsize=14)
        plt.tight_layout()
        plot_buffer = io.BytesIO()
        plt.savefig(plot_buffer, format='png')
        plot_buffer.seek(0)  # Move the buffer cursor to the beginnin
        image_name = "ALL SUBJECTS RESULT"
        st.image(plot_buffer, caption=image_name, use_column_width=True)
        zip_file.writestr(f"{image_name}.png", plot_buffer.read())

        # Reset the pointer of the BytesIO object to the beginning
        zip_stream.seek(0)

        return output, zip_stream
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
image_path = os.path.join(current_dir, "static", "1614776.jpg")
set_background(image_path)
st.title('Result Analysis App', help="A tool for analyzing result PDFs")
# File uploader for PDF files
pdf_file = st.file_uploader("Upload a PDF file(2019 Pattern) SPPU", type=["pdf"])
# Example of a styled button
st.write('Upload your PDF file and process it.')
if st.button('Analyze PDF and Generate Reports', key='process', help="Click to process the uploaded PDF"):
    if pdf_file is not None:
        try:
            processing_message = st.empty()
            processing_message.write('Processing...')
            pdf_name = os.path.splitext(pdf_file.name)[0]
            # Process the uploaded PDF
            res = process_pdf(pdf_file)
            excel_data = res[0]
            zip_stream = res[1]
            # Display a success message

            st.download_button(
                label="Download Excel File",
                data=excel_data,
                file_name="{}.xlsx".format(pdf_name),
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
            st.download_button(
                label="Download All Plots",
                data=zip_stream,
                file_name="plots.zip",
                mime="application/zip"
            )
            processing_message.empty()
        except Exception:
            st.error("Upload a valid PDF File")