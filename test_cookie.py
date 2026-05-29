import streamlit as st
from streamlit_cookies_controller import CookieController
import time

st.title("Cookie Test")

controller = CookieController()

if "login" in st.query_params:
    st.write("Logging in...")
    controller.set("my_token", "secret123", max_age=3600)
    st.query_params.clear()
    st.rerun()

token = controller.get("my_token")

if token:
    st.success(f"Logged in! Token: {token}")
    if st.button("Logout"):
        controller.remove("my_token")
        st.rerun()
else:
    st.error("Not logged in. URL param ?login=1 to login")
    
    st.write("Current cookies:", controller.getAll())
