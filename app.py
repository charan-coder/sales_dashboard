import streamlit as st
import pandas as pd
import sqlite3
import plotly.express as px
import os

# --- Configuration & Setup ---
DB_FILE = "sales_data.db"
TABLE_NAME = "sales"
MAPPING_FILE = "mapping.csv"

# --- Database Functions ---
def get_db_connection():
    """Creates a connection to the SQLite database."""
    conn = sqlite3.connect(DB_FILE)
    return conn

def init_db():
    """Initializes the database and table if they don't exist."""
    conn = get_db_connection()
    c = conn.cursor()
    c.execute(f'''
        CREATE TABLE IF NOT EXISTS {TABLE_NAME} (
            OrderID TEXT,
            Date TEXT,
            SKU TEXT,
            MSKU TEXT,
            Quantity INTEGER,
            Price REAL,
            Status TEXT
        )
    ''')
    conn.commit()
    conn.close()

# --- Data Processing Functions ---
def load_mapping_data():
    """Loads the SKU to MSKU mapping from the CSV file."""
    if not os.path.exists(MAPPING_FILE):
        st.error(f"Mapping file not found: {MAPPING_FILE}")
        return None
    return pd.read_csv(MAPPING_FILE)

def process_and_store_data(df, mapping_df):
    """Cleans data, maps SKUs, clears the DB, and stores new data."""
    # 1. Clean and prepare data
    # Ensure required columns exist
    required_cols = ['Date', 'SKU', 'Quantity', 'Price', 'Status', 'OrderID']
    if not all(col in df.columns for col in required_cols):
        missing = [col for col in required_cols if col not in df.columns]
        st.error(f"The uploaded CSV is missing required columns: {', '.join(missing)}")
        return None

    df['Date'] = pd.to_datetime(df['Date'])
    # Ensure SKU columns are strings for a reliable merge
    df['SKU'] = df['SKU'].astype(str)
    mapping_df['SKU'] = mapping_df['SKU'].astype(str)

    # 2. Map SKUs to MSKUs
    processed_df = pd.merge(df, mapping_df, on='SKU', how='left')
    processed_df['MSKU'].fillna('UNKNOWN', inplace=True)

    # 3. Store in database (clearing previous data)
    conn = get_db_connection()
    c = conn.cursor()
    # Clear the table to ensure the dashboard reflects only the uploaded file
    c.execute(f"DELETE FROM {TABLE_NAME}")
    conn.commit()
    
    # Reorder columns to match DB schema for robustness
    db_columns = ['OrderID', 'Date', 'SKU', 'MSKU', 'Quantity', 'Price', 'Status']
    processed_df = processed_df[db_columns]

    processed_df.to_sql(TABLE_NAME, conn, if_exists='append', index=False)
    conn.close()
    return processed_df

# --- Streamlit UI ---
st.set_page_config(layout="wide", page_title="Sales Dashboard")

st.title("📊 Sales Analysis Dashboard")
st.markdown("Upload your sales CSV file to get instant insights.")

# --- Sidebar for Uploading ---
with st.sidebar:
    st.header("Upload Data")
    uploaded_file = st.file_uploader(
        "Drag and drop your sales CSV here", 
        type=["csv"]
    )

    if uploaded_file:
        st.success("File uploaded successfully!")

# --- Main Panel for Dashboards ---
if uploaded_file is not None:
    try:
        sales_df = pd.read_csv(uploaded_file)
        mapping_df = load_mapping_data()

        if mapping_df is not None:
            # Process and display a preview
            st.subheader("Raw Data Preview")
            st.dataframe(sales_df.head())

            with st.spinner('Processing data, mapping SKUs, and updating database...'):
                processed_df = process_and_store_data(sales_df, mapping_df)
            
            if processed_df is not None:
                st.success("Data processed and stored successfully!")
                st.subheader("Processed Data with MSKUs")
                st.dataframe(processed_df.head())

                # --- Metrics & Visualizations ---
                st.header("Dashboard")
            
            # 1. Total Sales per Product (MSKU)
            sales_by_msku = processed_df.groupby('MSKU')['Quantity'].sum().sort_values(ascending=False).reset_index()
            fig_sales = px.bar(
                sales_by_msku, 
                x='MSKU', 
                y='Quantity', 
                title='Total Sales per Product (MSKU)',
                labels={'Quantity': 'Total Quantity Sold'}
            )
            st.plotly_chart(fig_sales, use_container_width=True)

            # 2. Most Returned Items
            # Assuming 'Status' column contains 'Returned'
            if 'Status' in processed_df.columns:
                returns_df = processed_df[processed_df['Status'].str.lower() == 'returned']
                if not returns_df.empty:
                    most_returned = returns_df.groupby('MSKU')['Quantity'].sum().sort_values(ascending=False).reset_index()
                    fig_returns = px.pie(
                        most_returned, 
                        names='MSKU', 
                        values='Quantity', 
                        title='Most Returned Items'
                    )
                    st.plotly_chart(fig_returns, use_container_width=True)
                else:
                    st.info("No returned items found in the uploaded data.")
            
            # 3. Sales Trend Over Time
            sales_trend = processed_df.groupby(pd.Grouper(key='Date', freq='M'))['Quantity'].sum().reset_index()
            fig_trend = px.line(
                sales_trend, 
                x='Date', 
                y='Quantity', 
                title='Sales Trend Over Time',
                markers=True
            )
            st.plotly_chart(fig_trend, use_container_width=True)

    except Exception as e:
        st.error(f"An error occurred: {e}")
else:
    st.info("Awaiting for a file to be uploaded.")

# Initialize the database on first run
init_db()
