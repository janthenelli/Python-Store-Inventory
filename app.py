import csv
import datetime
import os

from collections import OrderedDict
from decimal import Decimal
from peewee import *


db = SqliteDatabase('inventory.db')

class Product(Model):
    product_id = AutoField()
    product_name = CharField(max_length=255, unique=True)
    product_quantity = IntegerField(default=0)
    product_price = IntegerField(null=False)
    date_updated = DateTimeField(default=datetime.datetime.now)

    class Meta:
        database = db


def clear():
    """clear console"""
    os.system('cls' if os.name == 'nt' else 'clear')

def add_to_db(**kwargs):
    """adds cleaned items to database"""
    for item in inventory:
        try:
            Product.create(**item)
        except IntegrityError:
            item_record = Product.get(product_name=item['product_name'])
            item_record.product_price = item['product_price']
            item_record.product_quantity = item['product_quantity']
            item_record.date_updated = item['date_updated']
            item_record.save()

def view_product():
    """View product in inventory by ID"""
    try:
        id = input("Enter the ID of the item you would like to view: ")
        product = Product.get(Product.product_id == id)
        display_product(product)
    except DoesNotExist:
        print("No item with an ID of {} exists, please enter a valid ID".format(id))
        view_product()
    another = input("\n\nWould you like to view another product? [Yn] ")
    if another.lower() != 'n':
        print("")
        view_product()
    clear()
    

def display_product(product):
    temp_price = str(product.product_price)
    if len(temp_price) < 3:
        temp_price = "0" + temp_price
    temp_price = temp_price[:-2] + "." + temp_price[-2:]
    print("\n" + product.product_name)
    print("="*len(product.product_name))
    print("Price: ${}".format(temp_price))
    print("Quantity: {}".format(product.product_quantity))
    print("Last updated: {}".format(product.date_updated.date().strftime('%m/%d/%Y')))

def add_product():
    """Add new product to inventory or update existing one"""
    while True:
        try:
            name = input("Enter the name of the product you would lke to add: ").title()
            temp_name = name.replace(" ", "")
            if not temp_name.isalpha():
                raise TypeError 
            price = input("Enter the price for one {}, (format: 3.29): ".format(name))
            if not price.isnumeric() and price.count('.') > 1:
                raise TypeError
            price = Decimal(price).quantize(Decimal('1.00'))
            quantity = input("Enter the amount of {} you would like to add: ".format(name))
            if not quantity.isnumeric():
                raise TypeError

            print(f"\nProduct name: {name}\nProduct price: ${price}\nProduct quantity: {quantity}\n")
            confirm_add = input("Would you like to add this product to the inventory? [Yn] ")
            if confirm_add.lower() != 'n':
                try:
                    Product.create(
                        product_name=name,
                        product_price=int(str(price).replace('.', '')),
                        product_quantity=quantity
                    )
                    print("\nProduct created successfully!")
                    break
                except IntegrityError:
                    product_last_updated = Product.select().where(Product.product_name == name).get().date_updated
                    updated = datetime.date()
                    if product_last_updated <= updated:
                        product_record = Product.select().where(Product.product_name == name).get()
                        product_record.product_price = int(price.replace('.', ''))
                        product_record.product_quantity = quantity
                        product_record.date_updated = datetime.datetime.now()
                        product_record.save()
                        print("{} already exists and has been updated.".format(name))
                    break
            else:
                break
            
        except TypeError:
            print("Please enter a valid entry\n")
    

def backup_inventory():
    """Backup inventory"""
    with open('inventory_backup.csv', 'w', newline='') as file:
        writer = csv.writer(file)
        items = Product.select(
            Product.product_name,
            Product.product_price,
            Product.product_quantity,
            Product.date_updated
        )
        writer.writerow(item.keys())
        writer.writerows(items.tuples())
        print("\nBackup successful!\n")

def menu_loop():
    """handles general menu functionality of the program"""
    choice = None
    while choice != 'q':
        print("\n" + "="*10, "MENU", "="*10)
        print("\nEnter 'q' to quit\n")
        for key, value in menu.items():
            print("{}) {}".format(key, value.__doc__))
        try: 
            choice = input("\nAction: ").lower().strip()
            if choice not in menu and choice != 'q':
                raise ValueError
            if choice in menu:
                clear()
                menu[choice]()
        except ValueError:
            print("\nYou must select from the menu options or enter 'q' to quit.")

menu = OrderedDict([
    ('v', view_product),
    ('a', add_product),
    ('b', backup_inventory)
])


if __name__ == '__main__':
    inventory = []
    with open("inventory.csv", newline="") as file:
        data = csv.DictReader(file)
        for row in data:
            inventory.append(dict(row))
        for item in inventory:
            item['product_price'] = int(item['product_price'].replace('$', '').replace('.', ''))
            item['product_quantity'] = int(item['product_quantity'])
            item['date_updated'] = datetime.datetime.strptime(item['date_updated'], '%m/%d/%Y')

    db.connect()
    db.create_tables([Product], safe=True)
    add_to_db(
        product_name=item['product_name'],
        product_price=item['product_price'],
        product_quantity=item['product_quantity'],
        date_updated=item['date_updated']
    )
    menu_loop()