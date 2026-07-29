# dashboard/app.py
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np
import requests
import json
from datetime import datetime, timedelta

# Page config
st.set_page_config(
    page_title="AI AutoML Platform - Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

API_URL = "http://localhost:8000/api/v1"


def get_auth_token():
    """Get authentication token."""
    if "token" not in st.session_state:
        st.session_state.token = None
    return st.session_state.token


def api_request(endpoint, method="GET", data=None):
    """Make API request."""
    headers = {"Authorization": f"Bearer {get_auth_token()}"}
    url = f"{API_URL}{endpoint}"
    try:
        if method == "GET":
            resp = requests.get(url, headers=headers)
        elif method == "POST":
            resp = requests.post(url, headers=headers, json=data)
        return resp.json() if resp.status_code == 200 else None
    except Exception as e:
        st.error(f"API Error: {e}")
        return None


# Sidebar
with st.sidebar:
    st.title("🤖 AI AutoML Platform")
    st.markdown("---")

    page = st.radio(
        "Navigation",
        ["📊 Overview", "📈 EDA Explorer", "🤖 Model Performance",
         "🔮 Predictions", "📋 Reports", "⚙️ Settings"],
    )

    st.markdown("---")
    st.markdown(f"**Logged in as:** Analyst")
    st.markdown(f"**Date:** {datetime.now().strftime('%Y-%m-%d')}")


# Main content
if page == "📊 Overview":
    st.header("Platform Overview")

    # KPI Row
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Datasets", "24", delta="+3 this week")
    with col2:
        st.metric("Active Projects", "12", delta="+2")
    with col3:
        st.metric("Models Deployed", "8", delta="+1")
    with col4:
        st.metric("Avg. Accuracy", "92.3%", delta="+1.2%")

    st.markdown("---")

    # Charts
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Weekly Analysis Activity")
        days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
        analyses = [4, 6, 3, 8, 5, 2, 1]
        fig = go.Figure(data=[go.Bar(x=days, y=analyses, marker_color="#3B82F6")])
        fig.update_layout(height=350, margin=dict(t=20, b=20))
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.subheader("Model Type Distribution")
        model_types = ["Classification", "Regression", "Clustering", "Time Series"]
        counts = [45, 30, 15, 10]
        fig = px.pie(values=counts, names=model_types, hole=0.4)
        fig.update_layout(height=350, margin=dict(t=20, b=20))
        st.plotly_chart(fig, use_container_width=True)

    # Recent activity
    st.subheader("Recent Activity")
    activity_data = pd.DataFrame({
        "Time": ["2 min ago", "15 min ago", "1 hr ago", "3 hrs ago", "5 hrs ago"],
        "Action": ["Model deployed", "Analysis completed", "Dataset uploaded",
                   "Report generated", "Model retrained"],
        "Project": ["Sales Prediction", "Customer Churn", "Q3 Revenue",
                    "Marketing ROI", "Inventory Forecast"],
        "Status": ["✅ Success", "✅ Success", "✅ Success", "✅ Success", "⚠️ Warning"],
    })
    st.dataframe(activity_data, use_container_width=True, hide_index=True)


elif page == "📈 EDA Explorer":
    st.header("Exploratory Data Analysis")

    # File selector
    dataset = st.selectbox("Select Dataset", ["Sales_Data_2024.csv", "Customer_Churn.xlsx", "Revenue.json"])

    if st.button("Run EDA"):
        with st.spinner("Running EDA..."):
            # Generate sample EDA
            st.success("EDA Complete!")

    # Sample charts
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Distribution")
        data = np.random.normal(100, 15, 1000)
        fig = px.histogram(x=data, nbins=50, title="Revenue Distribution")
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.subheader("Correlation Heatmap")
        corr_data = np.random.rand(6, 6)
        corr_data = (corr_data + corr_data.T) / 2
        np.fill_diagonal(corr_data, 1)
        labels = ["Revenue", "Units", "Price", "Discount", "Region", "Season"]
        fig = px.imshow(corr_data, x=labels, y=labels, text_auto=".2f",
                       color_continuous_scale="RdBu_r")
        st.plotly_chart(fig, use_container_width=True)


elif page == "🤖 Model Performance":
    st.header("Model Performance Comparison")

    # Model comparison table
    models_data = pd.DataFrame({
        "Model": ["XGBoost", "Random Forest", "LightGBM", "Logistic Regression", "SVM"],
        "Accuracy": [0.943, 0.921, 0.938, 0.876, 0.891],
        "Precision": [0.938, 0.915, 0.932, 0.871, 0.885],
        "Recall": [0.941, 0.918, 0.935, 0.869, 0.882],
        "F1 Score": [0.939, 0.916, 0.933, 0.870, 0.883],
        "Training Time (s)": [12.3, 8.7, 6.2, 1.1, 15.8],
    })

    st.dataframe(
        models_data.style.highlight_max(subset=["Accuracy", "Precision", "Recall", "F1 Score"], color="lightgreen"),
        use_container_width=True,
        hide_index=True,
    )

    # Performance chart
    st.subheader("Accuracy Comparison")
    fig = go.Figure()
    for _, row in models_data.iterrows():
        fig.add_trace(go.Bar(
            x=[row["Model"]],
            y=[row["Accuracy"]],
            name=row["Model"],
        ))
    fig.update_layout(yaxis_range=[0.8, 1.0], height=400)
    st.plotly_chart(fig, use_container_width=True)


elif page == "🔮 Predictions":
    st.header("Make Predictions")

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Input Features")
        feature1 = st.number_input("Feature 1 (Revenue)", value=50000.0)
        feature2 = st.number_input("Feature 2 (Units Sold)", value=1200)
        feature3 = st.number_input("Feature 3 (Discount %)", value=15.0)
        feature4 = st.selectbox("Region", ["North", "South", "East", "West"])

        if st.button("🔮 Predict", type="primary"):
            with st.spinner("Making prediction..."):
                # Simulate prediction
                prediction = np.random.choice(["High", "Medium", "Low"], p=[0.6, 0.3, 0.1])
                confidence = np.random.uniform(0.75, 0.98)

            st.success(f"**Prediction:** {prediction}")
            st.metric("Confidence", f"{confidence*100:.1f}%")

    with col2:
        st.subheader("Prediction History")
        history = pd.DataFrame({
            "Time": ["10:30", "10:25", "10:20", "10:15", "10:10"],
            "Prediction": ["High", "Medium", "High", "Low", "High"],
            "Confidence": ["94%", "87%", "91%", "78%", "96%"],
        })
        st.dataframe(history, hide_index=True)


elif page == "📋 Reports":
    st.header("Generated Reports")

    reports = [
        {"name": "Q3 Sales Analysis Report", "type": "PDF", "date": "2024-07-28", "size": "2.4 MB"},
        {"name": "Customer Churn Model Report", "type": "PDF", "date": "2024-07-27", "size": "1.8 MB"},
        {"name": "Revenue Forecast Summary", "type": "PPTX", "date": "2024-07-26", "size": "5.1 MB"},
        {"name": "Data Quality Assessment", "type": "XLSX", "date": "2024-07-25", "size": "890 KB"},
    ]

    for report in reports:
        col1, col2, col3, col4 = st.columns([3, 1, 1, 1])
        with col1:
            st.write(f"📄 **{report['name']}**")
        with col2:
            st.write(report["type"])
        with col3:
            st.write(report["date"])
        with col4:
            st.download_button("⬇️", data=b"sample", file_name=report["name"])

    st.markdown("---")
    if st.button("📝 Generate New Report"):
        st.info("Report generation started. You'll be notified when ready.")


elif page == "⚙️ Settings":
    st.header("Platform Settings")

    tab1, tab2, tab3 = st.tabs(["General", "ML Configuration", "Deployment"])

    with tab1:
        st.subheader("General Settings")
        st.text_input("Platform Name", value="AI AutoML Platform")
        st.selectbox("Default LLM Provider", ["OpenAI GPT-4", "Gemini Pro", "Local LLM"])
        st.slider("Max Upload Size (MB)", 10, 1000, 500)

    with tab2:
        st.subheader("ML Configuration")
        st.multiselect(
            "Default Algorithms",
            ["XGBoost", "LightGBM", "Random Forest", "Logistic Regression", "SVM"],
            default=["XGBoost", "Random Forest"],
        )
        st.slider("Cross-Validation Folds", 3, 10, 5)
        st.checkbox("Enable Hyperparameter Tuning", value=True)
        st.checkbox("Enable Auto Feature Engineering", value=True)

    with tab3:
        st.subheader("Deployment Settings")
        st.text_input("AWS Region", value="us-east-1")
        st.text_input("S3 Bucket", value="automl-platform-storage")
        st.checkbox("Auto-deploy best model", value=True)
        st.checkbox("Enable model monitoring", value=True)
