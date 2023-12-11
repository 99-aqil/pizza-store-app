import json
import tkinter as tk
from abc import ABC, abstractmethod
from tkinter import ttk, messagebox, simpledialog
from data_layer import Recipe, AbstractInventory, Menu, Order
from business_layer import AbstractStore, RecipeManager, InventoryManager, PizzaMenuStore


#  RECIPE  MANAGEMENT
class AbstractRecipeForm(tk.Toplevel, ABC):
    def __init__(self, parent, manager, recipe=None):
        super().__init__(parent)
        self.manager = manager
        self.recipe = recipe
        if self.recipe:
            self.title("Update Recipe")
        else:
            self.title("Add Recipe")

        self.name_label = ttk.Label(self, text="Name:")
        self.name_entry = ttk.Entry(self)

        self.category_label = ttk.Label(self, text="Category:")
        self.category_combobox = ttk.Combobox(self, values=["Vegetarian", "Meat Lovers", "Specialty"])

        self.ingredients_label = ttk.Label(self, text="Ingredients:")
        self.ingredients_entry = ttk.Entry(self)

        self.save_button = ttk.Button(self, text="Save", command=self.save_recipe)

        self.name_label.grid(row=0, column=0, sticky=tk.W)
        self.name_entry.grid(row=0, column=1, padx=10, pady=5)

        self.category_label.grid(row=1, column=0, sticky=tk.W)
        self.category_combobox.grid(row=1, column=1, padx=10, pady=5)

        self.ingredients_label.grid(row=2, column=0, sticky=tk.W)
        self.ingredients_entry.grid(row=2, column=1, padx=10, pady=5)

        self.save_button.grid(row=3, column=1, pady=10)

        if self.recipe:
            self.name_entry.insert(0, self.recipe.name)
            self.category_combobox.set(self.recipe.category)
            self.ingredients_entry.insert(0, ', '.join(self.recipe.ingredients))

    @abstractmethod
    def save_recipe(self):
        pass

class RecipeForm(AbstractRecipeForm):
    def save_recipe(self):
        name = self.name_entry.get()
        category = self.category_combobox.get()
        ingredients = self.ingredients_entry.get().split(',')

        if self.recipe:
            new_recipe = Recipe(name, category, ingredients)
            self.manager.update_recipe(self.recipe, new_recipe)
        else:
            new_recipe = Recipe(name, category, ingredients)
            self.manager.add_recipe(new_recipe)

        self.manager.save_to_file('data.json')
        self.destroy()

