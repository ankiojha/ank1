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
    st.write("Preview:", df.head())

    num_cols = df.select_dtypes(include='number').columns.tolist()

    # Histogram
    st.subheader("📌 Histogram")
    col = st.selectbox("Select column", num_cols, key="hist")
    fig1, ax1 = plt.subplots()
    sns.histplot(df[col].dropna(), kde=True, ax=ax1)
    st.pyplot(fig1)
    save_chart(fig1, "histogram")
    with open(chart_files["histogram"], "rb") as f:
        st.download_button("Download Histogram", f, "histogram.png", "image/png")

    # Correlation Heatmap
    st.subheader("🧊 Correlation Heatmap")
    fig2, ax2 = plt.subplots()
    sns.heatmap(df[num_cols].corr(), annot=True, cmap="coolwarm", ax=ax2)
    st.pyplot(fig2)
    save_chart(fig2, "heatmap")
    with open(chart_files["heatmap"], "rb") as f:
        st.download_button("Download Heatmap", f, "heatmap.png", "image/png")

    # Scatter Plot
    st.subheader("🟢 Scatter Plot")
    x = st.selectbox("X axis", num_cols, key="x")
    y = st.selectbox("Y axis", num_cols, key="y")
    fig3, ax3 = plt.subplots()
    sns.scatterplot(x=df[x], y=df[y], ax=ax3)
    st.pyplot(fig3)
    save_chart(fig3, "scatter")
    with open(chart_files["scatter"], "rb") as f:
        st.download_button("Download Scatter Plot", f, "scatter.png", "image/png")

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
            st.download_button("Download PDF", f, "charts.pdf", "application/pdf")

else:
    st.info("Please upload a CSV file.")
