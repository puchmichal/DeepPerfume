import tqdm
from urllib.request import urlopen
from bs4 import BeautifulSoup
import pandas as pd

def generate_url_page(page_number):
  base_url = "https://www.iperfumy.pl/perfumy/"

  if page_number == 1:
    return base_url
  
  current_url = base_url + "?f=" + str(page_number) + "-1-6362"
  return current_url

scrapped_data = pd.DataFrame({"brand": [], "product_name": [], "image_link": [],
                              "description": [], "list_description": [],
                              "price": []})

page_number = 1
pbar = tqdm.tqdm(total = 439*24)

def scrap_link(link):
    pbar.update(1)

    try: 
        page = urlopen(link)
    except:
        print("Error opening the URL")
    soup = BeautifulSoup(page, 'html.parser')
    
    brand_and_product = soup.find_all("h1", {"itemprop": "name"})[0].find_all("span")
    
    brand_name = brand_and_product[0].text
    product_name = brand_and_product[1].text
    price = soup.find_all("div", {"id":"pd-price"})[0].find_all("span")[0].text
    
    main_description = ""
    list_description = ""

    try:
      description = soup.find_all("div", {"id": "pd-description-text"})[0]

      try:
          for paragraph in description.find_all("p"):
              main_description += paragraph.text + " "
          main_description = main_description[:-1]
      except:
          print("nie ma description" + " " + link)

      try:
          for bullet_point in description.find_all("li"):
              list_description += bullet_point.text + " "
          list_description = list_description[:-1]
      except:
          print("nie ma punktów" + " " + link)
    except:
        print("nie ma opisu" +" " + link)
    
    image = soup.find_all("img", {"id": "pd-image-main"})[0]["src"]
    
    scrapped_data.loc[scrapped_data.shape[0], :] = [brand_name, product_name, 
                     image, main_description, list_description, price]


while True:
    current_url = generate_url_page(page_number)
    try: 
        page = urlopen(current_url)
    except:
        print("Error opening the URL")
    soup = BeautifulSoup(page, 'html.parser')
    links_on_current_page = soup.find_all('a', {"class": "spc"})

    links = [str(link['href']) for link in links_on_current_page]

    for link in links:
        scrap_link(link)

    next_page = soup.find_all('a', {"class": "next"})

    if not next_page:
        break

    page_number += 1
pbar.close()


