"""
Create portfolio_deployments table in Neon database
"""
from config.database import get_database_connection

def create_portfolio_deployments_table():
    """Create the portfolio_deployments table if it doesn't exist"""
    try:
        with get_database_connection() as conn:
            cursor = conn.cursor()
            
            print("Creating portfolio_deployments table...")
            
            # Create the table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS portfolio_deployments (
                    id SERIAL PRIMARY KEY,
                    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
                    portfolio_name TEXT NOT NULL,
                    deployment_url TEXT NOT NULL,
                    admin_url TEXT,
                    site_id TEXT,
                    deployed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    status TEXT DEFAULT 'active',
                    CONSTRAINT unique_deployment UNIQUE (user_id, site_id)
                )
            """)
            
            # Create index for faster queries
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_deployments_user_id 
                ON portfolio_deployments(user_id)
            """)
            
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_deployments_status 
                ON portfolio_deployments(status)
            """)
            
            conn.commit()
            
            print("✅ portfolio_deployments table created successfully!")
            
            # Verify the table exists
            cursor.execute("""
                SELECT column_name, data_type 
                FROM information_schema.columns 
                WHERE table_name = 'portfolio_deployments'
                ORDER BY ordinal_position
            """)
            
            columns = cursor.fetchall()
            print("\n📋 Table structure:")
            for col in columns:
                print(f"   - {col[0]}: {col[1]}")
            
            # Check if there are any existing deployments
            cursor.execute("SELECT COUNT(*) FROM portfolio_deployments")
            count = cursor.fetchone()[0]
            print(f"\n📊 Current deployments in database: {count}")
            
            return True
            
    except Exception as e:
        print(f"❌ Error creating table: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("Portfolio Deployments Table Migration")
    print("=" * 60)
    print()
    
    success = create_portfolio_deployments_table()
    
    print()
    print("=" * 60)
    if success:
        print("✅ Migration completed successfully!")
        print()
        print("You can now:")
        print("1. Deploy portfolios from the Portfolio Generator")
        print("2. View deployment history in 'My History' page")
        print("3. Access live URLs and admin panels")
    else:
        print("❌ Migration failed. Please check the error above.")
    print("=" * 60)
