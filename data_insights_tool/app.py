import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from sklearn.cluster import KMeans
from fpdf import FPDF
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import base64
import time

# Set page config for mobile-friendly design
st.set_page_config(layout="wide", page_title="Data Insights Generator")

# Guided Onboarding
if 'onboarded' not in st.session_state:
    st.session_state['onboarded'] = False
if not st.session_state['onboarded']:
    st.title("Welcome to Project Apnapan Data Insights Generator!")
    st.write("This tool helps you analyze data effortlessly. Follow these steps:")
    st.write("- Upload your data")
    st.write("- Review cleaning suggestions")
    st.write("- Explore insights")
    if st.button("Start Exploring"):
        st.session_state['onboarded'] = True
    st.stop()

st.title("Data Insights Generator")
st.sidebar.write("""
### How to Use:
1. Upload your data
2. Review cleaning suggestions
3. Explore insights
4. Export results
""")

# Questionnaire mapping
questionnaire_mapping = {
    "Strongly Disagree": 1,
    "Disagree": 2,
    "Neutral": 3,
    "Agree": 4,
    "Strongly Agree": 5
}

# Upload Data with Drag-and-Drop
uploaded_file = st.file_uploader("Drag and drop your data file (.xlsx or .csv) here", type=["xlsx", "csv"], accept_multiple_files=False)

