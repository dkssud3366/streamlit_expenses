import streamlit as st
import time
import numpy as np
from streamlit_extras.floating_button import floating_button

with st.spinner("hello" ):
     time.sleep(2)

st.button("Button in main app", help="Warning! Slow SPINNER!")


@st.fragment
def simple_chart1():
    time.sleep(1)
    st.write("When you move the slider, only the chart updates, and not the spinner above 👆")
    val = st.slider("Number of bars", 1, 20, 4)
    st.bar_chart(np.random.default_rng().random(val))

@st.fragment
def simple_chart2():
    time.sleep(1)
    st.write("When you move the slider, only the chart updates, and not the 👆")
    val = st.slider("Number ", 1, 20, 4)
    st.bar_chart(np.random.default_rng().random(val))

simple_chart1()
simple_chart2()

@st.fragment
def enter_button():
    save = floating_button("insert") 
    if save:
       st.write("inset form")

enter_button()
   

