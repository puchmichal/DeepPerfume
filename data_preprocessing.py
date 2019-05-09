from math import ceil

import pandas as pd
from nltk import tokenize

data = pd.read_csv("raw_data.csv", encoding="utf-8-sig")

# splitting data into full and bullet descriptions
full_description = data["description"]
full_description = full_description[~full_description.isna()]

bullet_description = data["bullet_description"]
bullet_description = bullet_description[~bullet_description.isna()]



# cutting descriptions into max two sentences observation
#
two_sentences_data = []
for index in range(len(full_description)):
    row = full_description.iloc[index]
    # nltk.download("punkt")
    sentences = tokenize.sent_tokenize(row)
    for i in range(ceil(len(sentences)/2)):
        if i == len(sentences)//2:
            two_sentences_data.append((sentences[2*i]).strip("Skład zapachu"))
        else:
            two_sentences_data.append(
                (sentences[2*i] + " " + sentences[2*i + 1]).strip("Skład zapachu"))

for i in range(len(bullet_description)):
    sentence = bullet_description.iloc[i]
    sentence = sentence[0].upper() + sentence[1:]
    sentence = sentence + "."
    two_sentences_data.append(sentence)

pd.DataFrame(two_sentences_data).to_csv(
    "preprocessed_data.csv",
    encoding="utf-8-sig",
    index=False,
)





