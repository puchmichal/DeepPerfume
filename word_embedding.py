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

def remove_tokens_with_no_value(raw_text):
    no_value = ['historia zapachu', 'skład zapachu',
    'właściwości: sposób użycia:świeczkę ustawiaj na powierzchniach odpornych na działanie temperatury.',
    'właściwości: sposób użycia:używaj zgodnie z załączoną instrukcją.',
    'właściwości: sposób użycia:wymień wkład zgodnie z załączoną instrukcją.',
    'właściwości: sposób użycia:nigdy nie pozostawiaj rozpuszczającego się wosku bez nadzoru i w pobliżu łatwopalnych przedmiotów.', 
    'nie pozostawiaj produktu w zasięgu dzieci lub zwierząt domowych.',
    'właściwości: sposób użycia:',
    'właściwości:',
    'opis:']
    for token in no_value:
        if token in raw_text:
            raw_text = raw_text.replace(token, ' ')
    return(raw_text)
    
def remove_punctuation_and_numbers(raw_text):
    # removing all numbers from the string with punctuation removed 
    return(re.sub(r'[0-9]+', '', re.sub(r'[^\w\s]','',raw_text)))



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

raw_text = remove_tokens_with_no_value(raw_text)

raw_text = remove_punctuation_and_numbers(raw_text)

vectorized_text, not_in_vocab, in_vocab = vectorize_text(raw_text, model)

# check how many words we missed 

missed_words = len(not_in_vocab)

missed_words_without_spaces = len([word for word in not_in_vocab if word != ''])

missed_unique_words = len(set(not_in_vocab))

included_words = len(in_vocab)

included_unique_words = len(set(in_vocab))

# we missed ~1.6% of words 

perc = missed_words_without_spaces / (missed_words_without_spaces + included_words) * 100



    

    


