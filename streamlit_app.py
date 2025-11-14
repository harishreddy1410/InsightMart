import streamlit as st
import sqlite3
from llm_interface import generate_sql_from_prompt
from db_utils import is_safe_sql
from chart_renderer import try_render_chart
import pandas as pd
from charts import render_auto_charts
from chart_utils import show_time_series_chart


DB_PATH = "insightmart.db"

st.set_page_config(
    page_title="InsightMart - AI SQL Assistant",
    page_icon="📊",
    layout="wide",
)

# ---- Sidebar ----
st.sidebar.title("📘 InsightMart Dashboard")
st.sidebar.markdown("Your AI-powered SQL analytics assistant.")

st.sidebar.subheader("💡 Example Questions")
example_queries = [
    "List total sales grouped by city",
    "Daily sales trend for the last 30 days",
    "Top 5 customers by sales",
    "Show total sales in the last month",    
    "Which products generated the highest revenue?",    
]
for q in example_queries:
    if st.sidebar.button(q):
        st.session_state["pre_filled_query"] = q

st.sidebar.markdown("---")
st.sidebar.subheader("📦 Database")
st.sidebar.markdown("Using **SQLite: insightmart.db**")

st.sidebar.subheader("🤖 Model")
st.sidebar.markdown("LLM Provider: **HuggingFace**")


# ---- Header ----
st.markdown("### 📊 InsightMart AI Assistant")
st.markdown(
    "<div style='font-size:18px; color:#666;'>Ask any business question about your retail data using natural language. "
    "InsightMart converts your question → SQL → results and visual charts.</div>",
    unsafe_allow_html=True,
)

st.markdown("<br>", unsafe_allow_html=True)

# ---- User Input ----
default_prompt = st.session_state.get("pre_filled_query", "")
user_prompt = st.text_input("🔎 What insight do you want?", value=default_prompt, placeholder="e.g., Show monthly sales by category")

generate_btn = st.button("✨ Generate SQL & Run")

st.markdown("<br>", unsafe_allow_html=True)


# ---- SQL Runner ----
def run_sql_query(query):
    if not is_safe_sql(query):
        return None, None, "Unsafe SQL. Only SELECT allowed."

    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.execute(query)
        rows = cursor.fetchall()
        columns = [col[0] for col in cursor.description]
        conn.close()
        return rows, columns, None
    except Exception as e:
        return None, None, str(e)


# ---- When user clicks generate ----
if generate_btn and user_prompt.strip():
    st.subheader("🧠 Generated SQL Query")

    with st.spinner("Talking to LLM..."):
        sql_query = generate_sql_from_prompt(user_prompt)

    st.code(sql_query, language="sql")

    st.markdown("<br>", unsafe_allow_html=True)

    st.subheader("📊 Query Results")

    rows, columns, error = run_sql_query(sql_query)

    if error:
        st.error(f"❌ {error}")
    else:
        if rows:
            df = pd.DataFrame(rows, columns=columns)
            st.dataframe(df, use_container_width=True)

            # 🔥 Auto Chart Rendering
            # Auto-detect & render chart
            show_time_series_chart(rows, columns)
             # 🔥 Auto Chart Rendering
            render_auto_charts(df)
        else:
            st.info("No results returned from the query.")

