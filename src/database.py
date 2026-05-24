import sqlite3
import pandas as pd
import os

DB_PATH = "database/crisis.db"

def create_database():
    """
    Creates SQLite database and tables
    """
    print("Creating database...")
    os.makedirs("database", exist_ok=True)
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS crisis_events (
            id INTEGER PRIMARY KEY,
            title TEXT,
            country TEXT,
            severity TEXT,
            severity_encoded INTEGER,
            type_EQ INTEGER,
            type_FL INTEGER,
            type_DR INTEGER,
            type_TC INTEGER,
            type_VO INTEGER,
            year INTEGER,
            month INTEGER,
            day INTEGER,
            weekday INTEGER,
            is_weekend INTEGER,
            is_high_alert INTEGER,
            is_recent INTEGER
        )
    ''')
    
    conn.commit()
    conn.close()
    print("✅ Database and table created!")

def load_data_to_db():
    """
    Loads processed CSV data into SQLite database
    """
    print("Loading processed data into database...")
    df = pd.read_csv("data/processed/crisis_processed.csv")
    
    conn = sqlite3.connect(DB_PATH)
    df.to_sql('crisis_events', conn, if_exists='replace', index=False)
    conn.close()
    print(f"✅ {len(df)} records loaded into database!")

def query_db(query):
    """
    Runs any SQL query and returns a DataFrame
    """
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df

def get_summary():
    """
    Shows key stats using SQL queries
    """
    print("\n📊 DATABASE SUMMARY")
    print("=" * 40)

    # Total events
    df = query_db("SELECT COUNT(*) as total_events FROM crisis_events")
    print(f"Total Events: {df['total_events'][0]}")

    # Events by type
    print("\n🌍 Events by Disaster Type:")
    df = query_db("""
        SELECT severity, COUNT(*) as count 
        FROM crisis_events 
        GROUP BY severity 
        ORDER BY count DESC
    """)
    print(df.to_string(index=False))

    # High alert events
    print("\n🔴 High Alert Events by Country:")
    df = query_db("""
        SELECT country, COUNT(*) as high_alert_count
        FROM crisis_events
        WHERE is_high_alert = 1
        GROUP BY country
        ORDER BY high_alert_count DESC
        LIMIT 10
    """)
    print(df.to_string(index=False))

    # Recent events
    print("\n📅 Events by Year:")
    df = query_db("""
        SELECT year, COUNT(*) as count
        FROM crisis_events
        GROUP BY year
        ORDER BY year DESC
    """)
    print(df.to_string(index=False))

if __name__ == "__main__":
    create_database()
    load_data_to_db()
    get_summary()