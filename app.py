import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="India NFHS Dashboard", layout="wide")

@st.cache_data
def load_data():
    df = pd.read_csv('All India National Family Health Survey.csv')
    # Clean the numeric columns
    for col in df.columns[3:]:
        df[col] = pd.to_numeric(df[col].astype(str).str.replace(r'[^\d.]+', '', regex=True), errors='coerce')
    return df

df = load_data()

st.title("🇮🇳 National Family Health Survey (NFHS) Dashboard")
st.markdown("Explore health and population indicators across India.")

# Sidebar filters
st.sidebar.header("Filters")
states = sorted(df['India/States/UTs'].unique())
selected_states = st.sidebar.multiselect("Select States/UTs", states, default=["India"])

areas = df['Area'].unique()
selected_area = st.sidebar.selectbox("Select Area Type", areas, index=0)

# Filter data
filtered_df = df[(df['India/States/UTs'].isin(selected_states)) & (df['Area'] == selected_area)]

# Main Dashboard
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
