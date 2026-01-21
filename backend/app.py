from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os

app = Flask(__name__)
CORS(app)  # Allow React frontend to connect

# ========== RENDER POSTGRESQL SETUP ==========
# Render automatically provides DATABASE_URL environment variable
database_url = os.getenv('DATABASE_URL')

if database_url:
    # FIX for Render's format: postgres:// → postgresql://
    if database_url.startswith('postgres://'):
        database_url = database_url.replace('postgres://', 'postgresql://', 1)
    app.config['SQLALCHEMY_DATABASE_URI'] = database_url
    print("✅ Connected to Render PostgreSQL")
else:
    # Local development fallback
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///inventory.db'
    print("⚠️  Using SQLite (local development)")

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# ========== DATABASE MODEL ==========
class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    category = db.Column(db.String(50), default='General')
    quantity = db.Column(db.Integer, default=0)
    price = db.Column(db.Float, default=0.0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'category': self.category,
            'quantity': self.quantity,
            'price': self.price,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

# Create tables if they don't exist
with app.app_context():
    db.create_all()
    print(f"✅ Database tables ready!")

# ========== API ROUTES ==========
@app.route('/')
def home():
    return jsonify({
        "message": "🚀 Inventory API Deployed on Render!",
        "database": "PostgreSQL" if 'postgresql' in app.config['SQLALCHEMY_DATABASE_URI'] else "SQLite",
        "status": "running",
        "endpoints": [
            "GET /api/products - Get all products",
            "POST /api/products - Add new product",
            "GET /api/products/<id> - Get single product",
            "PUT /api/products/<id> - Update product",
            "DELETE /api/products/<id> - Delete product"
        ]
    })

@app.route('/api/health')
def health():
    return jsonify({
        "status": "healthy",
        "database": "connected" if 'postgresql' in app.config['SQLALCHEMY_DATABASE_URI'] else "sqlite",
        "timestamp": datetime.utcnow().isoformat()
    })

# GET all products
@app.route('/api/products', methods=['GET'])
def get_products():
    products = Product.query.order_by(Product.created_at.desc()).all()
    return jsonify([p.to_dict() for p in products])

# ADD new product
@app.route('/api/products', methods=['POST'])
def add_product():
    try:
        data = request.json
        
        # Validate required fields
        if not data.get('name'):
            return jsonify({"error": "Product name is required"}), 400
            
        product = Product(
            name=data['name'],
            category=data.get('category', 'General'),
            quantity=data.get('quantity', 1),
            price=data.get('price', 0.0)
        )
        
        db.session.add(product)
        db.session.commit()
        
        return jsonify({
            "message": "Product added successfully!",
            "product": product.to_dict()
        }), 201
        
    except Exception as e:
        return jsonify({"error": str(e)}), 400

# GET single product
@app.route('/api/products/<int:id>', methods=['GET'])
def get_product(id):
    product = Product.query.get(id)
    if not product:
        return jsonify({"error": "Product not found"}), 404
    return jsonify(product.to_dict())

# UPDATE product
@app.route('/api/products/<int:id>', methods=['PUT'])
def update_product(id):
    product = Product.query.get(id)
    if not product:
        return jsonify({"error": "Product not found"}), 404
    
    data = request.json
    product.name = data.get('name', product.name)
    product.category = data.get('category', product.category)
    product.quantity = data.get('quantity', product.quantity)
    product.price = data.get('price', product.price)
    
    db.session.commit()
    return jsonify({"message": "Product updated", "product": product.to_dict()})

# DELETE product
@app.route('/api/products/<int:id>', methods=['DELETE'])
def delete_product(id):
    product = Product.query.get(id)
    if not product:
        return jsonify({"error": "Product not found"}), 404
    
    db.session.delete(product)
    db.session.commit()
    return jsonify({"message": "Product deleted"})

# STATS endpoint
@app.route('/api/stats')
def stats():
    from sqlalchemy import func
    
    total_products = Product.query.count()
    total_quantity = db.session.query(func.sum(Product.quantity)).scalar() or 0
    total_value = db.session.query(func.sum(Product.price * Product.quantity)).scalar() or 0
    
    return jsonify({
        "total_products": total_products,
        "total_quantity": total_quantity,
        "total_inventory_value": float(total_value),
        "database_type": "PostgreSQL" if 'postgresql' in app.config['SQLALCHEMY_DATABASE_URI'] else "SQLite"
    })

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    app.run(host='0.0.0.0', port=port)