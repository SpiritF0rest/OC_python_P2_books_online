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
# product_url = "http://books.toscrape.com/catalogue/eragon-the-inheritance-cycle-1_153/index.html"
# category_page_url = "http://books.toscrape.com/catalogue/category/books/fantasy_19/page-" + i + ".html"
category_page_url = "http://books.toscrape.com/catalogue/category/books/fantasy_19/page-2.html"


def get_product_information(product_url):
    product = []
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
    return product


def get_products_url_for_one_category_page(category_page_url):
    category_page = requests.get(category_page_url).content
    category_html = BeautifulSoup(category_page, "html.parser")
    products_url = category_html.findAll("div", class_="image_container")
    products_list_url = []
    products_final_url_list = []
    for product in products_url:
        products_list_url.append(product.a["href"].split("../")[-1])
    for product in products_list_url:
        products_final_url_list.append("http://books.toscrape.com/catalogue/" + product)
    return products_final_url_list


def get_products_info_for_one_category_page(products_url):
    for product_url in products_url:
        product_info = get_product_information(product_url)
        products.append(product_info)


get_products_info_for_one_category_page(get_products_url_for_one_category_page(category_page_url))


with open("products.csv", "w") as f:
    writer = csv.writer(f, delimiter=",")
    writer.writerow(product_header)
print(products)
for product in products:
    with open("products.csv", "a") as f:
        writer = csv.writer(f, delimiter=",")
        if products[0]:
                writer.writerow(product)
        else:
            print("There's no product!")
