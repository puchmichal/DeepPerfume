import pandas as pd
import re
#import spacy
#import en_core_web_sm
from gensim.models import KeyedVectors

# FUNCTIONS

def remove_brands_and_product_names(data_all, raw_text):
    
    for brand in data_all["brand"]:
        try:
            if brand.lower() in raw_text:
                raw_text = raw_text.replace(' ' + brand.lower() + ' ', ' ')
        except AttributeError:
            pass
        
    for product_name in data_all["product_name"]:
        try:
            if product_name.lower() in raw_text:
                raw_text = raw_text.replace(' ' + product_name.lower() + ' ', ' ')
        except AttributeError:
            pass
        
    return(raw_text)
    
def remove_punctuation(raw_text):
    return(re.sub(r'[^\w\s]','',raw_text))

def vectorize_text(raw_text, model):
    
    vectorized_text = []
    not_in_vocab = []
    in_vocab = []
    
    for x in raw_text.split(' '):
        try:
            vectorized_text.append(model[x])
            in_vocab.append(x)
        except KeyError:
            not_in_vocab.append(x)
            
    return(vectorized_text, not_in_vocab, in_vocab)
    
# loading data 
    
data_all = pd.read_csv("raw_data.csv") 
df = pd.read_csv("preprocessed_data.csv", encoding="utf-8-sig")

# Load vectors from file - workaround as fastText bin can't be loaded 
# https://fasttext.cc/docs/en/crawl-vectors.html -> source of vecs

embedding_dict = KeyedVectors.load_word2vec_format('cc.pl.300.vec', 
                                          binary = False)
embedding_dict.save_word2vec_format('saved_model'+".bin", 
                                    binary = True)
model = KeyedVectors.load_word2vec_format('saved_model'+".bin", 
                                          binary = True)

# text transformation

raw_text = " ".join(df["0"].unique()).lower()

raw_text = remove_brands_and_product_names(data_all, raw_text)

raw_text = remove_punctuation(raw_text)

vectorized_text, not_in_vocab, in_vocab = vectorize_text(raw_text, model)

# check how many words we missed 

missed_words = len(not_in_vocab)

missed_unique_words = len(set(not_in_vocab))

included_words = len(in_vocab)

included_unique_words = len(set(in_vocab))

# we missed 3.67% of words 

perc = missed_words / (missed_words + included_words) * 100




    

    


