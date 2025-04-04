import streamlit as st
import pandas as pd
import plotly.express as px

# Set page layout to wide
st.set_page_config(layout="centered")

st.title("Julius Center Publication Dashboard")

# Load Data
file_path = "Julius Center KPI Dashboard.xlsx"
xls = pd.ExcelFile(file_path)
df_data = pd.read_excel(xls, sheet_name="Data")

# Data Processing
df_data["Publication Year"] = pd.to_numeric(df_data["Publication Year"], errors='coerce').fillna(0).astype(int)
df_data["Number of Citations"] = pd.to_numeric(df_data["Number of Citations"], errors='coerce').fillna(0).astype(int)
df_data["Publication Date"] = pd.to_datetime(df_data["Publication Date"]).dt.date

departments = [
    "Data Science and Biostatistics",
    "Global Health and Bioethics",
    "General Practice and Nursing Science",
    "Epidemiology and Health Economics"
]

# Define consistent color mapping for departments
department_colors = {
    "Data Science and Biostatistics": "#1f77b4",
    "Global Health and Bioethics": "#ff7f0e",
    "General Practice and Nursing Science": "#2ca02c",
    "Epidemiology and Health Economics": "#d62728"
}

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
fig_pub = px.line(pub_per_year_dept, x="Publication Year", y="Number of Publications", color="Department", title="Publications Per Year Per Department", color_discrete_map=department_colors, labels={'x': None})
fig_pub.update_layout(legend=dict(orientation="h", yanchor="top", xanchor="center", x=0.5))
fig_pub.update_layout(xaxis_title=None)
st.plotly_chart(fig_pub, use_container_width=True)

# Citations per Year per Department
st.subheader("Citations Per Year Per Department")
citations_per_year_dept = df_filtered.groupby(["Publication Year", "Department"])['Number of Citations'].sum().reset_index()
fig_cit = px.line(citations_per_year_dept, x="Publication Year", y="Number of Citations", color="Department", title="Citations Per Year Per Department", color_discrete_map=department_colors)
fig_cit.update_layout(legend=dict(orientation="h", yanchor="top", xanchor="center", x=0.5))
fig_cit.update_layout(xaxis_title=None)
st.plotly_chart(fig_cit, use_container_width=True)

# Most Common Journals Per Department
st.subheader("Top 10 Journals Published In, By Department")
top_journals = df_filtered["Journal"].value_counts().head(10).index
journal_counts = df_filtered[df_filtered["Journal"].isin(top_journals)].groupby(["Journal", "Department"]).size().reset_index(name="Count")
journal_counts["Journal"] = journal_counts["Journal"].apply(lambda x: x[:30] + "..." if len(x) > 30 else x)

# Sort journals by total count
total_counts = journal_counts.groupby("Journal")["Count"].sum().reset_index()
journal_counts = journal_counts.merge(total_counts, on="Journal", suffixes=("", "_Total"))
journal_counts = journal_counts.sort_values(by="Count_Total", ascending=True)

# Create horizontal bar chart
fig_journals = px.bar(journal_counts, y="Journal", x="Count", color="Department", title="Top 10 Journals Published In, By Department", barmode="group", orientation="h", color_discrete_map=department_colors)
fig_journals.update_layout(legend=dict(orientation="h", yanchor="top", xanchor="center", x=0.5))
fig_journals.update_layout(xaxis_title=None)
st.plotly_chart(fig_journals, use_container_width=True)

# Most Recent Publications
st.subheader("5 Most Recent Publications")
recent_pubs = df_data.sort_values(by="Publication Date", ascending=False).head(5)
st.dataframe(recent_pubs[["Title", "Authors", "Publication Date", "Journal", "Number of Citations"]])

# Top Cited Papers in Past X Years
st.subheader("Top 5 Most Cited Papers in the Past X Years")
x_years = st.number_input("Enter number of years:", min_value=1, max_value=20, value=5)
current_year = df_data["Publication Year"].max()
top_cited_pubs = df_data[(df_data["Publication Year"] >= current_year - x_years)].sort_values(by="Number of Citations", ascending=False).head(5)
st.dataframe(top_cited_pubs[["Title", "Authors", "Publication Date", "Journal", "Number of Citations"]])

# Search for Author
st.subheader("Search Publications by Author")
author_name = st.text_input("Enter Author Name:")
if author_name:
    author_pubs = df_data[df_data["Authors"].str.contains(author_name, case=False, na=False)]
    st.write(f"### Papers authored by {author_name}")
    st.dataframe(author_pubs[["Title", "Authors", "Publication Date", "Journal", "Number of Citations"]])
