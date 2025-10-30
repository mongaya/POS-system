import csv
import os # To check if files exist
import datetime # Used for the Timestamp

# --- CSV FILE OPERATIONS ---

# 📂 Load Menu & Stock from CSV
def load_menu_stock():
    """Load menu and stock from menu_stock.csv."""
    menu = {}
    stock = {}
    filename = 'menu_stock.csv'
    if not os.path.exists(filename):
        print(f"⚠️ {filename} not found. Starting with empty menu/stock.")
        return menu, stock

    try:
        with open(filename, mode='r', newline='') as file:
            # Use DictReader for easy mapping to dictionaries
            reader = csv.DictReader(file)
            for row in reader:
                item = row['Item']
                try:
                    # Convert to float for price and int for stock
                    menu[item] = float(row['Price'])
                    stock[item] = int(row['Stock'])
                except (ValueError, KeyError) as e:
                    print(f"Error loading data for {item}: {e}. Skipping row.")
        print(f"✅ Loaded {len(menu)} items from {filename}")
    except Exception as e:
        print(f"An error occurred while loading {filename}: {e}")
    return menu, stock

# 📝 Save Menu & Stock to CSV
def save_menu_stock(menu, stock):
    """Save current menu and stock to menu_stock.csv."""
    filename = 'menu_stock.csv'
    fieldnames = ['Item', 'Price', 'Stock']
    data_to_write = [{'Item': item, 'Price': price, 'Stock': stock.get(item, 0)} 
                     for item, price in menu.items()]
    
    try:
        with open(filename, mode='w', newline='') as file:
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(data_to_write)
        print(f"✅ Menu and Stock saved to {filename}")
    except Exception as e:
        print(f"An error occurred while saving {filename}: {e}")


# 📚 Log Transaction to CSV (Bookkeeping) - MODIFIED
def log_transaction(order, menu, total):
    """Log a completed transaction to data.csv with simplified fields."""
    filename = 'data.csv'
    # 'a' mode appends to the file.
    file_exists = os.path.exists(filename)
    
    # Fieldnames for the simplified transaction log
    fieldnames = ['Timestamp', 'Item', 'Quantity'] # REMOVED Price_per_Unit, Subtotal, Order_Total
    
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    data_to_write = []
    for item, qty in order.items():
        # Create a dictionary for each item in the order
        data_to_write.append({
            'Timestamp': timestamp,
            'Item': item,
            'Quantity': qty,
        })
    
    try:
        with open(filename, mode='a', newline='') as file:
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            if not file_exists or os.path.getsize(filename) == 0:
                writer.writeheader() # Write header only if file is new/empty
            writer.writerows(data_to_write)
        print(f"✅ Transaction logged to {filename} (Simplified)")
    except Exception as e:
        print(f"An error occurred while logging transaction to {filename}: {e}")

# 💰 Calculate Historical Income - REMOVED FUNCTION
# The logic to calculate income is now more complex as prices are not logged.
# It requires reading data.csv and cross-referencing prices from menu_stock.csv or a separate historical price log.
# For simplicity, we will just use the session total sales in the main function.

# --- ORIGINAL POS FUNCTIONS (Minor changes for CSV integration) ---

def input_menu():
    """Initial product/stock input - now only runs if load_menu_stock returns empty."""
    # This is slightly modified to be called by main only if no data is loaded.
    menu = {}
    stock = {}
    print("Enter available Strains or Products. \nType 'done' when finished.")
    # ... (The rest of the input_menu logic remains the same for data entry)
    while True:
        name = input("\tEnter STRAIN NAME or PRODUCTS (or type 'done' if finished): ").strip()
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


# 🟡 Monitor Low or Out of Stock Items
def monitor_stock(stock):
    low_stock = {item: qty for item, qty in stock.items() if 0 < qty <= 3}
    out_of_stock = [item for item, qty in stock.items() if qty == 0]
    
    if low_stock:
        print("🟡 LOW STOCK Items (Qty <= 3):")
        for item, qty in low_stock.items():
            print(f"    • {item}: {qty}")
            
    if out_of_stock:
        print("🔴 OUT OF STOCK Items:")
        for item in out_of_stock:
            print(f"    • {item}")

    if not low_stock and not out_of_stock:
        print("\t✅ All products sufficiently stocked.")
    print("---------------------------")


# 🔵 Display All Stock Levels
def display_stock_count(stock):
    print("\n📦 CURRENT STOCK LEVELS:")
    if not stock:
        print("⚠️ No products in inventory.")
        return
    for item, qty in stock.items():
        print(f"    {item:<15}: {qty} in stock")
    print("---------------------------")


