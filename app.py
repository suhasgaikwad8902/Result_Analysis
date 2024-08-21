import streamlit as st
import PyPDF2
import numpy as np
import pandas as pd
import seaborn as sns
from matplotlib import pyplot as plt
import os, time, shutil,io


# Function to process the PDF
def process_pdf(pdf_file):
    pdfdoc = PyPDF2.PdfReader(pdf_file)
    num_pages = len(pdfdoc.pages)

    # '''***************SAVE ALL STUDENT RECORDS IN DICTIONARY*******************'''

    list_dict = []
    sub_set = set()
    flag = 'green'
    for j in range(num_pages - 1):
        page = pdfdoc.pages[j]
        page_content = page.extract_text()
        records_per_page = page_content.count('CONFIDENTIAL')
        Students = page_content.split("CONFIDENTIAL")[:2]  # only first 2 elements
        #     type 1: 1 page 1 record  ---> records_per_page = 1
        #     type 2: 1 page 2 records ---> records_per_page = 2
        #     type 3: second record on page 1 + 2 both
        # '''*****page format accomodation(type 1, 2, 3)************'''
        if records_per_page != 2:  # record of 2nd student on two pages
            page2 = pdfdoc.pages[j + 1].extract_text()
            Students[1] = Students[1] + '\n' + page2  # also covers type 1
            flag = 'red'
            if len(page2.strip()) == 0:  # if page 2 is blank only 1 iteration for last page in below for loop
                Students = Students[:1]
        if flag == 'red' and j % 2 != 0:
            continue
        # '''******************************************'''

        for i in Students:
            lines = []
            student_dict = {}  # one dictionary for each student. key is sub name, value is records
            ind_sn = i.find("SEAT NO.:") + 9
            i = i[ind_sn - 10:i.find("CONFIDENTIAL")]  # trim unnecessary page contains
            # '''detect subjects'''
            _=[lines.append(line) for line in i.splitlines() if ('/' in line or ' PP ' in line or ' AC ' in line)]

            ind_sn = i.find("SEAT NO.:") + 9
            ind_name = i.find("NAME :") + 7
            ind_mother = i.find("MOTHER : ")
            ind_prn = i.find("PRN :") + 5
            ind_SGPA1 = i.find('SGPA1 : ') + 8 if 'SGPA1' in i else i.find('SGPA : ') + 7
            #         ind_SGPA1 = i.find(sgpa) + 8
            ind_crd = i.find('TOTAL CREDITS EARNED : ') + 23

            st_sn = i[ind_sn:ind_sn + 11].strip()
            st_name = i[ind_name:ind_mother].strip()
            st_mother = i[ind_mother + 8: ind_prn - 5].strip()
            st_prn = i[ind_prn: ind_prn + 10]
            st_SGPA = i[ind_SGPA1: i.find('TOTAL CREDITS')].strip().strip(",")
            st_credits = i[ind_crd: ind_crd + 2].strip()

            #         print(st_sn,st_name,st_mother,st_prn,st_SGPA, st_credits, sep='\n')

            student_dict['SEAT NO'] = st_sn
            student_dict['NAME'] = st_name
            student_dict['PRN'] = st_prn
            student_dict['MOTHER NAME'] = st_mother
            student_dict['SGPA'] = st_SGPA
            student_dict['CREDITS'] = st_credits
            z = 1
            for line in lines:

                line = ' '.join(line.split())  # to replace multiple spaces to single
                sub = line.strip().rsplit(" ", 14)  # why 13
                #             print(sub)
                if '*' in sub[0]:
                    sub[0] = sub[0].strip('*')
                    sub[0] = sub[0].strip()
                else:
                    sub[0] = sub[0].strip()

                data = sub[1:]
                # Identify if sub has TW, OR, PR
                sub_sc = ''
                if data[2] == '---':
                    # sub is TW | OR | PR
                    sub_sc = 'TW' if '/' in data[3] else ''
                    sub_sc = sub_sc + 'PR' if '/' in data[4] else sub_sc
                    sub_sc = sub_sc + 'OR' if '/' in data[5] else sub_sc
                student_dict[sub[0] + " " + sub_sc] = data

            list_dict.append(student_dict)
    df_students = pd.DataFrame(list_dict)
    #
    # '''**************************RECORDS SAVED IN DICTIONARY********************************'''
    # '''***************************SAVING DATAFRAME IN MULTIINDEX FORMAT*******************'''
    overAlldf = pd.DataFrame()
    for i in list_dict:
        temp = pd.DataFrame(i, index=['ISE', 'ESE', 'TOTAL', 'TW', 'PR', 'OR', 'TUT', 'Tot%', 'Crd', 'Grd', 'GP', 'CP',
                                      'P&R', 'ORD'])
        overAlldf = pd.concat([temp, overAlldf], axis=0)

    overAlldf = overAlldf.reset_index()
    overAlldf_sorted = overAlldf.sort_values(['SEAT NO'])
    multiindex_df = overAlldf_sorted.set_index(['SEAT NO', 'NAME', 'PRN', 'MOTHER NAME', 'CREDITS', 'SGPA', 'index'])
    multiindex_df = multiindex_df.unstack()
    t1 = time.time()
    # print("TIME FOR CREATING DATAFRAMES FROM DICT DATA", t1 - start)
    # '''data transformation and cleaning'''
    # sub list Hardcoded if mother name , seat no is excluded from result need change
    sub_list = df_students.columns[6:].tolist()
    # sub_list
    # print(sub_list)
    sub_det = ['ISE', 'ESE', 'TOTAL', 'TW', 'PR', 'OR', 'TUT', 'Tot%', 'Crd', 'Grd', 'GP', 'CP', 'P&R', 'ORD']
    # replacing .., by FAIL
    df_students['SGPA'][df_students['SGPA'] == '--'] = 'FAIL'

    # all sub-->list element-->transform-->dictionary--->why ->can be conv to dataframe directly
    subElement_todict = [df_students[y].apply(lambda x: {x: y for x, y in zip(sub_det, x)} if isinstance(x, list)
    else {x: y for x, y in zip(sub_det, [np.nan] * len(sub_det))}).to_list()
                         for y in sub_list]
    # create list of df-->one df for one sub
    list_subdf = [pd.DataFrame(i) for i in subElement_todict]
    first_sixCol = df_students.iloc[:, :6]
    # concat along axis 1 ie columnwise
    list_subdf = [pd.concat([first_sixCol, i], axis=1) for i in list_subdf]
    # filter dataframe --> if ISE == false -->not opted for sub
    list_subdf = [i.dropna().reset_index(drop=True) for i in list_subdf]
    # save subwise dataframe in excel sheet
    '''EXCEL FILES'''
    output = io.BytesIO()
    writer = pd.ExcelWriter(output,engine='xlsxwriter')
    _=[list_subdf[i].to_excel(writer, sheet_name="{}".format(sub_list[i].replace('/', '-')[:31]), index=False, ) for i in
     range(len(sub_list))]
    multiindex_df.to_excel(writer, sheet_name="ALL SUBJECTS RESULT")
    backlogs = multiindex_df.apply(lambda row: row.value_counts().get("FF", 0), axis=1)  # backlogs
    backlogs.to_excel(writer, sheet_name='BACKLOGS')
    # '''*****************YEAR DOWN STUDENTS********************'''
    text_onpage = pdfdoc.pages[0].extract_text()
    yd_st = pd.DataFrame()
    if ('SEM.:2' in text_onpage and 'F.E.' in text_onpage):
        yd_st = df_students.iloc[:, 0:6][pd.to_numeric(df_students['CREDITS'], errors='coerce') < 22]

    if ('SEM.:2' in text_onpage and 'S.E.' in text_onpage):
        yd_st = df_students.iloc[:, 0:6][pd.to_numeric(df_students['CREDITS'], errors='coerce') < 22]

    if ('SEM.:2' in text_onpage and 'T.E.' in text_onpage):
        print("in te")
        yd_st = df_students.iloc[:, 0:6][pd.to_numeric(df_students['CREDITS'], errors='coerce') < 20]

    if 'SEM.:2' in text_onpage and 'B.E.' in text_onpage:
        yd_st = df_students.iloc[:, 0:6][pd.to_numeric(df_students['CREDITS'], errors='coerce') < 20]

    yd_st.to_excel(writer, sheet_name='YEAR DOWN', index=False)

    # '''top ten sgpa '''
    new = pd.to_numeric(df_students['SGPA'], errors='coerce')
    tenth_sgpa = sorted(new.dropna().unique(), reverse=True)[9]
    top_ten = df_students[['SEAT NO', 'NAME', 'PRN', 'SGPA']][new >= tenth_sgpa].sort_values(['SGPA'], ascending=False)
    top_ten.to_excel(writer, sheet_name='TOP_TEN', index=False)
    # writer.save()
    # writer.close()
    # t2 = time.time()
    # print(" time for writing excel files", t2 - t1)
    # '''*****************Data cleaning and Processing********************'''
    tot_no_students = len(df_students[df_students['PRN'].notnull()])
    failed_students = len(df_students[df_students['SGPA'] == 'FAIL'])
    allclear_students = len(df_students[pd.to_numeric(df_students['SGPA'], errors='coerce').notnull()])
    bins = [39, 49, 59, 69, 79, 89, 100]  # bin is (excluding, including])
    sub_analy_list = []
    k = 0
    # print("list_subdf",list_subdf)
    for df in list_subdf:
        total_numeric = pd.to_numeric(df['Tot%'], errors='coerce')
        topper = df[['SEAT NO', 'NAME', 'PRN', 'SGPA', 'CREDITS', 'TOTAL']][total_numeric == total_numeric.max()]
        topper['SUBJECT'] = sub_list[k]
        sub_analy = {'subname': sub_list[k], 'opted': df.shape[0], 'absent': len(df[df['Grd'] == 'IC']),
                     'failed': len(df[df['Tot%'] == 'FF']), 'avg': total_numeric.mean(),
                     'max': total_numeric.max(),
                     'min': total_numeric.min(),
                     'per_passed': (df.shape[0] - len(df[df['Tot%'] == 'FF'])) * 100 / df.shape[0],
                     'range_marks': (pd.cut(total_numeric, bins).value_counts(sort=False).to_list())[-1::-1],
                     'toppers': topper
                     }
        sub_analy_list.append(sub_analy)
        k = k + 1
    t3 = time.time()
    # print("time for creating sub analysis list", t3 - t2)
    # '''Toppers list'''
    ola = pd.DataFrame()
    for i in sub_analy_list:
        ola = pd.concat([ola, i['toppers']], axis=0)
    # ola = ola[ola['SUBJECT'].apply(lambda x : ('TW'not in x and 'OR' not in x and 'PR' not in x) )]
    ola = ola.set_index(['SUBJECT', 'SEAT NO'])
    v = pd.DataFrame(sub_analy_list)[['subname', 'opted', 'absent', 'failed', 'avg', 'per_passed', 'max']]
    v.columns = ['SUBJECT', 'APPEARED', 'ABSENT', 'FAILED', 'AVERAGE MARKS(%)', 'PASS RESULT (%)', 'HIGHEST MARKS(%)']
    ola.reset_index(inplace=True)
    c = pd.merge(ola[['SUBJECT', 'NAME']], v, left_on='SUBJECT', right_on='SUBJECT')
    c.rename(columns={'NAME': 'TOPPER'}, inplace=True)
    c.set_index(['SUBJECT', 'APPEARED', 'ABSENT', 'FAILED', 'AVERAGE MARKS(%)', 'PASS RESULT (%)', 'HIGHEST MARKS(%)',
                 'TOPPER'], inplace=True)
    c.to_excel(writer, sheet_name="SUBJECT WISE RESULT")
    writer.close()
    output.seek(0)
    data = ['MARKS ABOVE 90', 'MARKS [ 80-90]', 'MARKS [70-80]', 'MARKS [60-70]', 'MARKS [50-60]', 'MARKS [40-50]',
            'FAIL', 'ABSENT']
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
        # Provide download buttons for the plots
        st.download_button(
            label= "{}.png".format(sub['subname'].replace('/', '-')),
            data=plt,
            file_name="{}.png".format(sub['subname'].replace('/', '-')[:31]),  # Name based on the PDF file
            mime="image/png"
        )
        plt.close()
    return output


# Define custom CSS for fonts and colors
st.markdown(
    """
    <style>
    .reportview-container {
        background: url('/static/1614776.jpg');
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
    pdf_name = os.path.splitext(pdf_file.name)[0]

    # Process the uploaded PDF
    excel_data = process_pdf(pdf_file)

    # Display a success message
    st.success("PDF processed successfully!")

    # Optionally display the extracted text
    # st.write("Extracted Text:")
    # st.text_area("Text", value=text, height=200)

    # Allow user to download the extracted text as a file
    # st.download_button("Download Text", data=text, file_name="extracted_text.txt")
    st.download_button(
        label="Download Excel File",
        data=excel_data,
        file_name="{}.xlsx".format(pdf_name),
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )