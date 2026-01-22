import React, { useState, useEffect } from 'react';
import './App.css';

// Update the API URL to FastAPI's default port (8000)
const API_URL = 'https://inventory-management-1-51nd.onrender.com/';  

function App() {
  const [products, setProducts] = useState([]);
  const [form, setForm] = useState({
    name: '',
    category: 'Electronics',
    quantity: 1,
    price: 0
  });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  // Fetch products
  const fetchProducts = async () => {
    try {
      setError('');
      const response = await fetch(`${API_URL}/products`);
      
      if (!response.ok) {
        // FastAPI returns error details in JSON
        const errorData = await response.json();
        throw new Error(errorData.detail || `HTTP error! status: ${response.status}`);
      }
      
      const data = await response.json();
      setProducts(data);
    } catch (error) {
      console.error('Error:', error);
      setError(`Failed to load products: ${error.message}`);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchProducts();
  }, []);

  // Handle form input
  const handleChange = (e) => {
    setForm({
      ...form,
      [e.target.name]: e.target.type === 'number' ? 
        parseFloat(e.target.value) || 0 : 
        e.target.value
    });
  };

  // Add product
  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    
    try {
      // Prepare data for FastAPI (matches Pydantic model)
      const productData = {
        name: form.name.trim(),
        category: form.category,
        quantity: form.quantity,
        price: parseFloat(form.price)
      };

      const response = await fetch(`${API_URL}/products`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(productData)
      });
      
      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || `HTTP error! status: ${response.status}`);
      }
      
      const newProduct = await response.json();
      
      // Reset form
      setForm({ name: '', category: 'Electronics', quantity: 1, price: 0 });
      
      // Update products list (add new product to beginning)
      setProducts([newProduct, ...products]);
      
    } catch (error) {
      console.error('Error:', error);
      setError(`Failed to add product: ${error.message}`);
    }
  };

  // Delete product
  const handleDelete = async (id) => {
    if (window.confirm('Delete this product?')) {
      try {
        const response = await fetch(`${API_URL}/products/${id}`, {
          method: 'DELETE'
        });
        
        if (!response.ok) {
          const errorData = await response.json();
          throw new Error(errorData.detail || `HTTP error! status: ${response.status}`);
        }
        
        // Remove product from state
        setProducts(products.filter(product => product.id !== id));
        
      } catch (error) {
        console.error('Error:', error);
        setError(`Failed to delete product: ${error.message}`);
      }
    }
  };

  // Calculate totals
  const calculateTotals = () => {
    const totalValue = products.reduce((sum, product) => 
      sum + (product.price * product.quantity), 0
    );
    const totalQuantity = products.reduce((sum, product) => 
      sum + product.quantity, 0
    );
    return { totalValue, totalQuantity };
  };

  const { totalValue, totalQuantity } = calculateTotals();

  if (loading) {
    return <div className="loading">Loading products...</div>;
  }

  return (
    <div className="app">
      <h1>📦 Inventory Management (FastAPI)</h1>
      
      {/* Stats Summary */}
      <div className="stats-container">
        <div className="stat-card">
          <h3>Total Products</h3>
          <p className="stat-value">{products.length}</p>
        </div>
        <div className="stat-card">
          <h3>Total Quantity</h3>
          <p className="stat-value">{totalQuantity}</p>
        </div>
        <div className="stat-card">
          <h3>Total Value</h3>
          <p className="stat-value">${totalValue.toFixed(2)}</p>
        </div>
      </div>
      
      {/*Error Display */}
      {error && (
        <div className="error-message">
          ⚠️ {error}
          <button onClick={() => setError('')} className="close-error">×</button>
        </div>
      )}
      
      {/* Add Product Form */}
      <div className="form-container">
        <h2>Add New Product</h2>
        <form onSubmit={handleSubmit}>
          <input
            type="text"
            name="name"
            placeholder="Product Name"
            value={form.name}
            onChange={handleChange}
            required
          />
          <select name="category" value={form.category} onChange={handleChange}>
            <option value="Electronics">Electronics</option>
            <option value="Clothing">Clothing</option>
            <option value="Books">Books</option>
            <option value="Food">Food</option>
            <option value="Other">Other</option>
          </select>
          <input
            type="number"
            name="quantity"
            placeholder="Quantity"
            value={form.quantity}
            onChange={handleChange}
            min="0"
            required
          />
          <input
            type="number"
            name="price"
            placeholder="Price"
            value={form.price}
            onChange={handleChange}
            step="0.01"
            min="0"
            required
          />
          <button type="submit">Add Product</button>
        </form>
      </div>

      {/* Products List */}
      <div className="products-container">
        <div className="products-header">
          <h2>Products ({products.length})</h2>
          <button onClick={fetchProducts} className="refresh-btn">
            🔄 Refresh
          </button>
        </div>
        
        {products.length === 0 ? (
          <p className="empty">No products yet. Add one above!</p>
        ) : (
          <div className="products-grid">
            {products.map(product => (
              <div key={product.id} className="product-card">
                <div className="product-header">
                  <h3>{product.name}</h3>
                  <span className="product-id">#{product.id}</span>
                </div>
                <p className="category">📁 {product.category}</p>
                <div className="details">
                  <span>📦 Qty: {product.quantity}</span>
                  <span className="price">💰 ${parseFloat(product.price).toFixed(2)}</span>
                </div>
                <div className="card-value">
                  Value: ${(product.price * product.quantity).toFixed(2)}
                </div>
                {product.created_at && (
                  <div className="created-at">
                    Added: {new Date(product.created_at).toLocaleDateString()}
                  </div>
                )}
                <button 
                  onClick={() => handleDelete(product.id)}
                  className="delete-btn"
                >
                  🗑️ Delete
                </button>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

export default App;
