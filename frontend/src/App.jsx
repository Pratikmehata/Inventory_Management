import React, { useState, useEffect } from 'react';
import './App.css';

// Use proxy for local development
const API_URL = '/api';  // Vite proxy will redirect to localhost:5000

function App() {
  const [products, setProducts] = useState([]);
  const [form, setForm] = useState({
    name: '',
    category: 'Electronics',
    quantity: 1,
    price: 0
  });
  const [loading, setLoading] = useState(true);

  // Fetch products
  const fetchProducts = async () => {
    try {
      const response = await fetch(`${API_URL}/products`);
      const data = await response.json();
      setProducts(data);
    } catch (error) {
      console.error('Error:', error);
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
      [e.target.name]: e.target.value
    });
  };

  // Add product
  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      const response = await fetch(`${API_URL}/products`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(form)
      });
      
      if (response.ok) {
        setForm({ name: '', category: 'Electronics', quantity: 1, price: 0 });
        fetchProducts();
      }
    } catch (error) {
      console.error('Error:', error);
    }
  };

  // Delete product
  const handleDelete = async (id) => {
    if (window.confirm('Delete this product?')) {
      try {
        await fetch(`${API_URL}/products/${id}`, {
          method: 'DELETE'
        });
        fetchProducts();
      } catch (error) {
        console.error('Error:', error);
      }
    }
  };

  if (loading) {
    return <div className="loading">Loading products...</div>;
  }

  return (
    <div className="app">
      <h1>📦 Inventory Management</h1>
      
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
        <h2>Products ({products.length})</h2>
        {products.length === 0 ? (
          <p className="empty">No products yet. Add one above!</p>
        ) : (
          <div className="products-grid">
            {products.map(product => (
              <div key={product.id} className="product-card">
                <h3>{product.name}</h3>
                <p className="category">{product.category}</p>
                <div className="details">
                  <span>Qty: {product.quantity}</span>
                  <span className="price">${parseFloat(product.price).toFixed(2)}</span>
                </div>
                <button 
                  onClick={() => handleDelete(product.id)}
                  className="delete-btn"
                >
                  Delete
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