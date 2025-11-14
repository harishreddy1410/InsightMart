import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt


# -----------------------------
#  Pie Chart Renderer
# -----------------------------
def try_render_pie_chart(df: pd.DataFrame):
    """
    Automatically renders a pie chart if the dataframe
    has exactly 2 columns: category + numeric.
    """
    if df.shape[1] != 2:
        return  # Pie chart not applicable

    col1, col2 = df.columns

    # Check if the second column is numeric
    if not pd.api.types.is_numeric_dtype(df[col2]):
        return

    try:
        fig, ax = plt.subplots()
        ax.pie(
            df[col2],
            labels=df[col1],
            autopct="%1.1f%%",
            startangle=90
        )
        ax.axis('equal')  # Circular shape

        st.subheader("🥧 Pie Chart")
        st.pyplot(fig)

    except Exception as e:
        st.warning(f"Pie Chart could not be generated: {e}")


# -----------------------------
#  Bar Chart Renderer
# -----------------------------
def try_render_bar_chart(df: pd.DataFrame):
    """
    Renders a bar chart if exactly one categorical
    and one numeric column are detected.
    """
    if df.shape[1] != 2:
        return

    col1, col2 = df.columns

    if not pd.api.types.is_numeric_dtype(df[col2]):
        return

    try:
        fig, ax = plt.subplots()
        ax.bar(df[col1], df[col2])
        plt.xticks(rotation=45, ha='right')

        st.subheader("📊 Bar Chart")
        st.pyplot(fig)

    except Exception as e:
        st.warning(f"Bar Chart could not be generated: {e}")


# -----------------------------
#  Auto Chart Orchestrator
# -----------------------------
def render_auto_charts(df: pd.DataFrame):
    """
    Runs all chart attempts.
    - Pie chart
    - Bar chart
    More types can be added here later.
    """
    try_render_pie_chart(df)
    try_render_bar_chart(df)
