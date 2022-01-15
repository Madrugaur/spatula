import requests
from bs4 import BeautifulSoup
import os
import csv
def getSoup(url):
  page_res = requests.get(url)
  return BeautifulSoup(page_res.content, "html.parser")

def pullRecipe(url, name):
  recipe_string = name
  page = getSoup(url)
  ingrediant_body = page.find("div", class_="o-Ingredients__m-Body")
  ingrediant_elements = ingrediant_body.findAll("p", class_="o-Ingredients__a-Ingredient")
  ingrediant_elements.pop(0)
  for elm in ingrediant_elements:
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
      print(str(i))
      for link in links:
        recipe_strings.append(pullRecipe("https:" + link['href'], link.text))
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

with open(os.path.join(os.getcwd(), "recipes.csv"), "w") as file:
  writer = csv.writer(file)
  for recipe in master_recipe_list:
    writer.writerow(recipe)

