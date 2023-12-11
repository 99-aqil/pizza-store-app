import tkinter as tk
from abc import ABC, abstractmethod
from data_layer import PizzaStore, Ingredient, AbstractInventory, Ingredient, AbstractMenu


#  RECIPE  MANAGEMENT
class AbstractStore(ABC):
    @abstractmethod
    def add_recipe(self, recipe):
        pass

    @abstractmethod
    def delete_recipe(self, recipe):
        pass

    @abstractmethod
    def update_recipe(self, old_recipe, new_recipe):
        pass

    @abstractmethod
    def get_recipes_by_category(self, category):
        pass

    @abstractmethod
    def search_recipes(self, search_term):
        pass

    @abstractmethod
    def save_to_file(self, filename):
        pass

    @abstractmethod
    def load_from_file(self, filename):
        pass

class RecipeManager(AbstractStore):
    def __init__(self):
        self.store = PizzaStore()

    def add_recipe(self, recipe):
        self.store.add_recipe(recipe)

    def delete_recipe(self, recipe):
        self.store.delete_recipe(recipe)

    def update_recipe(self, old_recipe, new_recipe):
        self.store.update_recipe(old_recipe, new_recipe)

    def get_recipes_by_category(self, category):
        return self.store.get_recipes_by_category(category)

    def search_recipes(self, search_term):
        return self.store.search_recipes(search_term)

    def save_to_file(self, filename):
        self.store.save_to_file(filename)

    def load_from_file(self, filename):
        self.store.load_from_file(filename)

    def get_all_recipes(self):
        return self.store.recipes


#  INVENTORY  MANAGEMENT
class AbstractInventoryManager(ABC):
    @abstractmethod
    def add_ingredient(self, name, stock):
        pass

    @abstractmethod
    def get_inventory(self):
        pass

    @abstractmethod
    def save_inventory_to_json(self, filename):
        pass

    @abstractmethod
    def load_inventory_from_json(self, filename):
        pass
    
    @abstractmethod
    def delete_ingredient(self, name):
        pass

    @abstractmethod
    def update_ingredient(self, name, stock):
        pass


class InventoryManager(AbstractInventoryManager):
    def __init__(self, inventory: AbstractInventory):
        self.inventory = inventory

    def add_ingredient(self, name, stock):
        ingredient = Ingredient(name, stock)
        self.inventory.add_ingredient(ingredient)

    def get_inventory(self):
        return self.inventory.get_ingredients()

    def save_inventory_to_json(self, filename):
        self.inventory.save_to_json(filename)

    def load_inventory_from_json(self, filename):
        self.inventory.load_from_json(filename)
    
    def delete_ingredient(self, name):
        self.inventory.delete_ingredient(name)

    def update_ingredient(self, name, stock):
        self.inventory.update_ingredient(name, stock)

#  MENU  MANAGEMENT
class AbstractMenuStore(ABC):
    @abstractmethod
    def load_data(self):
        pass

    @abstractmethod
    def save_data(self):
        pass

    @abstractmethod
    def add_pizza_to_menu(self, name, description, ingredients, price):
        pass

    @abstractmethod
    def add_side_dish_to_menu(self, name, description, price):
        pass

class PizzaMenuStore(AbstractMenuStore):
    def __init__(self, data_handler: AbstractMenu):
        self.data_handler = data_handler
        self.menu = {}

    def load_data(self):
        self.data_handler.load_menu()
        self.menu = self.data_handler.menu

    def save_data(self):
        self.data_handler.menu = self.menu
        self.data_handler.save_menu()

    def add_pizza_to_menu(self, name, description, ingredients, price):
        pizza = {'name': name, 'description': description, 'ingredients': ingredients, 'price': price}

        if 'Pizza' in self.menu:
            self.menu['Pizza'].append(pizza)
        else:
            self.menu['Pizza'] = [pizza]

        self.save_data()

    def add_side_dish_to_menu(self, name, description, price):
        side_dish = {'name': name, 'description': description, 'price': price}

        if 'Side Dish' in self.menu:
            self.menu['Side Dish'].append(side_dish)
        else:
            self.menu['Side Dish'] = [side_dish]

        self.save_data()

    def update_pizza_in_menu(self, old_name, new_name, description, ingredients, price):
        if 'Pizza' in self.menu:
            for pizza in self.menu['Pizza']:
                if pizza['name'] == old_name:
                    pizza['name'] = new_name
                    pizza['description'] = description
                    pizza['ingredients'] = ingredients
                    pizza['price'] = price
                    self.save_data()
                    break

    def update_side_dish_in_menu(self, old_name, new_name, description, price):
        if 'Side Dish' in self.menu:
            for side_dish in self.menu['Side Dish']:
                if side_dish['name'] == old_name:
                    side_dish['name'] = new_name
                    side_dish['description'] = description
                    side_dish['price'] = price
                    self.save_data()
                    break
    
    def delete_item_from_menu(self, category, name):
        if category in self.menu and name in [item['name'] for item in self.menu[category]]:
            self.menu[category] = [item for item in self.menu[category] if item['name'] != name]
            self.save_data()

    def get_item_by_name(self, category, name):
        if category in self.menu and name in [item['name'] for item in self.menu[category]]:
            return next(item for item in self.menu[category] if item['name'] == name)
        else:
            return None

