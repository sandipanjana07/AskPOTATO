import sqlite3
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def init_database(db_path='potato.db'):
    """
    Initialize the database with all required tables
    Includes timestamps and proper foreign key constraints
    """
    
    # check if database already exists
    db_file = Path(db_path)
    if db_file.exists():
        response = input(f"Database '{db_path}' already exists. Recreate? (y/N): ")
        if response.lower() != 'y':
            logger.info("Keeping existing database")
            return
        db_file.unlink()
        logger.info("Deleted existing database")
    
    try:
        conn = sqlite3.connect(db_path)
        cur = conn.cursor()
        
        # enable foreign keys
        cur.execute("PRAGMA foreign_keys = ON")
        
        # scenarios table
        cur.execute("""
            CREATE TABLE IF NOT EXISTS scenarios (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                area TEXT NOT NULL,
                type TEXT NOT NULL,
                assigned_to TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        logger.info("Created scenarios table")
        
        # steps table
        cur.execute("""
            CREATE TABLE IF NOT EXISTS steps (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                scenario_id INTEGER NOT NULL,
                step_number INTEGER NOT NULL,
                step_name TEXT NOT NULL,
                status TEXT DEFAULT 'Not Started',
                assigned_to TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (scenario_id) REFERENCES scenarios(id) ON DELETE CASCADE,
                UNIQUE(scenario_id, step_number)
            )
        """)
        logger.info("Created steps table")
        
        # defects table
        cur.execute("""
            CREATE TABLE IF NOT EXISTS defects (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                scenario_id INTEGER NOT NULL,
                step_number INTEGER NOT NULL,
                title TEXT NOT NULL,
                status TEXT DEFAULT 'Open',
                reported_by TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (scenario_id) REFERENCES scenarios(id) ON DELETE CASCADE
            )
        """)
        logger.info("Created defects table")
        
        # proofs table
        cur.execute("""
            CREATE TABLE IF NOT EXISTS proofs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                scenario_id INTEGER NOT NULL,
                step_number INTEGER NOT NULL,
                filename TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (scenario_id) REFERENCES scenarios(id) ON DELETE CASCADE
            )
        """)
        logger.info("Created proofs table")
        
        # create indexes for better performance
        cur.execute("CREATE INDEX IF NOT EXISTS idx_steps_scenario ON steps(scenario_id)")
        cur.execute("CREATE INDEX IF NOT EXISTS idx_defects_scenario ON defects(scenario_id)")
        cur.execute("CREATE INDEX IF NOT EXISTS idx_defects_status ON defects(status)")
        cur.execute("CREATE INDEX IF NOT EXISTS idx_proofs_scenario ON proofs(scenario_id)")
        logger.info("Created indexes")
        
        conn.commit()
        logger.info(f"✅ Database '{db_path}' initialized successfully!")
        
        # insert sample data for testing (optional)
        insert_sample = input("\nInsert sample data for testing? (y/N): ")
        if insert_sample.lower() == 'y':
            insert_sample_data(cur)
            conn.commit()
            logger.info("✅ Sample data inserted!")
        
        conn.close()
        
    except sqlite3.Error as e:
        logger.error(f"Database error: {e}")
        raise


def insert_sample_data(cur):
    """Insert some sample data for testing"""
    
    # sample scenarios
    scenarios = [
        ("Login Functionality Test", "Authentication", "Functional", "John Doe"),
        ("Payment Gateway Integration", "Payment", "Integration", "Jane Smith"),
        ("Dashboard Performance", "UI/UX", "Performance", "Bob Johnson")
    ]
    
    for scenario in scenarios:
        cur.execute("""
            INSERT INTO scenarios (name, area, type, assigned_to, created_at)
            VALUES (?, ?, ?, ?, datetime('now'))
        """, scenario)
        
        scenario_id = cur.lastrowid
        
        # create 5 steps for each scenario
        for i in range(1, 6):
            cur.execute("""
                INSERT INTO steps (scenario_id, step_number, step_name, status, created_at)
                VALUES (?, ?, ?, ?, datetime('now'))
            """, (scenario_id, i, f"Step {i}", 'Not Started' if i > 2 else 'Passed'))
        
        # add a defect to first step
        cur.execute("""
            INSERT INTO defects (scenario_id, step_number, title, reported_by, created_at)
            VALUES (?, ?, ?, ?, datetime('now'))
        """, (scenario_id, 1, f"Issue in {scenario[0]} - Step 1", scenario[3]))
    
    logger.info("Inserted 3 scenarios with 5 steps each and sample defects")


if __name__ == "__main__":
    print("=" * 60)
    print("AskPOTATO Database Initialization")
    print("=" * 60)
    init_database()
    print("\n✨ All done! Run 'python app.py' to start the application")
