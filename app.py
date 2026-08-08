import streamlit as st

st.set_page_config(
    page_title="Macro Tracker",
    page_icon="🥗",
    layout="wide"
)

st.title("🥗 My Macro Tracker")

st.write("Welcome to your personal macro tracker!")

st.divider()

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Calories", "0 / 2400")

with col2:
    st.metric("Protein", "0 / 180 g")

with col3:
    st.metric("Carbs", "0 / 250 g")

with col4:
    st.metric("Fat", "0 / 80 g")

st.divider()

st.header("Today's Meals")

st.info("No food logged yet.")

if st.button("➕ Add Food"):
    st.write("Food entry coming next...")
