import csv
from app import db, app
from app.models import Bridge

data = [
    {
        'number': '925',
        'name': 'Harbor River',
        'facility': 'US 21',
        'crossing': 'Harbor River',
        'location': 'Beaufort',
        'longitude': None,  # Replace with the actual longitude if available
        'latitude': None,   # Replace with the actual latitude if available
        'photo_url': None,  # Replace with the actual photo URL if available
    },
    # Add more dictionaries for other rows of data
]

with app.app_context():
    with open('bridges.csv', mode='r', encoding='utf-8-sig') as csvfile:
        reader = csv.DictReader(csvfile)
        
        # ... (previous code)

        # Loop through the rows in the CSV file and insert data into the database
        for row in reader:
            # Convert 'None' strings to actual None values for longitude and latitude
            longitude = float(row['longitude']) if row['longitude'] is not None and row['longitude'] != 'None' else None
            latitude = float(row['latitude']) if row['latitude'] is not None and row['latitude'] != 'None' else None

            # Create a new Bridge object with the data
            bridge = Bridge(
                id=row['id'],
                number=row['number'],
                name=row['name'],
                facility=row['facility'],
                crossing=row['crossing'],
                location=row['location'],
                longitude=longitude,
                latitude=latitude,
                photo_url=row['photo_url']
            )

            # Add the Bridge object to the session
            db.session.add(bridge)

        # Commit the changes to the database
        db.session.commit()
        print('Items have been populated into the database.')
