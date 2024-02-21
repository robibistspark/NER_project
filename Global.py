from os import walk
from re import sub,finditer
from pymystem3 import Mystem
from json import dump
from functions.process_cluster import process_cluster
from functions.main import main

m = Mystem()

# Gazetteers
jobs_l=[]

with open('../gazetteers/jobs.txt',encoding='utf-8') as f:
    for i in f:
        if i.strip().endswith('а') or i.strip().endswith('ь'):
            jobs_l.append(i.strip()[:-1].lower())
        else:
            jobs_l.append(i.lower().strip())

names=set()

with open('../gazetteers/russian_surnames.csv',encoding='utf-8') as f:
    f.readline()
    for i in f:
        if i.split(';')[1][0] == i.split(';')[1][0].upper():
            if i.split(';')[1].endswith('а') or i.split(';')[1].endswith('ь') or i.split(';')[1].endswith('й')\
            or i.split(';')[1].endswith('я'):
                if len(i.split(';')[1][:-1]) > 3:
                    names.add(i.split(';')[1][:-1])
            else:
                if len(i.split(';')[1]) > 3:
                    names.add(i.split(';')[1])

with open('../gazetteers/russian_names.csv', encoding='utf-8') as f:
    f.readline()
    for i in f:
        if i.split(';')[1][0] == i.split(';')[1][0].upper():
            if i.split(';')[1].endswith('а') or i.split(';')[1].endswith('ь') or i.split(';')[1].endswith('й')\
            or i.split(';')[1].endswith('я'):
                if len(i.split(';')[1][:-1]) > 3:
                    names.add(i.split(';')[1][:-1])
                else:
                    if len(i.split(';')[1]) > 3:
                        names.add(i.split(';')[1])

sp_v=[]

with open('../gazetteers/verbs.csv', encoding='utf-8') as f:
    f.readline()
    for i in f:
        if i.split(';')[1].endswith('ся'):
            a=i.split(';')[1][:-5]
        else:
            a=i.split(';')[1][:-3]
        if len(a) > 3:
            sp_v.append(a)

# Global

for root,j,k in walk('../texts'):
    files=k

for newspiece in files:
    with open(root+'/'+newspiece, encoding='utf-8') as f:
        text=f.read().strip()
    
    text=sub('\n+',' ',text)
    
    nice_text=text
    punct=',!"?/;:()[]«»'
    
    text=text.replace('/',' ')
    text=text.replace(' - ',' ')
    text=text.replace(' – ',' ')
    text=text.replace(' — ',' ')
    text=sub('"\w+"','',text)
    text=sub('\s+',' ',text)
    
    for i in punct:
        text=text.replace(i,'')
    
    
    re1=finditer('\s([А-Я][а-я]+)(\s[^А-Я]|\.\s)',text)
    re2=finditer('(\s[А-Я][а-я]+){2,}(\s\w|.\s)',text)
    
    list_re1=[]
    list_re2=[]
    
    for i in re2:
            list_re2.append({'find':i.group().strip('. '),'span':i.span()})
    
    for i in re1:
        list_re1.append({'find':i.group(1),'span':i.span()})
    
    
    for i in range(len(list_re2)):
        if process_cluster(list_re2[i]['find']):
            list_re2[i]['find']=process_cluster(list_re2[i]['find'])
    
    for i in list_re1:
        for j in list_re2:
            if i['span'][1] == j['span'][1]:
                list_re1.remove(i)
    for i in list_re1:
        for j in list_re2:
            if i['span'][1] == j['span'][1]:
                list_re1.remove(i)
    
    mentions1=[]
    mentions2=[]
    
    for i in list_re1:
        if main(i['find'],i['span'],text,0,jobs_l,sp_v,names)[1] >= 4:
            mentions1.append(main(i['find'],i['span'],text,0,jobs_l,sp_v,names)[0])
    
    for i in list_re2:
        if main(i['find'],i['span'],text,1,jobs_l,sp_v,names)[1] >= 4:
            mentions2.append(main(i['find'],i['span'],text,1,jobs_l,sp_v,names)[0])
            
    # Groups
    lemmas1=[]
    lemmas2=[]
    
    for i in range(len(mentions1)):
        lemmas1.append(m.lemmatize(mentions1[i])[0])
    for i in range(len(mentions2)):
        lemmas2.append(''.join(m.lemmatize(mentions2[i])[:-1]))
    
    set1 = set(lemmas1)
    set2 = set(lemmas2)
    
    persons={}
    
    for i in set1:
        persons[i] = []
    for i in set2:
        persons[i] = []
    
    for i in range(len(lemmas1)):
        for j in range(len(lemmas2)):
            if lemmas1[i] in lemmas2[j]:
                persons[lemmas2[j]].append(mentions1[i])
                break
        else:
            persons[lemmas1[i]].append(mentions1[i])
    
    for i in range(len(lemmas2)):
        persons[lemmas2[i]].append(mentions2[i])
    
    l=[]
    
    for i,j in persons.items():
        if j == []:
            l.append(i)
    
    for i in l:
        del persons[i]
    
    with open(root+'/'+newspiece.replace('.txt',' PER.json'),'w',encoding='utf-8') as f:
        dump({'text':nice_text,'persons':persons}, f, indent='\t')