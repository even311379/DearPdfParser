import regex as re
import pandas as pd
import pdftotext
import numpy as np
from tqdm import tqdm


def LoadFilesFromGroup(Group=0, AllFiles=False):
    pass


class ScoreSheetParser:

    @staticmethod
    def parse_generic_info(PDF, FilePath):
        t = FilePath.split('/')
        TT = re.findall(r'姓名：(.*?)\r', PDF[0])
        if TT:
            name = TT[0]
        else:
            name = "Error!! Manual is required"
        return [t[-2], t[-3], name]


class Parser_0(ScoreSheetParser):

    @classmethod
    def parse_info(cls, PDF, FilePath):
        # this is a mixed group
        score_sheet = PDF[2]
        IID, SID, SName = cls.parse_generic_info(PDF, FilePath)
        extra_info = 'P0'
        line1 = score_sheet.split('\r')[0]
        for ww in ['班級百', '類組百', '年級百']:
            if ww in score_sheet:
                try:
                    if '學生個人成績單' in line1:
                        School = re.findall('^\s*(.*?)學生個人成績\r', score_sheet)[0]
                    else:
                        School = re.findall('^\s*(.*?)\r', score_sheet)[0]

                    for w in ['智育成績', '學科平均']:
                        if w in score_sheet:
                            s = re.findall(w+'(.*?)\r', score_sheet)[0]
                            T = re.findall(r'\d{1,3}\.?\d{0,2}', s)
                            if len(T) != 24: raise
                            LL = [round(float(T[i]) * 0.01, 4) for i in [3,7,10,13,16]]
                            if ww == '年級百':
                                LL = [np.nan] * 10 + LL
                            elif ww == '類組百':
                                LL = [np.nan] * 5 + LL + [np.nan] * 5
                            else:
                                LL = LL + [np.nan] * 10
                            return [IID, SID, SName, School] + LL + [extra_info + '_1']

                except:
                    extra_info += ' manual work is required!!'
                    return [IID, SID, SName, ''] + [np.nan] * 15 +[extra_info]

        if '學業成績' in score_sheet:
            try:
                School = re.findall('^\s*(.*?)\r', score_sheet)[0]
                extra_info += '_2'
                s = re.findall('學業成績(.*?)\r', score_sheet)[0] + ' '
                L = re.findall(r'\s(\d+)\s', s)
                if len(L) != 3: raise
                LL = [round(int(L[0])*0.01, 4)]*5 + [round(int(L[1])*0.01, 4)]*5 + [int(L[2])*0.01] * 5
                return [IID, SID, SName, School] + LL + [extra_info]
            except:
                extra_info += ' manual work is required!!'
                return [IID, SID, SName, ''] + [np.nan] * 15 +[extra_info]
        else:
            extra_info += ' manual work is required!!'
            return [IID, SID, SName, ''] + [np.nan] * 15 +[extra_info]




class Parser_1(ScoreSheetParser):

    @classmethod
    def parse_info(cls, PDF, FilePath):
        # try:
        score_sheet = PDF[2]
        IID, SID, SName = cls.parse_generic_info(PDF, FilePath)
        School = re.findall(r'^\s*(.*?)個人成績單', score_sheet)[0]
        extra_info = 'P1'

        if '年級排名百分' in score_sheet:
            CL = cls.parse_001(PDF)
            s0 = re.findall(r'年級排名百分.*三上\s*\d*', score_sheet)[0]
            YL = [round(int(n) * 0.01, 4) for n in re.findall(r'(\d{1,3})', s0)]
        elif '班級排名百分' in score_sheet:
            s0 = re.findall(r'班級排名百分.*三上\s*\d*', score_sheet)[0]
            CL = [round(int(n) * 0.01, 4) for n in re.findall(r'(\d{1,3})', s0)]
            YL = [np.nan] * 5
        else:
            CL = cls.parse_001(PDF)
            YL = [np.nan] * 5

        return [IID, SID, SName, School] + CL + [np.nan] * 5 + YL + [extra_info]

    @staticmethod
    def parse_001(PDF):
        if '學業平均' in PDF[2]:
            ss = PDF[2]
        else:
            ss = PDF[3]
        s = re.findall(r'學業平均(.*?)\r', ss)[0]
        s0 = re.findall(r'(\d{1,3}\.?\d{0,2})', s)
        N = int(re.findall(r'班級人數..(\d*?)\r', ss)[0])

        if len(s0) in [20, 21, 23]:
            return [round(int(s0[i]) / N, 4) for i in [2, 5, 8, 11, 14]]
        elif len(s0) == 26:
            return [round(int(s0[i]) / N, 4) for i in [2, 6, 10, 14, 18]]
        else:
            return [np.nan] * 5