class RecipeManagement:
    def __init__(self, root, manager: AbstractStore):
        self.root = root
        self.root.title("Pizza Store Recipe Management")
        self.root.geometry("800x600")

        self.manager = manager

        self.manage_frame = ttk.Frame(root)
        self.manage_frame.pack()

        self.load_button = ttk.Button(self.manage_frame, text="Load Recipes", command=self.load_recipes)
        self.load_button.pack(pady=10)

        self.search_entry = ttk.Entry(self.manage_frame, width=30)
        self.search_entry.pack(pady=5)

        self.search_button = ttk.Button(self.manage_frame, text="Search Recipes", command=self.search_recipes)
        self.search_button.pack(pady=5)

        self.recipe_listbox = tk.Listbox(self.manage_frame, selectmode=tk.SINGLE)
        self.recipe_listbox.pack(pady=10)

        self.view_button = ttk.Button(self.manage_frame, text="View Recipe", command=self.view_recipe)
        self.view_button.pack(pady=5)

        self.add_button = ttk.Button(self.manage_frame, text="Add Recipe", command=self.add_recipe)
        self.add_button.pack(pady=5)

        self.update_button = ttk.Button(self.manage_frame, text="Update Recipe", command=self.update_recipe)
        self.update_button.pack(pady=5)

        self.delete_button = ttk.Button(self.manage_frame, text="Delete Recipe", command=self.delete_recipe)
        self.delete_button.pack(pady=5)

    def load_recipes(self):
        self.manager.load_from_file('data.json')
        self.update_recipe_listbox()
    
    def search_recipes(self):
        search_term = self.search_entry.get()
        if search_term:
            matching_recipes = self.manager.search_recipes(search_term)
            self.update_recipe_listbox(recipes=matching_recipes)
        else:
            messagebox.showwarning("Empty Search", "Please enter a search term.")

    def update_recipe_listbox(self, recipes=None):
        self.recipe_listbox.delete(0, tk.END)
        recipes = recipes or self.manager.get_all_recipes()
        for recipe in recipes:
            self.recipe_listbox.insert(tk.END, f"{recipe.name} - {recipe.category}")

    def view_recipe(self):
        selected_index = self.recipe_listbox.curselection()
        if selected_index:
            selected_recipe = self.manager.get_all_recipes()[selected_index[0]]
            messagebox.showinfo("Recipe Details", f"Name: {selected_recipe.name}\nCategory: {selected_recipe.category}\nIngredients: {', '.join(selected_recipe.ingredients)}")
        else:
            messagebox.showwarning("No Recipe Selected", "Please select a recipe to view.")

    def add_recipe(self):
        RecipeForm(self.root, self.manager)
        self.update_recipe_listbox()

    def update_recipe(self):
        selected_index = self.recipe_listbox.curselection()
        if selected_index:
            selected_recipe = self.manager.get_all_recipes()[selected_index[0]]
            RecipeForm(self.root, self.manager, recipe=selected_recipe)
            self.update_recipe_listbox()
        else:
            messagebox.showwarning("No Recipe Selected", "Please select a recipe to update.")

    def delete_recipe(self):
        selected_index = self.recipe_listbox.curselection()
        if selected_index:
            selected_recipe = self.manager.get_all_recipes()[selected_index[0]]
            response = messagebox.askyesno("Confirm Deletion", f"Do you want to delete the recipe: {selected_recipe.name}?")
            if response:
                self.manager.delete_recipe(selected_recipe)
                self.manager.save_to_file('data.json')
                self.update_recipe_listbox()
        else:
            messagebox.showwarning("No Recipe Selected", "Please select a recipe to delete.")


#  INVENTORY  MANAGEMENT
class AbstractInventoryApp(tk.Tk, ABC):
    @abstractmethod
    def __init__(self, root):
        pass

    @abstractmethod
    def refresh_inventory(self):
        pass

    @abstractmethod
    def add_ingredient(self):
        pass

    @abstractmethod
    def on_close(self):
        pass
    
    @abstractmethod
    def delete_ingredient(self):
        pass

    @abstractmethod
    def update_ingredient(self):
        pass

