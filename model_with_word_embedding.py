from gensim.models import KeyedVectors
from keras.models import Sequential
from keras.layers import Dense
from keras.layers import Dropout
from keras.layers import LSTM
from keras.utils import np_utils
import pandas as pd
import numpy as np
import re

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


def vectorize_text(raw_text, embedding):
    
    vectorized_text = []
    not_in_vocab = []
    in_vocab = []
    
    for x in raw_text.split(' '):
        try:
            vectorized_text.append(embedding[x])
            in_vocab.append(x)
        except KeyError("nie ma slowa w slowniku"):
            not_in_vocab.append(x)
            
    return(vectorized_text, not_in_vocab, in_vocab)
    
# loading data 
    
data_all = pd.read_csv("raw_data.csv", encoding="utf-8-sig") 
df = pd.read_csv("preprocessed_data.csv", encoding="utf-8-sig")

whole_text = " ".join(df["0"]).lower()
raw_text = whole_text

# Load vectors from file - workaround as fastText bin can't be loaded 
# https://fasttext.cc/docs/en/crawl-vectors.html -> source of vecs

embedding_dict = KeyedVectors.load_word2vec_format('cc.pl.300.vec', 
                                          binary = False)
embedding_dict.save_word2vec_format('saved_embedding'+".bin", 
                                    binary = True)
embedding = KeyedVectors.load_word2vec_format('saved_embedding'+".bin", 
                                        binary = True)

# text transformation

raw_text = " ".join(df["0"].unique()).lower()

raw_text = remove_brands_and_product_names(data_all, raw_text)

raw_text = remove_tokens_with_no_value(raw_text)

raw_text = remove_punctuation_and_numbers(raw_text)

vectorized_text, not_in_vocab, in_vocab = vectorize_text(raw_text, embedding)


n_words = len(vectorized_text)
seq_length = 20 
dataX = np.zeros((n_words - seq_length, 20, 300))
dataY = np.zeros((n_words - seq_length, 300))

for i in range(0, n_words - seq_length):
	seq_in = vectorized_text[i:i + seq_length]
	seq_out = vectorized_text[i + seq_length]
	dataX[i, :, :] = np.array(seq_in)
	dataY[i, :] = seq_out
n_patterns = len(dataX)
print ("Total Patterns: ", n_patterns)

X = dataX
y = dataY

model = Sequential()
model.add(LSTM(64, input_shape=(X.shape[1], X.shape[2])))
#model.add(Dropout(0.2))
model.add(Dense(y.shape[1], activation='softmax'))
model.compile(loss='cosine_proximity', optimizer='adam')


model.fit(X, y, epochs=10, batch_size=10) 

start = np.random.randint(0, len(dataX)-1)
pattern = dataX[start]
print("Seed:")
print("\"", ''.join([embedding.most_similar(positive=[word], topn=1)[0][0] + " " for word in pattern]), "\"")
# generate characters
for i in range(30):
    x = np.reshape(pattern, (1, pattern.shape[0], pattern.shape[1]))
    prediction = model.predict(x, verbose=0)
    word_predicted = embedding.most_similar(positive=[prediction[0, :]], topn=1)[0][0]
    print(word_predicted + " ", end='')
    pattern = np.roll(pattern, -1)
    pattern[-1, :] = prediction[0, :]

model.save('model_with_embeddings.h5')