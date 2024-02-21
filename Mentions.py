from re import sub,finditer
from pymystem3 import Mystem
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

#%% Mentions

newspiece=input('Введите адрес .txt файла с текстом новости: ')
with open(newspiece, encoding='utf-8') as f:
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

mentions=[]

for i in list_re1:
    print(main(i['find'],i['span'],text,0,jobs_l,sp_v,names))
    if main(i['find'],i['span'],text,0,jobs_l,sp_v,names)[1] >= 4:
        mentions.append(main(i['find'],i['span'],text,0,jobs_l,sp_v,names)[0])

for i in list_re2:
    print(main(i['find'],i['span'],text,1,jobs_l,sp_v,names))
    if main(i['find'],i['span'],text,1,jobs_l,sp_v,names)[1] >= 4:
        mentions.append(main(i['find'],i['span'],text,1,jobs_l,sp_v,names)[0])