class InventoryManagement(AbstractInventoryApp):
    def __init__(self, root, manager: InventoryManager):
        super().__init__(root)
        self.root = root
        self.root.title("Pizza Store Inventory")

        # Create inventory manager
        self.inventory_manager = manager

        # Load existing data from JSON
        try:
            self.inventory_manager.load_inventory_from_json('data.json')
        except FileNotFoundError:
            pass  # File doesn't exist yet

        # Create GUI components
        self.label = ttk.Label(root, text="Ingredient Inventory")
        self.label.pack()

        self.tree = ttk.Treeview(root, columns=('Name', 'Stock'), show='headings')
        self.tree.heading('Name', text='Name')
        self.tree.heading('Stock', text='Stock')
        self.tree.pack()

        self.refresh_button = ttk.Button(root, text='Refresh', command=self.refresh_inventory)
        self.refresh_button.pack(side=tk.LEFT, padx=5, pady=(10, 5))

        self.add_ingredient_button = ttk.Button(root, text='Add Ingredient', command=self.add_ingredient)
        self.add_ingredient_button.pack(side=tk.LEFT, padx=5, pady=(10, 5))

        self.update_button = ttk.Button(root, text='Update Ingredient', command=self.update_ingredient)
        self.update_button.pack(side=tk.LEFT, padx=5, pady=(10, 5))

        self.delete_button = ttk.Button(root, text='Delete Ingredient', command=self.delete_ingredient)
        self.delete_button.pack(side=tk.LEFT, padx=5, pady=(10, 5))

        # Save data on window close
        root.protocol("WM_DELETE_WINDOW", self.on_close)

    def refresh_inventory(self):
        # Clear the treeview
        for row in self.tree.get_children():
            self.tree.delete(row)

        # Populate the treeview with inventory data
        for ingredient in self.inventory_manager.get_inventory():
            self.tree.insert('', 'end', values=(ingredient.name, ingredient.stock))

    def add_ingredient(self):
        # Prompt the user for ingredient details using a pop-up window
        ingredient_name = simpledialog.askstring("Add Ingredient", "Enter ingredient name:")
        if ingredient_name:
            try:
                ingredient_stock = int(simpledialog.askstring("Add Ingredient", "Enter stock for {}:".format(ingredient_name)))
                self.inventory_manager.add_ingredient(ingredient_name, ingredient_stock)
                self.refresh_inventory()  # Update the treeview
            except ValueError:
                messagebox.showerror("Error", "Stock must be a valid integer.")
    
    def delete_ingredient(self):
        selected_item = self.tree.selection()
        if selected_item:
            ingredient_name = self.tree.item(selected_item, 'values')[0]
            confirmation = messagebox.askokcancel("Delete Ingredient", f"Are you sure you want to delete {ingredient_name}?")
            if confirmation:
                self.inventory_manager.delete_ingredient(ingredient_name)
                self.refresh_inventory()

    def update_ingredient(self):
        selected_item = self.tree.selection()
        if selected_item:
            ingredient_name = self.tree.item(selected_item, 'values')[0]
            new_stock = simpledialog.askinteger("Update Stock", f"Enter new stock for {ingredient_name}:")
            if new_stock is not None:
                self.inventory_manager.update_ingredient(ingredient_name, new_stock)
                self.refresh_inventory()

    def on_close(self):
        # Save data to JSON on window close
        self.inventory_manager.save_inventory_to_json('data.json')
        self.root.destroy()

#  MENU  MANAGEMENT
class PizzaMenuApp:
    def __init__(self, root, pizza_store):
        self.root = root
        self.pizza_store = pizza_store
        self.root.title("Pizza Store Menu Management")
        self.root.geometry("800x600")

        # Load data
        self.pizza_store.load_data()

        # GUI components
        self.menu_frame = tk.Frame(root)
        self.menu_frame.pack(padx=10, pady=10)

        self.add_pizza_button = tk.Button(self.menu_frame, text="Add Pizza", command=self.show_pizza_form)
        self.add_pizza_button.grid(row=0, column=0, padx=10, pady=10)

        self.add_side_dish_button = tk.Button(self.menu_frame, text="Add Side Dish", command=self.show_side_dish_form)
        self.add_side_dish_button.grid(row=0, column=1, padx=10, pady=10)

        self.load_data_button = tk.Button(self.menu_frame, text="Load Items", command=self.load_data)
        self.load_data_button.grid(row=0, column=2, padx=10, pady=10)

        self.edit_button = tk.Button(self.menu_frame, text="Edit Item", command=self.edit_item)
        self.edit_button.grid(row=0, column=3, padx=10, pady=10)

        self.delete_button = tk.Button(self.menu_frame, text="Delete Item", command=self.delete_item)
        self.delete_button.grid(row=0, column=4, padx=10, pady=10)

        self.menu_treeview = ttk.Treeview(self.root, columns=('Description', 'Price'))
        self.menu_treeview.heading('#0', text='Item')
        self.menu_treeview.heading('Description', text='Description')
        self.menu_treeview.heading('Price', text='Price')
        self.menu_treeview.pack(padx=10, pady=10)

    def show_pizza_form(self, item_name=None):
        pizza_form = PizzaForm(self.root, self.pizza_store, 'Pizza', item_name)

    def show_side_dish_form(self, item_name=None):
        side_dish_form = PizzaForm(self.root, self.pizza_store, 'Side Dish', item_name)

    def load_data(self):
        self.pizza_store.data_handler.load_menu()
        self.pizza_store.load_data()
        self.menu_treeview.delete(*self.menu_treeview.get_children())

        pizza_heading = self.menu_treeview.insert('', 'end', text='Pizzas', open=True)
        side_dish_heading = self.menu_treeview.insert('', 'end', text='Side Dishes', open=True)

        for category, items in self.pizza_store.menu.items():
            category_heading = pizza_heading if category == "Pizza" else side_dish_heading

            for item in items:
                name = item['name']
                description = item.get('description', '')
                price = f"${item.get('price', 0.0)}"

                self.menu_treeview.insert(
                    category_heading,
                    'end',
                    text=name,
                    values=(description, price)
                )

    def edit_item(self):
        selected_item = self.menu_treeview.selection()
        if not selected_item:
            messagebox.showwarning("Error", "Please select an item to edit.")
            return

        item_name = self.menu_treeview.item(selected_item, "text")
        item_category = self.get_item_category(item_name)

        if item_category == "Pizza":
            self.show_pizza_form(item_name)
        elif item_category == "Side Dish":
            self.show_side_dish_form(item_name)

    def delete_item(self):
        selected_item = self.menu_treeview.selection()
        if not selected_item:
            messagebox.showwarning("Error", "Please select an item to delete.")
            return

        item_name = self.menu_treeview.item(selected_item, "text")
        item_category = self.get_item_category(item_name)

        result = messagebox.askyesno("Confirm Deletion", f"Are you sure you want to delete {item_name}?")
        if result:
            self.pizza_store.delete_item_from_menu(item_category, item_name)
            self.load_data()

    def get_item_category(self, item_name):
        for category, items in self.pizza_store.menu.items():
            if any(item['name'] == item_name for item in items):
                return category

