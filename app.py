import streamlit as st
import pandas as pd
import numpy as np
import re
import plotly.express as px
import plotly.graph_objects as go

# -------------------------
# PAGE CONFIG
# -------------------------
st.set_page_config(
    page_title="Indian E-Commerce Analytics Dashboard",
    layout="wide",
    page_icon="📊"
)

st.title("🛒 Indian E-Commerce Pricing, Revenue & Growth Dashboard")
st.markdown("Clean • Transform • Regex Extraction • Visualization • Filters")

# -------------------------
# FILE UPLOAD
# -------------------------
uploaded_file = st.file_uploader("Upload your E-Commerce CSV Dataset", type=["csv"])

if uploaded_file is not None:

    # -------------------------
    # LOAD DATA
    # -------------------------
    df = pd.read_csv(uploaded_file)

    st.subheader("📌 Raw Dataset Preview")
    st.dataframe(df.head())

    # -------------------------
    # DATA CLEANING
    # -------------------------
    st.subheader("🧹 Data Cleaning")

    # Remove duplicate rows
    df = df.drop_duplicates()

    # Standardize column names (lowercase + underscores)
    df.columns = [col.strip().lower().replace(" ", "_") for col in df.columns]

    # Handle missing values
    df = df.fillna({
        col: 0 for col in df.select_dtypes(include=np.number).columns
    })

    st.success("Data cleaned: duplicates removed, columns standardized, null values handled.")

    # -------------------------
    # REGEX EXTRACTION (ADVANCED FEATURE)
    # -------------------------
    st.subheader("🔍 Regex Feature Extraction")

    # Extract numeric discount from discount column (if exists)
    if "discount_percentage" in df.columns:
        df["discount_numeric"] = df["discount_percentage"].astype(str).apply(
            lambda x: float(re.findall(r"\d+\.?\d*", x)[0]) if re.findall(r"\d+\.?\d*", x) else 0
        )

    # Extract month & year from reporting_date using regex
    if "reporting_date" in df.columns:
        df["reporting_date"] = pd.to_datetime(df["reporting_date"], errors="coerce")
        df["year"] = df["reporting_date"].dt.year
        df["month"] = df["reporting_date"].dt.month_name()

    st.info("Regex used for extracting discount numbers and date components.")

    # -------------------------
    # SIDEBAR FILTERS
    # -------------------------
    st.sidebar.header("🎛️ Dashboard Filters")

    # Dynamic filters based on dataset
    if "state" in df.columns:
        selected_state = st.sidebar.multiselect(
            "Select State",
            options=df["state"].unique(),
            default=df["state"].unique()
        )
        df = df[df["state"].isin(selected_state)]

    if "product_category" in df.columns:
        selected_category = st.sidebar.multiselect(
            "Select Category",
            options=df["product_category"].unique(),
            default=df["product_category"].unique()
        )
        df = df[df["product_category"].isin(selected_category)]

    if "brand_type" in df.columns:
        selected_brand = st.sidebar.multiselect(
            "Select Brand Type",
            options=df["brand_type"].unique(),
            default=df["brand_type"].unique()
        )
        df = df[df["brand_type"].isin(selected_brand)]

    # -------------------------
    # DATA TRANSFORMATION (KPIs)
    # -------------------------
    st.subheader("📊 Key Performance Indicators")

    total_revenue = df["revenue"].sum() if "revenue" in df.columns else 0
    total_units = df["units_sold"].sum() if "units_sold" in df.columns else 0
    avg_discount = df["discount_numeric"].mean() if "discount_numeric" in df.columns else 0

    col1, col2, col3 = st.columns(3)
    col1.metric("💰 Total Revenue", f"₹ {total_revenue:,.0f}")
    col2.metric("📦 Total Units Sold", f"{total_units:,.0f}")
    col3.metric("🏷️ Avg Discount %", f"{avg_discount:.2f}%")

    # -------------------------
    # VISUALIZATIONS
    # -------------------------
    st.subheader("📈 Revenue Trend Over Time")

    if "reporting_date" in df.columns and "revenue" in df.columns:
        revenue_trend = df.groupby("reporting_date")["revenue"].sum().reset_index()
        fig1 = px.line(
            revenue_trend,
            x="reporting_date",
            y="revenue",
            title="Monthly Revenue Trend",
            markers=True
        )
        st.plotly_chart(fig1, use_container_width=True)

    # Category Analysis
    st.subheader("🛍️ Category-wise Revenue Analysis")

    if "product_category" in df.columns and "revenue" in df.columns:
        cat_rev = df.groupby("product_category")["revenue"].sum().reset_index()
        fig2 = px.bar(
            cat_rev,
            x="product_category",
            y="revenue",
            color="product_category",
            title="Revenue by Product Category"
        )
        st.plotly_chart(fig2, use_container_width=True)

    # State-wise Sales
    st.subheader("🌍 State-wise Sales Performance")

    if "state" in df.columns and "revenue" in df.columns:
        state_rev = df.groupby("state")["revenue"].sum().reset_index()
        fig3 = px.pie(
            state_rev,
            names="state",
            values="revenue",
            title="Revenue Distribution by State"
        )
        st.plotly_chart(fig3, use_container_width=True)

    # Discount vs Units Sold (Pricing Analysis)
    st.subheader("🏷️ Discount vs Units Sold (Pricing Sensitivity)")

    if "discount_numeric" in df.columns and "units_sold" in df.columns:
        fig4 = px.scatter(
            df,
            x="discount_numeric",
            y="units_sold",
            color="product_category" if "product_category" in df.columns else None,
            title="Discount Impact on Demand",
            size="revenue" if "revenue" in df.columns else None
        )
        st.plotly_chart(fig4, use_container_width=True)

    # -------------------------
    # DATA EXPORT (PRO FEATURE)
    # -------------------------
    st.subheader("📥 Download Cleaned Data")
    csv = df.to_csv(index=False).encode("utf-8")
    st.download_button(
        label="Download Processed Dataset",
        data=csv,
        file_name="cleaned_ecommerce_data.csv",
        mime="text/csv"
    )

else:
    st.warning("Please upload your dataset to start the analysis.")


