import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Set the page configuration for a wider layout
st.set_page_config(layout="wide")

# Use a caching decorator to load data only once
@st.cache_data
def load_data(url):
    """Loads data from a URL and cleans it, returns a DataFrame."""
    df = pd.read_csv(url)
    # Perform the same cleaning as before
    df.dropna(subset=['Year', 'Publisher'], inplace=True)
    df['Year'] = df['Year'].astype(int)
    return df

# --- Main App ---

# Load the data using our cached function
try:
    df = load_data("https://gist.githubusercontent.com/designernatan/27da044c6dc823f7ac7fe3a01f4513ed/raw/d15b5c7d7a5efb38750b16ec935fc126ec9a6e79/vgsales.csv")
except Exception as e:
    st.error(f"Error loading data: {e}")
    st.stop() # Stop the app if data fails to load

# --- Sidebar for Filters ---
st.sidebar.header("Filter Options")

# Get a list of unique genres for the multiselect widget
genres = sorted(df['Genre'].unique())
selected_genres = st.sidebar.multiselect(
    'Select Genre(s):',
    options=genres,
    default=genres  # Select all by default
)

# Get a list of unique platforms for the multiselect widget
platforms = sorted(df['Platform'].unique())
selected_platforms = st.sidebar.multiselect(
    'Select Platform(s):',
    options=platforms,
    default=['PS2', 'X360', 'PS3', 'Wii', 'DS'] # Sensible defaults
)

# Add a slider for selecting a range of years.
min_year = df['Year'].min()
max_year = df['Year'].max()

selected_year_range = st.sidebar.slider(
    'Select Year Range:',
    min_value=min_year,
    max_value=max_year,
    value=(min_year, max_year) # Default to the full range
)


# Filter the DataFrame based on ALL user selections
filtered_df = df[
    (df['Genre'].isin(selected_genres)) &
    (df['Platform'].isin(selected_platforms)) &
    (df['Year'] >= selected_year_range[0]) &
    (df['Year'] <= selected_year_range[1])
]

# --- Main Page Content ---
st.title("Video Game Sales Analysis Dashboard")
st.write("Use the filters on the left to explore the dataset.")

# --- Display Metrics ---
total_sales = filtered_df['Global_Sales'].sum()
num_games = len(filtered_df)

col1, col2 = st.columns(2)
col1.metric("Total Global Sales (Millions)", f"${total_sales:,.2f}M")
col2.metric("Number of Games Selected", f"{num_games:,}")

# --- Display Charts ---
st.header("Visualizations")

if not filtered_df.empty:
    ## TIME-SERIES: New chart to show sales trends over time.
    st.subheader("Total Sales Over Time")
    # Group the filtered data by year and sum the global sales.
    sales_over_time = filtered_df.groupby('Year')['Global_Sales'].sum()
    # Use Streamlit's built-in line chart function.
    st.line_chart(sales_over_time)


    # Chart 1: Sales by Genre
    st.subheader("Total Sales by Genre")
    sales_by_genre = filtered_df.groupby('Genre')['Global_Sales'].sum().sort_values(ascending=False)
    
    fig1, ax1 = plt.subplots(figsize=(10, 5))
    sns.barplot(x=sales_by_genre.index, y=sales_by_genre.values, ax=ax1, palette="viridis")
    ax1.set_ylabel("Global Sales (in Millions)")
    ax1.set_xlabel("Genre")
    plt.xticks(rotation=45, ha='right')
    st.pyplot(fig1)

    # Chart 2: Sales by Platform
    st.subheader("Total Sales by Platform")
    sales_by_platform = filtered_df.groupby('Platform')['Global_Sales'].sum().sort_values(ascending=False)
    
    fig2, ax2 = plt.subplots(figsize=(10, 5))
    sns.barplot(x=sales_by_platform.index, y=sales_by_platform.values, ax=ax2, palette="plasma")
    ax2.set_ylabel("Global Sales (in Millions)")
    ax2.set_xlabel("Platform")
    plt.xticks(rotation=90)
    st.pyplot(fig2)
else:
    st.warning("No data available for the selected filters. Please adjust your selections.")

# --- Display Raw Data ---
st.header("Filtered Data")
st.dataframe(filtered_df)
