from urllib.request import urlopen

import pandas as pd
import tqdm
from bs4 import BeautifulSoup


# functions
def generate_url_page(page_no):
    base_url = "https://www.iperfumy.pl/perfumy/"

    if page_no == 1:
        return base_url

    url = base_url + "?f=" + str(page_no) + "-1-6362"
    return url


def scrap_link(link):
    loading_bar.update(1)

    perfume_page = urlopen(link)

    perfume_soup = BeautifulSoup(perfume_page, 'html.parser')
    
    brand_and_product = perfume_soup.find_all("h1", {"itemprop": "name"})[0].find_all("span")
    
    brand_name = ""
    product_name = ""
    
    try:
        brand_name = brand_and_product[0].text
    except: 
        print("nie ma brandu" + " " + link)
    
    try:
        product_name = brand_and_product[1].text
    except:
        print("nie ma nazwy produktu" + " " + link)
        
    price = perfume_soup.find_all("div", {"id": "pd-price"})[0].find_all("span")[0].text

    main_description = ""
    list_description = ""

    try:
        description = perfume_soup.find_all("div", {"id": "pd-description-text"})[0]

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
        print("nie ma opisu" + " " + link)

    fragrance_group = ""

    try:
        fragrance_information = perfume_soup.find_all("div", {"id": "pdCharacteristics"})[0]
        fragrance_group = fragrance_information.find_all("dd")[-1].text
    except:
        print("nie ma grupy zapachowej" + " " + link)

    image = perfume_soup.find_all("img", {"id": "pd-image-main"})[0]["src"]

    scrapped_data.loc[scrapped_data.shape[0], :] = [brand_name, product_name,
                                                    fragrance_group, image, main_description,
                                                    list_description,
                                                    price]


# start scrapping
page_number = 1
loading_bar = tqdm.tqdm(total=439*24)

scrapped_data = pd.DataFrame({"brand": [], "product_name": [], "fragrance_group": [],
                              "image_link": [], "description": [], "list_description": [],
                              "price": []})

# looping over all pages with perfumes, each page 24 perfumes
while True:
    # creating url fot page_number-th page
    current_url = generate_url_page(page_number)

    # opening page
    page = urlopen(current_url)
    soup = BeautifulSoup(page, 'html.parser')

    # finding all links to perfume's pages
    links_on_current_page = soup.find_all('a', {"class": "spc"})
    links = [str(link['href']) for link in links_on_current_page]

    if page_number == 1:
        next_pages_links = soup.find("span", {"class": "pages"})
        number_of_pages = int(next_pages_links.find_all("a")[-2].text)
        loading_bar = tqdm.tqdm(total=number_of_pages*24, smoothing=0)

    # scrapping all information about each perfume
    for link in links:
        # scrapped data is appended to scrapped_data pandas
        scrap_link(link)

    # checking if there is another page, if not finish scrapping
    next_page = soup.find_all('a', {"class": "next"})

    if not next_page:
        break

    page_number += 1

loading_bar.close()

# saving scrapped data to csv
scrapped_data.to_csv("raw_data.csv")
