from flask import Flask, render_template, request, redirect, url_for
from pymongo import MongoClient
from bson.objectid import ObjectId

app = Flask(__name__)

# --- CONFIGURATION (Hardcoded for Speed) ---
# Your specific Cloud MongoDB Atlas URI
MONGO_URI = "mongodb+srv://taha_admin:hospital123@cluster0.ukoxtzf.mongodb.net/hospital_crm_db?retryWrites=true&w=majority&appName=Cluster0&authSource=admin"

# Connect to the Cloud Database
client = MongoClient(MONGO_URI)

# The URI points to 'hospital_crm_db', so we use that.
db = client['hospital_crm_db']
assets_collection = db['assets']

# --- ROUTES ---

@app.route('/')
def dashboard():
    # 1. Fetch all assets
    all_assets = list(assets_collection.find())
    
    # 2. Calculate Stats for the Dashboard
    total_assets = len(all_assets)
    # Check status safely (using .get in case field is missing)
    in_stock = sum(1 for a in all_assets if a.get('status') == 'In')
    out_stock = sum(1 for a in all_assets if a.get('status') == 'Out')
    
    # Pass data to the template
    return render_template('dashboard.html', 
                           assets=all_assets, 
                           total=total_assets, 
                           in_stock=in_stock, 
                           out_stock=out_stock)

@app.route('/add', methods=['POST'])
def add_asset():
    # Add new machine to DB
    assets_collection.insert_one({
        'description': request.form.get('description'),
        'serial_number': request.form.get('serial_number'),
        'status': 'In',        # Default status is always In
        'location': 'Warehouse' # Default location
    })
    return redirect(url_for('dashboard'))

@app.route('/update_status/<id>', methods=['POST'])
def update_status(id):
    # Handle Check-In / Check-Out logic
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