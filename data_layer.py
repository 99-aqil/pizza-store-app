import json

#  RECIPE  MANAGEMENT
class Recipe:
    def __init__(self, name, category, ingredients):
        self.name = name
        self.category = category
        self.ingredients = ingredients

    def to_dict(self):
        return {'name': self.name, 'category': self.category, 'ingredients': self.ingredients}

class PizzaStore:
    def __init__(self):
        self.recipes = []

    def add_recipe(self, recipe):
        self.recipes.append(recipe)

    def delete_recipe(self, recipe):
        self.recipes.remove(recipe)

    def update_recipe(self, old_recipe, new_recipe):
        index = self.recipes.index(old_recipe)
        self.recipes[index] = new_recipe

    def get_recipes_by_category(self, category):
        return [recipe for recipe in self.recipes if recipe.category == category]

    def search_recipes(self, search_term):
        search_term = search_term.lower()
        return [recipe for recipe in self.recipes if search_term in recipe.name.lower() or search_term in recipe.category.lower()]

    def save_to_file(self, filename):
        existing_data = {}
        try:
            with open(filename, 'r') as file:
                existing_data = json.load(file)
        except FileNotFoundError:
            pass

        existing_data['recipes'] = [recipe.to_dict() for recipe in self.recipes]

        with open(filename, 'w') as file:
            json.dump(existing_data, file)

    def load_from_file(self, filename):
        with open(filename, 'r') as file:
            data = json.load(file)
            recipes_data = data.get('recipes', [])
            self.recipes = [Recipe(recipe['name'], recipe['category'], recipe['ingredients']) for recipe in recipes_data]

#  INVENTORY  MANAGEMENT
class AbstractIngredient:
    def __init__(self, name, stock):
        self.name = name
        self.stock = stock

class Ingredient(AbstractIngredient):
    pass

class AbstractInventory:
    def __init__(self):
        self.ingredients = []

    def add_ingredient(self, ingredient):
        self.ingredients.append(ingredient)

    def get_ingredients(self):
        return self.ingredients

    def save_to_json(self, filename):
        try:
            with open(filename, 'r') as file:
                data = json.load(file)
                data['inventory'] = [{"name": ingredient.name, "stock": ingredient.stock} for ingredient in self.ingredients]

            with open(filename, 'w') as file:
                json.dump(data, file)
        except FileNotFoundError:
            pass  # File doesn't exist yet

    def load_from_json(self, filename):
        try:
            with open(filename, 'r') as file:
                data = json.load(file)
                inventory_data = data.get('inventory', [])
                self.ingredients = [Ingredient(item["name"], item["stock"]) for item in inventory_data]
        except FileNotFoundError:
            pass  # File doesn't exist yet
    
    def delete_ingredient(self, ingredient_name):
        self.ingredients = [ingredient for ingredient in self.ingredients if ingredient.name != ingredient_name]

    def update_ingredient(self, ingredient_name, new_stock):
        for ingredient in self.ingredients:
            if ingredient.name == ingredient_name:
                ingredient.stock = new_stock
                break

#  MENU  MANAGEMENT
class AbstractMenu:
    def __init__(self):
        self.menu_file = 'data.json'
        self.menu = {}

    def load_menu(self):
        try:
            with open(self.menu_file, 'r') as file:
                data = json.load(file)
                loaded_menu = data.get('menu', {})
                self.menu.update(loaded_menu)
        except FileNotFoundError:
            self.menu = {}

    def save_menu(self):
        try:
            with open(self.menu_file, 'r') as file:
                data = json.load(file)
        except FileNotFoundError:
            data = {}

        data['menu'] = self.menu

        with open(self.menu_file, 'w') as file:
            json.dump(data, file)

class Menu(AbstractMenu):
    pass


#  CUSTOMER  ORDER
class Order:
    def __init__(self):
        self.items = []

    def add_item(self, name, quantity, total_price, ingredients=None):
        item = {"name": name, "quantity": quantity, "total_price": total_price, "ingredients": ingredients}
        self.items.append(item)

    def get_items(self):
        return self.items

    def get_order_details(self):
        return {"items": self.items}
