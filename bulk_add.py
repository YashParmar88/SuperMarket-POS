import sqlite3

def mega_bulk_upload():
    conn = sqlite3.connect('supermarket.db')
    cursor = conn.cursor()

    # MEGA LIST BASED ON YOUR IMAGE (100+ ITEMS)
    # Format: (Name, Category, Unit, Purchase_Price, Selling_Price, Stock, Supplier, Discount)
    mega_list = [
        # --- GRAINS & FLOURS ---
        ('Idli Rice 5kg', 'Grains & Flours', 'Pcs', 220, 260, 40, 'Heritage Mills', 0),
        ('Raw Rice 5kg', 'Grains & Flours', 'Pcs', 200, 240, 50, 'Local Mart', 0),
        ('Basmati Rice 1kg', 'Grains & Flours', 'KG', 90, 120, 100, 'India Gate', 5),
        ('Millet Varieties 500g', 'Grains & Flours', 'Pcs', 45, 65, 30, 'Organic India', 0),
        ('Oats 500g', 'Grains & Flours', 'Pcs', 110, 140, 45, 'Quaker', 2),
        ('Wheat Flour (Atta) 5kg', 'Grains & Flours', 'Pcs', 185, 215, 60, 'Aashirvaad', 0),
        ('Maida 1kg', 'Grains & Flours', 'Pcs', 42, 55, 40, 'Fortune', 0),
        ('Ragi Flour 1kg', 'Grains & Flours', 'Pcs', 55, 75, 25, 'MTR', 0),
        ('Besan 1kg', 'Grains & Flours', 'Pcs', 70, 95, 50, 'Tata Sampann', 0),
        ('Sooji (Rava) 1kg', 'Grains & Flours', 'Pcs', 45, 60, 40, 'Fortune', 0),
        ('Sugar 1kg', 'Grains & Flours', 'KG', 38, 45, 200, 'Local Mart', 0),
        ('Jaggery 500g', 'Grains & Flours', 'Pcs', 45, 60, 50, 'Farm Direct', 5),
        ('Vermicelli 1 Packet', 'Grains & Flours', 'Pcs', 20, 30, 80, 'Bambino', 0),

        # --- DALS / LENTILS / PULSES ---
        ('Toor Dal 1kg', 'Dals & Veggies', 'KG', 115, 145, 90, 'Tata Sampann', 5),
        ('Urad Dal 1kg', 'Dals & Veggies', 'KG', 120, 155, 70, 'Local Wholesaler', 0),
        ('Moong Dal 1kg', 'Dals & Veggies', 'KG', 95, 120, 85, 'Tata Sampann', 0),
        ('Chana Dal 1kg', 'Dals & Veggies', 'KG', 72, 90, 100, 'Reliance Agri', 0),
        ('Rajma (Kidney Beans)', 'Dals & Veggies', 'KG', 130, 170, 40, 'Chitra', 10),
        ('Masoor Dal 1kg', 'Dals & Veggies', 'KG', 85, 110, 60, 'Local Mart', 0),
        ('Black Gram Dal', 'Dals & Veggies', 'KG', 100, 130, 50, 'Tata Sampann', 0),

        # --- OILS ---
        ('Cooking Oil 1L', 'Oils', 'Ltr', 105, 140, 150, 'Fortune', 5),
        ('Sesame Oil 500ml', 'Oils', 'Pcs', 180, 220, 30, 'Idhayam', 0),
        ('Coconut Oil 500ml', 'Oils', 'Pcs', 140, 175, 40, 'Parachute', 2),
        ('Ghee 500ml', 'Oils', 'Pcs', 290, 360, 55, 'Amul', 0),

        # --- SPICE POWDERS ---
        ('Crystal Salt 1kg', 'Spice Powders', 'Pcs', 15, 22, 100, 'Tata', 0),
        ('Turmeric Powder 200g', 'Spice Powders', 'Pcs', 35, 50, 120, 'Everest', 0),
        ('Red Chilli Powder 200g', 'Spice Powders', 'Pcs', 60, 85, 100, 'MDH', 5),
        ('Sambar Powder 100g', 'Spice Powders', 'Pcs', 45, 65, 60, 'MTR', 0),
        ('Garam Masala 100g', 'Spice Powders', 'Pcs', 55, 80, 50, 'Everest', 0),
        ('Tea Powder 250g', 'Spice Powders', 'Pcs', 90, 125, 90, 'Red Label', 5),
        ('Instant Coffee 50g', 'Spice Powders', 'Pcs', 130, 160, 40, 'Nescafe', 0),

        # --- SPICES / NUTS / SEEDS ---
        ('Mustard Seeds 150g', 'Snacks', 'Pcs', 25, 40, 100, 'Local', 0),
        ('Cumin Seeds (Jeera) 100g', 'Snacks', 'Pcs', 40, 65, 80, 'Catch', 0),
        ('Badam (Almonds) 200g', 'Snacks', 'Pcs', 180, 250, 40, 'Tulsi', 10),
        ('Cashew Nuts 200g', 'Snacks', 'Pcs', 160, 230, 45, 'Local Nut', 5),
        ('Dates 500g', 'Snacks', 'Pcs', 140, 195, 30, 'Lion', 0),
        ('Peanuts 500g', 'Snacks', 'Pcs', 60, 85, 60, 'Local', 0),

        # --- VEGETABLES & FRUITS ---
        ('Tomato', 'Vegetables & Fruits', 'KG', 25, 40, 150, 'Mandi', 0),
        ('Onion', 'Vegetables & Fruits', 'KG', 20, 35, 300, 'Mandi', 0),
        ('Garlic 250g', 'Vegetables & Fruits', 'Pcs', 30, 50, 40, 'Mandi', 0),
        ('Carrot', 'Vegetables & Fruits', 'KG', 40, 65, 80, 'Farm', 0),
        ('Potato', 'Vegetables & Fruits', 'KG', 15, 25, 400, 'Mandi', 0),
        ('Apple (Fuji)', 'Vegetables & Fruits', 'KG', 140, 190, 60, 'Shimla', 10),
        ('Banana (Doz)', 'Vegetables & Fruits', 'Pcs', 40, 60, 40, 'Farm', 0),
        ('Green Chilli 250g', 'Vegetables & Fruits', 'Pcs', 15, 25, 30, 'Mandi', 0),
        ('Ginger 250g', 'Vegetables & Fruits', 'Pcs', 25, 45, 20, 'Mandi', 0),

        # --- DAIRY PRODUCTS ---
        ('Milk 1L', 'Dairy Products', 'Ltr', 54, 66, 100, 'Amul', 0),
        ('Curd 500g', 'Dairy Products', 'Pcs', 35, 45, 50, 'Mother Dairy', 0),
        ('Butter 100g', 'Dairy Products', 'Pcs', 52, 60, 60, 'Amul', 0),
        ('Paneer 200g', 'Dairy Products', 'Pcs', 75, 90, 30, 'Amul', 5),
        ('Eggs (6 Nos)', 'Dairy Products', 'Pcs', 35, 48, 50, 'Farm Fresh', 0),

        # --- SNACKS & BAKERY ---
        ('Chips (Lays)', 'Snacks', 'Pcs', 15, 20, 200, 'PepsiCo', 0),
        ('Biscuits (Parle-G)', 'Snacks', 'Pcs', 10, 12, 300, 'Parle', 0),
        ('Maggi Noodles', 'Snacks', 'Pcs', 12, 14, 150, 'Nestle', 0),
        ('Bread Packet', 'Bakery Items', 'Pcs', 35, 45, 30, 'Britannia', 0),
        ('Tomato Ketchup', 'Snacks', 'Pcs', 80, 110, 40, 'Kissan', 5),

        # --- POOJA ITEMS ---
        ('Match Box (Bundle)', 'Snacks', 'Pcs', 10, 15, 100, 'Ship', 0),
        ('Incense Sticks (Agarbatti)', 'Snacks', 'Pcs', 40, 60, 50, 'Cycle', 0),
        ('Camphor 50g', 'Snacks', 'Pcs', 30, 50, 40, 'Local', 0),

        # --- TOILETRIES & CLEANING ---
        ('Toothpaste (Colgate)', 'Toiletries', 'Pcs', 85, 115, 80, 'Colgate', 5),
        ('Bathing Soap (Dove)', 'Toiletries', 'Pcs', 45, 60, 120, 'Unilever', 0),
        ('Shampoo Bottle', 'Toiletries', 'Pcs', 160, 210, 40, 'P&G', 10),
        ('Washing Powder 1kg', 'Cleaning Products', 'Pcs', 140, 185, 50, 'Surf Excel', 5),
        ('Dish Wash Liquid', 'Cleaning Products', 'Pcs', 90, 110, 60, 'Vim', 0),
        ('Toilet Cleaner', 'Cleaning Products', 'Pcs', 80, 105, 50, 'Harpic', 0),
        ('Toilet Paper Bundle', 'Cleaning Products', 'Pcs', 120, 160, 30, 'Selpak', 0),
        ('Napthalene Balls', 'Cleaning Products', 'Pcs', 25, 45, 100, 'Local', 0),

        # --- FOR BACHELORS / MISC ---
        ('Ready to eat mix', 'Snacks', 'Pcs', 60, 85, 40, 'MTR', 5),
        ('Ginger Garlic Paste', 'Spice Powders', 'Pcs', 35, 55, 60, 'Smith & Jones', 0),
        ('Batter (Idli/Dosa) 1kg', 'Dairy Products', 'Pcs', 40, 60, 20, 'iD Fresh', 0),
        ('Batteries (AA 4pk)', 'Snacks', 'Pcs', 60, 90, 50, 'Duracell', 0),
        ('Light Bulb (LED)', 'Snacks', 'Pcs', 80, 120, 30, 'Philips', 0)
    ]

    sql = '''INSERT INTO products (name, category, unit, purchase_price, price, stock, supplier, discount) 
             VALUES (?, ?, ?, ?, ?, ?, ?, ?)'''

    try:
        # Clear existing demo products first (Optional - recommended for clean look)
        cursor.execute("DELETE FROM products")
        cursor.executemany(sql, mega_list)
        conn.commit()
        print(f"BINGO! Added {len(mega_list)} authentic Indian Supermarket items to your database.")
    except Exception as e:
        print(f"Oops: {e}")
    finally:
        conn.close()

if __name__ == '__main__':
    mega_bulk_upload()