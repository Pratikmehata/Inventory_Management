import psycopg2

# Your Render PostgreSQL connection string
DATABASE_URL = "postgresql://inventory_jq0q_user:mpKXPTDaKSIsykdnSiuOKLoTV6EfrjaR@dpg-d5oh9hogjchc73a61a50-a.oregon-postgres.render.com/inventory_jq0q"

try:
    # Try to connect
    conn = psycopg2.connect(DATABASE_URL)
    cursor = conn.cursor()
    
    # Test connection
    cursor.execute("SELECT version();")
    version = cursor.fetchone()
    print(f"✅ SUCCESS! PostgreSQL Version: {version[0]}")
    
    # Check if product table exists
    cursor.execute("""
        SELECT EXISTS (
            SELECT FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_name = 'product'
        );
    """)
    
    table_exists = cursor.fetchone()[0]
    
    if table_exists:
        print("✅ 'product' table exists!")
        
        # Count products
        cursor.execute("SELECT COUNT(*) FROM product;")
        count = cursor.fetchone()[0]
        print(f"📦 Total products in database: {count}")
        
        if count > 0:
            cursor.execute("SELECT * FROM product LIMIT 3;")
            products = cursor.fetchall()
            print("\nSample products:")
            for p in products:
                print(f"  - {p}")
    else:
        print("❌ 'product' table doesn't exist yet")
    
    cursor.close()
    conn.close()
    print("\n🔒 Connection closed successfully!")
    
except Exception as e:
    print(f"❌ ERROR: {e}")
    print("\n💡 Tips:")
    print("1. Make sure your PostgreSQL instance is running on Render (green light)")
    print("2. Check if psycopg2 is installed: pip install psycopg2-binary")
    print("3. Verify the connection string is correct")