import streamlit as st

st.title("Test HTML")

test_html = '''
<style>
.my-div { color: red; }
</style>
<div class="my-div">
Hello World
</div>
'''

st.html(test_html)

st.markdown(test_html, unsafe_allow_html=True)
