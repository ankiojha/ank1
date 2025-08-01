import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import streamlit as st
import tempfile
import os
from fpdf import FPDF
from io import BytesIO

st.set_page_config(page_title="CSV Report Generator", layout="wide")
st.title("📊 CSV Analyzer & PDF Report Generator")

chart_images = {}
chart_tables = {}

def save_chart_image(fig, label):
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".png")
    fig.savefig(tmp.name, bbox_inches="tight")
    chart_images[label] = tmp.name

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

file = st.file_uploader("Upload a CSV file", type=["csv"])

if file:
    df = pd.read_csv(file)
    st.write("📄 Data Preview", df.head())
    num_cols = df.select_dtypes(include="number").columns.tolist()
    cat_cols = df.select_dtypes(include="object").columns.tolist()

    summary = df.describe(include="all").fillna("").round(2)
    st.write("📈 Summary Statistics", summary)

    # Histogram
    st.subheader("📌 Histogram")
    hist_col = st.selectbox("Select column for histogram", num_cols, key="hist")
    fig1, ax1 = plt.subplots()
    sns.histplot(df[hist_col].dropna(), kde=True, ax=ax1)
    st.pyplot(fig1)
    save_chart_image(fig1, "Histogram")
    chart_tables["Histogram"] = df[[hist_col]].dropna()

    # Heatmap
    st.subheader("🧊 Correlation Heatmap")
    fig2, ax2 = plt.subplots()
    corr = df[num_cols].corr()
    sns.heatmap(corr, annot=True, cmap="coolwarm", ax=ax2)
    st.pyplot(fig2)
    save_chart_image(fig2, "Heatmap")
    chart_tables["Heatmap"] = corr.reset_index().rename(columns={"index": "Feature"})

    # Scatter Plot
    st.subheader("🟢 Scatter Plot")
    scatter_x = st.selectbox("X-axis", num_cols, key="scatter_x")
    scatter_y = st.selectbox("Y-axis", num_cols, key="scatter_y")
    fig3, ax3 = plt.subplots()
    sns.scatterplot(data=df, x=scatter_x, y=scatter_y, ax=ax3)
    st.pyplot(fig3)
    save_chart_image(fig3, "Scatter Plot")
    chart_tables["Scatter Plot"] = df[[scatter_x, scatter_y]].dropna()

    # Bar Chart
    st.subheader("📋 Bar Chart")
    if cat_cols:
        bar_cat = st.selectbox("Bar Chart X-axis (category)", cat_cols, key="bar_cat")
        bar_val = st.selectbox("Bar Chart Y-axis (numeric)", num_cols, key="bar_val")
        bar_data = df.groupby(bar_cat)[bar_val].mean().sort_values(ascending=False).head(10).reset_index()
        fig4, ax4 = plt.subplots()
        sns.barplot(data=bar_data, x=bar_cat, y=bar_val, ax=ax4)
        st.pyplot(fig4)
        save_chart_image(fig4, "Bar Chart")
        chart_tables["Bar Chart"] = bar_data

    # Pie Chart
    st.subheader("🧁 Pie Chart")
    if cat_cols:
        pie_col = st.selectbox("Pie Chart Column", cat_cols, key="pie")
        pie_data = df[pie_col].value_counts().head(10).reset_index()
        pie_data.columns = [pie_col, "Count"]
        fig5, ax5 = plt.subplots()
        ax5.pie(pie_data["Count"], labels=pie_data[pie_col], autopct="%1.1f%%", startangle=90)
        ax5.axis("equal")
        st.pyplot(fig5)
        save_chart_image(fig5, "Pie Chart")
        chart_tables["Pie Chart"] = pie_data

    # Line Chart
    st.subheader("📈 Line Chart")
    line_x = st.selectbox("Line X-axis", df.columns, key="line_x")
    line_y = st.selectbox("Line Y-axis", num_cols, key="line_y")
    try:
        df_sorted = df.sort_values(by=line_x)
        fig6, ax6 = plt.subplots()
        sns.lineplot(x=df_sorted[line_x], y=df_sorted[line_y], ax=ax6)
        st.pyplot(fig6)
        save_chart_image(fig6, "Line Chart")
        chart_tables["Line Chart"] = df_sorted[[line_x, line_y]].dropna()
    except:
        st.warning("⚠️ Could not plot line chart due to unsortable X column")

    # Generate single PDF
    st.subheader("📄 Download Full Report as PDF")
    if st.button("Generate Report"):
        pdf = FPDF()
        pdf.set_auto_page_break(auto=True, margin=10)

        # Table preview
        render_table_to_pdf(pdf, df.head(30), "Data Preview")

        # Summary
        render_table_to_pdf(pdf, summary.reset_index(), "Summary Statistics")

        # Charts + data
        for title, path in chart_images.items():
            render_image_to_pdf(pdf, path, f"{title}")
            if title in chart_tables:
                render_table_to_pdf(pdf, chart_tables[title], f"{title} Data")

        final_path = os.path.join(tempfile.gettempdir(), "final_report.pdf")
        pdf.output(final_path)
        with open(final_path, "rb") as f:
            st.download_button("📥 Download Full Report", f, file_name="csv_report.pdf", mime="application/pdf")

else:
    st.info("📂 Upload a CSV file to begin.")