class Parser_2(ScoreSheetParser):

    @classmethod
    def parse_info(cls, PDF, FilePath):
        # try:
        score_sheet = PDF[2]
        IID, SID, SName = cls.parse_generic_info(PDF, FilePath)
        School = 'Requires Manual Check (文字亂碼)'
        extra_info = 'P2'
        for gb in ['學國學學/班百分比', '學職學學/班百身比', '學學學學/班百分比', '學業學學/班百分比', '學業成績/班百分比']:
            if gb in score_sheet:
                CL = [round(float(s) * 0.01, 4) for s in re.findall(gb + '\s+.*?\s+(\d{1,3}\.\d{0,2})', score_sheet)[0:5]]
                break
        else:
            CL = [np.nan] * 5
        for gb in ['組百身比', '組百分比']:
            if gb in score_sheet:
                TL = [round(float(s) * 0.01, 4) for s in re.findall(gb + '\s+(\d{1,3}\.\d{0,2})', score_sheet)[0:5]]
                break
        else:
            TL = [np.nan] * 5
        for gb in ['學國百分比', '學私百分比', '年級百分比', '學國百身比', '學級百身比', '學揚百身比', '學興百身比', '學級百分比']:
            if gb in score_sheet:
                YL = [round(float(s) * 0.01, 4) for s in re.findall(gb + '\s+(\d{1,3}\.\d{0,2})', score_sheet)[0:5]]
                break
        else:
            YL = [np.nan] * 5

        return [IID, SID, SName, School] + CL + TL + YL + [extra_info]


class Parser_3(ScoreSheetParser):

    @classmethod
    def parse_info(cls, PDF, FilePath):
        score_sheet = PDF[2]
        IID, SID, SName = cls.parse_generic_info(PDF, FilePath)
        School = re.findall(r'\s(\w*)\s*申請入學', score_sheet)[0]
        extra_info = 'P3'
        if '學業成績' not in score_sheet:
            score_sheet = PDF[3]
        s = re.findall('學業成績.*?\r', score_sheet)[0]
        # s = re.findall('學業成績.*\r\s*\d?.*\r', score_sheet)[0] # parse to next line in order to make special case works
        TL = re.findall('(\d{1,3}\.?\d{0,2})', s)
        if len(TL) != 35:
            extra_info += ' Manual Check! Rare Special Cases(lacking semester or become two lines...)'
            return [IID, SID, SName, School] + [np.nan]*15 + [extra_info]
        return [IID, SID, SName, School] + [round(float(TL[i])*0.01, 4) for i in
                                            [4, 11, 18, 25, 32, 5, 12, 19, 26, 33, 6, 13, 20, 27, 34]] + [extra_info]


class Parser_4(ScoreSheetParser):

    @classmethod
    def parse_info(cls, PDF, FilePath):
        score_sheet = PDF[2]
        IID, SID, SName = cls.parse_generic_info(PDF, FilePath)
        School = ""
        extra_info = 'P4 Encrypted File!! Manual work is unavoidable... '
        return [IID, SID, SName, School] + [np.nan]*15 + [extra_info]


class Parser_5(ScoreSheetParser):

    @classmethod
    def parse_info(cls, PDF, FilePath):
        score_sheet = PDF[2]
        IID, SID, SName = cls.parse_generic_info(PDF, FilePath)

        temp = re.findall(r'(.*?)\s.*?成績證明書', score_sheet)
        if temp[0]:
            extra_info = "P5-1 (桃園市新興高中?)"
            TT = re.findall(r'(\d{1,2})%', score_sheet)
            return [IID, SID, SName, temp[0]] + [round(int(TT[0])*0.01, 4)] * 5 + [round(int(TT[1])*0.01, 4)] * 5 + [np.nan] * 5 + [extra_info]

        School = re.findall(r'\s*(.*?)\s*成績證明書', score_sheet)[0]
        extra_info = 'P5-2 (新北市立板橋高中?)'
        s = re.findall('班級排名百分比.*?\r', score_sheet)[0]
        CL = [round(float(i) * 0.01, 4) for i in re.findall(r'\d{1,2}\.\d\d', s)]
        s = re.findall('校組排名百分比.*?\r', score_sheet)[0]
        TL = [round(float(i) * 0.01, 4) for i in re.findall(r'\d{1,2}\.\d\d', s)]
        return [IID, SID, SName, School] + CL + TL + [np.nan]*5 + [extra_info]


