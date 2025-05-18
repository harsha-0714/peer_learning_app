import streamlit as st
import pandas as pd
import sqlite3
from database import get_connection, initialize_db, hash_password

initialize_db()
conn = get_connection()
cursor = conn.cursor()

<<<<<<< HEAD
# --- Authentication System ---
def authenticate_admin(username, password):
=======
# --- Authentication ---
def authenticate_user(username, password):
>>>>>>> 291916fad73862314b9225bf115406f8e1c9048c
    hashed = hash_password(password)
    cursor.execute("SELECT * FROM Admin WHERE Username=? AND Password=?", (username, hashed))
    return cursor.fetchone()

<<<<<<< HEAD
def authenticate_user(email):
    cursor.execute("SELECT * FROM Students WHERE Email=?", (email,))
    student = cursor.fetchone()
    cursor.execute("SELECT * FROM Faculty WHERE Email=?", (email,))
    faculty = cursor.fetchone()
    return student or faculty

# --- Login Page ---
=======
>>>>>>> 291916fad73862314b9225bf115406f8e1c9048c
if "authenticated" not in st.session_state:
    st.session_state.update({
        "authenticated": False,
        "user_type": None,
        "user_email": None
    })

if not st.session_state.authenticated:
<<<<<<< HEAD
    st.title("🔐 SkillSync Login")
    col1, col2 = st.columns([1, 2])
    with col1:
        st.image("https://cdn-icons-png.flaticon.com/512/5087/5087579.png", width=150)
    
    with col2:
        user_type = st.radio("Login as:", ["Admin", "Student/Faculty"], horizontal=True)
        
        if user_type == "Admin":
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            if st.button("🔑 Admin Login"):
                if authenticate_admin(username, password):
                    st.session_state.update({
                        "authenticated": True,
                        "user_type": "admin",
                        "user_email": username
                    })
                    st.rerun()
                else:
                    st.error("Invalid admin credentials")
        else:
            email = st.text_input("Email Address")
            if st.button("👤 User Login"):
                if user := authenticate_user(email):
                    st.session_state.update({
                        "authenticated": True,
                        "user_type": "user",
                        "user_email": email
                    })
                    st.rerun()
                else:
                    st.error("Email not registered")
    st.stop()

# --- Logout Button ---
with st.sidebar:
    if st.button("🚪 Logout"):
        st.session_state.authenticated = False
        st.rerun()

