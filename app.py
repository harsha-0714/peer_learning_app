import streamlit as st
import pandas as pd
from database import get_connection, initialize_db

initialize_db()
conn = get_connection()
cursor = conn.cursor()

# -- LOGIN FUNCTION --
def authenticate_user(username, password):
    cursor.execute("SELECT * FROM Admin WHERE Username=? AND Password=?", (username, password))
    return cursor.fetchone()

# -- LOGIN INTERFACE --
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    st.title("🔐 Admin Login")
    user = st.text_input("Username")
    pwd = st.text_input("Password", type="password")
    if st.button("Login"):
        if authenticate_user(user, pwd):
            st.success("Logged in successfully!")
            st.session_state.authenticated = True
            st.rerun()
        else:
            st.error("Invalid credentials.")

# MAIN APP
if st.session_state.authenticated:
    st.title("📘 Skill-Based Peer Learning Platform")

    tabs = st.tabs([
        "Add Student", 
        "Add Faculty", 
        "Add Skill", 
        "Assign Skill", 
        "Schedule Session", 
        "Admin Dashboard", 
        "Export Data"
    ])

    # TAB 1: Add Student
    with tabs[0]:
        st.header("➕ Add Student")
        name = st.text_input("Student Name")
        email = st.text_input("Student Email")
        year = st.selectbox("Year", [1, 2, 3, 4])
        if st.button("Add Student"):
            try:
                cursor.execute("INSERT INTO Students (Name, Email, Year) VALUES (?, ?, ?)", (name, email, year))
                conn.commit()
                st.success("Student added.")
            except:
                st.error("Email already exists.")

    # TAB 2: Add Faculty
    with tabs[1]:
        st.header("👩‍🏫 Add Faculty")
        fname = st.text_input("Faculty Name")
        femail = st.text_input("Faculty Email")
        dept = st.text_input("Department")
        if st.button("Add Faculty"):
            try:
                cursor.execute("INSERT INTO Faculty (Name, Email, Department) VALUES (?, ?, ?)", (fname, femail, dept))
                conn.commit()
                st.success("Faculty added.")
            except:
                st.error("Faculty email already exists.")

    # TAB 3: Add Skill
    with tabs[2]:
        st.header("💡 Add Skill")
        skill = st.text_input("Skill Name")
        if st.button("Add Skill"):
            try:
                cursor.execute("INSERT INTO Skills (SkillName) VALUES (?)", (skill,))
                conn.commit()
                st.success("Skill added.")
            except:
                st.error("Skill already exists.")

    # TAB 4: Assign Skill
    with tabs[3]:
        st.header("🔗 Assign Skill to Student")
        students = cursor.execute("SELECT StudentID, Name FROM Students").fetchall()
        skills = cursor.execute("SELECT SkillID, SkillName FROM Skills").fetchall()
        if students and skills:
            student = st.selectbox("Select Student", students, format_func=lambda x: f"{x[1]} (ID: {x[0]})")
            skill = st.selectbox("Select Skill", skills, format_func=lambda x: f"{x[1]} (ID: {x[0]})")
            prof = st.radio("Proficiency", ["Beginner", "Intermediate", "Advanced"])
            if st.button("Assign"):
                cursor.execute("INSERT OR REPLACE INTO StudentSkills VALUES (?, ?, ?)", (student[0], skill[0], prof))
                conn.commit()
                st.success("Skill assigned.")
        else:
            st.warning("Please add students and skills first.")

    # TAB 5: Schedule Session
    with tabs[4]:
        st.header("🗓 Schedule Session")
        if students:
            tutor = st.selectbox("Tutor", students, format_func=lambda x: x[1])
            learner = st.selectbox("Learner", students, format_func=lambda x: x[1])
            date = st.date_input("Date")
            topic = st.text_input("Topic")
            if st.button("Schedule"):
                if tutor[0] != learner[0]:
                    cursor.execute("INSERT INTO Sessions (TutorID, LearnerID, Date, Topic) VALUES (?, ?, ?, ?)",
                                   (tutor[0], learner[0], date.isoformat(), topic))
                    conn.commit()
                    st.success("Session scheduled.")
                else:
                    st.error("Tutor and learner must be different.")
        else:
            st.warning("Add students first.")

    # TAB 6: Admin Dashboard
    with tabs[5]:
        st.header("📊 Admin Dashboard")

        st.subheader("Students")
        students_df = pd.read_sql("SELECT * FROM Students", conn)
        st.dataframe(students_df, use_container_width=True)

        st.subheader("Faculties")
        faculty_df = pd.read_sql("SELECT * FROM Faculty", conn)
        st.dataframe(faculty_df, use_container_width=True)

        st.subheader("Skills Assigned")
        skills_df = pd.read_sql('''
        SELECT s.Name AS Student, sk.SkillName, ss.Proficiency 
        FROM StudentSkills ss
        JOIN Students s ON ss.StudentID = s.StudentID
        JOIN Skills sk ON ss.SkillID = sk.SkillID
        ''', conn)
        st.dataframe(skills_df, use_container_width=True)

        st.subheader("Sessions")
        session_df = pd.read_sql('''
        SELECT s1.Name AS Tutor, s2.Name AS Learner, Date, Topic
        FROM Sessions
        JOIN Students s1 ON s1.StudentID = Sessions.TutorID
        JOIN Students s2 ON s2.StudentID = Sessions.LearnerID
        ''', conn)
        st.dataframe(session_df, use_container_width=True)

    # TAB 7: Export
    with tabs[6]:
        st.header("⬇️ Export Data")
        file_map = {
            "Students": students_df,
            "Faculties": faculty_df,
            "Skills Assigned": skills_df,
            "Sessions": session_df
        }

        for label, df in file_map.items():
            csv = df.to_csv(index=False).encode()
            st.download_button(f"Download {label} CSV", csv, file_name=f"{label.lower().replace(' ', '_')}.csv")

