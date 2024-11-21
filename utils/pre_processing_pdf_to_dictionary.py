import PyPDF2


def convert_pdf_to_dict(pdf_file):
    "Analyzing PDF"
    pdfdoc = PyPDF2.PdfReader(pdf_file)
    num_pages = len(pdfdoc.pages);
    list_dict = []
    data = ""
    for j in range(num_pages - 1):
        page = pdfdoc.pages[j]
        page_content = page.extract_text()
        data = data + "\n" + page_content.strip()
    Students = data.split("CONFIDENTIAL")  # only first 2 elements
    Students.pop()  # remove string after last CONFIDENTIAL
    for i in Students:
        lines = []
        student_dict = {}  # one dictionary for each student. key is sub name, value is records
        ind_sn = i.find("SEAT NO.:") + 9
        i = i[ind_sn - 10:i.find("CONFIDENTIAL")]  # trim unnecessary page contains
        '''detect subjects'''
        [lines.append(line) for line in i.splitlines() if
         (('/' in line or ' PP ' in line or ' AC ' in line) and 'CGPA' not in line)]  # update cgpa for new pdfs

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
                ind = sub[0].find('*')
                sub[0] = sub[0][:ind].strip()
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
    return list_dict, pdfdoc
