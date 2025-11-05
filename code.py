import csv
import os
import json # Used to save/load the 'order_items' dictionary within the transactions CSV

# CSV FILE CONSTANTS 
INVENTORY_FILE = 'inventory.csv'
SALES_FILE = 'transactions.csv'

def load_data():
    """Load menu and stock data from INVENTORY_FILE."""
    menu = {}
    stock = {}
    if os.path.exists(INVENTORY_FILE):
        print("\n")
        try:
            with open(INVENTORY_FILE, mode='r', newline='') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    key = row['item_key']
                    menu[key] = float(row['price'])
                    stock[key] = int(row['stock'])
            print("Inventory loaded successfully.")
        except Exception as e:
            print("\n")
    return menu, stock

#inventory csv
def save_inventory(menu, stock):
    """Save menu and stock data to INVENTORY_FILE."""
    try:
        with open(INVENTORY_FILE, mode='w', newline='') as file:
            fieldnames = ['item_key', 'price', 'stock']
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            writer.writeheader()
            for item_key, price in menu.items():
                writer.writerow({
                    'item_key': item_key,
                    'price': price,
                    'stock': stock.get(item_key, 0)
                })
        # print(f"Inventory saved to {INVENTORY_FILE}")
    except Exception as e:
        print(f"Error saving inventory: {e}")

#transaction csv
def load_transactions():
    """Load transaction history from SALES_FILE."""
    transactions = []
    if os.path.exists(SALES_FILE):
        print("\n")
        try:
            with open(SALES_FILE, mode='r', newline='') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    # Convert total_amount to float and order_items (JSON string) back to dict
                    row['total_amount'] = float(row['total_amount'])
                    row['order_items'] = json.loads(row['order_items'])
                    transactions.append(row)
            print("Transactions loaded successfully.")
        except Exception as e:
            print(f"Error loading transactions: {e}. Starting with empty history.")
    return transactions

def save_transaction(tx):
    """Append a single transaction to SALES_FILE."""
    # Convert 'order_items' dict to JSON string for CSV storage
    tx_to_save = tx.copy()
    tx_to_save['order_items'] = json.dumps(tx_to_save['order_items'])

    is_new_file = not os.path.exists(SALES_FILE)
    try:
        with open(SALES_FILE, mode='a', newline='') as file:
            fieldnames = ['customer', 'total_amount', 'method', 'status', 'order_items']
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            if is_new_file:
                writer.writeheader()
            writer.writerow(tx_to_save)
        # print(f"Transaction appended to {SALES_FILE}")
    except Exception as e:
        print(f"Error saving transaction: {e}")

def rewrite_transactions(transactions):
    """Overwrite the entire SALES_FILE after a transaction removal."""
    try:
        with open(SALES_FILE, mode='w', newline='') as file:
            fieldnames = ['customer', 'total_amount', 'method', 'status', 'order_items']
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            writer.writeheader()
            for tx in transactions:
                 # Convert 'order_items' dict to JSON string for CSV storage
                tx_to_save = tx.copy()
                tx_to_save['order_items'] = json.dumps(tx_to_save['order_items'])
                writer.writerow(tx_to_save)
        print(f"Transaction history saved to {SALES_FILE}")
    except Exception as e:
        print(f"Error rewriting transactions: {e}")

# --- ORIGINAL FUNCTIONS MODIFIED/RETAINED ---

def input_menu():
    # Only runs if no data was loaded initially
    menu = {}
    stock = {}
    print("Enter available Strains or Products. \nType 'done' when finished.")
    while True:
        name = input("\tEnter STRAIN NAME or PRODUCTS (or type 'done' if finished): ").strip()
        if name.lower() == 'done':
            break
        if not name:
            print("Product name cannot be empty. Try again.")
            continue
        
        key_name = name.lower()
        if key_name in menu:
            print(f"Product '{name}' already exists. Use Update option instead.")
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

            menu[key_name] = price
            stock[key_name] = qty_in_stock

        except ValueError:
            print("Invalid input (price or stock). Try again.")

    return menu, stock

def display_stock_count(stock):
    print("\n📦 CURRENT STOCK:")
    if not stock:
        print("⚠️ No products in inventory.")
        return
    for item, qty in stock.items():
        print(f"    {item.title():<15}: {qty} in stock")
    print("---------------------------")


