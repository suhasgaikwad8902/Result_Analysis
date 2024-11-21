import pandas as pd
import io
import streamlit as st


def create_excel(sub_list, list_subdf, multiindex_df, pdfdoc, df_students):
    # '''EXCEL FILES'''
    processing_message = st.empty()
    processing_message.write("Creating Excel sheets")
    output = io.BytesIO()
    writer = pd.ExcelWriter(output, engine='xlsxwriter')
    _ = [list_subdf[i].to_excel(writer, sheet_name="{}".format(sub_list[i].replace('/', '-')[:31]), index=False, ) for i
         in
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
    # '''*****************Data cleaning and Processing********************'''
    tot_no_students = len(df_students[df_students['PRN'].notnull()])
    failed_students = len(df_students[df_students['SGPA'] == 'FAIL'])
    allclear_students = len(df_students[pd.to_numeric(df_students['SGPA'], errors='coerce').notnull()])
    bins = [39, 49, 59, 69, 79, 89, 100]  # bin is (excluding, including])
    global sub_analy_list;
    sub_analy_list = []
    k = 0
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
    return sub_analy_list, output, failed_students, bins
