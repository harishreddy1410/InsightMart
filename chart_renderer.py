import streamlit as st
import pandas as pd

def try_render_chart(df: pd.DataFrame):
    """Intelligently detect chart type from query results and render it."""
    if df is None or df.empty:
        return

    numeric_cols = df.select_dtypes(include=['int64', 'float64']).columns.tolist()
    text_cols = df.select_dtypes(include=['object']).columns.tolist()
    date_cols = df.select_dtypes(include=['datetime64']).columns.tolist()

    # Try converting non-date columns into datetime (if possible)
    for col in df.columns:
        try:
            df[col] = pd.to_datetime(df[col])
            if col not in date_cols:
                date_cols.append(col)
        except:
            pass

    # 1️⃣ Case: Text + Numeric → Bar chart
    if len(text_cols) >= 1 and len(numeric_cols) >= 1:
        st.subheader("📊 Auto Chart")
        st.bar_chart(df.set_index(text_cols[0])[numeric_cols[0]])
        return

    # 2️⃣ Case: Date + Numeric → Line chart
    if len(date_cols) >= 1 and len(numeric_cols) >= 1:
        st.subheader("📈 Time Series Chart")
        st.line_chart(df.set_index(date_cols[0])[numeric_cols[0]])
        return

    # 3️⃣ Case: Two numeric columns → Scatter plot
    if len(numeric_cols) >= 2:
        st.subheader("🔵 Scatter Plot")
        st.scatter_chart(df[numeric_cols[:2]])
        return

    # Otherwise → No chart
    st.info("ℹ️ Chart not generated (data not suitable for visualization).")
