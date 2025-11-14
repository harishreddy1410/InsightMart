import streamlit as st
import pandas as pd

def show_time_series_chart(rows, columns):
    """
    Detects if the SQL result represents a time series and plots a line chart.
    """
    if not rows or "SaleDate" not in columns:
        return

    try:
        df = pd.DataFrame(rows, columns=columns)
        df["SaleDate"] = pd.to_datetime(df["SaleDate"])

        numeric_cols = [col for col in df.columns if df[col].dtype in ["int64", "float64"]]

        if len(numeric_cols) == 1:
            metric = numeric_cols[0]

            st.subheader("📈 Sales Trend")
            st.line_chart(
                df.set_index("SaleDate")[metric],
                use_container_width=True
            )
    except Exception as e:
        st.error(f"Chart Error: {e}")
