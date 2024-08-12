import requests
from bs4 import BeautifulSoup

Not_found_link = 'https://static.vecteezy.com/system/resources/previews/005/337/799/original/icon-image-not-found-free-vector.jpg'

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

        return Not_found_link