# Form for adding Pizzas and Side Dishes
class PizzaForm:
    def __init__(self, parent, pizza_store, item_type, item_name=None):
        self.pizza_store = pizza_store
        self.form = tk.Toplevel(parent)
        self.form.title(f"Add {item_type}")
        self.form.geometry("400x300")

        self.create_gui_components(item_type)
        self.item_name = item_name

        if item_name:
            # If item_name is provided, initialize the form with existing values
            item = self.pizza_store.get_item_by_name(item_type, item_name)
            self.name_entry.insert(0, item['name'])
            self.description_entry.insert(0, item.get('description', ''))
            self.price_entry.insert(0, item.get('price', ''))
            if hasattr(self, 'ingredients_entry'):
                self.ingredients_entry.insert(0, item.get('ingredients', ''))

    def add_item(self):
        name = self.name_entry.get()
        description = self.description_entry.get()
        price = float(self.price_entry.get())

        if hasattr(self, 'ingredients_entry'):
            ingredients = self.ingredients_entry.get()
            category = "Pizza"
            if self.item_name:
                # Update existing item
                self.pizza_store.update_pizza_in_menu(self.item_name, name, description, ingredients, price)
            else:
                # Add new item
                self.pizza_store.add_pizza_to_menu(name, description, ingredients, price)
        else:
            category = "Side Dish"
            if self.item_name:
                # Update existing item
                self.pizza_store.update_side_dish_in_menu(self.item_name, name, description, price)
            else:
                # Add new item
                self.pizza_store.add_side_dish_to_menu(name, description, price)

        messagebox.showinfo("Item Added", f"{name} {'' if self.item_name else 'added to'} the menu.")
        self.form.destroy()

    def create_gui_components(self, item_type):
        # GUI components
        self.name_entry = tk.Entry(self.form, width=30)
        self.name_entry.grid(row=0, column=1, padx=10, pady=10)
        tk.Label(self.form, text=f"{item_type} Name:").grid(row=0, column=0, padx=10, pady=10)

        self.description_entry = tk.Entry(self.form, width=30)
        self.description_entry.grid(row=1, column=1, padx=10, pady=10)
        tk.Label(self.form, text="Description:").grid(row=1, column=0, padx=10, pady=10)

        self.price_entry = tk.Entry(self.form, width=30)
        self.price_entry.grid(row=2, column=1, padx=10, pady=10)
        tk.Label(self.form, text="Price:").grid(row=2, column=0, padx=10, pady=10)

        if item_type == 'Pizza':
            self.ingredients_entry = tk.Entry(self.form, width=30)
            self.ingredients_entry.grid(row=3, column=1, padx=10, pady=10)
            tk.Label(self.form, text="Ingredients:").grid(row=3, column=0, padx=10, pady=10)

        self.add_button = tk.Button(self.form, text=f"Add {item_type}", command=self.add_item)
        self.add_button.grid(row=4, column=0, columnspan=2, pady=10)