class Parser_6(ScoreSheetParser):

    @classmethod
    def parse_info(cls, PDF, FilePath):
        IID, SID, SName = cls.parse_generic_info(PDF, FilePath)
        score_sheet = PDF[2]
        School = re.findall(r'\s*(.*?)學生個人成績單', score_sheet)[0]
        extra_info = 'P6'
        for W in ['學科平均', '智育成績']:
            if W in PDF[2]:
                s = re.findall(W+'.*\r', score_sheet)[0]
                break
            elif W in PDF[3]:
                score_sheet = PDF[3]
                s = re.findall(W + '.*\r', score_sheet)[0]
                break
        else:
            return [IID, SID, SName, School] + [np.nan] * 15 + [extra_info+' strange']
        t = re.findall(r'\d{1,2}\.?\d{0,2}', s)
        return [IID, SID, SName, School] + [round(float(t[i])*0.01, 4) for i in [3, 9, 15, 21, 27, 5, 11, 17, 23, 29]] + [np.nan] * 5 + [extra_info]


class Parser_7(ScoreSheetParser):

    @classmethod
    def parse_info(cls, PDF, FilePath):
        IID, SID, SName = cls.parse_generic_info(PDF, FilePath)
        score_sheet = PDF[2]
        extra_info = 'P7'
        School = re.findall(r'\s*(.*?)\s*學生個人成績證明書', score_sheet)[0]
        LL = []
        s = re.findall('百分比(.*?)\r', score_sheet)
        if len(s) != 3:
            s = re.findall('百分比(.*?)\r', score_sheet+PDF[3])
        for ss in s:
            LL += [round(float(i)*0.01, 4) for i in re.findall(r'\d{1,3}', ss)]
        if len(s) == 2 and '班百分比' in score_sheet and '年百分比' in score_sheet:
            LL = LL[0:5]+[np.nan]*5+LL[5:]
        return [IID, SID, SName, School] + LL + [extra_info]


class Parser_8(ScoreSheetParser):

    @classmethod
    def parse_info(cls, PDF, FilePath):
        IID, SID, SName = cls.parse_generic_info(PDF, FilePath)
        score_sheet = PDF[2]
        extra_info = 'P8'
        LL = []

        if re.findall('\w高中部歷年成績單', score_sheet):
            extra_info += '-2'
            School = re.findall(r'\s*(.*?)高中部歷年成績單', score_sheet)[0]
            for w in ['原始成績班排名', '原始成績校排名']:
                s = re.findall(w + '(.*?)\r', score_sheet)[0]
                TL = re.findall(r'\s(\d+)\s', s + ' ')
                if len(TL) == 5:
                    LL += [float(i) * 0.01 for i in TL]
                else:
                    LL += [np.nan] * 5
            LL = LL[0:5] + [np.nan] * 5 + LL[5:]
        elif '學生成績證明書' in score_sheet:
            extra_info += '-3'
            School = re.findall(r'^\s*(.*?)\r', score_sheet)[0]
            for w in ['班級排名', '類組排名', '年級排名']:
                s = re.findall(w + '(.*?)\r', score_sheet)[0]
                TL = re.findall(r'\s(\d+)\s', s+' ')
                if len(TL) == 5:
                    LL += [round(float(i) * 0.01, 4) for i in TL]
                else:
                    LL += [np.nan] * 5
        else:
            extra_info += '-1'
            School = re.findall(r'^\s*(.*?)\s', score_sheet)[0]
            LL = []
            if '班級排名' in score_sheet:
                s = re.findall('[班|類|年].排名(.*?)\r', score_sheet)
            else:
                s = re.findall('各學期成績.排(.*?)\r', score_sheet)
            for ss in s:
                TL = re.findall(r'\s(\d+)\s', ss + ' ')
                if len(TL) == 5:
                    LL += [round(float(i) * 0.01, 4) for i in TL]
                else:
                    LL += [np.nan] * 5

        return [IID, SID, SName, School] + LL + [extra_info]


class Parser_9(ScoreSheetParser):

    @classmethod
    def parse_info(cls, PDF, FilePath):
        IID, SID, SName = cls.parse_generic_info(PDF, FilePath)
        score_sheet = PDF[2]
        extra_info = 'P9'
        School = re.findall('^\s*(.*?)學生個人',score_sheet)[0]
        W = ''
        for w in ['智育成績', '學科平均']:
            if w in score_sheet:
                W = w
                break
            if w in PDF[3]:
                score_sheet = PDF[3]
                W = w
                break
        s = re.findall(W+'(.*?)\r',score_sheet)[0]
        L =re.findall('\d{1,3}\.?\d{0,2}', s)
        if len(L) == 20:
            LL = [round(float(L[12])*0.01, 4)]*5 + [round(float(L[15])*0.01, 4)]*5 + [round(float(L[18])*0.01, 4)]*5
        else:
            extra_info += 'something wrong!! need manual check'
            LL = [np.nan]*15
        return [IID, SID, SName, School] + LL + [extra_info]


