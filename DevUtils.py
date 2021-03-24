"""
Rewrite the parsers to increase completeness
1. Scan all files and group them
2. For each group create a parser
3. integrate the parsers to a better extensible format
"""

import pdftotext
import os
import jieba
import re
from sklearn.feature_extraction.text import TfidfVectorizer
from scipy.cluster.hierarchy import ward, dendrogram
from sklearn.cluster import AgglomerativeClustering
import matplotlib.pyplot as plt
from tqdm import tqdm
import pandas as pd
import random

"""
check groupps in all example files and return a path : group dict
"""


def ScanGroups():
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

    print(f'{len(NonFiles)} : {len(StrangeFiles)} : {len(files)}')

    ## run grouping
    SS = []
    for file in tqdm(files):
        with open(file, 'rb') as f:
            pdf = pdftotext.PDF(f)
            score_sheet = pdf[2]
        SS.append(" ".join(jieba.cut(re.sub(r"\W|\d[a-zA-Z]", '', score_sheet), cut_all=False)))
    print('Load file finished!')

    vect = TfidfVectorizer(min_df=1)
    tfidf = vect.fit_transform(SS)
    SS_sim_mat = (tfidf * tfidf.T).A
    linkage_matrix = ward(SS_sim_mat)

    # plt.figure(figsize=(20, 7))
    # dd = dendrogram(
    #     linkage_matrix,
    #     orientation='top',
    #     distance_sort='descending',
    #     show_leaf_counts=True,
    #     no_labels=True,
    #     color_threshold=15
    # )
    # plt.savefig("ViewExampleGroups.png", dpi=60)

    """
    N is roughly 19!
    Let's create Gourp Id for each file!!
    """
    cluster = AgglomerativeClustering(n_clusters=19, affinity='euclidean', linkage='ward')
    cluster.fit_predict(SS_sim_mat)
    f = open('ExampleGroups.csv', 'w')
    f.write('Group,FilePath\n')
    for i, file in enumerate(files):
        f.write(f'{cluster.labels_[i]},{file}' + '\n')
    f.close()

    # for p in NonFiles:
    #     print('******')
    #     print(p)
    #     [print(f) for f in os.listdir(p)]

'''
Generate the raw X file for training a group determination model!

Should collect vocabulary 
Use pipeline...
https://scikit-learn.org/stable/modules/generated/sklearn.feature_extraction.text.TfidfTransformer.html
'''
def GenerateXFile():
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
    SS = []
    for file in tqdm(files):
        with open(file, 'rb') as f:
            pdf = pdftotext.PDF(f)
            score_sheet = pdf[2]
        SS.append(" ".join(jieba.cut(re.sub(r"\W|\d|[a-zA-Z1-9]", '', score_sheet), cut_all=False)))

    vect = TfidfVectorizer(min_df=1)
    tfidf = vect.fit_transform(SS)
    features = vect.get_feature_names()
    with open('tokens.txt', 'w', encoding='utf-8') as f:
        f.write(str(features))



def show_group_info():
    gdata = pd.read_csv('ExampleGroups.csv')
    for i in range(19):
        print(f'{i}:{len(gdata[gdata["Group"] == i])}')



def open_random_group(group=0, ID=0, is_random=True):
    gdata = pd.read_csv('ExampleGroups.csv')
    g = gdata[gdata['Group'] == group]
    if is_random:
        f = g.iloc[random.randint(0, len(g) - 1)].FilePath
    else:
        if ID < len(g):
            f = g.iloc[ID].FilePath
        else:
            print('Error, in valid ID, open the first one!!')
            f = g.iloc[0].FilePath
    os.startfile(os.getcwd() + '/' + f)


if __name__ == '__main__':
    show_group_info()
    for i in range(10):
        open_random_group(17, i, True)
