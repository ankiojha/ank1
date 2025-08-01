import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import streamlit as st
import tempfile
import os
from fpdf import FPDF

st.set_page_config(page_title="CSV Chart Analyzer", layout="wide")
st.title("📊 CSV Chart Viewer & Reporter")

chart_files = {}
chart_data = {}

def save_chart(fig, name):
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".png")
    fig.savefig(tmp.name, bbox_inches='tight')
    chart_files[name] = tmp.name

def render_table_to_pdf(pdf, df, title, max_rows=30):
    pdf.add_page()
    pdf.set_font("Arial", "B", 14)
    pdf.cell(200, 10, title, ln=1)
    pdf.set_font("Arial", "", 8)

    col_width = 190 / max(len(df.columns), 1)
    row_height = 6

    # Header
    for col in df.columns:
        pdf.cell(col_width, row_height, str(col)[:15], border=1)
    pdf.ln(row_height)

    # Rows
    for i, row in df.iterrows():
        for item in row:
            pdf.cell(col_width, row_height, str(item)[:15], border=1)
        pdf.ln(row_height)
        if i >= max_rows:
            pdf.cell(200, 10, "...Table truncated", ln=1)
            break

def render_image_to_pdf(pdf, img_path, title):
    pdf.add_page()
    pdf.set_font("Arial", "B", 14)
    pdf.cell(200, 10, title, ln=1)
    pdf.image(img_path, x=10, y=30, w=180)

# Upload CSV
file = st.file_uploader("Upload CSV", type="csv")

if file:
    df = pd.read_csv(file)
    st.write("📄 Preview:", df.head())

    num_cols = df.select_dtypes(include='number').columns.tolist()
    cat_cols = df.select_dtypes(include='object').columns.tolist()

    # Summary
    st.subheader("📈 Summary Statistics")
    summary = df.describe(include='all').fillna("").round(2)
    st.dataframe(summary)

    # Histogram
    st.subheader("📌 Histogram")
    col = st.selectbox("Select column", num_cols, key="hist")
    fig1, ax1 = plt.subplots()
    sns.histplot(df[col].dropna(), kde=True, ax=ax1)
    st.pyplot(fig1)
    save_chart(fig1, "Histogram")
    chart_data["Histogram"] = df[[col]]

    with open(chart_files["Histogram"], "rb") as f:
        st.download_button("📥 Download Histogram", f, "histogram.png", "image/png")

    # Correlation Heatmap
    st.subheader("🧊 Correlation Heatmap")
    fig2, ax2 = plt.subplots()
    heatmap_data = df[num_cols].corr()
    sns.heatmap(heatmap_data, annot=True, cmap="coolwarm", ax=ax2)
    st.pyplot(fig2)
    save_chart(fig2, "Heatmap")
    chart_data["Heatmap"] = heatmap_data.reset_index()

    with open(chart_files["Heatmap"], "rb") as f:
        st.download_button("📥 Download Heatmap", f, "heatmap.png", "image/png")

    # Scatter Plot
    st.subheader("🟢 Scatter Plot")
    x = st.selectbox("X-axis", num_cols, key="x")
    y = st.selectbox("Y-axis", num_cols, key="y")
    fig3, ax3 = plt.subplots()
    sns.scatterplot(x=df[x], y=df[y], ax=ax3)
    st.pyplot(fig3)
    save_chart(fig3, "Scatter Plot")
    chart_data["Scatter Plot"] = df[[x, y]].dropna()

    with open(chart_files["Scatter Plot"], "rb") as f:
        st.download_button("📥 Download Scatter Plot", f, "scatter.png", "image/png")

    # Bar Chart
    st.subheader("📋 Bar Chart")
    if cat_cols:
        bar_cat = st.selectbox("Bar Chart X-axis", cat_cols, key="bar_x")
        bar_val = st.selectbox("Bar Chart Y-axis", num_cols, key="bar_y")
        bar_data = df.groupby(bar_cat)[bar_val].mean().sort_values(ascending=False).head(10).reset_index()
        fig4, ax4 = plt.subplots()
        sns.barplot(data=bar_data, x=bar_cat, y=bar_val, ax=ax4)
        plt.xticks(rotation=45)
        st.pyplot(fig4)
        save_chart(fig4, "Bar Chart")
        chart_data["Bar Chart"] = bar_data

        with open(chart_files["Bar Chart"], "rb") as f:
            st.download_button("📥 Download Bar Chart", f, "bar_chart.png", "image/png")

    # Line Chart
    st.subheader("📈 Line Chart")
    line_x = st.selectbox("Line Chart X-axis", df.columns, key="line_x")
    line_y = st.selectbox("Line Chart Y-axis", num_cols, key="line_y")
    try:
        df_sorted = df.sort_values(by=line_x)
        fig5, ax5 = plt.subplots()
        sns.lineplot(x=df_sorted[line_x], y=df_sorted[line_y], ax=ax5)
        st.pyplot(fig5)
        save_chart(fig5, "Line Chart")
        chart_data["Line Chart"] = df_sorted[[line_x, line_y]]

        with open(chart_files["Line Chart"], "rb") as f:
            st.download_button("📥 Download Line Chart", f, "line_chart.png", "image/png")
    except:
        st.warning("⚠️ Line chart requires sortable X values like dates or numbers.")

    # Download All Charts as PDF
    st.subheader("📑 Download All Charts PDF")
    if st.button("Generate Charts PDF Only"):
        pdf = FPDF()
        pdf.set_auto_page_break(auto=True, margin=10)
        for name, path in chart_files.items():
            render_image_to_pdf(pdf, path, name)
        charts_pdf_path = os.path.join(tempfile.gettempdir(), "charts_only.pdf")
        pdf.output(charts_pdf_path)
        with open(charts_pdf_path, "rb") as f:
            st.download_button("📥 Download Charts PDF", f, "charts_only.pdf", "application/pdf")

    # Full Summary Report PDF
    st.subheader("📘 Generate Full Summary Report PDF")
    if st.button("Generate Full Report PDF"):
        pdf = FPDF()
        pdf.set_auto_page_break(auto=True, margin=10)

        render_table_to_pdf(pdf, df.head(30), "🔍 Data Preview")
        render_table_to_pdf(pdf, summary.reset_index(), "📈 Summary Statistics")

        for name in chart_files:
            render_image_to_pdf(pdf, chart_files[name], name)
            if name in chart_data:
                render_table_to_pdf(pdf, chart_data[name], f"{name} Data")

        full_path = os.path.join(tempfile.gettempdir(), "full_report.pdf")
        pdf.output(full_path)
        with open(full_path, "rb") as f:
            st.download_button("📥 Download Full Report PDF", f, "full_report.pdf", "application/pdf")

else:
    st.info("📂 Please upload a CSV file.")
