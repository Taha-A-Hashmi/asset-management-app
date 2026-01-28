import os
import datetime
from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
from pymongo import MongoClient
from bson.objectid import ObjectId

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FRONTEND_DIST = os.path.join(BASE_DIR, '../public')

app = Flask(__name__, static_folder=FRONTEND_DIST, static_url_path='')
CORS(app, resources={r"/api/*": {"origins": "*"}})

# Hardcoded DB Connection
mongo_uri = "mongodb+srv://taha_admin:hospital123@cluster0.ukoxtzf.mongodb.net/hospital_crm_db?retryWrites=true&w=majority&appName=Cluster0&authSource=admin"
client = MongoClient(mongo_uri)
db = client['hospital_crm_db']
assets_collection = db['assets']

def serialize_asset(asset):
    asset['_id'] = str(asset['_id'])
    return asset

# --- API Routes ---

# app.py (Crucial Part)
@app.route('/api/assets', methods=['GET'])
def get_assets():
    try:
        all_assets = list(assets_collection.find())
        serialized_assets = [serialize_asset(asset) for asset in all_assets]
        
        # Stats logic
        total_assets = len(serialized_assets)
        in_stock = sum(1 for a in serialized_assets if a.get('status') in ['Available', 'In'])
        out_stock = sum(1 for a in serialized_assets if a.get('status') in ['Allocated', 'Picked', 'On Hold', 'Dispatched'])
        
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
    data = request.get_json()
    new_asset = {
        'description': data.get('description'),
        'serial_number': data.get('serial_number'),
        'status': 'Available',       # Default state: "Stock Laying in Allocation Area" or Racks
        'location': 'Warehouse-A',   # Default Rack
        'allocation_batch': None,
        'created_at': datetime.datetime.utcnow() # crucial for FIFO
    }
    result = assets_collection.insert_one(new_asset)
    return jsonify(serialize_asset(assets_collection.find_one({'_id': result.inserted_id}))), 201

# --- WORKFLOW IMPLEMENTATION (Based on PDF) ---

# STEP 1: "Marking of Lot following FIFO"
@app.route('/api/dispatch/allocate', methods=['POST'])
def allocate_fifo():
    # Trigger: "Sales Order Received Through Email"
    qty = request.json.get('quantity', 1)
    allocation_number = f"ALLOC-{int(datetime.datetime.now().timestamp())}"
    
    # FIFO Logic: Find oldest 'Available' assets
    candidates = list(assets_collection.find({'status': 'Available'}).sort('_id', 1).limit(qty))
    
    if len(candidates) < qty:
        return jsonify({'error': 'Not enough stock for FIFO allocation'}), 400

    ids = [c['_id'] for c in candidates]
    
    # Update status to "Allocated"
    assets_collection.update_many(
        {'_id': {'$in': ids}},
        {'$set': {
            'status': 'Allocated',
            'allocation_batch': allocation_number,
            'location': 'Staging Area'
        }}
    )
    
    # Simulated Step: "Email the Allocation to AF & AW"
    print(f"📧 EMAIL SENT: Allocation {allocation_number} sent to AF & AW.")
    
    return jsonify({'message': f'Allocated {len(ids)} items', 'batch': allocation_number}), 200

# STEP 2 & 3: Workflow Transitions
@app.route('/api/dispatch/status', methods=['PUT'])
def update_workflow_status():
    asset_id = request.json.get('assetId')
    action = request.json.get('action') # pick, hold, approve, return
    
    update_fields = {}
    
    if action == 'pick':
        # "Picked the Allocated item Lot from Racks" -> "LOT/Qty Fulfilment in NetSuite"
        update_fields = {'status': 'Picked'}
        print("✅ NETSUITE SYNC: Quantity Fulfilled in NetSuite.") 

    elif action == 'hold':
        # Path: "DO/INV Not Receive, HOLD"
        update_fields = {'status': 'On Hold'}

    elif action == 'approve':
        # Path: "Approved DO/INV Received" -> "Final Dispatch"
        update_fields = {'status': 'Dispatched', 'location': 'Customer Site'}

    elif action == 'return':
        # Path: "Return Authorization" OR "Allocation Cancelled" -> "Stock Return to Racks"
        update_fields = {
            'status': 'Available', 
            'allocation_batch': None,
            'location': 'Warehouse-A'
        }

    assets_collection.update_one({'_id': ObjectId(asset_id)}, {'$set': update_fields})
    return jsonify({'message': 'Status updated'}), 200

# --- Standard React Serve ---
@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve_react(path):
    if path != "" and os.path.exists(os.path.join(app.static_folder, path)):
        return send_from_directory(app.static_folder, path)
    return send_from_directory(app.static_folder, 'index.html')

if __name__ == '__main__':
    app.run(debug=True, port=5000)