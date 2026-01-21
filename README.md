# 🏪 Inventory Management System

A full-stack inventory management application built with React, Flask, and PostgreSQL, deployed on Render.

## 🌐 Live Demo

- **Frontend (React):** https://inventory-frontend.onrender.com
- **Backend API (Flask):** https://inventory-backend.onrender.com
- **API Documentation:** https://inventory-backend.onrender.com/api/docs

## 🚀 Features

- ✅ **Full CRUD Operations** - Create, Read, Update, Delete products
- ✅ **RESTful API** - Clean, well-documented endpoints
- ✅ **PostgreSQL Database** - Relational database with SQLAlchemy ORM
- ✅ **React Frontend** - Modern, responsive user interface
- ✅ **Deployed on Render** - Production-ready cloud hosting
- ✅ **CORS Configured** - Secure frontend-backend communication
- ✅ **Environment-based Config** - Different setups for dev/production

## 🏗️ Tech Stack

### **Frontend**
- React 18
- Vite (Build tool)
- CSS3 (Responsive design)
- Axios (HTTP client)

### **Backend**
- Flask (Python web framework)
- Flask-SQLAlchemy (ORM)
- Flask-CORS (Cross-origin support)
- PostgreSQL (Production database)
- SQLite (Development database)
- Gunicorn (Production server)

### **Infrastructure**
- Render (Hosting & deployment)
- PostgreSQL (Managed database)
- GitHub (Version control)

## 📁 Project Structure

inventory-app/
├── backend/
│ ├── app.py # Main Flask application
│ ├── requirements.txt # Python dependencies
│ ├── Procfile # Render startup command
│ └── .gitignore # Ignored files
├── frontend/
│ ├── src/
│ │ ├── App.jsx # Main React component
│ │ ├── App.css # Styling
│ │ └── main.jsx # React entry point
│ ├── index.html # HTML template
│ ├── package.json # Node dependencies
│ └── vite.config.js # Vite configuration
└── README.md # This file


## 🛠️ Installation & Setup

### **1. Clone Repository**
```bash
git clone https://github.com/yourusername/inventory-app.git
cd inventory-app

##Backend Setting
cd backend

# Create virtual environment
python -m venv venv

# Activate (Windows)
venv\Scripts\activate
# Activate (Mac/Linux)
# source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run locally (uses SQLite)
python app.py


and for the frontend

cd frontend

# Install dependencies
npm install

# Run development server
npm run dev
