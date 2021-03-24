import ScoreSheetParsers as SSP
import pickle
import os
import numpy as np
import pandas as pd
from tqdm import tqdm
from tqdm.contrib import tzip
import pdftotext
import jieba
import re
from sklearn.feature_extraction.text import TfidfVectorizer
'''
1. Which group this file is?
2. Parse them
3. Collect result and distribute unhandled files
4. Double Check result & Manual process unhandled files
5. Done!
'''

def GetFileGroup(folder):
    files = []
    invalid_dir = []
    for md in os.listdir(folder):
        for ld in os.listdir(f'{folder}/{md}'):
            p = f'{folder}/{md}/{ld}'
            file = f'{p}/{ld}.pdf'
            if os.path.exists(file):
                files.append(file)
            else:
                invalid_dir.append(p)

    with open('tokens.txt', 'r', encoding='utf-8') as ff:
        tokens = eval(ff.read())

    corpus = []
    for file in tqdm(files):
        with open(file, 'rb') as f:
            pdf = pdftotext.PDF(f)
            score_sheet = pdf[2]
        corpus.append(" ".join(jieba.cut(re.sub(r"\W|\d|[a-zA-Z]", '', score_sheet), cut_all=False)))

    Vect = TfidfVectorizer(vocabulary=tokens)
    X = Vect.fit_transform(corpus)
    with open('ScoreSheetGroupModel.pickle', 'rb') as f:
        svm = pickle.load(f)
    G = svm.predict(X)

    return G, files, invalid_dir

def ParseFiles(group, files, invalid):

    Cols = ['系所代碼', '准考證號碼', '姓名', '學校', '一上班排百分', '一下班排百分', '二上班排百分', '二下班排百分', '三上班排百分',
            '一上組排百分', '一下組排百分', '二上組排百分', '二下組排百分', '三上組排百分', '一上校排百分', '一下校排百分', '二上校排百分',
            '二下校排百分', '三上校排百分', 'ParserInfo', 'FilePath']
    L = []
    for g, f in tzip(group, files):
        with open(f, 'rb') as ff:
            pdf = pdftotext.PDF(ff)
        try:
            L.append(eval(f'SSP.Parser_{g}.parse_info(pdf, f)') + [f])
        except Exception as e:
            print(f, g, e)
            L.append(list(SSP.ScoreSheetParser.parse_generic_info(pdf, f)) + [np.nan] * 16 + [f"Parser {g} failed! Or it's a new pattern!? ", f])
    for f in invalid:
        t = f.split('/')
        L.append([t[1], t[2]]+[np.nan]*17+['Raw File Not Exist!!', f])
    data = pd.DataFrame(L)
    data.columns = Cols
    data.to_csv('Out.csv', index=False)



if __name__ == '__main__':
    # Good the group is at least correct! (its from same data set... they must be correct!)
    G, valid_files, invalids = GetFileGroup('Data/109')
    ParseFiles(G, valid_files, invalids)