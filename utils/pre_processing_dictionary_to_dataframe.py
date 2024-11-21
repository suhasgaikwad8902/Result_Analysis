import pandas as pd
import numpy as np
import streamlit as st

def convert_dict_to_dataframe(list_dict, index):
    processing_message = st.empty()
    processing_message.write("Analyzing Dictionary")
    # '''***************************SAVING DATAFRAME IN MULTIINDEX FORMAT*******************'''
    df_students = pd.DataFrame(list_dict)
    # ['ISE', 'ESE', 'TOTAL', 'TW', 'PR', 'OR', 'TUT', 'Tot%', 'Crd', 'Grd', 'GP', 'CP',
    #  'P&R', 'ORD']
    overAlldf = pd.DataFrame()
    for i in list_dict:
        temp = pd.DataFrame(i, index= index)
        overAlldf = pd.concat([temp, overAlldf], axis=0)
    processing_message = st.empty()
    processing_message.write("overalldf created")
    overAlldf = overAlldf.reset_index()
    overAlldf_sorted = overAlldf.sort_values(['SEAT NO'])
    multiindex_df = overAlldf_sorted.set_index(['SEAT NO', 'NAME', 'PRN', 'MOTHER NAME', 'CREDITS', 'SGPA', 'index'])
    multiindex_df = multiindex_df.unstack()
    # '''data transformation and cleaning'''
    # sub list Hardcoded if mother name , seat no is excluded from result need change
    sub_list = df_students.columns[6:].tolist()
    # sub_list
    # print(sub_list)
    sub_det = index
    # replacing .., by FAIL
    df_students['SGPA'][df_students['SGPA'] == '--'] = 'FAIL'
    processing_message = st.empty()
    processing_message.write("sub det ")
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
    return sub_list, list_subdf, multiindex_df, df_students
