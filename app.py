import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import streamlit as st
import tempfile
from fpdf import FPDF
import os

st.set_page_config(page_title="📊 Universal CSV Analyzer", layout="wide")
st.title("📈 Universal Data Insights Dashboard")

# Store figure paths
fig_paths = []

def save_fig(fig):
    temp_path = tempfile.NamedTemporaryFile(delete=False, suffix=".png")
    fig.savefig(temp_path.name, bbox_inches='tight')
    fig_paths.append(temp_path.name)

uploaded_file = st.file_uploader("Upload your CSV file", type=["csv"])

if uploaded_file:
    df = pd.read_csv(uploaded_file)
    df = df.apply(lambda col: pd.to_numeric(col, errors='ignore') if col.dtype == 'object' else col)

    st.subheader("🔍 Raw Data Preview")
    st.dataframe(df.head())

    st.subheader("📊 Column Summary")
    st.write(df.describe(include='all'))

    numeric_cols = df.select_dtypes(include='number').columns.tolist()
    categorical_cols = df.select_dtypes(include='object').columns.tolist()

    # Histogram
    st.subheader("📌 Histogram")
    hist_col = st.selectbox("Select a numeric column", numeric_cols)
    fig1, ax1 = plt.subplots()
    sns.histplot(df[hist_col].dropna(), kde=True, ax=ax1)
    st.pyplot(fig1)
    save_fig(fig1)

    # Correlation Heatmap
    if len(numeric_cols) >= 2:
        st.subheader("🧊 Correlation Heatmap")
        fig2, ax2 = plt.subplots()
        corr = df[numeric_cols].corr()
        sns.heatmap(corr, annot=True, cmap="coolwarm", ax=ax2)
        st.pyplot(fig2)
        save_fig(fig2)

    # Pair Plot
    st.subheader("🔄 Pair Plot")
    selected_pair_cols = st.multiselect("Choose numeric columns for pairplot", numeric_cols, default=numeric_cols[:2])
    if len(selected_pair_cols) >= 2:
        fig3 = sns.pairplot(df[selected_pair_cols].dropna())
        st.pyplot(fig3)
        fig3.savefig("pairplot.png")
        fig_paths.append("pairplot.png")
    else:
        st.warning("Select at least 2 numeric columns for pairplot.")

    # Pie Chart
    st.subheader("🧁 Pie Chart")
    if categorical_cols:
        pie_col = st.selectbox("Choose a categorical column", categorical_cols)
        pie_data = df[pie_col].value_counts().head(10)
        fig4, ax4 = plt.subplots()
        ax4.pie(pie_data, labels=pie_data.index, autopct='%1.1f%%', startangle=90)
        ax4.axis('equal')
        st.pyplot(fig4)
        save_fig(fig4)

    # Box Plot
    st.subheader("📦 Box Plot")
    if numeric_cols and categorical_cols:
        cat_col = st.selectbox("Category (X-axis)", categorical_cols, key="box_cat")
        num_col = st.selectbox("Numeric (Y-axis)", numeric_cols, key="box_num")
        fig5, ax5 = plt.subplots()
        sns.boxplot(x=cat_col, y=num_col, data=df, ax=ax5)
        plt.xticks(rotation=45)
        st.pyplot(fig5)
        save_fig(fig5)

    # Line Chart
    st.subheader("📈 Line Chart")
    date_cols = df.select_dtypes(include=['datetime', 'object']).columns
    time_col = st.selectbox("Select a column for X-axis (dates or categories)", date_cols, key="line_time")
    line_y = st.selectbox("Select a numeric column for Y-axis", numeric_cols, key="line_y")
    if time_col and line_y:
        if not pd.api.types.is_datetime64_any_dtype(df[time_col]):
            try:
                df[time_col] = pd.to_datetime(df[time_col])
            except:
                st.warning("Couldn't parse dates in selected column.")
        df_sorted = df.sort_values(by=time_col)
        st.line_chart(df_sorted[[time_col, line_y]].set_index(time_col))

    # Bar Chart
    st.subheader("📋 Bar Chart")
    if categorical_cols and numeric_cols:
        bar_cat = st.selectbox("Choose a categorical column (X-axis)", categorical_cols, key="bar_cat")
        bar_val = st.selectbox("Choose a numeric column (Y-axis)", numeric_cols, key="bar_val")
        bar_data = df.groupby(bar_cat)[bar_val].mean().sort_values(ascending=False).head(10)
        fig6, ax6 = plt.subplots()
        bar_data.plot(kind='bar', ax=ax6)
        ax6.set_ylabel(f"Average of {bar_val}")
        ax6.set_xlabel(bar_cat)
        st.pyplot(fig6)
        save_fig(fig6)

    # Scatter Plot
    st.subheader("🟢 Scatter Plot")
    if len(numeric_cols) >= 2:
        scatter_x = st.selectbox("X-axis (numeric)", numeric_cols, key="scatter_x")
        scatter_y = st.selectbox("Y-axis (numeric)", numeric_cols, key="scatter_y")
        fig7, ax7 = plt.subplots()
        sns.scatterplot(data=df, x=scatter_x, y=scatter_y, ax=ax7)
        st.pyplot(fig7)
        save_fig(fig7)

    # Generate and download PDF
    st.subheader("📥 Download All Figures as PDF")
    if st.button("Generate PDF"):
        pdf = FPDF()
        pdf.set_auto_page_break(auto=True, margin=10)
        for path in fig_paths:
            pdf.add_page()
            pdf.image(path, x=10, y=20, w=180)
        pdf_path = os.path.join(tempfile.gettempdir(), "all_charts.pdf")
        pdf.output(pdf_path)
        with open(pdf_path, "rb") as f:
            st.download_button(
                label="📄 Download Charts PDF",
                data=f,
                file_name="universal_data_charts.pdf",
                mime="application/pdf"
            )
else:
    st.info("Please upload a CSV file to begin.")
