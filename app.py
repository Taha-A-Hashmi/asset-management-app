from flask import Flask, render_template, request, redirect, url_for
from pymongo import MongoClient
from bson.objectid import ObjectId

app = Flask(__name__)

# --- DATABASE CONNECTION ---
# Ensure MongoDB is running on default port 27017
client = MongoClient('mongodb://localhost:27017/')
db = client['asset_management_db']
assets_collection = db['assets']

@app.route('/')
def dashboard():
    all_assets = list(assets_collection.find())
    total_assets = len(all_assets)
    in_stock = sum(1 for a in all_assets if a.get('status') == 'In')
    out_stock = sum(1 for a in all_assets if a.get('status') == 'Out')
    return render_template('dashboard.html', assets=all_assets, total=total_assets, in_stock=in_stock, out_stock=out_stock)

@app.route('/add', methods=['POST'])
def add_asset():
    assets_collection.insert_one({
        'description': request.form.get('description'),
        'serial_number': request.form.get('serial_number'),
        'status': 'In',
        'location': 'Warehouse'
    })
    return redirect(url_for('dashboard'))

@app.route('/update_status/<id>', methods=['POST'])
def update_status(id):
    action = request.form.get('action')
    new_location = request.form.get('location')
    
    if action == 'checkout':
        update_data = {'status': 'Out', 'location': new_location}
    elif action == 'checkin':
        update_data = {'status': 'In', 'location': 'Warehouse'}
        
    assets_collection.update_one({'_id': ObjectId(id)}, {'$set': update_data})
    return redirect(url_for('dashboard'))

@app.route('/delete/<id>')
def delete_asset(id):
    assets_collection.delete_one({'_id': ObjectId(id)})
    return redirect(url_for('dashboard'))

if __name__ == '__main__':
    app.run(debug=True)
