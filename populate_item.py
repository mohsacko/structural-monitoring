import csv
from app import db, app
from app.models import Item, Product

with app.app_context():
    with open('item.csv', mode='r', encoding='utf-8-sig') as csvfile:
        reader = csv.DictReader(csvfile)
        
        for row in reader:
            # Fetch the Product using the product_id from the CSV
            product_id = int(row['products'])  # Assuming product_id is an integer
            product = Product.query.get(product_id)

            if product:
                # Create an instance of the Item model with the row data
                item = Item(
                    id=row['id'],
                    reference=row['reference'],
                    condition=row['condition'],
                    unit=row['unit'],
                    measurement=row['measurement'],
                    products=[product],  # Assign as a list
                )
                # Add to the session
                db.session.add(item)
        
        # Commit the session to save all new Items
        db.session.commit()
        print('Items have been populated into the database.')

