import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import streamlit as st
import tempfile
import os
from fpdf import FPDF

st.set_page_config(page_title="Simple CSV Analyzer", layout="wide")
st.title("📊 Simple CSV Chart Viewer")

# Store charts
chart_files = {}

def save_chart(fig, name):
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".png")
    fig.savefig(tmp.name, bbox_inches='tight')
    chart_files[name] = tmp.name

# Upload CSV
file = st.file_uploader("Upload CSV", type="csv")

if file:
    df = pd.read_csv(file)
    st.write("📄 Data Preview", df.head())

    num_cols = df.select_dtypes(include='number').columns.tolist()
    cat_cols = df.select_dtypes(include='object').columns.tolist()

    # Histogram
    st.subheader("📌 Histogram")
    col = st.selectbox("Select numeric column", num_cols, key="hist")
    fig1, ax1 = plt.subplots()
    sns.histplot(df[col].dropna(), kde=True, ax=ax1)
    st.pyplot(fig1)
    save_chart(fig1, "histogram")
    with open(chart_files["histogram"], "rb") as f:
        st.download_button("📥 Download Histogram", f, "histogram.png", "image/png")

    # Correlation Heatmap
    st.subheader("🧊 Correlation Heatmap")
    fig2, ax2 = plt.subplots()
    sns.heatmap(df[num_cols].corr(), annot=True, cmap="coolwarm", ax=ax2)
    st.pyplot(fig2)
    save_chart(fig2, "heatmap")
    with open(chart_files["heatmap"], "rb") as f:
        st.download_button("📥 Download Heatmap", f, "heatmap.png", "image/png")

    # Scatter Plot
    st.subheader("🟢 Scatter Plot")
    x = st.selectbox("X axis", num_cols, key="x")
    y = st.selectbox("Y axis", num_cols, key="y")
    fig3, ax3 = plt.subplots()
    sns.scatterplot(x=df[x], y=df[y], ax=ax3)
    st.pyplot(fig3)
    save_chart(fig3, "scatter")
    with open(chart_files["scatter"], "rb") as f:
        st.download_button("📥 Download Scatter Plot", f, "scatter.png", "image/png")

    # Bar Chart
    st.subheader("📋 Bar Chart")
    if cat_cols:
        bar_cat = st.selectbox("Category (X-axis)", cat_cols, key="bar_cat")
        bar_val = st.selectbox("Numeric (Y-axis)", num_cols, key="bar_val")
        bar_data = df.groupby(bar_cat)[bar_val].mean().sort_values(ascending=False).head(10)
        fig4, ax4 = plt.subplots()
        bar_data.plot(kind="bar", ax=ax4)
        ax4.set_ylabel(f"Avg of {bar_val}")
        st.pyplot(fig4)
        save_chart(fig4, "bar")
        with open(chart_files["bar"], "rb") as f:
            st.download_button("📥 Download Bar Chart", f, "bar_chart.png", "image/png")

    # Pie Chart
    st.subheader("🧁 Pie Chart")
    if cat_cols:
        pie_col = st.selectbox("Choose a categorical column", cat_cols, key="pie")
        pie_data = df[pie_col].value_counts().head(10)
        fig5, ax5 = plt.subplots()
        ax5.pie(pie_data, labels=pie_data.index, autopct="%1.1f%%", startangle=90)
        ax5.axis("equal")
        st.pyplot(fig5)
        save_chart(fig5, "pie")
        with open(chart_files["pie"], "rb") as f:
            st.download_button("📥 Download Pie Chart", f, "pie_chart.png", "image/png")

    # Line Chart
    st.subheader("📈 Line Graph")
    line_x = st.selectbox("X-axis", df.columns, key="line_x")
    line_y = st.selectbox("Y-axis", num_cols, key="line_y")
    try:
        df_sorted = df.sort_values(by=line_x)
        fig6, ax6 = plt.subplots()
        sns.lineplot(x=df_sorted[line_x], y=df_sorted[line_y], ax=ax6)
        st.pyplot(fig6)
        save_chart(fig6, "line")
        with open(chart_files["line"], "rb") as f:
            st.download_button("📥 Download Line Graph", f, "line_graph.png", "image/png")
    except:
        st.warning("Line chart requires sortable X values like dates or numbers.")

    # Data Table
    st.subheader("📊 Full Data Table")
    if st.checkbox("Show entire table"):
        st.dataframe(df)

    # Download all as PDF
    st.subheader("📄 Download All Charts as PDF")
    if st.button("Generate PDF"):
        pdf = FPDF()
        pdf.set_auto_page_break(auto=True, margin=10)
        for name, path in chart_files.items():
            pdf.add_page()
            pdf.image(path, x=10, y=20, w=180)
        pdf_path = os.path.join(tempfile.gettempdir(), "charts.pdf")
        pdf.output(pdf_path)
        with open(pdf_path, "rb") as f:
            st.download_button("📥 Download All Charts PDF", f, "charts.pdf", "application/pdf")

else:
    st.info("Please upload a CSV file.")
