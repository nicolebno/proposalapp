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

# Step 2: Employer contribution logic (dynamic UI)
st.subheader("🏥 Employer Medical Contribution Setup")

include_er_contributions = st.checkbox("Would you like to see results with employer contributions?")
class_based_contribution = st.checkbox("Employer contribution varies by employee class?")

# Default values
flat_ee = flat_dep = percent_ee = percent_dep = 0.0
use_waterfall = False
contribution_scope = "Employee Only"
ee_only_type = family_contribution_type = "None"

if include_er_contributions:
    if class_based_contribution:
        st.info("✅ Perfect — we’ll come back to this later.")
    else:
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

# Step 3: File Uploads
st.subheader("📁 Upload Required Documents")

uploaded_file = st.file_uploader("📄 Upload Census File (.xlsx)", type=["xlsx"])
rate_file = st.file_uploader("📊 Upload Medical Table Rates (.xlsx)", type=["xlsx"])
benefit_summary_pdf = st.file_uploader("📎 Upload Benefit Summary (.pdf)", type=["pdf"])
ancillary_proposal_pdf = st.file_uploader("📎 Upload Ancillary Carrier Proposal (.pdf)", type=["pdf"])


# Categorize uploaded files
census_file = rate_file = benefit_summary_pdf = ancillary_proposal_pdf = None

if uploaded_files:
    for file in uploaded_files:
        name = file.name.lower()

        if "census" in name and file.type == "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet":
            census_file = file
        elif "rate" in name and file.type == "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet":
            rate_file = file
        elif "benefit" in name and file.type == "application/pdf":
            benefit_summary_pdf = file
        elif "ancillary" in name and file.type == "application/pdf":
            ancillary_proposal_pdf = file

    st.markdown("### 🧾 File Detection Summary")
    st.write(f"📄 Census file: `{census_file.name if census_file else '❌ Not found'}`")
    st.write(f"📊 Rate file: `{rate_file.name if rate_file else '❌ Not found'}`")
    st.write(f"📑 Benefit Summary PDF: `{benefit_summary_pdf.name if benefit_summary_pdf else '❌ Not found'}`")
    st.write(f"📃 Ancillary Proposal PDF: `{ancillary_proposal_pdf.name if ancillary_proposal_pdf else '❌ Not found'}`")
