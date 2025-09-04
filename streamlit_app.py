import streamlit as st

# Define your pages
lab1 = st.Page("lab_1.py", title="Lab 1", icon="🧪")
lab2 = st.Page("lab_2.py", title="Lab 2", icon="📄")

# Build the navigation (set Lab 2 as default)
pg = st.navigation([lab1, lab2], default=lab2)

# Run the selected page
pg.run()
