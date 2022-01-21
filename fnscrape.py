import requests
from bs4 import BeautifulSoup
import os
import csv

def getSoup(url):
  page_res = requests.get(url)
  return BeautifulSoup(page_res.content, "html.parser")

def pullRecipe(url, name):
  print("Pulling: ", name)
  recipe_string = name
  page = getSoup(url)
  ingredient_body = page.find("div", class_="o-Ingredients__m-Body")
  ingredient_elements = ingredient_body.findAll("p", class_="o-Ingredients__a-Ingredient")
  print(ingredient_elements.prettify)
  ingredient_elements.pop(0)
  for elm in ingredient_elements:
    recipe_string += ", " + elm.text.strip()
  return recipe_string

def pullRecipes(url, subpage_count):
  print("starting recipe link extraction...")
  recipe_strings = list()
  for i in range(1, subpage_count + 1):
    try:
      subpage_url = url + "/p/" + str(i)
      subpage = getSoup(subpage_url)
      page_body = subpage.find("div", class_="o-Capsule__m-Body")
      links = page_body.findAll("a")
      print("Page " + str(i), end=" ")
      for link in links:
        recipe_strings.append(pullRecipe("https:" + link['href'], link.text))
      print("done")
    except Exception as err:
      print(err)

  print(" done")
  return recipe_strings


def extractPaginationCount(page):
  pagination_section = page.find("section", class_="o-Pagination")
  links = pagination_section.findAll("a")
  greatest = 0
  for link in links:
    text = link.text
    try:
      index = int(text)
      if index > greatest:
        greatest = index
    except:
      pass
  return greatest

def main():
  BASE_URL = "https://www.foodnetwork.com/recipes/recipes-a-z/"

  subpage_ids = list()
  subpage_ids.append('123')
  # for i in range(ord('a'), ord('b')):
  #   subpage_ids.append(chr(i))
  # subpage_ids.append('xyz')


  master_recipe_list = list()

  for elm in subpage_ids:
    print("reading " + elm + ": ")
    page_url = BASE_URL + elm
    page = getSoup(page_url)
    subpage_count = extractPaginationCount(page)
    recipes = pullRecipes(page_url, subpage_count)
    master_recipe_list += recipes

  with open(os.path.join(os.getcwd(), "recipes.txt"), "w") as file:
    for recipe in master_recipe_list:
      file.write(recipe + "\n")

def test():
  pullRecipe("https://www.foodnetwork.com/recipes/smores-cake-8603003", "S'mores Cake")

if __name__ == "__main__":
  test()


