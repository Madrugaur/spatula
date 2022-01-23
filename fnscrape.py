import requests
from bs4 import BeautifulSoup
import os
import csv
from pprint import pprint
import json


def getSoup(url):
    page_res = requests.get(url)
    return BeautifulSoup(page_res.content, "html.parser")


def pullIngredientsList(page):
    ingredient_body = page.find("div", class_="o-Ingredients__m-Body")
    if ingredient_body is None:
        raise Exception("Invalid Recipe Schema: missing ingredients")
    ingredient_elements = ingredient_body.findAll(
        "p", class_="o-Ingredients__a-Ingredient")
    ingredient_elements.pop(0)
    ingredients_list = list()
    for elm in ingredient_elements:
        ingredients_list.append(elm.text.strip())
    return ingredients_list


def convertToMinutes(time_text):
    tokens = time_text.split(" ")
    total = 0
    for i in range(0, len(tokens), 2):
        unit = tokens[i + 1]
        if unit == 'min':
            total += int(tokens[i])
        elif unit == "hr":
            total += int(tokens[i]) * 60
    return total


def pullCookTime(container):
    time_container = container.find("ul", class_="o-RecipeInfo__m-Time")
    components = time_container.find_all("li")
    if len(components) == 0:
        return -1
    if components[0].find("span", class_="o-RecipeInfo__a-Headline m-RecipeInfo__a-Headline--Total") is not None:
        return convertToMinutes(components[0].find("span", class_="o-RecipeInfo__a-Description m-RecipeInfo__a-Description--Total").text.strip())
    else:
        time_texts = [comp.find(
            "span", class_="o-RecipeInfo__a-Description").text.strip() for comp in components]
        total = 0
        for time_text in time_texts:
            total += convertToMinutes(time_text)
        return total


def pullRecipeInfo(page):
    recipe_info_container = page.find("div", class_="o-RecipeInfo")

    level_container = recipe_info_container.find(
        "ul", class_="o-RecipeInfo__m-Level")
    if level_container is None:
        level = "Medium"
    else:
        level = level_container.find(
            "span", class_="o-RecipeInfo__a-Description").text

    yield_container = recipe_info_container.find(
        "ul", class_="o-RecipeInfo__m-Yield")
    if yield_container is None:
        yield_ = "Unknown"
    else:
        yield_ = yield_container.find(
            "span", class_="o-RecipeInfo__a-Description").text

    cook_time = pullCookTime(recipe_info_container)
    return [level, yield_, cook_time]


def pullName(page):
    author_container = page.find("div", class_="o-Attribution__m-Author")
    if author_container is None:
        return "Unknown"
    author_text = author_container.text.strip()
    return author_text.replace("Recipe courtesy of ", "")


def pullTags(page):
    tag_section = page.find("section", class_="o-Capsule o-Tags")
    if tag_section is None:
        return []
    tag_links = tag_section.find_all("a", class_="o-Capsule__a-Tag a-Tag")
    return [link.text for link in tag_links]


def pullSpecialNote(page):
    try:
        special_section = page.find("section", class_="o-SpecialEquipment")
        return special_section.text.strip()
    except Exception as e:
        return ""


def pullSteps(page):
    steps_container = page.find("div", class_="o-Method__m-Body")
    if steps_container is None:
        raise Exception("Invalid Recipe Schema: missing directions")
    steps = steps_container.find_all("li")
    return [step.text.strip() for step in steps]


def pullRecipe(url, name):
    page = getSoup(url)
    level, yield_, cook_time = pullRecipeInfo(page)
    recipe_obj = {
        "name": name,
        "fully_qualified_name": url[url.index("recipes") + 8:],
        "description": name,
        "ingredients": pullIngredientsList(page),
        "level": level,
        "yield": yield_,
        "author": pullName(page),
        "categories": pullTags(page),
        "cook_time": cook_time,
        "steps": pullSteps(page),
        "special_note": pullSpecialNote(page)
    }
    return recipe_obj


def pullRecipes(url, subpage_count):
    print("starting recipe link extraction...")
    recipe_objs = list()
    for i in range(1, subpage_count + 1):
        subpage_url = url + "/p/" + str(i)
        subpage = getSoup(subpage_url)
        page_body = subpage.find("div", class_="o-Capsule__m-Body")
        links = page_body.findAll("a")
        header = " Page {0} of {1} ".format(str(i), str(subpage_count))
        dashes = "-" * int((82 - len(header)) / 2)
        print("{0:^82}".format(dashes + header + dashes))
        for link in links:
            try:
                recipe_objs.append(pullRecipe(
                    "https:" + link['href'], link.text))
                print("|{0: <10}{1:>70}|".format("✓ Pulled: ", link.text))
            except Exception as e:
                print("|✘ Failed: ", link.text, ", because", e, "|")
    return recipe_objs


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
    for i in range(ord('a'), ord('w') + 1):
        subpage_ids.append(chr(i))
    subpage_ids.append('xyz')

    master_recipe_list = list()

    for elm in subpage_ids:
        print("#" * 20, "Reading", elm, "#" * 20)
        page_url = BASE_URL + elm
        page = getSoup(page_url)
        subpage_count = extractPaginationCount(page)
        recipes = pullRecipes(page_url, subpage_count)
        master_recipe_list += recipes

    with open(os.path.join(os.getcwd(), "recipes.json"), "w") as file:
        json.dump(master_recipe_list, file)


def test():
    pullRecipe("https://www.foodnetwork.com/recipes/smores-cake-8603003",
               "Pacific Cod and Clam Cacciucco")


if __name__ == "__main__":
    main()
