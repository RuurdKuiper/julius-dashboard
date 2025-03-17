import streamlit as st
import pandas as pd
import plotly.express as px

# Set page layout to wide
st.set_page_config(layout="wide")

# Load Data
file_path = "Julius Center KPI Dashboard.xlsx"
xls = pd.ExcelFile(file_path)
df_data = pd.read_excel(xls, sheet_name="Data")

# Data Processing
df_data["Publication Year"] = pd.to_numeric(df_data["Publication Year"], errors='coerce').fillna(0).astype(int)
df_data["Number of Citations"] = pd.to_numeric(df_data["Number of Citations"], errors='coerce').fillna(0).astype(int)

departments = [
    "Data Science and Biostatistics",
    "Global Health and Bioethics",
    "General Practice and Nursing Science",
    "Epidemiology and Health Economics"
]

def expand_departments(df):
    expanded_rows = []
    seen_papers = set()
    for _, row in df.iterrows():
        paper_departments = set(str(row["Department"]).split(";"))  # Use a set to avoid duplicates
        for dept in paper_departments:
            dept = dept.strip()
            if dept in departments:
                paper_id = (row["Title"], dept)  # Unique paper-title + department combination
                if paper_id not in seen_papers:
                    seen_papers.add(paper_id)
                    new_row = row.copy()
                    new_row["Department"] = dept
                    expanded_rows.append(new_row)
    return pd.DataFrame(expanded_rows)

df_expanded = expand_departments(df_data)

# Filter to range 2010-2025
df_filtered = df_expanded[(df_expanded["Publication Year"] >= 2010) & (df_expanded["Publication Year"] <= 2025)]

# Publications per Year per Department
st.subheader("Publications Per Year Per Department")
pub_per_year_dept = df_filtered.groupby(["Publication Year", "Department"]).size().reset_index(name="Number of Publications")
fig_pub = px.line(pub_per_year_dept, x="Publication Year", y="Number of Publications", color="Department", title="Publications Per Year Per Department")
fig_pub.update_layout(legend=dict(orientation="h", yanchor="bottom", y=-0.3, xanchor="center", x=0.5))
st.plotly_chart(fig_pub, use_container_width=True)

# Citations per Year per Department
st.subheader("Citations Per Year Per Department")
citations_per_year_dept = df_filtered.drop_duplicates(subset=["Title"]).groupby(["Publication Year", "Department"])['Number of Citations'].sum().reset_index()
fig_cit = px.line(citations_per_year_dept, x="Publication Year", y="Number of Citations", color="Department", title="Citations Per Year Per Department")
fig_cit.update_layout(legend=dict(orientation="h", yanchor="bottom", y=-0.3, xanchor="center", x=0.5))
st.plotly_chart(fig_cit, use_container_width=True)
