from bs4 import BeautifulSoup
import csv
from urllib.parse import urljoin
import os
from pathlib import Path
from word2number import w2n
import requests


def get_all_categories(home_url):
    """Retrieve HTML anchors containing category URLs and names

    Args:
        home_url(str): Home page URL

    Returns:
        list: List of categories anchors (HTML)
    """
    home_page = requests.get(home_url).content
    home_html = BeautifulSoup(home_page, "html.parser")
    return home_html.find("div", class_="side_categories").findAll("a")


def transform_categories_data_to_dict(all_categories_data, home_url):
    """Build dict for each category with name and URL and add them in a list

    Args:
        all_categories_data(list): List of categories anchors (html)
        home_url(str): Home page URL

    Returns:
        list: List of all categories dict with name and URL
    """
    categories_list = []
    for category in all_categories_data[1:]:
        categories_list.append({
            "category_name": "_".join(category.string.strip().lower().split(" ")),
            "category_url": urljoin(home_url, category["href"])})
    return categories_list


def get_product_information(product_url):
    """Retrieve information for a product (via HTML) and inserts it into a dict

    Args:
        product_url(str): Product page URL

    Returns:
        dict: Product dictionary
    """
    print("Step 3: get information of a product")
    product = {}
    product_page = requests.get(product_url).content
    product_html = BeautifulSoup(product_page, "html.parser")
    product["product_page_url"] = product_url
    product["universal_product_code"] = product_html.table.findAll("tr")[0].td.string
    product["title"] = product_html.h1.string
    product["price_including_tax"] = product_html.table.findAll("tr")[3].td.string
    product["price_excluding_tax"] = product_html.table.findAll("tr")[2].td.string
    if "In stock" in product_html.table.findAll("tr")[5].td.string:
        product["number_available"] = product_html.table.findAll("tr")[5].td.string.split("(")[1].split(" ")[0]
    else:
        product["number_available"] = 0
    product["product_description"] = product_html.find("article", class_="product_page").findAll("p")[3].string
    product["category"] = product_html.find("ul", class_="breadcrumb").findAll("a")[2].string
    # w2n allows to transform the review rating's word into a number
    product["review_rating"] = w2n.word_to_num(product_html.find("p", class_="star-rating")["class"][1])
    # urljoin allows to construct a full URL by combining a "base URL" with another URL
    product["image_url"] = urljoin(product_url, product_html.find("div", class_="item active").find("img")["src"])
    return product


def get_products_url_for_one_category(category_page_url, category, products_final_url_list):
    """Retrieve the url of the products (via the HTML of the pages) of the same category

    Args:
        category_page_url(str): URL of the category's page
        category(str): Name of the category
        products_final_url_list(list): List of all product URL for this category

    Returns:
        list: List of all product URL for this category
    """
    print(f"Step 1: get products url of {category}")
    category_page = requests.get(category_page_url).content
    category_html = BeautifulSoup(category_page, "html.parser")
    products_url = category_html.findAll("div", class_="image_container")
    for product in products_url:
        products_final_url_list.append(urljoin(category_page_url, product.a["href"]))
    if category_html.find("li", class_="next"):
        next_category_url = urljoin(category_page_url, category_html.find("li", class_="next").a["href"])
        get_products_url_for_one_category(next_category_url, category, products_final_url_list)
    return products_final_url_list


def get_products_info_for_one_category(products_url):
    """Use get_product_information() to retrieve the info of each product via the URL list of products in a category

    Args:
        products_url(list): URL list of all products in one category

    Returns:
        list: List of all products (with all info) for a category
    """
    print("Step 2: get products info of category")
    products = []
    for product_url in products_url:
        product_info = get_product_information(product_url)
        products.append(product_info)
    return products


def get_all_products_info(categories):
    """Retrieve all information of all products of all categories

    Args:
        categories(list): List of all dict of categories

    Returns:
        list: List of dict containing each category name with all products for these categories
    """
    print("Step 0: start get all products info process")
    all_products = []
    for category in categories:
        products_final_url_list = []
        all_products.append({
            "category": category["category_name"],
            "products_list": get_products_info_for_one_category(get_products_url_for_one_category(category["category_url"], category["category_name"], products_final_url_list))})
        products_final_url_list.clear()
    return all_products


def create_files_tree(categories):
    """Create directories tree for csv and images files

    Args:
        categories(list): List of all dict of categories
    """
    current_path = Path.cwd()
    directories = [os.path.join(current_path, "Csv"), os.path.join(current_path, "Images")]
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
    for category in categories:
        category_path = os.path.join(f"{current_path}/Images", category["category_name"])
        os.makedirs(category_path, exist_ok=True)


def create_csv_files(all_products):
    """Create csv files for each category, each file contains a header and all products info by category

    Args:
        all_products(list): List of dict containing each category name with its products list
    """
    print("Step 4: create csv file")
    for category in all_products:
        with open(f"Csv/{category['category']}.csv", "w") as f:
            if category["products_list"][0]:
                writer = csv.DictWriter(f, fieldnames=category["products_list"][0], delimiter=";")
                writer.writeheader()
                writer.writerows(category["products_list"])
            else:
                f.write("There is no product in this category.")


def download_images_product(all_products):
    """Download each image of all products by category and put them in the corresponding directories

    Args:
        all_products(list): List of dict containing each category name with its products list

    Returns:

    """
    for category in all_products:
        print(f"Step 5: download {category['category']} images")
        for product in category["products_list"]:
            image = requests.get(product["image_url"]).content
            with open(f"Images/{category['category']}/{product['product_page_url'].split('/')[-2].split('_')[0]}.jpg", "wb") as f:
                f.write(image)


if __name__ == '__main__':
    home_url = "http://books.toscrape.com/index.html"
    categories_data = get_all_categories(home_url)
    categories = transform_categories_data_to_dict(categories_data, home_url)
    products = get_all_products_info(categories)
    create_files_tree(categories)
    create_csv_files(products)
    download_images_product(products)