def update_menu(menu, stock):
    print("\n--- UPDATE PRODUCTS & STOCK ---")
    while True:
        print("\nCurrent Products:")
        for item, price in menu.items():
            qty = stock.get(item, 0)
            print(f"  {item.title():<15} ₱{price:<8.2f} ({qty} in stock)")

        display_stock_count(stock)

        print("\nOptions:")
        print("1. Update Price")
        print("2. Add Stock")
        print("3. Add New Product/Strain")
        print("4. Remove Product/Strain")
        print("5. Return to Main Menu")

        choice = input("Select an option (1-5): ").strip()
        
        def get_key_name(prompt):
            item = input(prompt).strip().lower()
            return item if item in menu else None

        if choice == '1':
            key = get_key_name("Enter product/strain name to update price: ")
            if key:
                try:
                    new_price = float(input(f"Enter new price for {key.title()}: ₱"))
                    if new_price <= 0:
                        print("Price must be positive.")
                        continue
                    menu[key] = new_price
                    print(f"✅ Price for {key.title()} updated to ₱{new_price:.2f}")
                    save_inventory(menu, stock) # Save after update
                except ValueError:
                    print("Invalid price input.")
            else:
                print("Product/strain not found.")

        elif choice == '2':
            key = get_key_name("Enter product/strain name to add stock: ")
            if key:
                try:
                    add_qty = int(input(f"Enter quantity to add for {key.title()}: "))
                    if add_qty < 0:
                        print("Quantity cannot be negative.")
                        continue
                    stock[key] += add_qty
                    print(f"✅ Added {add_qty} units to {key.title()}. New stock: {stock[key]}")
                    save_inventory(menu, stock) # Save after update
                    display_stock_count(stock)
                except ValueError:
                    print("Invalid quantity input.")
            else:
                print("Product/strain not found.")

        elif choice == '3':
            new_item_name = input("Enter NEW PRODUCT OR STRAIN NAME: ").strip()
            new_item_key = new_item_name.lower()
            
            if new_item_key in menu:
                print("Product/strain already exists. Use Update instead.")
                continue
            try:
                new_price = float(input(f"Enter price for {new_item_name}: ₱"))
                new_stock = int(input(f"Enter stock for {new_item_name}: "))
                if new_price <= 0 or new_stock < 0:
                    print("Invalid price or stock input.")
                    continue
                menu[new_item_key] = new_price
                stock[new_item_key] = new_stock
                print(f"✅ Added new product: {new_item_name.title()} (₱{new_price:.2f}, {new_stock} in stock)")
                save_inventory(menu, stock) # Save after update
                
            except ValueError:
                print("Invalid input. Try again.")

        elif choice == '4':
            key = get_key_name("Enter product/strain name to remove: ")
            if key:
                confirm = input(f"Are you sure you want to remove {key.title()}? (yes/no): ").lower()
                if confirm == 'yes':
                    del menu[key]
                    del stock[key]
                    print(f"✅ {key.title()} removed from the menu.")
                    save_inventory(menu, stock) # Save after update
                    
                else:
                    print("Removal canceled.")
            else:
                print("Product / Strain not found.")

        elif choice == '5':
            print("Returning to main menu...")
            break

        else:
            print("Invalid choice. Please choose 1-5.")

def take_order(menu, stock):
    order = {}
    
    print("\nTAKE CUSTOMER ORDER. TYPE 'DONE' WHEN FINISHED or 'CANCEL' to canceled.") 

    print("\t\tLORENCE'S BETTA FISH")
    print("\n\t--- Available Strains and Products ---")
    for item_key, price in menu.items():
        qty = stock.get(item_key, 0)
        # We keep the stock status here for ordering
        stock_status = f"({qty} in stock)" if qty > 0 else "(OUT OF STOCK)"
        print(f"\t{item_key.title():<15} ₱{price:.2f} {stock_status}")
    print("\t ----------------------------------")

    while True:
        item_input = input("\tEnter product/strain name to order (or 'done' to checkout / 'cancel' to cancelled): ").strip()
        item_key = item_input.lower()
        
        if item_key == 'cancel':
            print("\n❌ Order cancelled by user. Returning to main menu.")
            return {}, "" 
        
        if item_key == 'done':
            break
        
        if item_key not in menu:
            print(f"\tSorry, we don't have {item_input.title()}. Please order from the menu.")
            continue

        available_stock = stock.get(item_key, 0)
        ordered_so_far = order.get(item_key, 0)
        remaining_stock = available_stock - ordered_so_far

        if remaining_stock <= 0:
            print(f"\tSorry, {item_key.title()} is OUT OF STOCK or fully reserved in this order.")
            continue

        try:
            qty = int(input(f"\tEnter quantity for {item_key.title()} (Max: {remaining_stock}): "))
            if qty <= 0:
                print("Quantity must be positive.")
                continue
            if qty > remaining_stock:
                print(f"\tInsufficient stock! Only {remaining_stock} of {item_key.title()} available.")
                continue
            
            order[item_key] = order.get(item_key, 0) + qty
            print(f"  Added {qty}x {item_key.title()} to order. Type 'done' to finish or 'cancel' to abort.")
            
        except ValueError:
            print("Invalid quantity. Try again.")
            
    if order:
        customer_name = input("\n👤 Order finished. Enter Customer Name: ").strip() or "Guest Customer"
        print(f"Processing final order for: **{customer_name}**")
    else:
        customer_name = "Guest Customer"

    return order, customer_name 