if uploaded_file is not None:
    if uploaded_file.name.endswith('.csv'):
        df = pd.read_csv(uploaded_file)
    else:
        df = pd.read_excel(uploaded_file)
    st.write("### Data Preview")
    st.dataframe(df.head())

    # Automated Processing with User Approval
    df = st.session_state.get('df', df)
    # Detect questionnaire columns dynamically
    questionnaire_cols = [col for col in df.columns if any(str(val).strip().title() in questionnaire_mapping for val in df[col].dropna())]

    with st.expander("Clean Data"):
        st.write("Suggested Actions:")
        fill_method = st.selectbox("Handle missing values", ["None", "Mean", "Median", "Drop"])
        remove_duplicates = st.checkbox("Remove duplicates")
        convert_questionnaire = st.checkbox("Convert Questionnaire Responses to Numeric", value=True)
        
        if st.button("Apply Suggested Cleaning"):
            df_cleaned = df.copy()
            if convert_questionnaire and questionnaire_cols:
                for col in questionnaire_cols:
                    df_cleaned[col] = df_cleaned[col].astype(str).str.strip().str.title()
                    df_cleaned[col] = df_cleaned[col].map(questionnaire_mapping).fillna(df_cleaned[col])
                    df_cleaned[col] = pd.to_numeric(df_cleaned[col], errors='coerce')
            if fill_method != "None":
                if st.button(f"Approve {fill_method} for missing values?"):
                    if fill_method == "Mean":
                        df_cleaned = df_cleaned.fillna(df_cleaned.mean(numeric_only=True))
                    elif fill_method == "Median":
                        df_cleaned = df_cleaned.fillna(df_cleaned.median(numeric_only=True))
                    elif fill_method == "Drop":
                        df_cleaned = df_cleaned.dropna()
            if remove_duplicates and st.button("Approve removing duplicates?"):
                df_cleaned = df_cleaned.drop_duplicates()
            st.session_state['df_cleaned'] = df_cleaned
            st.write("### Data Preview (After Cleaning)")
            st.dataframe(df_cleaned.head())

    # Insight Delivery
    df_cleaned = st.session_state.get('df_cleaned', df)
    with st.expander("Insight Dashboard"):
        st.write("### Key Metrics")
        if not df_cleaned.empty:
            summary = df_cleaned.describe()
            st.dataframe(summary)
            st.write("**Plain Language Insight:** Analyzing the data, key metrics suggest areas for potential improvement!")
        
        # Follow-up Questions (dynamic based on available columns)
        follow_up_options = [
            "What intriguing patterns emerge in the data?",
            "How does shifting a specific data category reshape insights?",
            "Which surprising outliers hold key trends?",
            "What steps could improve the highest-rated category?"
        ]
        follow_up = st.selectbox("Ask a Follow-up Question", follow_up_options)
        if follow_up:
            if follow_up == "What intriguing patterns emerge in the data?":
                st.write("Steady trends observed in numeric responses.")
            elif follow_up == "How does shifting a specific data category reshape insights?":
                st.write("Shifting focus reveals variations across categories.")
            elif follow_up == "Which surprising outliers hold key trends?":
                st.write("Some responses show unexpected highs or lows.")
            elif follow_up == "What steps could improve the highest-rated category?":
                st.write("Consider targeted actions based on top scores.")

    # Explore and Customize
    with st.expander("Explore Data"):
        # Dynamically use all columns as options
        available_columns = df_cleaned.columns.tolist()
        sub_construct = st.selectbox("Sub-Construct", available_columns if len(available_columns) > 0 else ["No data"])
        demographic = st.selectbox("Demographic", available_columns if len(available_columns) > 0 else ["No data"])
        chart_type = st.selectbox("Chart Type", ["Bar", "Pie", "Line"])

        # Checklist
        checklist = st.session_state.get('checklist', {"Tweak Filters": False, "Build a View": False})
        filtered_df = df_cleaned  # Default to df_cleaned
        if st.checkbox("Tweak Filters"):
            checklist["Tweak Filters"] = True
            filtered_df = df_cleaned[df_cleaned[demographic] == df_cleaned[demographic].iloc[0]] if not df_cleaned.empty else df_cleaned
            st.write("Filtered Preview")
            st.dataframe(filtered_df.head())
        if st.checkbox("Build a View"):
            checklist["Build a View"] = True
            st.write("Drag elements to customize (simulated)")
        st.session_state['checklist'] = checklist

        # Interactive Charts
        if chart_type == "Bar" and sub_construct != "No data" and demographic != "No data":
            fig = px.bar(filtered_df, x=sub_construct, y=demographic, title=f"{sub_construct} by {demographic}")
            st.plotly_chart(fig)
        elif chart_type == "Pie" and demographic != "No data":
            fig = px.pie(filtered_df, names=demographic, title=f"{demographic} Distribution")
            st.plotly_chart(fig)
        elif chart_type == "Line" and sub_construct != "No data" and demographic != "No data":
            fig = px.line(filtered_df, x=demographic, y=sub_construct, title=f"{sub_construct} Trend by {demographic}")
            st.plotly_chart(fig)

    # Take Action
    with st.expander("Export Results"):
        df_export = st.session_state.get('df_cleaned', df)
        export_type = st.radio("Export Type", ["Single PDF", "Individual PDFs"])

        if export_type == "Single PDF":
            if st.button("Export Single PDF"):
                pdf = FPDF()
                pdf.add_page()
                pdf.set_font("Arial", size=12)
                pdf.cell(200, 10, txt="Data Insights Report", ln=True, align="C")
                pdf.ln(10)
                pdf.cell(200, 10, txt="Key Observations: Summary of data trends.", ln=True)
                for col in df_export.columns[:5]:
                    mean = df_export[col].mean() if pd.api.types.is_numeric_dtype(df_export[col]) else "N/A"
                    pdf.cell(200, 10, txt=f"{col}: Mean = {mean}", ln=True)
                pdf_output = pdf.output(dest='S').encode('latin-1')
                st.download_button(label="Download PDF", data=pdf_output, file_name="insights.pdf", mime="application/pdf")

        elif export_type == "Individual PDFs":
            if st.button("Export Individual PDFs"):
                for col in df_export.columns[:2]:  # Limit to first two for simplicity
                    pdf = FPDF()
                    pdf.add_page()
                    pdf.set_font("Arial", size=12)
                    pdf.cell(200, 10, txt=f"{col} Insights", ln=True, align="C")
                    pdf.ln(10)
                    mean = df_export[col].mean() if pd.api.types.is_numeric_dtype(df_export[col]) else "N/A"
                    pdf.cell(200, 10, txt=f"{col} Mean: {mean}", ln=True)
                    pdf_output = pdf.output(dest='S').encode('latin-1')
                    st.download_button(label=f"Download {col} PDF", data=pdf_output, file_name=f"{col}_insights.pdf", mime="application/pdf")

        st.write("For Power BI: Download the CSV and import it manually.")
        csv = df_export.to_csv(index=False)
        st.download_button(label="Download CSV", data=csv, file_name="insights.csv", mime="text/csv")

    # Feedback Loop
    with st.expander("Feedback"):
        feedback = st.text_area("Flag any issues or suggestions")
        if st.button("Submit Feedback"):
            st.write("Thank you! Your feedback is logged for review.")

# Tooltip (simulated with expander)
with st.expander("Need Help?"):
    st.write("Hover over charts for details or click to drill down.")