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

categories_list = []
products_final_url_list = []
category_url_start_frame = "http://books.toscrape.com/catalogue/category/books/"
home_url = "http://books.toscrape.com/index.html"


def get_all_categories():
    home_page = requests.get(home_url).content
    home_html = BeautifulSoup(home_page, "html.parser")
    all_categories_a = home_html.find("div", class_="side_categories").findAll("a")
    for category in all_categories_a[1:]:
        categories_list.append(category["href"].split("/")[3])


def get_product_information(product_url):
    print("step 3")
    print(product_url)
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


def get_products_url_for_one_category(category_page_url, category):
    print("step 1")
    print(category_page_url)
    category_page = requests.get(category_page_url).content
    category_html = BeautifulSoup(category_page, "html.parser")
    products_url = category_html.findAll("div", class_="image_container")
    products_list_url = []
    for product in products_url:
        products_list_url.append(product.a["href"].split("../")[-1])
    for product in products_list_url:
        products_final_url_list.append("http://books.toscrape.com/catalogue/" + product)
    if category_html.find("li", class_="next"):
        if not category_html.find("li", class_="previous"):
            next_category_url = category_url_start_frame + category + "/page-2.html"
        else:
            next_category_index_page = int(category_page_url.split("/page-")[1].split(".html")[0]) + 1
            next_category_url = category_url_start_frame + category + "/page-" + f"{next_category_index_page}" + ".html"
        get_products_url_for_one_category(next_category_url, category)
    return products_final_url_list


def get_products_info_for_one_category(products_url):
    print("step 2")
    print(products_url)
    products = []
    products.append(product_header)
    for product_url in products_url:
        product_info = get_product_information(product_url)
        products.append(product_info)
    return products


def get_all_products_info():
    print("step 0")
    get_all_categories()
    all_products = []
    for category in categories_list:
        category_url = category_url_start_frame + category + "/index.html"
        all_products.append({"category": category, "products_list": get_products_info_for_one_category(get_products_url_for_one_category(category_url, category))})
        products_final_url_list.clear()
    return all_products


def create_csv_files():
    for category in get_all_products_info():
        print(category)
        with open(f"{category['category']}.csv", "w") as f:
            writer = csv.writer(f, delimiter=";")
            if category["products_list"][0]:
                for product in category["products_list"]:
                    writer.writerow(product)
            else:
                print("There's no product in this category!")


create_csv_files()