# Update Products & Stock
def update_menu(menu, stock):
    print("\n--- UPDATE PRODUCTS & STOCK ---")
    while True:
        print("\nCurrent Products:")
        for item, price in menu.items():
            qty = stock.get(item, 0)
            print(f"  {item:<15} ₱{price:<8.2f} ({qty} in stock)")

        monitor_stock(stock)
        display_stock_count(stock)

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
                    display_stock_count(stock)
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
                display_stock_count(stock)
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
                    display_stock_count(stock)
                else:
                    print("Removal canceled.")
            else:
                print("Product / Strain not found.")

        elif choice == '5':
            save_menu_stock(menu, stock) # Save on exit from update menu
            print("Returning to main menu...")
            break

        else:
            print("Invalid choice. Please choose 1-5.")


def take_order(menu, stock):
    order = {}
    print("\nTAKE CUSTOMER ORDER. TYPE 'DONE' WHEN FINISHED")

    print("\t\tLORENCE'S BETTA FISH")
    print("\n\t\t--- Available Strains and Products ---")
    for item, price in menu.items():
        qty = stock.get(item, 0)
        stock_status = f"({qty} in stock)" if qty > 0 else "(OUT OF STOCK)"
        print(f"  \t{item:<15} ₱{price:.2f} {stock_status}")
    print("\t ----------------------------------")

    monitor_stock(stock)
    # display_stock_count(stock) # Already called by monitor_stock for visual clarity

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


def print_receipt(order, menu):
    print("\n" + "="*30)
    print("         ORDER RECEIPT")
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


# 💳 Payment Section (No stock monitoring here)
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
                    print("\n" + "="*30)
                    print(f"\n✅ Transaction Successful (Cash)")
                    print(f"💰 CHANGE: ₱{change:.2f}")
                    print("\n" + "="*30)
                    print("Thank you for ordering with us!")
                    print("="*30)
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


def deduct_stock(stock, order):
    for item, qty in order.items():
        if item in stock:
            stock[item] -= qty
    print("\n✅ Stock Updated After Sale.")
    display_stock_count(stock)
    monitor_stock(stock)

# --- MAIN LOGIC WITH CSV INTEGRATION (Modified for Income Logic Change) ---
def main():
    print("Welcome to the LORENCE'S BETTA FISH")

    # 1. Load data from CSV
    menu, stock = load_menu_stock()

    # 2. If no data loaded, prompt for initial input
    if not menu:
        print("\n--- INITIAL SETUP ---")
        menu, stock = input_menu()
        if not menu:
            print("No menu items entered. Exiting.")
            return
        save_menu_stock(menu, stock) # Save initial setup

    print("\n\t\t---- Strains and Products successfully loaded! ----")
    print("\t\t\tProduct | Price | Stock")
    for item, price in menu.items():
        qty = stock.get(item, 0)
        print(f"\t\t\t{item:<10}: ₱{price:.2f} ({qty})")

    monitor_stock(stock)
    display_stock_count(stock)

    session_total_sales = 0
    # Removed historical income calculation due to simplified data.csv structure
    print("💰 Historical income must be calculated externally using this log and price data.")


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
                
                # --- CSV LOGGING AND STOCK UPDATE ---
                log_transaction(order, menu, order_total) # 👈 Log to data.csv (Simplified)
                deduct_stock(stock, order) # 👈 stock shown here after payment
                save_menu_stock(menu, stock) # 👈 Save updated stock to menu_stock.csv
                # -----------------------------------
                
                session_total_sales += amount_paid

        elif choice == '2':
            update_menu(menu, stock) # Stock is saved inside update_menu when returning.

        elif choice == '3':
            # 3. Final Save and Report
            save_menu_stock(menu, stock) 
            # final_historical_income = calculate_historical_income() # Removed

            print("\n" + "="*40)
            print("         END OF SESSION REPORT")
            print("="*40)
            print(f"Revenue this Session: ₱{session_total_sales:.2f}")
            print("Historical Revenue not shown (log is simplified).")
            print("\n--- Remaining Inventory ---")
            for item, qty in stock.items():
                print(f"  {item:<15}: {qty} units")
            monitor_stock(stock)
            display_stock_count(stock)
            print("="*40)
            print("Exiting POS. Goodbye!")
            break

        else:
            print("Invalid choice. Please select 1-3.")


if __name__ == '__main__':
    main()