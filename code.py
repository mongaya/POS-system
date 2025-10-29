import csv
import os

# Load product data from CSV file
def load_data(filename="database.csv"):
    menu = {}
    stock = {}
    if os.path.exists(filename):
        with open(filename, mode="r", newline='', encoding="utf-8") as file:
            reader = csv.DictReader(file)
            for row in reader:
                name = row["Product"]
                price = float(row["Price"])
                qty = int(row["Stock"])
                menu[name] = price
                stock[name] = qty
        print(f"\n✅ Loaded existing data from {filename}.")
    else:
        print(f"\n⚠️ No existing data found. Starting a new database.")
    return menu, stock


# Save product data to CSV file
def save_data(menu, stock, filename="database.csv"):
    with open(filename, mode="w", newline='', encoding="utf-8") as file:
        fieldnames = ["Product", "Price", "Stock"]
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        for item, price in menu.items():
            writer.writerow({"Product": item, "Price": price, "Stock": stock.get(item, 0)})
    print(f"\n💾 Data saved to {filename}.")


#user input a product, prices, and stock
def input_menu():
    menu = {}
    stock = {}
    print("Enter available Strains or Products. \nType 'done' when finished.")
    while True:
        name = input("\tEnter STRAIN NAME or PRODUCTS (or type 'done' if finis): ").strip()
        if name.lower() == 'done':
            break

        if not name:
            print("Product name cannot be empty. Try again.")
            continue

        try:
            price = float(input(f"\tEnter PRICE for {name}: ₱"))
            if price <= 0:
                print("Price must be positive. Try again.")
                continue

            qty_in_stock = int(input(f"\tEnter initial STOCK for {name}: "))
            if qty_in_stock < 0:
                print("Stock quantity cannot be negative. Try again.")
                continue

            menu[name] = price
            stock[name] = qty_in_stock

        except ValueError:
            print("Invalid input (price or stock). Try again.")

    return menu, stock


# Update menu and stock
def update_menu(menu, stock):
    """Allows the user to update prices, stock, or add/remove products."""
    print("\n--- UPDATE PRODUCTS & STOCK ---")
    while True:
        print("\nCurrent Products:")
        for item, price in menu.items():
            qty = stock.get(item, 0)
            print(f"  {item:<15} ₱{price:<8.2f} ({qty} in stock)")

        print("\nOptions:")
        print("1. Update Price")
        print("2. Add Stock")
        print("3. Add New Product/Strain")
        print("4. Remove Product/Strain")
        print("5. Return to Main Menu")

        choice = input("Select an option (1-5): ").strip()

        if choice == '1':
            item = input("Enter product/strain name to update price: ").strip()
            if item in menu:
                try:
                    new_price = float(input(f"Enter new price for {item}: ₱"))
                    if new_price <= 0:
                        print("Price must be positive.")
                        continue
                    menu[item] = new_price
                    print(f"✅ Price for {item} updated to ₱{new_price:.2f}")
                except ValueError:
                    print("Invalid price input.")
            else:
                print("Product/strain not found.")

        elif choice == '2':
            item = input("Enter product/strain name to add stock: ").strip()
            if item in stock:
                try:
                    add_qty = int(input(f"Enter quantity to add for {item}: "))
                    if add_qty < 0:
                        print("Quantity cannot be negative.")
                        continue
                    stock[item] += add_qty
                    print(f"✅ Added {add_qty} units to {item}. New stock: {stock[item]}")
                except ValueError:
                    print("Invalid quantity input.")
            else:
                print("Product/strain not found.")

        elif choice == '3':
            new_item = input("Enter NEW PRODUCT OR STRAIN NAME: ").strip()
            if new_item in menu:
                print("Product/strain already exists. Use Update instead.")
                continue
            try:
                new_price = float(input(f"Enter price for {new_item}: ₱"))
                new_stock = int(input(f"Enter stock for {new_item}: "))
                if new_price <= 0 or new_stock < 0:
                    print("Invalid price or stock input.")
                    continue
                menu[new_item] = new_price
                stock[new_item] = new_stock
                print(f"✅ Added new product: {new_item} (₱{new_price:.2f}, {new_stock} in stock)")
            except ValueError:
                print("Invalid input. Try again.")

        elif choice == '4':
            item = input("Enter product/strain name to remove: ").strip()
            if item in menu:
                confirm = input(f"Are you sure you want to remove {item}? (yes/no): ").lower()
                if confirm == 'yes':
                    del menu[item]
                    del stock[item]
                    print(f"✅ {item} removed from the menu.")
                else:
                    print("Removal canceled.")
            else:
                print("Product / Strain not found.")

        elif choice == '5':
            print("Returning to main menu...")
            break

        else:
            print("Invalid choice. Please choose 1-5.")

        # ✅ Automatically save changes after each modification
        save_data(menu, stock)


