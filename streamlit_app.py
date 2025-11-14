import streamlit as st
import sqlite3
from llm_interface import generate_sql_from_prompt

DB_PATH = "insightmart.db"

st.set_page_config(page_title="InsightMart AI", layout="wide")

st.title("🧠 InsightMart — AI SQL Query Assistant")
st.write("Ask any question about your retail data, and I will generate SQL + run it!")

# -----------------------------
# Load SQLite DB
# -----------------------------
def run_sql_query(query):
    try:
        conn = sqlite3.connect(DB_PATH)
        df = conn.execute(query).fetchall()
        columns = [col[0] for col in conn.execute(query).description]
        conn.close()
        return df, columns, None
    except Exception as e:
        return None, None, str(e)


# -----------------------------
# UI Layout
# -----------------------------
with st.container():
    st.subheader("Ask your question:")

    user_prompt = st.text_input(
        "Enter question",
        placeholder="e.g., Show me total sales by city"
    )

    if st.button("Generate SQL"):
        if not user_prompt.strip():
            st.error("Please enter a question.")
        else:
            sql = generate_sql_from_prompt(user_prompt)

            st.subheader("Generated SQL Query")
            st.code(sql, language="sql")

            # Run SQL
            st.subheader("📊 Query Results")
            rows, cols, error = run_sql_query(sql)

            if error:
                st.error(error)
            else:
                if rows:
                    st.dataframe(
                        {cols[i]: [row[i] for row in rows] for i in range(len(cols))}
                    )
                else:
                    st.info("No rows found.")


# -----------------------------
# Quick Suggestions
# -----------------------------
st.sidebar.title("💡 Try These")
examples = [
    "Show me top 5 customers by total purchase amount",
    "List total sales grouped by city",
    "Show total revenue generated in the last 30 days",
    "Which product sold the most units?",
    "Top 10 products by revenue",
]

for q in examples:
    st.sidebar.write(f"➡️ {q}")
