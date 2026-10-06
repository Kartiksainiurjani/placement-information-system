import streamlit as st
import pandas as pd
import os
from groq import Groq

# Page Configuration
st.set_page_config(
    page_title="Campus Placement Information System",
    page_icon="🎓",
    layout="wide"
)

st.title("🎓 Campus Placement Information System")
st.write("Manage student placement records, track hiring status, and generate AI-driven career readiness reports.")

# Sidebar Navigation
with st.sidebar:
    st.header("⚙️ Navigation")
    role = st.radio("Select Portal Role", ["Student Portal", "TPO / Admin Dashboard"])

# Fetch Groq API Key from Environment Variables (Render standard) or Streamlit Secrets
groq_api_key = os.getenv("GROQ_API_KEY") or st.secrets.get("GROQ_API_KEY", None)

# Mock Student Database Setup using Session State
if "student_data" not in st.session_state:
    st.session_state.student_data = pd.DataFrame([
        {
            "Roll No": "101",
            "Name": "Kartik Saini",
            "Branch": "BCA (AI & ML)",
            "CGPA": 8.5,
            "Technical Skills": "Python, SQL, Streamlit, Machine Learning",
            "Placement Status": "Placed",
            "Company": "Panther Technologies",
            "Package (LPA)": 6.5
        },
        {
            "Roll No": "102",
            "Name": "Aman Verma",
            "Branch": "BCA",
            "CGPA": 7.2,
            "Technical Skills": "Java, HTML, CSS, MySQL",
            "Placement Status": "Unplaced",
            "Company": "N/A",
            "Package (LPA)": 0.0
        }
    ])

# ----------------- STUDENT PORTAL -----------------
if role == "Student Portal":
    st.subheader("👨‍🎓 Student Registration & AI Readiness Analysis")
    
    col1, col2 = st.columns(2)
    
    with col1:
        roll_no = st.text_input("Roll Number")
        name = st.text_input("Full Name")
        branch = st.selectbox("Branch / Course", ["BCA (AI & ML)", "BCA", "B.Tech CSE", "MCA"])
        cgpa = st.number_input("Current CGPA", min_value=0.0, max_value=10.0, value=7.5, step=0.1)
    
    with col2:
        skills = st.text_area("Technical & Soft Skills (Comma Separated)", placeholder="e.g. Python, SQL, Communication, React")
        target_role = st.text_input("Target Job Role", placeholder="e.g. Data Analyst, Software Engineer")
        status = st.selectbox("Current Placement Status", ["Unplaced", "Placed"])
        company = st.text_input("Company Name (If Placed)", value="N/A") if status == "Placed" else "N/A"
        package = st.number_input("Package in LPA (If Placed)", min_value=0.0, value=0.0) if status == "Placed" else 0.0

    if st.button("💾 Submit Student Record"):
        if not roll_no or not name or not skills:
            st.warning("Please fill in all mandatory fields.")
        else:
            new_record = {
                "Roll No": roll_no,
                "Name": name,
                "Branch": branch,
                "CGPA": cgpa,
                "Technical Skills": skills,
                "Placement Status": status,
                "Company": company,
                "Package (LPA)": package
            }
            st.session_state.student_data = pd.concat([st.session_state.student_data, pd.DataFrame([new_record])], ignore_index=True)
            st.success("Record submitted successfully to TPO Database!")

    st.divider()
    st.subheader("🤖 AI Placement Readiness Evaluator")
    
    if st.button("⚡ Generate AI Assessment"):
        if not groq_api_key:
            st.error("GROQ_API_KEY not set. Please add GROQ_API_KEY in Render Environment Variables.")
        elif not skills or not target_role:
            st.warning("Please enter your Technical Skills and Target Job Role above.")
        else:
            try:
                client = Groq(api_key=groq_api_key)
                
                prompt = f"""
                Act as a Senior TPO. Provide a concise placement readiness evaluation in short bullet points:
                
                Student: {name} | Branch: {branch} | CGPA: {cgpa} | Skills: {skills} | Target Role: {target_role}
                
                Format:
                ## 📈 Placement Readiness Score
                * Score: X/100 (1-line reason)
                
                ## 🎯 2 Alternate Matching Roles
                * Role 1 & Role 2
                
                ## 🛠️ Key Missing Skills
                * Top 3 missing skills for {target_role}
                
                ## 💡 Quick Preparation Tip
                * 2 short actionable tips for interview success
                """
                
                # Streaming response from Groq LPUs
                response = client.chat.completions.create(
                    messages=[{"role": "user", "content": prompt}],
                    model="llama3-8b-8192",
                    temperature=0.3,
                    max_tokens=400,
                    stream=True
                )
                
                st.write_stream(chunk.choices[0].delta.content for chunk in response if chunk.choices[0].delta.content)
                
            except Exception as e:
                st.error(f"Error processing request: {e}")

# ----------------- TPO / ADMIN DASHBOARD -----------------
else:
    st.subheader("📊 Training & Placement Officer (TPO) Analytics")
    
    df = st.session_state.student_data
    
    m1, m2, m3, m4 = st.columns(4)
    total_students = len(df)
    placed_students = len(df[df["Placement Status"] == "Placed"])
    unplaced_students = total_students - placed_students
    placement_rate = (placed_students / total_students * 100) if total_students > 0 else 0
    
    m1.metric("Total Registered", total_students)
    m2.metric("Placed Students", placed_students)
    m3.metric("Unplaced Students", unplaced_students)
    m4.metric("Placement Rate", f"{placement_rate:.1f}%")
    
    st.divider()
    
    st.subheader("🔍 Student Records Database")
    branch_filter = st.multiselect("Filter by Branch", options=df["Branch"].unique(), default=df["Branch"].unique())
    status_filter = st.multiselect("Filter by Placement Status", options=df["Placement Status"].unique(), default=df["Placement Status"].unique())
    
    filtered_df = df[(df["Branch"].isin(branch_filter)) & (df["Placement Status"].isin(status_filter))]
    st.dataframe(filtered_df, use_container_width=True)
    
    csv = filtered_df.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 Export Filtered Data to CSV",
        data=csv,
        file_name='placement_records.csv',
        mime='text/csv'
    )
