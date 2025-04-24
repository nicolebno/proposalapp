import streamlit as st
import pandas as pd
import re
from datetime import datetime
import io

st.set_page_config(page_title="Proposal App", layout="wide")
st.title("🧮 Employee Benefits Proposal App")
st.write("Upload a census file and age-based rate sheet to begin.")

# Step 1: Renewal/effective date
renewal_date = st.date_input(
    "📅 Enter Renewal or Effective Date", 
    value=datetime.today(),
    key="renewal_date_input"
)
renewal_date = pd.to_datetime(renewal_date)

# Step 1: Renewal/effective date
renewal_date = st.date_input(
    "📅 Enter Renewal or Effective Date", 
    value=datetime.today(),
    key="renewal_date_main"  # changed key to avoid duplication
)


# Step 2: Employer contribution logic (dynamic UI)
st.subheader("🏥 Employer Medical Contribution Setup")

include_er_contributions = st.checkbox("Include employer medical contributions in this model?")
class_based_contribution = st.checkbox("Employer contribution varies by employee class?")

# Default values
flat_ee = flat_dep = percent_ee = percent_dep = 0.0
use_waterfall = False
contribution_scope = "Employee Only"
ee_only_type = family_contribution_type = "None"

if include_er_contributions:
    if class_based_contribution:
        st.info("✅ Perfect — we’ll come back to class-based logic later.")

    contribution_scope = st.radio(
        "Does the employer contribute toward:",
        ["Employee Only", "Employee + Family"]
    )

    if contribution_scope == "Employee Only":
        ee_only_type = st.radio(
            "Choose contribution type for employee-only medical:",
            ["Flat Dollar", "Percentage"]
        )
        if ee_only_type == "Flat Dollar":
            flat_ee = st.number_input("Employer pays $_ toward **Employee-Only** Medical", min_value=0.0, step=10.0)
        else:
            percent_ee = st.number_input("Employer pays _% of **Employee-Only** Medical", min_value=0.0, max_value=100.0, step=1.0)

    else:
        family_contribution_type = st.radio(
            "Choose contribution type for Employee + Family medical:",
            ["Flat Dollar", "Percentage"]
        )
        if family_contribution_type == "Flat Dollar":
            flat_ee = st.number_input("Employer pays $_ toward **Employee-Only** Medical", min_value=0.0, step=10.0)
            flat_dep = st.number_input("Employer pays $_ toward **Dependent** Medical", min_value=0.0, step=10.0)
            use_waterfall = st.checkbox("Use waterfall contribution structure?")
        else:
            percent_ee = st.number_input("Employer pays _% of **Employee-Only** Medical", min_value=0.0, max_value=100.0, step=1.0)
            percent_dep = st.number_input("Employer pays _% of **Dependent** Medical", min_value=0.0, max_value=100.0, step=1.0)

# Set contribution_type for downstream logic
if not include_er_contributions:
    contribution_type = "None"
elif class_based_contribution:
    contribution_type = "Class-Based"
elif contribution_scope == "Employee Only":
    contribution_type = f"{ee_only_type} (EE Only)"
else:
    contribution_type = f"{family_contribution_type} (EE + Dep)"

# Step 3: Unified File Upload
st.subheader("📁 Upload Required Documents")
uploaded_files = st.file_uploader(
    "Drag and drop or browse to upload the following: Census (.xlsx), Table Rates (.xlsx), Benefit Summary (.pdf), Ancillary Proposal (.pdf)",
    type=["xlsx", "xls", "pdf"],
    accept_multiple_files=True
)

# Optional: Preview uploaded files
if uploaded_files:
    st.success(f"✅ {len(uploaded_files)} file(s) uploaded.")
    for file in uploaded_files:
        st.write(f"- {file.name}")
