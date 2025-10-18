
import os
import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DB_PATH = os.path.join(os.path.dirname(BASE_DIR), "backend", "app.db")

st.set_page_config(page_title="Cybercrime Dashboard", layout="wide")
st.title("Cybercrime Analytics Dashboard")

@st.cache_data
def load_table(q):
    con = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query(q, con)
    con.close()
    return df

tab1, tab2, tab3 = st.tabs(["Trends", "Geo Summary", "Hotspot Forecasts"])

with tab1:
    st.subheader("Crimes Over Time (Monthly)")
    df = load_table("""
        SELECT substr(date,1,7) as month, type, count(*) as n
        FROM crimes
        GROUP BY month, type
        ORDER BY month
    """)
    st.dataframe(df.head(20))
    pivot = df.pivot(index="month", columns="type", values="n").fillna(0)
    fig = plt.figure()
    pivot.plot(ax=plt.gca())
    st.pyplot(fig)

with tab2:
    st.subheader("Crimes by City/State")
    df = load_table("""
        SELECT city, state, count(*) as n, avg(severity) as avg_sev
        FROM crimes
        GROUP BY city, state
        ORDER BY n DESC
        LIMIT 25
    """)
    st.dataframe(df)

with tab3:
    st.subheader("Forecasted Hotspots")
    df = load_table("""
        SELECT city, state, month, round(risk_score,3) as risk, label
        FROM forecasts
        ORDER BY month DESC, risk DESC
        LIMIT 50
    """)
    st.dataframe(df)
