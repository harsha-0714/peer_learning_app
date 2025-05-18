import sqlite3
import hashlib

def get_connection():
    return sqlite3.connect("peer_learning.db", check_same_thread=False)

def hash_password(password):
    """Hashes a password using SHA-256."""
    return hashlib.sha256(password.encode()).hexdigest()

def initialize_db():
    conn = get_connection()
    cursor = conn.cursor()

    # Admin Table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS Admin (
        Username TEXT PRIMARY KEY,
        Password TEXT NOT NULL
    )
    ''')

    # Insert default admin if not exists (with hashed password)
    cursor.execute("SELECT * FROM Admin WHERE Username = 'admin'")
    if not cursor.fetchone():
        default_hashed = hash_password('admin123')
        cursor.execute("INSERT INTO Admin VALUES (?, ?)", ('admin', default_hashed))

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS Students (
        StudentID INTEGER PRIMARY KEY AUTOINCREMENT,
        Name TEXT NOT NULL, 
        Email TEXT UNIQUE NOT NULL, 
        Year INTEGER NOT NULL
    )
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS Faculty (
        FacultyID INTEGER PRIMARY KEY AUTOINCREMENT,
        Name TEXT NOT NULL,
        Email TEXT UNIQUE NOT NULL,
        Department TEXT NOT NULL
    )
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS Skills (
        SkillID INTEGER PRIMARY KEY AUTOINCREMENT,
        SkillName TEXT UNIQUE NOT NULL
    )
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS StudentSkills (
        StudentID INTEGER,
        SkillID INTEGER,
        Proficiency TEXT NOT NULL,
        PRIMARY KEY (StudentID, SkillID),
        FOREIGN KEY (StudentID) REFERENCES Students(StudentID),
        FOREIGN KEY (SkillID) REFERENCES Skills(SkillID)
    )
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS Sessions (
        SessionID INTEGER PRIMARY KEY AUTOINCREMENT,
        TutorID INTEGER,
        LearnerID INTEGER,
        Date TEXT NOT NULL,
        Topic TEXT NOT NULL,
        FOREIGN KEY (TutorID) REFERENCES Students(StudentID),
        FOREIGN KEY (LearnerID) REFERENCES Students(StudentID)
    )
    ''')

    conn.commit()
    conn.close()
