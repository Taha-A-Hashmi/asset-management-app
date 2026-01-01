import os
from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
from pymongo import MongoClient
from bson.objectid import ObjectId

# NOTE: Since we are hardcoding the password, do not upload this specific file 
# to a public GitHub repository.

# Build correct path to frontend/dist
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FRONTEND_DIST = os.path.join(BASE_DIR, '../frontend/dist')

app = Flask(__name__, static_folder=FRONTEND_DIST, static_url_path='')

# Enable CORS
CORS(app, resources={r"/api/*": {"origins": "*"}})

# --- MongoDB Configuration (Hardcoded) ---
# I've pasted your connection string directly here.
mongo_uri = "mongodb+srv://taha_admin:hospital123@cluster0.ukoxtzf.mongodb.net/hospital_crm_db?retryWrites=true&w=majority&appName=Cluster0&authSource=admin"

try:
    client = MongoClient(mongo_uri, serverSelectionTimeoutMS=5000)
    # Force a connection check to ensure the URI works immediately
    client.server_info()
    print("✅ Successfully connected to MongoDB")
except Exception as e:
    print(f"❌ Failed to connect to MongoDB: {e}")

db = client['hospital_crm_db']
assets_collection = db['assets']

# Helper function
def serialize_asset(asset):
    asset['_id'] = str(asset['_id'])
    return asset

# --- API Routes ---

@app.route('/api/assets', methods=['GET'])
def get_assets():
    try:
        all_assets = list(assets_collection.find())
        serialized_assets = [serialize_asset(asset) for asset in all_assets]
        
        # Stats logic
        total_assets = len(serialized_assets)
        in_stock = sum(1 for a in serialized_assets if a.get('status') == 'In')
        out_stock = sum(1 for a in serialized_assets if a.get('status') == 'Out')
        
        return jsonify({
            'assets': serialized_assets,
            'stats': {
                'total': total_assets,
                'in_stock': in_stock,
                'out_stock': out_stock
            }
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/assets', methods=['POST'])
def add_asset():
    try:
        data = request.get_json()
        if not data.get('description') or not data.get('serial_number'):
            return jsonify({'error': 'Description and serial number are required'}), 400
        
        new_asset = {
            'description': data.get('description'),
            'serial_number': data.get('serial_number'),
            'status': 'In', 
            'location': 'Warehouse' 
        }
        
        result = assets_collection.insert_one(new_asset)
        new_asset['_id'] = str(result.inserted_id)
        return jsonify(new_asset), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/assets/<id>', methods=['PUT'])
def update_asset(id):
    try:
        data = request.get_json()
        update_data = {}
        
        if 'status' in data: update_data['status'] = data['status']
        if 'location' in data: update_data['location'] = data['location']
        
        if not update_data:
            return jsonify({'error': 'No update data provided'}), 400
        
        result = assets_collection.update_one(
            {'_id': ObjectId(id)},
            {'$set': update_data}
        )
        
        if result.matched_count == 0:
            return jsonify({'error': 'Asset not found'}), 404
            
        updated_asset = assets_collection.find_one({'_id': ObjectId(id)})
        return jsonify(serialize_asset(updated_asset)), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/assets/<id>', methods=['DELETE'])
def delete_asset(id):
    try:
        result = assets_collection.delete_one({'_id': ObjectId(id)})
        if result.deleted_count == 0:
            return jsonify({'error': 'Asset not found'}), 404
        return jsonify({'message': 'Asset deleted successfully'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# --- Serve React Frontend ---
@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve_react(path):
    if path != "" and os.path.exists(os.path.join(app.static_folder, path)):
        return send_from_directory(app.static_folder, path)
    else:
        return send_from_directory(app.static_folder, 'index.html')

if __name__ == '__main__':
    app.run(debug=True, port=5000)