class Parser_10(ScoreSheetParser):

    @classmethod
    def parse_info(cls, PDF, FilePath):
        IID, SID, SName = cls.parse_generic_info(PDF, FilePath)
        score_sheet = PDF[2] if '學業平均' in PDF[2] else PDF[3]
        extra_info = 'P10'
        School = 'Manual is required'
        s = re.findall('學業平均(.*?)\r', score_sheet)[0]
        T = re.findall(r'\d{1,3}\.?\d{0,2}', s)
        if len(T) == 30:
            LL = [round(float(T[i]) * 0.01, 4) for i in [7, 12, 17, 22, 27, 9, 14, 19, 24, 29]] + [np.nan] * 5
        else:
            try:
                s += ' ' + re.findall('學業平均.*?\r\s*(.*?)\r', score_sheet)[0] + ' '
                T = re.findall('\d{1,3}\.?\d{0,2}', s)
                LL = [round(float(T[i]) * 0.01, 4) for i in [7, 12, 17, 22, 27, 9, 14, 19, 24, 29]] + [np.nan] * 5
            except:
                LL = [np.nan] * 15
                extra_info += ' Need manual'

        return [IID, SID, SName, School] + LL + [extra_info]


class Parser_11(ScoreSheetParser):

    @classmethod
    def parse_info(cls, PDF, FilePath):
        IID, SID, SName = cls.parse_generic_info(PDF, FilePath)
        extra_info = 'P11'
        School = re.findall('\s*(.*?)學生個人成績單', PDF[2])[0]
        W = ''
        score_sheet = PDF[2]
        for w in ['學科平均', '智育成績']:
            if w in score_sheet:
                W = w
                break
            if w in PDF[3]:
                score_sheet = PDF[3]
                W = w
                break
        s = re.findall(W + '(.*?)\r', score_sheet)[0]
        T = re.findall('\d{1,3}\.?\d{0,2}', s)
        if len(T) == 47:
            LL = [round(float(T[i])*0.01, 4) for i in [3, 11, 19, 27, 35, 6, 14, 22, 30, 38]]
            LL += [np.nan] * 5
        else:
            LL = [np.nan] * 15
            extra_info += ' Something wrong!'
        return [IID, SID, SName, School] + LL + [extra_info]


class Parser_12(ScoreSheetParser):

    @classmethod
    def parse_info(cls, PDF, FilePath):
        IID, SID, SName = cls.parse_generic_info(PDF, FilePath)
        extra_info = 'P12'
        School = re.findall('\s*(.*?)學生個人成績單', PDF[2])[0]
        W = ''
        score_sheet = PDF[2]
        for w in ['學科平均', '智育成績']:
            if w in score_sheet:
                W = w
                break
            if w in PDF[3]:
                score_sheet = PDF[3]
                W = w
                break
        s = re.findall(W + '(.*?)\r', score_sheet)[0]
        T = re.findall('\d{1,3}\.?\d{0,2}', s)
        if len(T) == 37:
            LL = [round(float(T[i])*0.01, 4) for i in [3, 9, 15, 21, 27, 5, 11, 17, 23, 30]]
            LL = LL[0:5] + [np.nan] * 5 + LL[5:]
        else:
            LL = [np.nan] * 15
            extra_info += ' Something wrong!'
        return [IID, SID, SName, School] + LL + [extra_info]


class Parser_13(ScoreSheetParser):

    @classmethod
    def parse_info(cls, PDF, FilePath):
        IID, SID, SName = cls.parse_generic_info(PDF, FilePath)
        extra_info = 'P13'
        School = '基隆市私立二信高級中學? Need double check!'
        score_sheet = PDF[2]
        s = re.findall('學業平均(.*?)\r', score_sheet)[0]
        T = re.findall(r'\d{1,3}[\./]?\d{0,2}', s)
        LL = [round(float(T[i]) * 0.01, 4) for i in [11, 18, 26, 33, 41, 15, 22, 30, 37, 45, 13, 20, 28, 35, 43]]
        return [IID, SID, SName, School] + LL + [extra_info]


