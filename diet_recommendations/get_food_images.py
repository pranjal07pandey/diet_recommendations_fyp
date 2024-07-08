import requests
from bs4 import BeautifulSoup

not_found_link=''

def get_images_links(searchTerm):
    try:
        searchUrl = f"https://www.google.com/search?q={searchTerm}&site=webhp&tbm=isch"
        d = requests.get(searchUrl).text
        soup = BeautifulSoup(d, 'html.parser')

        img_tags = soup.find_all('img')

        imgs_urls = []
        for img in img_tags:
            if img['src'].startswith("http"):
                imgs_urls.append(img['src'])

        return(imgs_urls[0])
    except:
        return not_found_link