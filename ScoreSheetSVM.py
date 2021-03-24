import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
import jieba
import pdftotext
from tqdm import tqdm
import re
import os
from sklearn import svm
from sklearn.metrics import accuracy_score
import random
import pickle

with open('features.txt', 'r', encoding='utf-8') as f:
    tokens = eval(f.read())

files = []
StrangeFiles = []
NonFiles = []
example_folders = ['Data/107', 'Data/108', 'Data/109']
for td in example_folders:
    for md in os.listdir(td):
        for ld in os.listdir(f'{td}/{md}'):
            p = f'{td}/{md}/{ld}'
            file = f'{p}/{ld}.pdf'
            if os.path.exists(file):
                files.append(file)
            elif len(os.listdir(p)) == 1:
                StrangeFiles.append(f'{p}/{os.listdir(p)[0]}')
            else:
                NonFiles.append(p)

corpus = []
for file in tqdm(files):
    with open(file, 'rb') as f:
        pdf = pdftotext.PDF(f)
        score_sheet = pdf[2]
    corpus.append(" ".join(jieba.cut(re.sub(r"\W|\d|[a-zA-Z]", '', score_sheet), cut_all=False)))

G = np.array(pd.read_csv('ExampleGroups.csv').Group.tolist())

Vect = TfidfVectorizer(vocabulary=tokens)
X = Vect.fit_transform(corpus)

Seed = set()
while len(Seed) < 500:
    Seed.add(random.randint(0, 2499))

TestSeed = list(Seed)
TrainSeed = list(set(range(2500)).difference(Seed))
for i in range(2500):
    if i not in TestSeed:
        TrainSeed.append(i)

TrainX = X[TrainSeed]
TrainY = G[TrainSeed]
TestX = X[TestSeed]
TestY = G[TestSeed]

# SVM

SVM = svm.SVC(C=1.0, kernel='linear', degree=3, gamma='auto')
SVM.fit(TrainX, TrainY)

Prediction = SVM.predict(TestX)
print(f'ACC: {accuracy_score(Prediction, TestY)*100}')


SS_Model = svm.SVC(C=1.0, kernel='linear', degree=3, gamma='auto')
SS_Model.fit(X, G)

with open('ScoreSheetGroupModel.pickle', 'wb') as f:
    pickle.dump(SS_Model, f)
