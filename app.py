import streamlit as st # type: ignore
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

st.markdown("""
    <style>
    /* General fix for all checkbox labels */
    .stCheckbox div[data-testid="stMarkdownContainer"] > p {
        color: black !important;
        font-weight: 500;
    }

    /* Extra fallback for some Streamlit versions */
    .stCheckbox label {
        color: black !important;
    }
    </style>
""", unsafe_allow_html=True)



import streamlit as st
import base64
import os

# Set page config
st.set_page_config(layout="wide", page_title="Data Insights Generator")

# Load and encode logo
logo_base64 = ""
logo_path = "project_apnapan_logo.png"  # Make sure this file is in your app folder
if os.path.exists(logo_path):
    with open(logo_path, "rb") as img_file:
        logo_base64 = base64.b64encode(img_file.read()).decode()

# Inject CSS for styling
st.markdown(f"""
    <style>
        .stApp {{
            background-color: #d6ecf9;
            font-family: 'Segoe UI', sans-serif;
            color: black !important;
        }}
        [data-testid="stSidebar"] > div:first-child {{
            background-color: #def2e3;
            border-radius: 10px;
            padding: 1rem;
            color: black !important;
        }}
        h1, h2, h3, h4 {{
            color: #003366 !important;
        }}
        .stMetric label, .stMetric span {{
            color: #003366 !important;
        }}
        button, .stDownloadButton button {{
            background-color: #ff6666 !important;
            color: white !important;
            border-radius: 8px;
        }}
        .stFileUploader {{
            border: 2px dashed #3366cc;
            padding: 10px;
            background-color: #ffffff;
            border-radius: 10px;
            color: black;
        }}
        .custom-logo {{
            display: flex;
            align-items: center;
            gap: 12px;
            margin-top: -10px;
            margin-bottom: 20px;
        }}
        .custom-logo img {{
            height: 60px;
        }}
        .custom-logo span {{
            font-size: 26px;
            font-weight: bold;
            color: #003366;
        }}
        .block-container {{
            padding-top: 1.5rem;
        }}
        .stAlert p, .stAlert div, .stAlert {{
            color: black !important;
        }}
        .css-1cpxqw2, .css-ffhzg2 {{
            color: black !important;
        }}
        label, .stCheckbox > div, .stRadio > div, .stSelectbox > div,
        .stMultiSelect > div, .css-16idsys, .css-1r6slb0, .css-1n76uvr {{
            color: black !important;
        }}
    </style>

    <div class="custom-logo">
        <img src="data:image/png;base64,{logo_base64}" />
        <span>Project Apnapan</span>
    </div>
""", unsafe_allow_html=True)


# Guided Onboarding
if 'onboarded' not in st.session_state:
    st.session_state['onboarded'] = False
if not st.session_state['onboarded']:
    st.title("Welcome to Data Insights Generator!")
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

import os
import pandas as pd
import streamlit as st

UPLOAD_HISTORY_DIR = "history"
os.makedirs(UPLOAD_HISTORY_DIR, exist_ok=True)

if "file_history" not in st.session_state:
    st.session_state["file_history"] = {}  # filename: DataFrame

    # Load previously saved files from disk
    for fname in os.listdir(UPLOAD_HISTORY_DIR):
        fpath = os.path.join(UPLOAD_HISTORY_DIR, fname)
        try:
            if fname.endswith(".csv"):
                df = pd.read_csv(fpath)
            elif fname.endswith(".xlsx"):
                df = pd.read_excel(fpath)
            else:
                continue
            st.session_state["file_history"][fname] = df
        except Exception as e:
            st.warning(f"⚠️ Could not load {fname}: {e}")


st.markdown("## Upload or Select Previous File")

uploaded_file = st.file_uploader("📂 Upload a new file (.csv or .xlsx)", type=["csv", "xlsx"])
use_history = False
df = None