# --- Admin Interface ---
if st.session_state.user_type == "admin":
    st.title("👨💼 Admin Dashboard")
    st.sidebar.success(f"Logged in as Admin: {st.session_state.user_email}")

    tabs = st.tabs([
        "➕ Add Records", 
        "🔗 Assign Skills", 
        "🗓 Schedule Sessions", 
        "📊 System Data",
        "⬇️ Export Data",
        "🗑️ Data Management"
    ])

    # TAB 1: Add Records
    with tabs[0]:
        st.header("📥 Add New Records")
        add_type = st.radio("Select Record Type:", 
                          ["Student", "Faculty", "Skill"], 
                          horizontal=True)
        
        if add_type == "Student":
            with st.form("student_form", clear_on_submit=True):
                name = st.text_input("Full Name")
                email = st.text_input("Email")
                year = st.selectbox("Academic Year", [1, 2, 3, 4])
                if st.form_submit_button("Add Student"):
                    try:
                        cursor.execute("INSERT INTO Students VALUES (NULL,?,?,?)", 
                                      (name, email, year))
                        conn.commit()
                        st.success("🎓 Student added successfully!")
                    except sqlite3.IntegrityError:
                        st.error("❌ Email already exists")

        elif add_type == "Faculty":
            with st.form("faculty_form", clear_on_submit=True):
                name = st.text_input("Full Name")
                email = st.text_input("Email")
                dept = st.text_input("Department")
                if st.form_submit_button("Add Faculty"):
                    try:
                        cursor.execute("INSERT INTO Faculty VALUES (NULL,?,?,?)", 
                                      (name, email, dept))
                        conn.commit()
                        st.success("👨🏫 Faculty added successfully!")
                    except sqlite3.IntegrityError:
                        st.error("❌ Faculty email exists")

        elif add_type == "Skill":
            with st.form("skill_form", clear_on_submit=True):
                skill = st.text_input("Skill Name")
                if st.form_submit_button("Add Skill"):
                    try:
                        cursor.execute("INSERT INTO Skills VALUES (NULL,?)", (skill,))
                        conn.commit()
                        st.success("💡 Skill added successfully!")
                    except sqlite3.IntegrityError:
                        st.error("❌ Skill already exists")

    # TAB 2: Assign Skills
    with tabs[1]:
        st.header("🔗 Skill Assignment")
        students = cursor.execute("SELECT StudentID, Name FROM Students").fetchall()
        skills = cursor.execute("SELECT SkillID, SkillName FROM Skills").fetchall()
        
        if students and skills:
            with st.form("assign_form"):
                student = st.selectbox("Student", students, 
                                      format_func=lambda x: f"{x[1]} (ID: {x[0]})")
                skill = st.selectbox("Skill", skills, 
                                    format_func=lambda x: f"{x[1]} (ID: {x[0]})")
                prof = st.select_slider("Proficiency Level", 
                                       ["Beginner", "Intermediate", "Advanced"])
                if st.form_submit_button("Assign Skill"):
                    cursor.execute("""
                        INSERT OR REPLACE INTO StudentSkills 
                        VALUES (?,?,?)
                    """, (student[0], skill[0], prof))
                    conn.commit()
                    st.success(f"✅ {student[1]} assigned {skill[1]} skill")
        else:
            st.warning("Please add students and skills first")

    # TAB 3: Schedule Sessions
    with tabs[2]:
        st.header("🗓 Session Scheduling")
        students = cursor.execute("SELECT StudentID, Name FROM Students").fetchall()
        
        if students:
            with st.form("session_form"):
                col1, col2 = st.columns(2)
                with col1:
                    tutor = st.selectbox("Tutor", students,
                                        format_func=lambda x: x[1])
                with col2:
                    learner = st.selectbox("Learner", students,
                                          format_func=lambda x: x[1])
                date = st.date_input("Session Date")
                topic = st.text_input("Session Topic")
                
                if st.form_submit_button("Schedule Session"):
                    if tutor[0] == learner[0]:
                        st.error("Tutor and learner must be different")
                    else:
                        cursor.execute("""
                            INSERT INTO Sessions 
                            VALUES (NULL,?,?,?,?)
                        """, (tutor[0], learner[0], date.isoformat(), topic))
                        conn.commit()
                        st.success("📅 Session scheduled successfully!")
        else:
            st.warning("Add students first")

    # TAB 4: System Data
    with tabs[3]:
        st.header("📊 System Dashboard")
        
        with st.expander("👥 Student Overview"):
            students_df = pd.read_sql("SELECT * FROM Students", conn)
            st.dataframe(students_df, use_container_width=True)
        
        with st.expander("🏫 Faculty Overview"):
            faculty_df = pd.read_sql("SELECT * FROM Faculty", conn)
            st.dataframe(faculty_df, use_container_width=True)
        
        with st.expander("📚 Skill Matrix"):
            skills_df = pd.read_sql("""
                SELECT s.Name AS Student, sk.SkillName, ss.Proficiency 
                FROM StudentSkills ss
                JOIN Students s ON ss.StudentID = s.StudentID
                JOIN Skills sk ON ss.SkillID = sk.SkillID
            """, conn)
            st.dataframe(skills_df, use_container_width=True)
        
        with st.expander("🗓️ Session Calendar"):
            session_df = pd.read_sql("""
                SELECT s1.Name AS Tutor, s2.Name AS Learner, Date, Topic
                FROM Sessions
                JOIN Students s1 ON s1.StudentID = Sessions.TutorID
                JOIN Students s2 ON s2.StudentID = Sessions.LearnerID
            """, conn)
            st.dataframe(session_df, use_container_width=True)

    # TAB 5: Export Data
    with tabs[4]:
        st.header("📤 Data Export")
        export_options = st.multiselect("Select Data to Export",
                                       ["Students", "Faculty", "Skills", "Sessions"])
        
        if export_options:
            for opt in export_options:
                df = pd.read_sql(f"SELECT * FROM {opt}", conn)
                csv = df.to_csv(index=False).encode()
                st.download_button(
                    f"Download {opt} Data",
                    csv,
                    file_name=f"{opt.lower()}_data.csv",
                    mime="text/csv"
                )

    # TAB 6: Data Management (Delete)
    with tabs[5]:
        st.header("⚠️ Data Management")
        
        delete_type = st.selectbox("Select Data Type to Manage",
                                  ["Students", "Faculty", "Skills", "Sessions"])
        
        if delete_type == "Students":
            data = cursor.execute("SELECT StudentID, Name FROM Students").fetchall()
            id_col = "StudentID"
        elif delete_type == "Faculty":
            data = cursor.execute("SELECT FacultyID, Name FROM Faculty").fetchall()
            id_col = "FacultyID"
        elif delete_type == "Skills":
            data = cursor.execute("SELECT SkillID, SkillName FROM Skills").fetchall()
            id_col = "SkillID"
        elif delete_type == "Sessions":
            data = cursor.execute("SELECT SessionID, Topic FROM Sessions").fetchall()
            id_col = "SessionID"
        
        if data:
            record = st.selectbox("Select Record to Delete", data,
                                 format_func=lambda x: f"{x[1]} (ID: {x[0]})")
            
            if st.button("🗑️ Delete Record", type="primary"):
                try:
                    cursor.execute(f"""
                        DELETE FROM {delete_type} 
                        WHERE {id_col} = ?
                    """, (record[0],))
                    conn.commit()
                    st.success("✅ Record deleted successfully")
                    st.rerun()
                except sqlite3.Error as e:
                    st.error(f"❌ Deletion failed: {str(e)}")
        else:
            st.info("No records available for deletion")

