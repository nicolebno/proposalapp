import streamlit as st
import pandas as pd
import re
from datetime import datetime

# 🔒 Prevent early reference errors
uploaded_files = None

st.set_page_config(page_title="Proposal App", layout="wide")
st.title("🧮 Employee Benefits Proposal App")
st.write("Upload a census file and age-based rate sheet to begin.")

# Step 1: Renewal/effective date
renewal_date = st.date_input(
    "📅 Enter Renewal or Effective Date",
    value=datetime.today(),
    key="renewal_date_main"
)
renewal_date = pd.to_datetime(renewal_date)

# Step 2: Employer contribution logic
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

# Set contribution_type label
if not include_er_contributions:
    contribution_type = "None"
elif class_based_contribution:
    contribution_type = "Class-Based"
elif contribution_scope == "Employee Only":
    contribution_type = f"{ee_only_type} (EE Only)"
else:
    contribution_type = f"{family_contribution_type} (EE + Dep)"

# Step 3: Upload files
st.subheader("📁 Upload Required Documents")
uploaded_files = st.file_uploader(
    "Drag and drop or browse to upload: Census (.xlsx), Rate Sheet (.xlsx), Benefit Summary (.pdf), Ancillary Proposal (.pdf)",
    type=["xlsx", "xls", "pdf"],
    accept_multiple_files=True
)

# Step 4: File categorization & preview
census_file = rate_file = benefit_summary_pdf = ancillary_proposal_pdf = None

if uploaded_files is not None and len(uploaded_files) > 0:
    for file in uploaded_files:
        name = file.name.lower()

        if "census" in name and file.type.endswith("spreadsheetml.sheet"):
            census_file = file
        elif "rate" in name and file.type.endswith("spreadsheetml.sheet"):
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

    st.markdown("### 🔍 File Preview (for troubleshooting only)")

    if census_file:
        st.subheader("📄 Census Preview")
        try:
            census_df = pd.read_excel(census_file)
            st.dataframe(census_df.head())
        except Exception as e:
            st.error(f"Could not preview census: {e}")

    if rate_file:
        st.subheader("📊 Rate Sheet Preview")
        try:
            rate_df = pd.read_excel(rate_file, skiprows=4)
            st.dataframe(rate_df.head())
        except Exception as e:
            st.error(f"Could not preview rate sheet: {e}")

    if benefit_summary_pdf:
        st.subheader("📑 Benefit Summary PDF")
        st.info("📎 File uploaded. PDF preview not supported, but we’ve got it!")

    if ancillary_proposal_pdf:
        st.subheader("📃 Ancillary Proposal PDF")
        st.info("📎 File uploaded. PDF preview not supported, but we’ve got it!")

    # Step 5: Parse census + rate sheet
    if census_file and rate_file:
        st.subheader("⚙️ Processing Census and Rate Sheet")

        try:
            df = pd.read_excel(census_file)
            df.columns = (
                df.columns
                .str.replace(u'\xa0', ' ', regex=False)
                .str.replace(r'\s+', ' ', regex=True)
                .str.replace(r'\.$', '', regex=True)
                .str.strip()
            )

            if "DOB" not in df.columns:
                st.error("❌ Your census file must include a column labeled 'DOB'.")
            else:
                df["DOB"] = pd.to_datetime(df["DOB"], errors="coerce")
                df["Age as of Renewal"] = df["DOB"].apply(
                    lambda dob: int((renewal_date - dob).days / 365.25) if pd.notnull(dob) else None
                )

                # Load and clean rate sheet
                raw_rates = pd.read_excel(rate_file, sheet_name=0, skiprows=4)
                raw_rates.columns = (
                    raw_rates.columns
                    .str.replace(u'\xa0', ' ', regex=False)
                    .str.replace(r'\s+', ' ', regex=True)
                    .str.replace(r'\.$', '', regex=True)
                    .str.strip()
                )

                cleaned_rates = raw_rates.rename(columns={raw_rates.columns[0]: "Age Range"}).dropna(subset=["Age Range"])

                def parse_age_range(age_range):
                    match = re.match(r"(\d+)\s*-\s*(\d+)", str(age_range))
                    return (int(match.group(1)), int(match.group(2))) if match else (None, None)

                cleaned_rates[["Min Age", "Max Age"]] = cleaned_rates["Age Range"].apply(
                    lambda x: pd.Series(parse_age_range(x))
                )

                plan_columns = [col for col in cleaned_rates.columns if col not in ["Age Range", "Min Age", "Max Age"]]

                def match_rate(age, plan):
                    match_row = cleaned_rates[
                        (cleaned_rates["Min Age"] <= age) & (cleaned_rates["Max Age"] >= age)
                    ]
                    return float(match_row.iloc[0][plan]) if not match_row.empty else None

                for plan in plan_columns:
                    df[f"{plan} Rate"] = df["Age as of Renewal"].apply(
                        lambda age: match_rate(age, plan) if pd.notnull(age) else None
                    )

                st.success("✅ Rates successfully matched to census by age.")
                st.dataframe(df.head())

        except Exception as e:
            st.error(f"❌ Failed to parse files: {e}")
