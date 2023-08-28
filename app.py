import os
import json
from flask import Flask, jsonify
from flask_cors import CORS, cross_origin
import gspread
from oauth2client.service_account import ServiceAccountCredentials

app = Flask(__name__)
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'

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
        self.gender: str = google_sheet_record['gender']
        self.sub_category: str = google_sheet_record['subCategory']
        self.price: float = float(str(google_sheet_record['price']).replace('$', ''))
        self.image_url: str = google_sheet_record['imageUrl']
        self.details: str = google_sheet_record['details']

    def to_json(self, details = False):
        product_json = {
            'id': self.id,
            'vendor': self.vendor,
            'name': self.name,
            'category': self.category,
            'gender': self.gender,
            'subCategory': self.sub_category,
            'price': self.price,
            'imageUrl': self.image_url
        }
        if details:
            product_json['details'] = self.details
        return product_json

# Routes
@app.route('/shop', methods = ['GET'])
@cross_origin()
def shop():
    return jsonify([product.to_json() for product in [Product(prod_dict) for prod_dict in google_sheet.worksheet('Products').get_all_records()]])

@app.route('/shop/<category>', methods = ['GET'])
@cross_origin()
def shop_category(category):
    products = [Product(product_dict) for product_dict in google_sheet.worksheet('Products').get_all_records()]
    filtered_products = [product for product in products if product.category == category]
    return jsonify([product.to_json() for product in filtered_products])

@app.route('/shop/<category>/<gender>', methods = ['GET'])
@cross_origin()
def shop_category_gender(category, gender):
    products = [Product(product_dict) for product_dict in google_sheet.worksheet('Products').get_all_records()]
    filtered_products = [product for product in products if (product.category == category) & (product.gender == gender)]
    return jsonify([product.to_json() for product in filtered_products])

@app.route('/shop/<category>/<gender>/<sub_category>', methods = ['GET'])
@cross_origin()
def shop_category_gender_subcategory(category, gender, sub_category):
    products = [Product(product_dict) for product_dict in google_sheet.worksheet('Products').get_all_records()]
    filtered_products = [product for product in products if (product.category == category) & (product.gender == gender) & \
                         (product.sub_category == sub_category)]
    return jsonify([product.to_json() for product in filtered_products])

@app.route('/product/<product_id>', methods = ['GET'])
@cross_origin()
def product(product_id):
    products = [Product(product_dict) for product_dict in google_sheet.worksheet('Products').get_all_records()]
    products_from_id = [product for product in products if str(product.id) == str(product_id)]
    if len(products_from_id) == 0:
        # Not found
        return jsonify({})
    return jsonify(products_from_id[0].to_json(details = True))
 
if __name__ == '__main__':
    app.run(debug = False)
