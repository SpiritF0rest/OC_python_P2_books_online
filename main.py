from bs4 import BeautifulSoup
import csv
from pathlib import Path
import requests

product_header = ["product_page_url",
                  "universal_product_code",
                  "title",
                  "price_including_tax",
                  "price_excluding_tax",
                  "number_available",
                  "product_description",
                  "category",
                  "review_rating",
                  "image_url"]
products = []
product = []
product_url = "http://books.toscrape.com/catalogue/eragon-the-inheritance-cycle-1_153/index.html"
product_page = requests.get(product_url).content
product_html = BeautifulSoup(product_page, "html.parser")
product.append(product_url)
product.append(product_html.table.findAll("tr")[0].td.string)
product.append(product_html.h1.string)
product.append(product_html.table.findAll("tr")[3].td.string)
product.append(product_html.table.findAll("tr")[2].td.string)
if "In stock" in product_html.table.findAll("tr")[5].td.string:
    product.append(product_html.table.findAll("tr")[5].td.string.split("(")[1].split(" ")[0])
product.append(product_html.find("article", class_="product_page").findAll("p")[3].string)
product.append(product_html.find("ul", class_="breadcrumb").findAll("a")[2].string)
product.append(product_html.find("p", class_="star-rating")["class"][1])
product.append(product_html.find("div", class_="item active").find("img")["src"])
products.append(product)

with open("products.csv", "w") as f:
    writer = csv.writer(f, delimiter=",")
    writer.writerow(product_header)
    if products[0]:
        for product in products:
            writer.writerow(product)