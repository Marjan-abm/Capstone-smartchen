"""
Module for the database class, MongoDB is used here.
"""
import pymongo
from pymongo import MongoClient
import os
from dotenv import load_dotenv
from scraper.utils import is_id_present
# from dotenv import cluster


# client = MongoClient(cluster)

# print(client.list_database_names())

# # db = client.test
# db = client.smartchen

# print(db.list_collection_names())

# RECIPE1 = {
#             'id': '1',
#             'name': 'Cake',
#             'description': 'My Cake',
#             'image url': 'https://m.ftscrt.com/static/recipe/d9f68f56.jpg',
#             'yields': '1',
#             'prep time': '1 mins',
#             'cook time': '2 mins'
#         }

# RECIPE2 = {
#             'id': '2',
#             'name': 'Fruit Juice',
#             'description': 'My Juice',
#             'image url': 'https://m.ftscrt.com/static/recipe/d9f68f56.jpg',
#             'yields': '1',
#             'prep time': '5 mins',
#             'meal types': [
#                 'drinks and beverages'
#             ],
#             'ingredients': [
#                 'water',
#                 'fruit'
#             ],
#             'instructions': [
#                 'Add water',
#                 'Add juice'
#             ]
#         }

# all_recipes = db.all_recipes #for adding collections to our database
# favorites = db.favorites
# result = all_recipes.insert_one(RECIPE1) #for adding data in our collections
# result = favorites.insert_one(RECIPE2)
# result = all_recipes.find_one()
# print(result)

# print(all_recipes.count_documents({}))


ALL_RECIPES = 0
FAVORITES = 1
ATTRIBUTES = {'id', 'image url', 'yields', 'prep time', 'cook time', 'meal types', 'name',
              'description', 'ingredients', 'instructions', 'popularity'}

# option 3 : https://www.fatsecret.com/recipes/invalid/Default.aspx
# https://www.fatsecret.com/recipes/banana-muffins/Default.aspx





class Database:
    """
    Database class that stores the database and tables using mongoDB.
    Support update and insert to the database.
    Check errors if document to insert is not valid.
    """

    def __init__(self):
        """
        Connect to database and initialize tables
        """
        load_dotenv()
        self.client = pymongo.MongoClient(os.getenv("cluster"))
        # self.client = pymongo.MongoClient(cluster)
        self.smartchen = self.client['smartchen']
        self.all_recipes = self.smartchen.all_recipes
        self.favorites = self.smartchen.favorites

    def is_recipe_exists_in_tb(self, recipe_dict, table_type):
        """
        Check whether recipe exists in all_recipes_table or favorites_table
        """
        recipe_id = recipe_dict['id']
        if table_type == ALL_RECIPES:
            recipe_info = self.all_recipes.find_one({'id': recipe_id})
        if table_type == FAVORITES:
            recipe_info = self.favorites.find_one({'id': recipe_id})
        if recipe_info:
            return True
        return False

    def update_on_tb(self, recipe_dict, table_type):
        """
        Update the table by recipe_dict

        Parameters:
        recipe_dict (dict): dict of recipe to update
        table (int): flag indicating the type of table in database, all_recipes or favorites
        """
        if not is_id_present(recipe_dict):
            print('Error: id is not found')
            return False
        # return False if recipe_dict not exists in table, cannot update
        if not self.is_recipe_exists_in_tb(recipe_dict, table_type):
            print('Cannot update table: recipe does not exist')
            return False
        recipe_id = recipe_dict['id']
        my_query = {'id': recipe_id}
        for attribute in recipe_dict.keys():
            # skip update id because id will not change
            if attribute == 'id':
                continue
            # check error of malformed data structure
            if attribute not in ATTRIBUTES:
                print(f'Malformed data structure: '
                      f'recipe with id {recipe_id} has invalid attribute {attribute}')
                continue
            if not recipe_dict[attribute]:
                print(f'Malformed data structure: '
                      f'recipe with id {recipe_id} has empty value for attribute {attribute}')
                continue
            # update valid attribute and value into food_recipes_table
            new_values = {'$set': {attribute: recipe_dict[attribute]}}
            if table_type == ALL_RECIPES:
                self.all_recipes.update_one(my_query, new_values)
                print(f'{attribute} entry of recipe with id {recipe_id} '
                      f'in all recipes table is updated')
            if table_type == FAVORITES:
                self.favorites.update_one(my_query, new_values)
                print(f'{attribute} entry of recipe with id {recipe_id} '
                      f'in favorites table is updated')
        return True

    def insert_into_tb(self, recipe_dict, table_type):
        """
        Insert recipe_dict into the table

        Parameters:
        recipe_dict (dict): dict of recipe to insert
        table (int): flag indicating the type of table in database, all_recipes_tb or favourites_tb
        """
        if not is_id_present(recipe_dict):
            print('Error: id is not found')
            return False
        # return False if recipe_dict exists in table, cannot insert
        if self.is_recipe_exists_in_tb(recipe_dict, table_type):
            print('Cannot insert into table: recipe already exists')
            return False
        to_insert = {}
        for attribute in recipe_dict.keys():
            # insert valid attributes and values into dict to_insert
            if attribute in ATTRIBUTES and recipe_dict[attribute]:
                to_insert[attribute] = recipe_dict[attribute]
        # insert to_insert to table in database
        recipe_id = recipe_dict['id']
        if table_type == ALL_RECIPES:
            self.all_recipes.insert_one(to_insert)
            print(f'recipe with id {recipe_id} is inserted into all recipes table')
        if table_type == FAVORITES:
            self.favorites.insert_one(to_insert)
            print(f'recipe with id {recipe_id} is inserted into favorites table')
        return True