def print_receipt(order, menu, customer_name=""):
    print("\n" + "="*40)
    print("           ORDER RECEIPT")
    if customer_name and customer_name != "Guest Customer":
        print(f"\tCustomer: {customer_name}")
    print("="*40)
    # New header format
    print(f"{'ITEM':<15}{'PRICE':>8}{'QTY':>4}{'TOTAL':>10}")
    print("-" * 40)
    
    total = 0
    for item_key, qty in order.items():
        price = menu[item_key]
        subtotal = price * qty
        total += subtotal
        
        # Displaying price before multiplication
        print(f"{item_key.title():<15} ₱{price:>7.2f} x{qty:<3} ₱{subtotal:>9.2f}")
        
    print("-" * 40)
    print(f"{'GRAND TOTAL':<30} ₱{total:>9.2f}")
    print("="*40)
    return total

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
                    print("\n" + "="*40)
                    print(f"\n✅ Transaction Successful (Cash)")
                    print(f"💰 CHANGE: ₱{change:.2f}")
                    print("\n" + "="*40)
                    print("Thank you for ordering with us! HAPPY FISH KEEPING")
                    print("="*40)
                    return total, "Cash", "PAID"
                except ValueError:
                    print("Invalid cash amount. Please enter a number.")
            
        elif method == '2':
            print("\n💳 GCash Payment Selected.")
            print(f"Scan QR or send ₱{total:.2f} to 0912789098 (L** P**).")
            confirm = input("Press Enter when payment is CONFIRMED, or type 'pending' to mark for later confirmation: ").lower().strip()
            
            if confirm == 'pending':
                print("⚠️ Transaction marked as **GCash Pending/UNPAID**.")
                return 0, "GCash", "UNPAID (GCash Pending)" 
            else:
                print(f"\n✅ Transaction Successful (GCash)")
                print("Thankyou for ordering us! HAPPY FISH KEEPING")
                print("No change needed.")
                return total, "GCash", "PAID"
            
        else:
            print("Invalid selection. Please choose '1' or '2'.")


def deduct_stock(stock, order):
    for item, qty in order.items():
        if item in stock:
            stock[item] -= qty
    print("\nStock Updated After Sale.")
    save_inventory(menu, stock) # Save inventory after stock change
    display_stock_count(stock)


def view_transactions(transactions):
    """Prints a numbered list of transactions."""
    print("\n📊 --- SESSION TRANSACTION HISTORY ---")
    if not transactions:
        print("No transactions recorded yet.")
        return False
    
    # Header
    print("-" * 60)
    print(f"{'No.':<4}{'CUSTOMER':<15}{'TOTAL (₱)':<12}{'METHOD':<8}{'STATUS':<21}")
    print("-" * 60)

    for i, t in enumerate(transactions, 1):
        status_color = "✅ PAID" if t['status'] == "PAID" else "🔴 UNPAID (GCash Pending)"
        print(f"{i:<4}{t['customer'][:14]:<15}{t['total_amount']:.2f}{'':<2}{t['method'][:7]:<8}{status_color:<21}")
    
    print("-" * 60)
    return True 

