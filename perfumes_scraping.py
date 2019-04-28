from urllib.request import urlopen

import pandas as pd
import tqdm
from bs4 import BeautifulSoup


# functions
def generate_url_page(page_no):
    base_url = "https://www.iperfumy.pl/perfumy/"

    if page_no == 1:
        return base_url
    # url pattern for each page except first
    url = base_url + "?f=" + str(page_no) + "-1-6362"
    return url


def scrap_link(link):
    loading_bar.update(1)

    perfume_page = urlopen(link)

    perfume_soup = BeautifulSoup(perfume_page, 'html.parser')
        
    try:
        brand_and_product = perfume_soup.find_all("h1", {"itemprop": "name"})[0].find_all("span")
        
        try:
            brand_name = brand_and_product[0].text
        except: 
            # if no brand name avaliable, empty string will be added
            brand_name = ""
            print("nie ma brandu w {}".format(link))
        
        try:
            product_name = brand_and_product[1].text
        except:
            # if no product name avaliable, empty string will be added
            product_name = ""
            print("nie ma nazwy produktu w {}".format(link))
    except:
        print("nie ma żadnej nazwy w {}".format(link))
        
    price = perfume_soup.find_all("div", {"id": "pd-price"})[0].find_all("span")[0].text
    
    # in case of missing information, empty strings will be added
    main_description = ""
    bullet_description = ""
    
    # caching all possible exceptions (missing brand, product or both)
    try:
        description = perfume_soup.find_all("div", {"id": "pd-description-text"})[0]

        try:
            # adding each paragraph to the descripton
            for paragraph in description.find_all("p"):
                main_description += paragraph.text + " "
        except:
            print("nie ma description w {}".format(link))

        try:
            # adding each bullet point to the descripton
            for bullet_point in description.find_all("li"):
                bullet_description += bullet_point.text + " "
        except:
            print("nie ma punktów w {}".format(link))
    except:
        print("nie ma opisu w {}".format(link))

    try:
        fragrance_information = perfume_soup.find_all("div", {"id": "pdCharacteristics"})[0]
        fragrance_group = fragrance_information.find_all("dd")[-1].text
    except:
        # if no fragrance group avaliable, empty string will be added
        fragrance_group = ""
        print("nie ma grupy zapachowej w {}".format(link))

    image = perfume_soup.find_all("img", {"id": "pd-image-main"})[0]["src"]
    
    # appending scrapped data to the data frame
    scrapped_data.loc[scrapped_data.shape[0], :] = [brand_name, product_name,
                                                    fragrance_group, image, main_description,
                                                    bullet_description,
                                                    price]


# start scrapping
page_number = 1
elements_on_page = 24

scrapped_data = pd.DataFrame({"brand": [], "product_name": [], "fragrance_group": [],
                              "image_link": [], "description": [], "bullet_description": [],
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
    
    # extracting all the links and converting them to the list
    links = list(map(lambda link: str(link['href']), links_on_current_page))
    
    if page_number == 1:
        next_pages_links = soup.find("span", {"class": "pages"})
        number_of_pages = int(next_pages_links.find_all("a")[-2].text)
        loading_bar = tqdm.tqdm(total=number_of_pages*elements_on_page, 
                                smoothing=0)

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