#  CUSTOMER  ORDER
class CustomerOrderApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Pizza Store Application")

        # Load menu and inventory data from the 'menu' and 'inventory' keys in data.json
        data = self.load_data("data.json")
        self.menu = data.get("menu", {})
        self.inventory = data.get("inventory", {})

        # Initialize the order
        self.order = Order()

        # Create UI elements
        self.create_menu_frame()
        self.create_order_frame()
        self.base_var = tk.StringVar()
        self.sauce_var = tk.StringVar()

    def create_menu_frame(self):
        menu_frame = ttk.LabelFrame(self.root, text="Menu")
        menu_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

        self.menu_tree = ttk.Treeview(menu_frame, columns=("Description", "Price"))
        self.menu_tree.heading("#0", text="Item")
        self.menu_tree.heading("Description", text="Description")
        self.menu_tree.heading("Price", text="Price")
        self.menu_tree.column("Description", width=200)
        self.menu_tree.column("Price", width=50)

        self.populate_menu()

        self.menu_tree.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

        add_to_order_button = ttk.Button(menu_frame, text="Add to Order", command=self.add_to_order)
        add_to_order_button.grid(row=1, column=0, pady=5)

        create_own_pizza_button = ttk.Button(menu_frame, text="Create Your Own Pizza", command=self.create_own_pizza)
        create_own_pizza_button.grid(row=2, column=0, pady=5)

    def create_order_frame(self):
        order_frame = ttk.LabelFrame(self.root, text="Order")
        order_frame.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")

        self.order_tree = ttk.Treeview(order_frame, columns=("Quantity", "Total Price"))
        self.order_tree.heading("#0", text="Item")
        self.order_tree.heading("Quantity", text="Quantity")
        self.order_tree.heading("Total Price", text="Total Price")
        self.order_tree.column("Quantity", width=70)
        self.order_tree.column("Total Price", width=100)

        self.order_tree.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

        place_order_button = ttk.Button(order_frame, text="Place Order", command=self.place_order)
        place_order_button.grid(row=1, column=0, pady=5)

    def populate_menu(self):
        for category, items in self.menu.items():
            category_node = self.menu_tree.insert("", "end", text=category)
            for item in items:
                self.menu_tree.insert(category_node, "end", text=item["name"],
                                      values=(item["description"], item["price"]))

    def add_to_order(self):
        selected_item = self.menu_tree.selection()
        if selected_item:
            item_name = self.menu_tree.item(selected_item, "text")
            quantity = self.get_quantity()
            if quantity > 0:
                item = self.find_item_by_name(item_name)
                total_price = quantity * item["price"]
                self.order.add_item(item_name, quantity, total_price)
                self.update_order_tree()

    def create_own_pizza(self):
        own_pizza_dialog = tk.Toplevel(self.root)
        own_pizza_dialog.title("Create Your Own Pizza")

        ttk.Label(own_pizza_dialog, text="Choose Pizza Base:").grid(row=0, column=0, padx=10, pady=5)
        ttk.Combobox(own_pizza_dialog, values=["Thin Crust", "Thick Crust", "Stuffed Crust"], textvariable=self.base_var).grid(row=0, column=1, padx=10, pady=5)

        ttk.Label(own_pizza_dialog, text="Choose Sauce:").grid(row=1, column=0, padx=10, pady=5)
        ttk.Combobox(own_pizza_dialog, values=["Tomato", "Pesto", "Alfredo"], textvariable=self.sauce_var).grid(row=1, column=1, padx=10, pady=5)

        ttk.Label(own_pizza_dialog, text="Select Ingredients:").grid(row=2, column=0, padx=10, pady=5)

        self.own_pizza_ingredients = {}

        for ingredient in self.inventory:
            ingredient_name = ingredient["name"]
            ingredient_var = tk.IntVar()
            ingredient_checkbutton = ttk.Checkbutton(own_pizza_dialog, text=ingredient_name, variable=ingredient_var)
            ingredient_checkbutton.grid(sticky="w", padx=10)
            self.own_pizza_ingredients[ingredient_name] = {"var": ingredient_var, "stock": ingredient["stock"]}

        ttk.Button(own_pizza_dialog, text="Add to Order", command=self.add_own_pizza_to_order).grid(row=len(self.inventory) + 5, column=0, columnspan=2, pady=10)

    def add_own_pizza_to_order(self):
        own_pizza_base = self.base_var.get()
        own_pizza_sauce = self.sauce_var.get()

        if not own_pizza_base or not own_pizza_sauce:
            messagebox.showinfo("Create Your Own Pizza", "Please choose pizza base and sauce.")
            return

        own_pizza_ingredients = []
        for ingredient_name, data in self.own_pizza_ingredients.items():
            if data["var"].get() == 1:
                own_pizza_ingredients.append(ingredient_name)

        if not own_pizza_ingredients:
            messagebox.showinfo("Create Your Own Pizza", "Please select at least one ingredient.")
            return

        quantity = self.get_quantity()
        if quantity > 0:
            own_pizza_price = 8.0  # Set your own price for the custom pizza
            total_price = quantity * own_pizza_price
            pizza_name = f"Custom Pizza ({own_pizza_base}, {own_pizza_sauce})"
            self.order.add_item(pizza_name, quantity, total_price, ingredients=own_pizza_ingredients)
            self.update_order_tree()

    def place_order(self):
        order_details = self.order.get_order_details()
        if not order_details["items"]:
            messagebox.showinfo("Place Order", "No items in the order. Please add items to the order.")
            return

        # Calculate total bill
        total_bill = sum(item["total_price"] for item in order_details["items"])

        # Display order summary popup
        summary_text = "Order Summary:\n"
        for item in order_details["items"]:
            summary_text += f"{item['name']}"
            if item.get("ingredients"):
                summary_text += f" - {', '.join(item['ingredients'])}"
            summary_text += f" - {item['quantity']} x ${item['total_price']:.2f}\n"

        summary_text += f"\nTotal Bill: ${total_bill:.2f}"

        messagebox.showinfo("Place Order", summary_text)

        # You can further implement actions like updating inventory, generating order slips, etc.
        self.clear_order()

    def update_order_tree(self):
        self.order_tree.delete(*self.order_tree.get_children())
        for item in self.order.get_items():
            self.order_tree.insert("", "end", text=item["name"],
                                   values=(item["quantity"], item["total_price"]))

    def get_quantity(self):
        quantity = simpledialog.askinteger("Quantity", "Enter quantity:")
        return quantity if quantity else 0

    def find_item_by_name(self, item_name):
        for category, items in self.menu.items():
            for item in items:
                if item["name"] == item_name:
                    return item
        return None

    def load_data(self, filename):
        with open(filename, "r") as file:
            data = json.load(file)
        return data


class PizzaStoreApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Pizza Store App")
        self.root.geometry("800x600") 

        # List to store the pages
        self.pages = []

        # Set the initial page to the Landing Page
        self.show_landing_page()

    def show_page(self, page_frame):
        # Hide the current page
        if self.pages:
            current_page = self.pages[-1]
            current_page.grid_forget()

        # Show the new page
        page_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        self.pages.append(page_frame)

    def show_landing_page(self):
        # Landing Page
        landing_frame = ttk.Frame(self.root, padding="20")
        landing_frame.grid(row=0, column=0, sticky="nsew")

        label = ttk.Label(landing_frame, text="Welcome to the Pizza Store !")
        label.grid(row=0, column=0, pady=10, columnspan=2)

        owner_button = ttk.Button(landing_frame, text="Owner", command=self.show_owner_page)
        owner_button.grid(row=1, column=0, pady=10, sticky="ew")

        customer_button = ttk.Button(landing_frame, text="Customer", command=self.show_customer_page)
        customer_button.grid(row=1, column=1, pady=10, sticky="ew")

        # Configure columns to be equally distributed
        landing_frame.columnconfigure(0, weight=1)
        landing_frame.columnconfigure(1, weight=1)

        # Center the frame in the main window
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)

        self.show_page(landing_frame)

    def show_owner_page(self):
        # Owner Page
        owner_frame = ttk.Frame(self.root, padding="20")
        owner_frame.grid(row=0, column=0, sticky="nsew")

        label = ttk.Label(owner_frame, text="Welcome Owner !")
        label.grid(row=0, column=0, pady=10, columnspan=3)

        recipe_management_button = ttk.Button(owner_frame, text="Recipe Management", command=self.recipe_management_page)
        recipe_management_button.grid(row=1, column=0, pady=10, sticky="ew")

        inventory_management_button = ttk.Button(owner_frame, text="Inventory Management", command=self.inventory_management_page)
        inventory_management_button.grid(row=1, column=1, pady=10, sticky="ew")

        menu_management_button = ttk.Button(owner_frame, text="Menu Management", command=self.menu_management_page)
        menu_management_button.grid(row=1, column=2, pady=10, sticky="ew")

        back_button = ttk.Button(owner_frame, text="Back", command=self.go_back)
        back_button.grid(row=2, column=0, pady=10, columnspan=3, sticky="ew")

        # Configure columns to be equally distributed
        owner_frame.columnconfigure(0, weight=1)
        owner_frame.columnconfigure(1, weight=1)
        owner_frame.columnconfigure(2, weight=1)

        # Center the frame in the main window
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)

        self.show_page(owner_frame)

    def show_customer_page(self):
        # Customer Page
        customer_frame = ttk.Frame(self.root, padding="20")
        customer_frame.grid(row=0, column=0, sticky="nsew")

        label = ttk.Label(customer_frame, text="Welcome Customer !")
        label.grid(row=0, column=0, pady=10, columnspan=2)

        menu_button = ttk.Button(customer_frame, text="Menu", command=self.menu_page)
        menu_button.grid(row=1, column=0, pady=10, columnspan=2, sticky="nsew")

        back_button = ttk.Button(customer_frame, text="Back", command=self.go_back)
        back_button.grid(row=2, column=0, pady=5, columnspan=2, sticky="nsew")

        # Configure columns to be equally distributed
        customer_frame.columnconfigure(0, weight=1)
        customer_frame.columnconfigure(1, weight=1)

        # Center the frame in the main window
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)

        self.show_page(customer_frame)

    def recipe_management_page(self):
        pizza_store_root = tk.Toplevel(self.root)
        manager = RecipeManager()
        pizza_store_app = RecipeManagement(pizza_store_root, manager)

    def inventory_management_page(self):
        pizza_store_root = tk.Toplevel(self.root)
        inventory_manager = InventoryManager(AbstractInventory())
        pizza_store_app = InventoryManagement(pizza_store_root, inventory_manager)

    def menu_management_page(self):
        pizza_store_root = tk.Toplevel(self.root)
        data_handler = Menu()
        pizza_store = PizzaMenuStore(data_handler)
        pizza_store_app = PizzaMenuApp(pizza_store_root, pizza_store)

    def menu_page(self):
        pizza_store_root = tk.Toplevel(self.root)
        pizza_store_app = CustomerOrderApp(pizza_store_root)

    def go_back(self):
        # Go back to the previous page
        if len(self.pages) > 1:
            current_page = self.pages.pop()
            current_page.grid_forget()
            previous_page = self.pages[-1]
            previous_page.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))


if __name__ == "__main__":
    root = tk.Tk()
    app = PizzaStoreApp(root)
    root.mainloop()