def manage_transactions(transactions, stock, session_total_sales):
    """Allows user to remove a single transaction and update stock/sales if necessary."""
    
    if not view_transactions(transactions):
        return session_total_sales
        
    while True:
        choice = input("\nEnter transaction number to REMOVE (or 'done' to exit management): ").strip()
        
        if choice.lower() == 'done':
            print("Exiting transaction management.")
            break

        try:
            index = int(choice) - 1
            
            if 0 <= index < len(transactions):
                tx = transactions[index]
                
                action = input(f"Transaction #{index+1} ({tx['customer']}, ₱{tx['total_amount']:.2f}, Status: {tx['status']}). Are you sure you want to **REMOVE** this transaction? (yes/no): ").lower().strip()
                
                if action == 'yes':
                    removed_status = tx['status']
                    removed_customer = tx['customer']
                    removed_total = tx['total_amount']
                    
                    # Refund stock if the order was unpaid (since it was never deducted)
                    if removed_status == "UNPAID (GCash Pending)":
                        for item_key, qty in tx['order_items'].items():
                            if item_key in stock:
                                stock[item_key] += qty
                                print(f"  ⬆️ Stock returned: {qty}x {item_key.title()}")
                    
                    # Deduct from sales if it was a PAID order being removed
                    elif removed_status == "PAID":
                        session_total_sales -= removed_total
                        print(f"  ⬇️ Sales adjusted: -₱{removed_total:.2f} removed from session total.")


                    del transactions[index]
                    
                    # Save updated inventory and transactions back to CSV
                    save_inventory(menu, stock) 
                    rewrite_transactions(transactions) 

                    print(f"✅ Transaction for **{removed_customer}** (Status: {removed_status}) has been **REMOVED** from history.")
                    
                    view_transactions(transactions) 
                    
                else:
                    print("Removal canceled.")
                    
            else:
                print("Invalid number. Please choose a number from the list or 'done'.")
                
        except ValueError:
            print("Invalid input. Please enter a number or 'done'.")
            
    return session_total_sales 

def main():
    global menu, stock # Make menu and stock global so sub-functions (like deduct_stock) can access them for saving

    print("Welcome to the LORENCE'S BETTA FISH")

    menu, stock = load_data()

    # If no data loaded, prompt for initial input
    if not menu:
        print("--- Initial Setup Required ---")
        menu, stock = input_menu()
        if not menu:
            print("No menu items entered. Exiting.")
            return
        save_inventory(menu, stock) # Save initial setup

    print("\n\t  -- Strains and Products successfully loaded/created! --")
    print("\t\t\tProduct | Price | Stock")
    for item, price in menu.items():
        qty = stock.get(item, 0)
        print(f"\t\t\t{item.title():<10}: ₱{price:.2f} ({qty})")

    transactions = load_transactions()
    
    # Recalculate sales total from loaded PAID transactions
    session_total_sales = sum(t['total_amount'] for t in transactions if t['status'] == 'PAID')
    print(f"\nLoaded Session Sales Total: ₱{session_total_sales:.2f}")


    while True:
        print("\nOptions:")
        print("1. Take a Order")
        print("2. Update Products/Stock")
        print("3. View Transactions")
        print("4. Manage Transactions")
        print("5. End Session")
        choice = input("Choose an option (1-5): ").strip()

        if choice == '1':
            order, customer_name = take_order(menu, stock) 
            
            if not order and not customer_name:
                print("Order process aborted. Returning to main menu.")
                continue 

            if not order:
                print("No items ordered.")
            else:
                order_total = print_receipt(order, menu, customer_name)
                
                paid_amount, method, status = process_payment(order_total) 
                
                new_transaction = {
                    'customer': customer_name,
                    'total_amount': order_total,
                    'method': method,
                    'status': status,
                    'order_items': order
                }

                transactions.append(new_transaction)
                save_transaction(new_transaction) # Save new transaction to CSV
                
                if status == "PAID":
                    session_total_sales += order_total
                    deduct_stock(stock, order)
                else:
                    print("⚠️ Stock not deducted for pending GCash payment.")

        elif choice == '2':
            update_menu(menu, stock) # Inventory saving is handled inside update_menu

        elif choice == '3':
            view_transactions(transactions)

        elif choice == '4':
            # Transaction management will update stock and rewrite transactions.csv
            session_total_sales = manage_transactions(transactions, stock, session_total_sales)

        elif choice == '5':
            print("\n" + "="*40)
            print("         END OF SESSION REPORT")
            print("="*40)
            print(f"Total Revenue (Paid Orders Only): ₱{session_total_sales:.2f}")
            print("\n--- Final Inventory ---")
            display_stock_count(stock)
            
            pending_tx = [t for t in transactions if t['status'] != "PAID"]
            if pending_tx:
                print("\n⚠️ NOTE: The following orders were UNPAID (GCash Pending):")
                for t in pending_tx:
                    print(f"  - {t['customer']} (₱{t['total_amount']:.2f})")
            
            print("="*40)
            # Final saves (optional, as updates are saved in real-time, but good for safety)
            save_inventory(menu, stock) 
            rewrite_transactions(transactions)
            print("Data saved. Exiting POS. Goodbye!")
            break

        else:
            print("Invalid choice. Please select 1-5.")


if __name__ == '__main__':
    # Initialize global variables before main runs (used in deduct_stock)
    menu = {}
    stock = {}
    main()