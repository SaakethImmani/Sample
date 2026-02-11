import streamlit as st
import pandas as pd

# Page Configuration
st.set_page_config(page_title="India NFHS Dashboard", layout="wide")

@st.cache_data
def load_data():
    # Load the dataset
    df = pd.read_csv('All India National Family Health Survey.csv')
    # Clean numeric columns: remove non-numeric text/symbols
    for col in df.columns[3:]:
        df[col] = pd.to_numeric(df[col].astype(str).str.replace(r'[^0-9.]+', '', regex=True), errors='coerce')
    return df

try:
    df = load_data()

    st.title("🇮🇳 National Family Health Survey (NFHS) Dashboard")
    st.markdown("Exploring health trends using native Streamlit charts.")

    # Sidebar Filters
    st.sidebar.header("Navigation")
    
    # 1. Filter by Area (Total/Urban/Rural)
    area_type = st.sidebar.selectbox("Select Area Type", df['Area'].unique())
    
    # 2. Filter by Indicator
    indicators = df.columns[3:].tolist()
    selected_ind = st.sidebar.selectbox("Select Health/Population Indicator", indicators)

    # Prepare Data for "State Comparison"
    # We want to see the selected indicator for all states in the chosen area type
    # Pivoting so that Survey years (NFHS-3, NFHS-4) are columns
    comparison_df = df[df['Area'] == area_type].pivot(
        index='India/States/UTs', 
        columns='Survey', 
        values=selected_ind
    )

    # Layout
    col1, col2 = st.columns([2, 1])

    with col1:
        st.subheader(f"Comparison: {selected_ind}")
        # Native Streamlit Chart
        st.bar_chart(comparison_df)

    with col2:
        st.subheader("State Spotlight")
        state_to_spotlight = st.selectbox("Pick a State/UT", sorted(df['India/States/UTs'].unique()))
        
        state_data = df[(df['India/States/UTs'] == state_to_spotlight) & (df['Area'] == area_type)]
        if not state_data.empty:
            # Show a simple summary table for the specific state
            st.table(state_data[['Survey', selected_ind]].set_index('Survey'))
        else:
            st.write("No data available for this state.")

    # Data Table View
    st.divider()
    if st.checkbox("Show raw data for all regions"):
        st.dataframe(df[df['Area'] == area_type][['India/States/UTs', 'Survey', selected_ind]])

except Exception as e:
    st.error(f"Error loading dashboard: {e}")
    st.info("Check if 'All India National Family Health Survey.csv' is in the same folder.")
col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("Indicator Selection")
    # Simplify column names for display if needed, but here we use original
    all_indicators = df.columns[3:].tolist()
    selected_indicator = st.selectbox("Choose an Indicator to Visualize", all_indicators)

with col2:
    st.subheader("Survey Comparison")
    # Pivot for comparison
    comp_df = filtered_df[['India/States/UTs', 'Survey', selected_indicator]].dropna()
    if not comp_df.empty:
        fig = px.bar(comp_df, x='India/States/UTs', y=selected_indicator, color='Survey',
                     barmode='group', title=f"{selected_indicator} by State")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("No data available for the selected combination.")

st.divider()

# Comparison of Multiple Indicators
st.subheader("Compare Multiple Indicators")
multi_indicators = st.multiselect("Select multiple indicators for comparison", all_indicators, 
                                  default=all_indicators[:3])

if multi_indicators:
    # Melt for easier plotting
    melted_df = filtered_df.melt(id_vars=['India/States/UTs', 'Survey'], value_vars=multi_indicators, 
                                 var_name='Indicator', value_name='Value')
    
    fig_multi = px.line(melted_df, x='Indicator', y='Value', color='India/States/UTs', 
                        markers=True, facet_col='Survey',
                        title="Trends across selected indicators")
    st.plotly_chart(fig_multi, use_container_width=True)

# Data Table
if st.checkbox("Show Raw Data"):
    st.dataframe(filtered_df)
