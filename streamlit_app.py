import streamlit as st

# Define your pages
lab1 = st.Page("labs/lab_1.py", title="Lab 1", icon="🧪")
lab2 = st.Page("labs/lab_2.py", title="Lab 2", icon="📄")
lab3 = st.Page("labs/lab_3.py", title = "Lab 3")

# Build the navigation (set Lab 2 as default)
pg = st.navigation([lab2, lab1, lab3])

# Run the selected page
pg.run()
