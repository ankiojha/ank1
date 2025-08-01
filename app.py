import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import streamlit as st
import tempfile
import os
from fpdf import FPDF
from io import BytesIO

st.set_page_config(page_title="CSV Chart Analyzer", layout="wide")
st.title("📊 CSV Chart Viewer")

chart_files = {}
chart_dataframes = {}

def save_chart(fig, name):
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".png")
    fig.savefig(tmp.name, bbox_inches='tight')
    chart_files[name] = tmp.name

def download_dataframe(df, name):
    excel_io = BytesIO()
    df.to_excel(excel_io, index=False, engine="openpyxl")
    st.download_button(f"📥 Download '{name}' Data", data=excel_io.getvalue(),
                       file_name=f"{name}_data.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

file = st.file_uploader("Upload CSV File", type="csv")

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
    chart_dataframes["histogram"] = df[[col]]
    with open(chart_files["histogram"], "rb") as f:
        st.download_button("📥 Download Histogram", f, "histogram.png", "image/png")
    download_dataframe(chart_dataframes["histogram"], "histogram")

    # Correlation Heatmap
    st.subheader("🧊 Correlation Heatmap")
    fig2, ax2 = plt.subplots()
    corr = df[num_cols].corr()
    sns.heatmap(corr, annot=True, cmap="coolwarm", ax=ax2)
    st.pyplot(fig2)
    save_chart(fig2, "heatmap")
    chart_dataframes["heatmap"] = corr.reset_index()
    with open(chart_files["heatmap"], "rb") as f:
        st.download_button("📥 Download Heatmap", f, "heatmap.png", "image/png")
    download_dataframe(chart_dataframes["heatmap"], "heatmap")

    # Scatter Plot
    st.subheader("🟢 Scatter Plot")
    x = st.selectbox("X axis", num_cols, key="x")
    y = st.selectbox("Y axis", num_cols, key="y")
    fig3, ax3 = plt.subplots()
    sns.scatterplot(x=df[x], y=df[y], ax=ax3)
    st.pyplot(fig3)
    save_chart(fig3, "scatter")
    chart_dataframes["scatter"] = df[[x, y]].dropna()
    with open(chart_files["scatter"], "rb") as f:
        st.download_button("📥 Download Scatter Plot", f, "scatter.png", "image/png")
    download_dataframe(chart_dataframes["scatter"], "scatter")

    # Bar Chart
    st.subheader("📋 Bar Chart")
    if cat_cols:
        bar_cat = st.selectbox("Bar X-axis (category)", cat_cols, key="bar_cat")
        bar_val = st.selectbox("Bar Y-axis (numeric)", num_cols, key="bar_val")
        bar_data = df.groupby(bar_cat)[bar_val].mean().sort_values(ascending=False).head(10).reset_index()
        fig4, ax4 = plt.subplots()
        sns.barplot(data=bar_data, x=bar_cat, y=bar_val, ax=ax4)
        st.pyplot(fig4)
        save_chart(fig4, "bar")
        chart_dataframes["bar"] = bar_data
        with open(chart_files["bar"], "rb") as f:
            st.download_button("📥 Download Bar Chart", f, "bar_chart.png", "image/png")
        download_dataframe(bar_data, "bar_chart")

    # Pie Chart
    st.subheader("🧁 Pie Chart")
    if cat_cols:
        pie_col = st.selectbox("Choose category column", cat_cols, key="pie")
        pie_data = df[pie_col].value_counts().head(10).reset_index()
        pie_data.columns = [pie_col, "Count"]
        fig5, ax5 = plt.subplots()
        ax5.pie(pie_data["Count"], labels=pie_data[pie_col], autopct="%1.1f%%", startangle=90)
        ax5.axis("equal")
        st.pyplot(fig5)
        save_chart(fig5, "pie")
        chart_dataframes["pie"] = pie_data
        with open(chart_files["pie"], "rb") as f:
            st.download_button("📥 Download Pie Chart", f, "pie_chart.png", "image/png")
        download_dataframe(pie_data, "pie_chart")

    # Line Chart
    st.subheader("📈 Line Chart")
    line_x = st.selectbox("Line X-axis", df.columns, key="line_x")
    line_y = st.selectbox("Line Y-axis", num_cols, key="line_y")
    try:
        df_sorted = df.sort_values(by=line_x)
        fig6, ax6 = plt.subplots()
        sns.lineplot(x=df_sorted[line_x], y=df_sorted[line_y], ax=ax6)
        st.pyplot(fig6)
        save_chart(fig6, "line")
        chart_dataframes["line"] = df_sorted[[line_x, line_y]]
        with open(chart_files["line"], "rb") as f:
            st.download_button("📥 Download Line Chart", f, "line_chart.png", "image/png")
        download_dataframe(chart_dataframes["line"], "line_chart")
    except:
        st.warning("⚠️ Line graph needs X values that can be sorted (e.g., dates or numbers)")

    # All chart PDF download
    st.subheader("📄 Download All Charts as PDF")
    if st.button("Generate PDF"):
        pdf = FPDF()
        pdf.set_auto_page_break(auto=True, margin=10)
        for name, path in chart_files.items():
            pdf.add_page()
            pdf.set_font("Arial", "B", 14)
            pdf.cell(200, 10, name.capitalize(), ln=1)
            pdf.image(path, x=10, y=20, w=180)
        pdf_path = os.path.join(tempfile.gettempdir(), "charts.pdf")
        pdf.output(pdf_path)
        with open(pdf_path, "rb") as f:
            st.download_button("📥 Download All Charts PDF", f, "charts.pdf", "application/pdf")

else:
    st.info("Please upload a CSV file to begin.")