if st.session_state["file_history"]:
    selected_history = st.selectbox("📜 Or select from upload history", list(st.session_state["file_history"].keys()))
    use_history = st.button("🔁 Load from History")


if uploaded_file is not None:
    filename = uploaded_file.name
    fpath = os.path.join(UPLOAD_HISTORY_DIR, filename)

    try:
        # Save uploaded file to disk
        with open(fpath, "wb") as f:
            f.write(uploaded_file.getbuffer())

        # Read into DataFrame
        if filename.endswith(".csv"):
            df = pd.read_csv(fpath)
        else:
            df = pd.read_excel(fpath)

        st.session_state["file_history"][filename] = df
        st.success(f"✅ '{filename}' uploaded and saved to history.")
    except Exception as e:
        st.error(f"❌ Failed to process uploaded file: {e}")


elif use_history and selected_history:
    df = st.session_state["file_history"].get(selected_history, None)
    if df is not None:
        st.success(f"✅ Loaded '{selected_history}' from history.")
    else:
        st.error("❌ Could not load the selected file.")

if df is not None:
    st.markdown("### 📊 Data Preview")
    st.dataframe(df.head())


st.markdown("### 🧹 Manage Upload History")

with st.expander("⚠️ Clear All Upload History"):
    st.warning("This will delete all saved files and history. Cannot be undone.")
    confirm_clear = st.checkbox("Yes, I want to delete all uploaded files.")

    if st.button("🗑️ Clear Upload History") and confirm_clear:
        try:
            # Clear session history
            st.session_state["file_history"] = {}

            # Delete files from folder
            for fname in os.listdir(UPLOAD_HISTORY_DIR):
                os.remove(os.path.join(UPLOAD_HISTORY_DIR, fname))

            st.success("✅ Upload history cleared successfully.")
        except Exception as e:
            st.error(f"❌ Failed to clear history: {e}")

    # Automated Processing with User Approval

    if df is None:
        st.warning("Please upload a file or choose one from history to begin.")
        st.stop()

    df = st.session_state.get('df', df)
    # Detect questionnaire columns dynamically
    questionnaire_cols = [col for col in df.columns if any(str(val).strip().title() in questionnaire_mapping for val in df[col].dropna())]

    with st.expander("Clean Data"):
        st.write("Suggested Actions:")
        fill_method = st.selectbox("Handle missing values", ["None", "Mean", "Median", "Drop"])
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
            st.session_state['df_cleaned'] = df_cleaned
            st.write("### Data Preview (After Cleaning)")
            st.dataframe(df_cleaned.head())

    # Insight Delivery
    df_cleaned = st.session_state.get('df_cleaned', df)

        # 🔹 Updated flexible keyword mapping based on your actual questions
    category_keywords = {
                "Safety": ["safe", "surakshit"],
                "Welcome": ["being welcomed", "swagat"],
                "Respect": ["respected", "izzat", "as much respect"],
                #"Friendship & Peer Acceptance": ["make friends", "like you", "socially accepted"],
                "Acknowledgement": [" other students like you", "notice when", "listen to you", "sunne", "dekhein", "acknowledge"],
                "Relationships with Teachers": ["one teacher", "share your problem", "care about your feelings", "close to your teachers"],
                "Participation": ["opportunities", "participate", "school activities"]
            }
    
    # 🔹 Match each category to actual question columns (case-insensitive + emoji safe)
    matched_questions = {
        cat: [col for col in df_cleaned.columns if any(k.lower() in col.lower() for k in keywords)]
        for cat, keywords in category_keywords.items()
    }

    kaash_col = [col for col in df_cleaned.columns if "kaash" in col.lower()]
    if kaash_col:
                df_cleaned["KaashScore"] = df_cleaned[kaash_col].apply(pd.to_numeric, errors="coerce").mean(axis=1)
    else:
                df_cleaned["KaashScore"] = 0

    # 🔹 Belonging score = average of all relevant responses minus KaashScore
    belonging_cols = [col for sublist in matched_questions.values() for col in sublist]
    df_cleaned["BelongingRaw"] = df_cleaned[belonging_cols].apply(pd.to_numeric, errors="coerce").sum(axis=1)
    df_cleaned["BelongingCount"] = df_cleaned[belonging_cols].apply(pd.to_numeric, errors="coerce").notna().sum(axis=1)
    df_cleaned["BelongingScore"] = (df_cleaned["BelongingRaw"] - df_cleaned["KaashScore"]) / df_cleaned["BelongingCount"]


    category_averages = {
    cat: df_cleaned[cols].apply(pd.to_numeric, errors='coerce').mean().mean()  # Compute question averages, then category average
    for cat, cols in matched_questions.items() if cols
     }


    # 🔹 Compute overall belonging score
    overall_belonging_score = (
        df_cleaned["BelongingScore"].mean()
        if category_averages else None
    )

    # 🔹 Detect best/worst experience categories
    if category_averages:
        highest_area = max(category_averages, key=category_averages.get)
        lowest_area = min(category_averages, key=category_averages.get)


    with st.expander("Insight Dashboard"):
        st.write("### Key Metrics")

        col1, col2, col3, col4 = st.columns(4)

        # Welcomed Metric Card
        if "Welcome" in category_averages:
            col4.markdown(f"""
                <div style="background-color:#ffffff; border-radius:10px; padding:1rem; text-align:center;
                            box-shadow: 0 2px 5px rgba(0,0,0,0.1); color:black;">
                    <h4>Welcomed</h4>
                    <h2 style="margin:0;">{category_averages['Welcome']:.2f}</h2>
                </div>
            """, unsafe_allow_html=True)

        if overall_belonging_score is not None:
            col1.markdown(f"""
                <div style="background-color:#ffffff; border-radius:10px; padding:1rem; text-align:center;
                            box-shadow: 0 2px 5px rgba(0,0,0,0.1); color:black;">
                    <h4>⭐ Overall Belonging Score</h4>
                    <h2 style="margin:0;">{overall_belonging_score:.2f}</h2>
                </div>
            """, unsafe_allow_html=True)

            col2.markdown(f"""
                <div style="background-color:#ffffff; border-radius:10px; padding:1rem; text-align:center;
                            box-shadow: 0 2px 5px rgba(0,0,0,0.1); color:black;">
                    <h4>Highest Score</h4>
                    <h3 style="margin:0;">{highest_area}</h3>
                    <h2 style="margin:0;">{category_averages[highest_area]:.2f}</h2>
                </div>
            """, unsafe_allow_html=True)
    
            col3.markdown(f"""
                <div style="background-color:#ffffff; border-radius:10px; padding:1rem; text-align:center;
                            box-shadow: 0 2px 5px rgba(0,0,0,0.1); color:black;">
                    <h4>Lowest Score</h4>
                    <h3 style="margin:0;">{lowest_area}</h3>
                    <h2 style="margin:0;">{category_averages[lowest_area]:.2f}</h2>
                </div>
            """, unsafe_allow_html=True)
            
        else:
            st.info("No survey columns matched the keyword categories.")

        if category_averages:
            st.subheader("Category‑wise Averages")
            st.dataframe(pd.DataFrame.from_dict(category_averages, orient="index", columns=["Average Score"]).round(2))

        if not df_cleaned.empty:
            summary = df_cleaned.describe()
            st.dataframe(summary)

         

    # Explore and Customize
    
    with st.expander(" Explore Belonging Across Groups"):
                    st.subheader("Compare How Different Student Groups Experience Belonging")
                    
                    def categorize_income(possessions: str) -> str:
                        if pd.isna(possessions):
                            return "Unknown"
                        
                        items = possessions.lower()

                        has_car = "car" in items
                        has_computer = "computer" in items or "laptop" in items
                        has_home = "apna ghar" in items
                        is_rented = "rent" in items

                        if has_car and has_home:
                            return "High"
                        if has_computer or (has_home and not has_car):
                            return "Mid"
                        return "Low"

                    
                    # Identify the correct column by checking column names
                    possessions_col = next((col for col in df_cleaned.columns if "what items among these do you have at home".lower() in col.lower()), None)

                    if possessions_col:
                       df_cleaned["Income Category"] = df_cleaned[possessions_col].apply(categorize_income)



                    group_columns = {
                        "Gender": ["gender", "Gender", "What gender do you use"],
                        "Grade": ["grade", "Which grade are you in"], "Income Status": ["Income Category"],
                        "Health Condition": ["health", "disability", "problem", "health condition"], 
                        "Ethnicity": ["ethnicity"], "Religion": ["religion"]
                    }

                    belonging_questions = category_keywords

                    selected_area = st.selectbox("Which belonging aspect do you want to explore?", list(belonging_questions.keys()))

                    if selected_area:
                        area_keywords = belonging_questions[selected_area]
                        matched_cols = [col for col in df_cleaned.columns if any(k.lower() in col.lower() for k in area_keywords)]

                        if not matched_cols:
                            st.warning("No matching questions found for this aspect.")
                        else:
                            target_col = matched_cols[0]
                            st.markdown(f"Showing results for: **{target_col}**")

                            col1, col2 = st.columns(2)
                            col_slots = [col1, col2]
                            chart_index = 0

                            for label, keywords in group_columns.items():
                                matched_group_col = next((col for col in df_cleaned.columns if any(k.lower() in col.lower() for k in keywords)), None)


                                if matched_group_col:
                                    plot_df = df_cleaned[[matched_group_col, target_col]].dropna()
                                    
                                    if target_col in plot_df.columns:
                                        plot_df[target_col] = pd.to_numeric(plot_df[target_col], errors="coerce")
                                    else:
                                        st.warning(f"Column '{target_col}' not found in the data.")


                                    group_avg = plot_df.groupby(matched_group_col)[target_col].mean().reset_index()

                                    # Simplify Ethnicity or Religion labels if needed
                                    if "ethnicity" in matched_group_col.lower():
                                        group_avg[matched_group_col] = group_avg[matched_group_col].replace({
                                            v: "General" if "general" in str(v).lower() else
                                            "SC" if "sc" in str(v).lower() else
                                            "OBC" if "other" in str(v).lower() else
                                            "Don't Know" if "do" in str(v).lower() else
                                            "ST" if "st" in str(v).lower() else v
                                            for v in group_avg[matched_group_col]
                                        })

                                    with col_slots[chart_index % 2]:
                                        fig = px.bar(
                                            group_avg,
                                            x=matched_group_col,
                                            y=target_col,
                                            text=target_col,
                                            title=f"{selected_area} by {label}",
                                            labels={matched_group_col: label, target_col: "Avg Score"},
                                            height=400
                                        )
                                        fig.update_traces(texttemplate='%{text:.2f}', textposition='outside', 
                                                          hovertemplate="%{x}<br>Avg Score: %{y:.2f}<extra></extra>")

                                        max_y = group_avg[target_col].max()
                                        fig.update_layout(
                                            margin=dict(t=50),
                                            yaxis=dict(range=[0, max_y + 0.5])  # Always add enough headroom
                                        )
 # lift y-axis max
                                        st.plotly_chart(fig, use_container_width=True)

                                    chart_index += 1
                                else:
                                    st.info(f"No data found for {label}.")

        
    # Take Action
    from fpdf import FPDF # type: ignore
    import streamlit as st # type: ignore
    import os
    import re
    from datetime import datetime

    # School name input
    school_name = st.text_input("Enter School Name", value="school name", key="school_input")
    generate_pdf = st.button("🎨 Generate PDF")

    logo_path = "project_apnapan_logo.png"
    logo_exists = os.path.exists(logo_path)

    # Replace with real computed values
    overall_belonging_score = 4.21
    category_averages = {
        "Safety": 4.10,
        "Respect": 4.33,
        "Welcome": 4.18
    }

    class ProStyledPDF(FPDF):
        def header(self):
            if logo_exists:
                self.image(logo_path, x=10, y=10, w=20)
            self.set_font("Arial", "B", 18)
            self.set_text_color(0, 51, 102)  # Navy Blue
            self.cell(0, 10, school_name, ln=True, align="C")
            self.set_font("Arial", "", 13)
            self.cell(0, 10, "Data Insights Snapshot", ln=True, align="C")
            self.ln(8)

        def footer(self):
            self.set_y(-20)
            self.set_font("Arial", "I", 10)
            self.set_text_color(100)
            self.cell(0, 10, "Generated using the Project Apnapan Data Insights Tool", 0, 1, "C")
            self.cell(0, 10, datetime.today().strftime("%B %d, %Y"), 0, 0, "C")

        def metric_card(self, label, value, color_rgb):
            self.set_fill_color(*color_rgb)
            self.set_text_color(255, 255, 255)
            self.set_font("Arial", "B", 12)
            self.cell(0, 12, f"{label}: {value:.2f}", ln=1, align="C", fill=True)
            self.ln(2)

        def intro_section(self):
            self.set_font("Arial", "", 12)
            self.set_text_color(0)
            self.multi_cell(0, 8, f"This report presents a snapshot of how students experience Belonging, "
                                f"Safety, Respect, and Welcome at {school_name}. The results are based on "
                                f"student-reported data collected from the survey file.")
            self.ln(8)

    # Generate on click
    if generate_pdf and school_name.strip():
        pdf = ProStyledPDF()
        pdf.add_page()

        # Intro
        pdf.intro_section()

        # Metrics – styled as cards
        pdf.metric_card("Overall Belonging Score", overall_belonging_score or 0, (0, 102, 204))  # Blue
        pdf.metric_card("Safety", category_averages.get("Safety", 0), (0, 153, 0))               # Green
        pdf.metric_card("Respect", category_averages.get("Respect", 0), (255, 153, 51))          # Orange
        pdf.metric_card("Welcomed", category_averages.get("Welcome", 0), (204, 0, 102))          # Pink

        # Output file name
        clean_name = re.sub(r'[^\w\s-]', '', school_name).strip().replace(' ', '_')
        safe_filename = f"{clean_name}_insights_report.pdf"

        # Save to memory
        pdf_output = pdf.output(dest='S').encode('latin-1')

        st.download_button(
            label="📄 Downloading Insights PDF in progres",
            data=pdf_output,
            file_name=safe_filename,
            mime="application/pdf"
        )


    # Feedback Loop
    import smtplib
    from email.message import EmailMessage

    def send_feedback_to_email(feedback_text):
        msg = EmailMessage()
        msg.set_content(feedback_text)
        msg['Subject'] = 'Feedback from Streamlit App'
        msg['From'] = "nbs917740@gmail.com"  # Replace with your Gmail
        msg['To'] = "buttysaylee4@gmail.com"

        # Send email using Gmail's SMTP server
        try:
            with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
                smtp.login("nbs917740@gmail.com", "thyo dcae vevx iimn")  # Replace with your Gmail & app password
                smtp.send_message(msg)
            return True
        except Exception as e:
            st.error(f"Failed to send feedback: {e}")
            return False

    # 💬 Feedback Block
    with st.expander("Feedback"):
        feedback = st.text_area("Flag any issues or suggestions")
        if st.button("Submit Feedback"):
            if feedback:
                if send_feedback_to_email(feedback):
                    st.success("Thank you! Your feedback has been sent.")
            else:
                st.warning("Please enter some feedback before submitting.")

# Tooltip (simulated with expander)
with st.expander("Need Help?"):
    st.write("Contact us at: Phone: +91 1234567890")