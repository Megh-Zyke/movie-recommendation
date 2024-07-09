import requests
from PIL import Image
from io import BytesIO
import matplotlib.pyplot as plt

def search_images(query):
    base_url = "https://www.googleapis.com/customsearch/v1"
    params = {
        'key': "",
        'cx': "",
        'searchType': 'image',
        'q': query + " actor photo"
    }
    response = requests.get(base_url, params=params)
    result = response.json()

    if 'items' in result:
        return result['items'][0]['link']
    else:
        print("No images found.")
        return "https://as2.ftcdn.net/v2/jpg/05/00/84/67/1000_F_500846725_VMs8ukEZTccAa9emn7AnihPh1gwrBTxx.jpg"

