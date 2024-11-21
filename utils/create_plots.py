import streamlit as st
import io, zipfile, base64
import seaborn as sns
from matplotlib import pyplot as plt
import pandas as pd


def result_plots(sub_analy_list, df_students, bins, failed_students):
    "Creating Plots"
    data = ['MARKS ABOVE 90', 'MARKS [ 80-90]', 'MARKS [70-80]', 'MARKS [60-70]', 'MARKS [50-60]', 'MARKS [40-50]',
            'FAIL', 'ABSENT']
    zip_stream = io.BytesIO()
    col1, col2, col3, col4, col5 = st.columns(5)
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
            image_name = f"{sub['subname'].replace('/', '-')}"
            # st.image(plot_buffer, caption=image_name, use_column_width=True)
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
        # st.image(plot_buffer, caption=image_name, use_column_width=True)
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
        # st.image(plot_buffer, caption=image_name, use_column_width=True)
        zip_file.writestr(f"{image_name}.png", plot_buffer.read())

        # Reset the pointer of the BytesIO object to the beginning
        zip_stream.seek(0)
        return zip_stream