# --- Student/Faculty Interface ---
else:
    st.title("👩🎓 Student/Faculty Portal")
    st.sidebar.success(f"Logged in as: {st.session_state.user_email}")
    
    # Get user details
    cursor.execute("SELECT * FROM Students WHERE Email=?", (st.session_state.user_email,))
    student_data = cursor.fetchone()
    cursor.execute("SELECT * FROM Faculty WHERE Email=?", (st.session_state.user_email,))
    faculty_data = cursor.fetchone()
    
    if student_data:
        st.header("🎓 Your Student Profile")
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Name", student_data[1])
            st.metric("Year", student_data[3])
        with col2:
            st.metric("Email", student_data[2])
        
        st.subheader("📚 Your Skills")
        skills_df = pd.read_sql(f'''
            SELECT sk.SkillName, ss.Proficiency 
            FROM StudentSkills ss
            JOIN Skills sk ON ss.SkillID = sk.SkillID
            WHERE ss.StudentID = {student_data[0]}
        ''', conn)
        st.dataframe(skills_df, use_container_width=True)
        
    elif faculty_data:
        st.header("👨🏫 Faculty Profile")
        st.metric("Name", faculty_data[1])
        st.metric("Department", faculty_data[3])
        
    st.subheader("🗓️ Upcoming Sessions")
    if student_data:
        session_df = pd.read_sql(f'''
=======
    st.title("🔐 Admin Login")
    col1, col2 = st.columns([1, 2])
    with col1:
        st.image("https://cdn-icons-png.flaticon.com/512/5087/5087579.png", width=150)
    with col2:
        user = st.text_input("Username", key="user")
        pwd = st.text_input("Password", type="password", key="pwd")
        if st.button("🚪 Login"):
            if authenticate_user(user, pwd):
                st.session_state.authenticated = True
                st.rerun()
            else:
                st.error("Invalid credentials")
    st.stop()

# --- Main App ---
st.title("📚 SkillSync: Peer Learning Management")
st.sidebar.success("Logged in as Admin")

tabs = st.tabs([
    "➕ Add Records", 
    "🔗 Assign Skills", 
    "🗓 Schedule Sessions", 
    "📊 Dashboard", 
    "⬇️ Export Data",
    "🗑️ Data Management"
])

# TAB 1: Add Records
with tabs[0]:
    st.header("📥 Add New Records")
    add_type = st.radio("Select Record Type:", 
                       ["Student", "Faculty", "Skill"], 
                       horizontal=True)
    
    if add_type == "Student":
        with st.form("student_form", clear_on_submit=True):
            name = st.text_input("Full Name")
            email = st.text_input("Email")
            year = st.selectbox("Academic Year", [1, 2, 3, 4])
            if st.form_submit_button("Add Student"):
                try:
                    cursor.execute("INSERT INTO Students VALUES (NULL,?,?,?)", 
                                  (name, email, year))
                    conn.commit()
                    st.toast("🎓 Student added successfully!", icon="✅")
                except sqlite3.IntegrityError:
                    st.error("❌ Email already exists")

    elif add_type == "Faculty":
        with st.form("faculty_form", clear_on_submit=True):
            name = st.text_input("Full Name")
            email = st.text_input("Email")
            dept = st.text_input("Department")
            if st.form_submit_button("Add Faculty"):
                try:
                    cursor.execute("INSERT INTO Faculty VALUES (NULL,?,?,?)", 
                                  (name, email, dept))
                    conn.commit()
                    st.toast("👨🏫 Faculty added successfully!", icon="✅")
                except sqlite3.IntegrityError:
                    st.error("❌ Faculty email exists")

    elif add_type == "Skill":
        with st.form("skill_form", clear_on_submit=True):
            skill = st.text_input("Skill Name")
            if st.form_submit_button("Add Skill"):
                try:
                    cursor.execute("INSERT INTO Skills VALUES (NULL,?)", (skill,))
                    conn.commit()
                    st.toast("💡 Skill added successfully!", icon="✅")
                except sqlite3.IntegrityError:
                    st.error("❌ Skill already exists")

# TAB 2: Assign Skills
with tabs[1]:
    st.header("🔗 Skill Assignment")
    students = cursor.execute("SELECT StudentID, Name FROM Students").fetchall()
    skills = cursor.execute("SELECT SkillID, SkillName FROM Skills").fetchall()
    
    if students and skills:
        with st.form("assign_form"):
            student = st.selectbox("Student", students, 
                                  format_func=lambda x: f"{x[1]} (ID: {x[0]})")
            skill = st.selectbox("Skill", skills, 
                                format_func=lambda x: f"{x[1]} (ID: {x[0]})")
            prof = st.select_slider("Proficiency Level", 
                                   ["Beginner", "Intermediate", "Advanced"])
            if st.form_submit_button("Assign Skill"):
                cursor.execute("""
                    INSERT OR REPLACE INTO StudentSkills 
                    VALUES (?,?,?)
                """, (student[0], skill[0], prof))
                conn.commit()
                st.toast(f"✅ {student[1]} assigned {skill[1]} skill", icon="✅")
    else:
        st.warning("Please add students and skills first")

# TAB 3: Schedule Sessions
with tabs[2]:
    st.header("🗓 Session Scheduling")
    students = cursor.execute("SELECT StudentID, Name FROM Students").fetchall()
    
    if students:
        with st.form("session_form"):
            col1, col2 = st.columns(2)
            with col1:
                tutor = st.selectbox("Tutor", students,
                                    format_func=lambda x: x[1])
            with col2:
                learner = st.selectbox("Learner", students,
                                      format_func=lambda x: x[1])
            date = st.date_input("Session Date")
            topic = st.text_input("Session Topic")
            
            if st.form_submit_button("Schedule Session"):
                if tutor[0] == learner[0]:
                    st.error("Tutor and learner must be different")
                else:
                    cursor.execute("""
                        INSERT INTO Sessions 
                        VALUES (NULL,?,?,?,?)
                    """, (tutor[0], learner[0], date, topic))
                    conn.commit()
                    st.toast("📅 Session scheduled successfully!", icon="✅")
    else:
        st.warning("Add students first")

# TAB 4: Dashboard
with tabs[3]:
    st.header("📊 System Dashboard")
    
    with st.expander("👥 Student Overview"):
        students_df = pd.read_sql("SELECT * FROM Students", conn)
        st.dataframe(students_df, use_container_width=True)
    
    with st.expander("🏫 Faculty Overview"):
        faculty_df = pd.read_sql("SELECT * FROM Faculty", conn)
        st.dataframe(faculty_df, use_container_width=True)
    
    with st.expander("📚 Skill Matrix"):
        skills_df = pd.read_sql("""
            SELECT s.Name AS Student, sk.SkillName, ss.Proficiency 
            FROM StudentSkills ss
            JOIN Students s ON ss.StudentID = s.StudentID
            JOIN Skills sk ON ss.SkillID = sk.SkillID
        """, conn)
        st.dataframe(skills_df, use_container_width=True)
    
    with st.expander("🗓️ Session Calendar"):
        session_df = pd.read_sql("""
>>>>>>> 291916fad73862314b9225bf115406f8e1c9048c
            SELECT s1.Name AS Tutor, s2.Name AS Learner, Date, Topic
            FROM Sessions
            JOIN Students s1 ON s1.StudentID = Sessions.TutorID
            JOIN Students s2 ON s2.StudentID = Sessions.LearnerID
<<<<<<< HEAD
            WHERE TutorID = {student_data[0]} OR LearnerID = {student_data[0]}
        ''', conn)
        st.dataframe(session_df, use_container_width=True)
    elif faculty_data:
        session_df = pd.read_sql('''
            SELECT s1.Name AS Tutor, s2.Name AS Learner, Date, Topic
            FROM Sessions
            JOIN Students s1 ON s1.StudentID = Sessions.TutorID
            JOIN Students s2 ON s2.StudentID = Sessions.LearnerID
        ''', conn)
        st.dataframe(session_df, use_container_width=True)
