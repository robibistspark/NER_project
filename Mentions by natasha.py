from natasha import (
    Segmenter,
    MorphVocab,
    
    NewsEmbedding,
    NewsNERTagger,
    
    Doc,

    PER,
    NamesExtractor,
)

segmenter = Segmenter()
morph_vocab = MorphVocab()

emb = NewsEmbedding()
ner_tagger = NewsNERTagger(emb)

names_extractor = NamesExtractor(morph_vocab)

newspiece=input('Введите название .txt файла с текстом новости: ')
with open(newspiece, encoding='utf-8') as f:
    text=f.read()

doc = Doc(text)

doc.segment(segmenter)
doc.tag_ner(ner_tagger)

mentions_natasha=[]

for i in range(len(doc.spans)):
    if doc.spans[i].type == PER:
        mentions_natasha.append(doc.spans[i].text)