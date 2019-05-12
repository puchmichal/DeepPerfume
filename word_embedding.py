import pandas as pd
#import spacy
#import en_core_web_sm
from gensim.models import KeyedVectors

# https://fasttext.cc/docs/en/crawl-vectors.html -> source of vecs

# Load vectors from file - workaround as fastText bin can't be loaded 

embedding_dict = KeyedVectors.load_word2vec_format('cc.pl.300.vec', 
                                          binary = False)
embedding_dict.save_word2vec_format('saved_model'+".bin", 
                                    binary = True)
model = KeyedVectors.load_word2vec_format('saved_model'+".bin", 
                                          binary = True)


df = pd.read_csv("preprocessed_data.csv", encoding="utf-8-sig")

whole_text = " ".join(df["0"].unique()).lower()
raw_text = whole_text

vectorized_text = []
not_in_vocab = []
in_vocab = []

for x in raw_text.split(' '):
    try:
        vectorized_text.append(model[x])
        in_vocab.append(x)
    except KeyError:
        not_in_vocab.append(x)
    
missed_words = len(raw_text.split(' ')) - len(vectorized_text)     