#customer order
def take_order(menu, stock):
    order = {}
    print("\nTAKE CUSTOMER ORDER. TYPE 'DONE' WHEN FINISHED")

    print("\t\tLORENCE'S BETTA FISH")
    print("\n\t\t--- Available Strains and Products ---")
    for item, price in menu.items():
        qty = stock.get(item, 0)
        stock_status = f"({qty} in stock)" if qty > 0 else "(OUT OF STOCK)"
        print(f"  \t{item:<15} ₱{price:.2f} {stock_status}")
    print("\t ----------------------------------")

    while True:
        item = input("\tEnter product/strain name to order (or 'done'): ").strip()
        if item.lower() == 'done':
            break
        if item not in menu:
            print(f"\tSorry, we don't have {item}. Please order from the menu.")
            continue

        available_stock = stock.get(item, 0)
        ordered_so_far = order.get(item, 0)
        remaining_stock = available_stock - ordered_so_far

        if remaining_stock <= 0:
            print(f"\tSorry, {item} is OUT OF STOCK or fully reserved in this order.")
            continue

        try:
            qty = int(input(f"\tEnter quantity for {item} (Max: {remaining_stock}): "))
            if qty <= 0:
                print("Quantity must be positive.")
                continue
            if qty > remaining_stock:
                print(f"\tInsufficient stock! Only {remaining_stock} of {item} available.")
                continue
            order[item] = order.get(item, 0) + qty
        except ValueError:
            print("Invalid quantity. Try again.")

    return order


#receipt
def print_receipt(order, menu):
    print("\n" + "="*30)
    print("       ORDER RECEIPT")
    print("="*30)
    total = 0
    for item, qty in order.items():
        price = menu[item]
        subtotal = price * qty
        total += subtotal
        print(f"{item:<15} x{qty:<3} ₱{subtotal:.2f}")
    print("-"*30)
    print(f"{'TOTAL':<20} ₱{total:.2f}")
    print("="*30)
    return total


# Function to handle payment
def process_payment(total):
    print("\n--- PAYMENT METHOD ---")
    while True:
        method = input("Choose payment method (1: Cash, 2: GCash): ").strip()
        if method == '1':
            while True:
                try:
                    paid_amount = float(input(f"Enter CASH TENDERED for ₱{total:.2f}: ₱"))
                    if paid_amount < total:
                        print("Insufficient amount. Please enter more or pay the exact amount.")
                        continue
                    change = paid_amount - total
                    print(f"\n✅ Transaction Successful (Cash)")
                    print(f"💰 CHANGE: ₱{change:.2f}")
                    return total
                except ValueError:
                    print("Invalid cash amount. Please enter a number.")
        elif method == '2':
            print("\n💳 GCash Payment Selected.")
            print(f"Scan QR or send ₱{total:.2f} to 0912789098 (L** P**).")
            input("Press Enter when payment is confirmed.")
            print(f"\n✅ Transaction Successful (GCash)")
            print("No change needed.")
            return total
        else:
            print("Invalid selection. Please choose '1' or '2'.")


# Deduct stock
def deduct_stock(stock, order):
    for item, qty in order.items():
        if item in stock:
            stock[item] -= qty


def main():
    print("Welcome to the LORENCE'S BETTA FISH")

    # ✅ Load existing data from CSV
    menu, stock = load_data()

    # If no data, allow user to input new products
    if not menu:
        menu, stock = input_menu()
        save_data(menu, stock)

    print("\n\t\t---- Current Strains and Products ----")
    print("\t\t\tProduct | Price | Stock")
    for item, price in menu.items():
        qty = stock.get(item, 0)
        print(f"\t\t\t{item:<10}: ₱{price:.2f} ({qty})")

    session_total_sales = 0

    while True:
        print("\nOptions:")
        print("1. Take a New Order")
        print("2. Update Products/Stock")
        print("3. End Session")
        choice = input("Choose an option (1-3): ").strip()

        if choice == '1':
            order = take_order(menu, stock)
            if not order:
                print("No items ordered.")
            else:
                order_total = print_receipt(order, menu)
                amount_paid = process_payment(order_total)
                session_total_sales += amount_paid
                deduct_stock(stock, order)
                save_data(menu, stock)  # ✅ Save updated stock
                print("\n" + "="*30)
                print("Thank you for ordering with us!")
                print("="*30)

        elif choice == '2':
            update_menu(menu, stock)

        elif choice == '3':
            print("\n" + "="*40)
            print("        END OF SESSION REPORT")
            print("="*40)
            print(f"Total Revenue from all orders: ₱{session_total_sales:.2f}")
            print("\n--- Remaining Inventory ---")
            for item, qty in stock.items():
                print(f"  {item:<15}: {qty} units")
            print("="*40)
            save_data(menu, stock)
            print("Exiting POS. Goodbye!")
            break

        else:
            print("Invalid choice. Please select 1-3.")


if __name__ == '__main__':
    main()