=======
        """, conn)
        st.dataframe(session_df, use_container_width=True)

# TAB 5: Export
with tabs[4]:
    st.header("📤 Data Export")
    export_options = st.multiselect("Select Data to Export",
                                   ["Students", "Faculty", "Skills", "Sessions"])
    
    if export_options:
        for opt in export_options:
            df = pd.read_sql(f"SELECT * FROM {opt}", conn)
            csv = df.to_csv(index=False).encode()
            st.download_button(
                f"Download {opt} Data",
                csv,
                file_name=f"{opt.lower()}_data.csv",
                mime="text/csv"
            )

# TAB 6: Data Management
with tabs[5]:
    st.header("⚠️ Data Management")
    
    delete_type = st.selectbox("Select Data Type to Manage",
                              ["Students", "Faculty", "Skills", "Sessions"])
    
    if delete_type == "Students":
        data = cursor.execute("SELECT StudentID, Name FROM Students").fetchall()
    elif delete_type == "Faculty":
        data = cursor.execute("SELECT FacultyID, Name FROM Faculty").fetchall()
    elif delete_type == "Skills":
        data = cursor.execute("SELECT SkillID, SkillName FROM Skills").fetchall()
    elif delete_type == "Sessions":
        data = cursor.execute("SELECT SessionID, Topic FROM Sessions").fetchall()
    
    if data:
        record = st.selectbox("Select Record to Delete", data,
                             format_func=lambda x: f"{x[1]} (ID: {x[0]})")
        
        if st.button("🗑️ Delete Record", type="primary"):
            with st.spinner("Deleting..."):
                try:
                    cursor.execute(f"""
                        DELETE FROM {delete_type} 
                        WHERE {delete_type[:-1]}ID = ?
                    """, (record[0],))
                    conn.commit()
                    st.toast("✅ Record deleted successfully", icon="✅")
                    st.rerun()
                except sqlite3.Error as e:
                    st.error(f"❌ Deletion failed: {str(e)}")
    else:
        st.info("No records available for deletion")


>>>>>>> 291916fad73862314b9225bf115406f8e1c9048c
