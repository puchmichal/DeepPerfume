import urllib.request
import pandas as pd
#import os 

raw_data = pd.read_csv("raw_data.csv") 

#os.chdir("C:\\Users\\Alicja Kocieniewska\\Desktop\\DeepPerfume\\images")

count_images = 1

for img in raw_data.image_link:
    try:
        urllib.request.urlretrieve(img, "image"+ str(count_images) + ".jpg")
        count_images += 1 
        print(f"Za nami {count_images} zdjęć!")
    except: 
        pass
        
