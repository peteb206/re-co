import os
import json
from flask import Flask, jsonify
import gspread
from oauth2client.service_account import ServiceAccountCredentials

app = Flask(__name__)

# Google Sheet
if os.path.isfile('.env'):
    with open('.env') as f:
        for line in f.read().split('\n'):
            key = line.split('=')[0]
            os.environ[key] = line.replace(f'{key}=', '')
google_sheet = gspread.authorize(
    ServiceAccountCredentials.from_json_keyfile_dict(
        json.loads(os.environ['GOOGLE_CLOUD_API_KEY']),
        [
            'https://spreadsheets.google.com/feeds',
            'https://www.googleapis.com/auth/drive'
        ]
    )
).open_by_key('12oIcVvDcdH6IO8fBOfUbU_stIDJLQwMk6oKs5eDThdU')

# Classes
class Product:
    def __init__(self, google_sheet_record: dict):
        self.id: int = google_sheet_record['id']
        self.vendor: str = google_sheet_record['vendor']
        self.name: str = google_sheet_record['name']
        self.category: str = google_sheet_record['category']
        self.price: float = float(str(google_sheet_record['price']).replace('$', ''))
        self.image_url: str = google_sheet_record['imageUrl']
        self.details: str = google_sheet_record['details']

    def to_json(self):
        return {
            'id': self.id,
            'vendor': self.vendor,
            'name': self.name,
            'category': self.category,
            'price': self.price,
            'imageUrl': self.image_url,
            'details': self.details
        }

# Routes
@app.route('/shop', methods = ['GET'])
def shop():
    return jsonify([Product(product_dict).to_json() for product_dict in google_sheet.worksheet('Products').get_all_records()])
 
if __name__ == '__main__':
    app.run(debug = True)