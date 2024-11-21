import os, io, zipfile

from utils.create_plots import result_plots
from utils.set_background import set_background
from utils.pre_processing_dictionary_to_dataframe import convert_dict_to_dataframe
from utils.create_excel_sheets import create_excel
from utils.pre_processing_pdf_to_dictionary import convert_pdf_to_dict

current_dir = os.path.dirname(os.path.abspath(__file__))


# Function to process the PDF
def process_pdf(pdf_file):
    # pdf to dictionary
    list_dict, pdfdoc = convert_pdf_to_dict(pdf_file)
    # dictionary to dataframe
    sub_list, list_subdf, multiindex_df, df_students = convert_dict_to_dataframe(list_dict)

    # save subwise dataframe in excel sheet
    sub_analy_list, output, failed_students, bins = create_excel(sub_list, list_subdf, multiindex_df, pdfdoc,
                                                                 df_students)
    # plots
    zip_stream = result_plots(sub_analy_list, df_students, bins, failed_students)

    return output, zip_stream


#  set background
st, pdf_file = set_background()
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
            # Combine both into a single ZIP file
            combined_zip = io.BytesIO()
            with zipfile.ZipFile(combined_zip, "w") as zipf:
                # Add the Excel file
                zipf.writestr("{}.xlsx".format(pdf_name), excel_data.getvalue())

                # Extract plot files from the original ZIP and add them to the combined ZIP
                with zipfile.ZipFile(zip_stream, "r") as plots_zip:
                    for file_name in plots_zip.namelist():
                        zipf.writestr(file_name, plots_zip.read(file_name))

            # st.download_button(
            #     label="Download Excel File",
            #     data=excel_data,
            #     file_name="{}.xlsx".format(pdf_name),
            #     mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            # )
            combined_zip.seek(0)
            st.download_button(
                label="Download All Plots and Excel",
                data=combined_zip,
                file_name="Excel_and_plots.zip",
                mime="application/zip"
            )
            processing_message.empty()
        except Exception:
            st.error("Upload a valid PDF File")
