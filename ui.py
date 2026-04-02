import streamlit as st
import pandas as pd
import requests
import plotly.express as px
import io

st.set_page_config(page_title="Log Classifier", layout="wide")

st.title("📊 Log Classification Dashboard")
st.markdown("Upload your log CSV file and explore predictions interactively.")

# ---------------- SIDEBAR ----------------
st.sidebar.header("Upload & Settings")
uploaded_file = st.sidebar.file_uploader("Upload CSV", type=["csv"])
api_url = st.sidebar.text_input("FastAPI Endpoint", "http://localhost:8000/classify/")

# Reset button
if st.sidebar.button("🔄 Reset Session"):
    st.session_state.clear()
    st.rerun()

# API status check
try:
    requests.get("http://localhost:8000/docs", timeout=1)
    st.sidebar.success("API Connected ✅")
except:
    st.sidebar.error("API Not Running ❌")

# ---------------- FILE UPLOAD ----------------
if uploaded_file:
    st.session_state["uploaded_file"] = uploaded_file

    df = pd.read_csv(uploaded_file)
    st.subheader("🔍 Raw Data Preview")
    st.dataframe(df.head(), use_container_width=True)

# ---------------- CLASSIFY BUTTON ----------------
if "uploaded_file" in st.session_state:
    if st.button("🚀 Classify Logs"):
        with st.spinner("Classifying logs..."):

            file = st.session_state["uploaded_file"]

            response = requests.post(
                api_url,
                files={"file": (file.name, file.getvalue(), "text/csv")}
            )

            if response.status_code == 200:
                st.session_state["classified_df"] = pd.read_csv(
                    io.BytesIO(response.content)
                )
            else:
                st.error(f"API Error: {response.text}")

# ---------------- DISPLAY RESULTS ----------------
if "classified_df" in st.session_state:
    classified_df = st.session_state["classified_df"]

    st.subheader("✅ Classified Logs")
    st.dataframe(classified_df, use_container_width=True)

    # ---------------- FILTERS ----------------
    st.subheader("🎯 Filter Logs")

    col1, col2 = st.columns(2)

    with col1:
        label_input = st.text_input(
            "🏷️ Label Tags (comma-separated)",
            placeholder="e.g. error, security"
        )

    with col2:
        dropdown_labels = st.multiselect(
            "Or select labels",
            options=classified_df["target_label"].unique()
        )

    filtered_df = classified_df.copy()

    # Tag filtering
    if label_input:
        tags = [t.strip().lower() for t in label_input.split(",")]
        filtered_df = filtered_df[
            filtered_df["target_label"]
            .str.lower()
            .apply(lambda x: any(tag in x for tag in tags))
        ]

    # Dropdown filtering
    if dropdown_labels:
        filtered_df = filtered_df[
            filtered_df["target_label"].isin(dropdown_labels)
        ]

    # Search
    search_query = st.text_input("🔍 Search in logs")
    if search_query:
        filtered_df = filtered_df[
            filtered_df["log_message"]
            .str.contains(search_query, case=False, na=False)
        ]

    st.write(f"📄 Showing {len(filtered_df)} logs")

    st.subheader("📂 Filtered Logs")
    st.dataframe(filtered_df, use_container_width=True)

    # ---------------- METRICS ----------------
    st.subheader("📈 Summary Metrics")
    col1, col2, col3 = st.columns(3)

    total_logs = len(filtered_df)
    unique_labels = filtered_df["target_label"].nunique()
    most_common = (
        filtered_df["target_label"].mode()[0]
        if not filtered_df.empty else "N/A"
    )

    col1.metric("Total Logs", total_logs)
    col2.metric("Unique Labels", unique_labels)
    col3.metric("Most Common", most_common)

    # ---------------- VISUALS ----------------
    st.subheader("📊 Label Distribution")
    label_counts = filtered_df["target_label"].value_counts().reset_index()
    label_counts.columns = ["Label", "Count"]

    fig1 = px.bar(label_counts, x="Label", y="Count", text="Count")
    st.plotly_chart(fig1, use_container_width=True)

    st.subheader("🔗 Source vs Label")
    cross_tab = pd.crosstab(filtered_df["source"], filtered_df["target_label"])

    fig2 = px.imshow(cross_tab, text_auto=True, aspect="auto")
    st.plotly_chart(fig2, use_container_width=True)

    if "timestamp" in filtered_df.columns:
        st.subheader("⏳ Logs Over Time")

        filtered_df["timestamp"] = pd.to_datetime(
            filtered_df["timestamp"], errors="coerce"
        )

        timeline = filtered_df.groupby(
            [pd.Grouper(key="timestamp", freq="D"), "target_label"]
        ).size().reset_index(name="count")

        fig3 = px.line(
            timeline,
            x="timestamp",
            y="count",
            color="target_label"
        )
        st.plotly_chart(fig3, use_container_width=True)

    # ---------------- DOWNLOAD ----------------
    st.download_button(
        label="📥 Download Filtered Results",
        data=filtered_df.to_csv(index=False),
        file_name="filtered_logs.csv",
        mime="text/csv"
    )

else:
    st.info("👈 Upload and classify a CSV file to get started")