class Parser_14(ScoreSheetParser):

    @classmethod
    def parse_info(cls, PDF, FilePath):
        IID, SID, SName = cls.parse_generic_info(PDF, FilePath)
        extra_info = 'P14'
        score_sheet = PDF[2]
        School = re.findall(r'學校：(.*?)\s', score_sheet)[0]
        LL = []
        for w in ['班', '組', '年級']:
            s = re.findall(w+'百(.*?)\r', score_sheet)
            if not s:
                LL += [np.nan]*5
                continue
            T = re.findall(r'(\d{1,3}\.\d{1,2})', s[0])
            if w == '班':
                LL += [round(float(T[i]) * 0.01, 4) for i in [1, 3, 5, 7, 9]]
            else:
                LL += [round(float(t) * 0.01, 4) for t in T[:5]]
        return [IID, SID, SName, School] + LL + [extra_info]


class Parser_15(ScoreSheetParser):

    @classmethod
    def parse_info(cls, PDF, FilePath):
        IID, SID, SName = cls.parse_generic_info(PDF, FilePath)
        extra_info = 'P15'
        score_sheet = PDF[2]
        School = re.findall(r'^\s*(.*?)\s', score_sheet)[0]
        s = re.findall(r'學業平均(.*?)\r', score_sheet)[0]
        T = re.findall(r'(\d{1,3}[\./]?\d{0,2})', s)
        if len(T) == 33:
            LL = [round(float(T[i]) * 0.01, 4) for i in [12, 16, 21, 25, 30, 7, 7, 7, 7, 7, 5, 5, 5, 5, 5]]
        elif len(T) == 28:
            LL = [round(float(T[i]) * 0.01, 4) for i in [12, 15, 19, 22, 26, 7, 7, 7, 7, 7, 5, 5, 5, 5, 5]]
        else:
            LL = [np.nan] * 15
            extra_info += '_Error!!'
        return [IID, SID, SName, School] + LL + [extra_info]

class Parser_16(ScoreSheetParser):

    @classmethod
    def parse_info(cls, PDF, FilePath):
        IID, SID, SName = cls.parse_generic_info(PDF, FilePath)
        extra_info = 'P16 - image file! No way to parse!'
        return [IID, SID, SName] + [np.nan] * 16 + [extra_info]


class Parser_17(ScoreSheetParser):

    @classmethod
    def parse_info(cls, PDF, FilePath):
        IID, SID, SName = cls.parse_generic_info(PDF, FilePath)
        extra_info = 'P17'
        score_sheet = PDF[2]
        try:
            School = re.findall(r'學校：\s?(.*?)\s', score_sheet)[0]
        except:
            School = ''
            extra_info += '_ need to add back school!'
        LL = []
        F = False
        for w in ['班', '組', '年級']:
            s = re.findall(w + '百分(.*?)\r', score_sheet)
            if not s:
                LL += [np.nan] * 5
                extra_info += " need to double check if some data really isn't there"
                continue
            T = re.findall(r'(\d{1,3}\.?\d{0,2})', s[0])
            if len(T) == 12:
                T = [T[i] for i in [1, 3, 5, 7, 9]]
            LL += [round(float(i) * 0.01, 4) for i in T[:5]]

        return [IID, SID, SName, School] + LL + [extra_info]


class Parser_18(ScoreSheetParser):

    @classmethod
    def parse_info(cls, PDF, FilePath):
        IID, SID, SName = cls.parse_generic_info(PDF, FilePath)
        extra_info = 'P18'
        score_sheet = PDF[2]
        School = re.findall('^\s*(.*?)\r', score_sheet)[0]
        LL = []
        for s in re.findall('..排名/..人數?(.*?)\r', score_sheet):
            LL += [round(eval(i), 4) if '/0' not in i else np.nan for i in re.findall(r'\d{1,3}/\d{1,3}', s)[:5]]
        if len(LL) != 15:
            LL += [np.nan] * (15-len(LL))
            extra_info += '_ missing some value!! need double check!'
        return [IID, SID, SName, School] + LL + [extra_info]
"""
required columns:
系所代碼、准考證、姓名、學校、一上~三上班排、一上~三上組排、一上~三上校排、Group ID
"""



if __name__ == '__main__':
    gdata = pd.read_csv('ExampleGroups.csv')
    g = gdata[gdata['Group'] == 11]
    L = []
    for f in tqdm(g.FilePath):
        # print(f)
        with open(f, 'rb') as ff:
            pdf = pdftotext.PDF(ff)
        L.append(Parser_11.parse_info(PDF=pdf, FilePath=f) + [f])
    pd.DataFrame(L).to_csv('DevG11.csv')
