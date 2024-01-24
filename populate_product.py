import csv
from app import db, app
from app.models import Product

with app.app_context():
    with open('products.csv', mode='r', encoding='utf-8-sig') as csvfile:
        reader = csv.DictReader(csvfile)
        
        for row in reader:
            # Create an instance of the Product model with the row data
            product = Product(
                id=row['id'],
                designation=row['designation'],
                supplier=row['supplier'],
                description=row['description'],
                parameters=row['parameters'],
                system=row['system'],
                photo=row['photo']
            )
            # Add to the session
            db.session.add(product)
        
        # Commit the session to save all new Products
        db.session.commit()
        print('Products have been populated into the database.')
