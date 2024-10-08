import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import hashlib
import os
import json

# Load your data here (replace with your actual data loading mechanism)
# For demonstration, let's create a sample DataFrame
data = {
    'DataClassification': ['Confidential', 'Confidential', 'Internal', 'Public', 'Public'],
    'Environment': ['Development', 'Production', 'Development', 'Production', 'Development'],
    'OverallRiskScore': [5, 10, 3, 8, 2],
    'risks': [
        [{'risk': 'Data Breach'}, {'risk': 'Compliance Risk'}],
        [{'risk': 'Data Loss'}],
        [{'risk': None}],
        [{'risk': 'Unauthorized Access'}],
        [{'risk': 'Misconfiguration'}]
    ]
}
records = pd.DataFrame(data)

# Generate a random hash for the filename suffix
hash_suffix = hashlib.md5(os.urandom(16)).hexdigest()[:8]
filename = f"mock-data-scored-{hash_suffix}.json"

# Save the updated records to a new JSON file
with open(filename, 'w') as f:
    json.dump(records.to_dict(orient='records'), f, indent=2)

# Output the filename for reference
st.write(f"Saved scored data to: {filename}")

# Load the JSON data into a DataFrame
df = pd.DataFrame(records)

# Convert risks column to a string for display, handling None values
def convert_risks(risks):
    return ', '.join([risk['risk'] for risk in risks if risk['risk'] is not None])

df['risks'] = df['risks'].apply(convert_risks)

# Find the top 10 riskiest assets
top_10_riskiest = df.nlargest(10, 'OverallRiskScore')

# Find the top 50 riskiest assets
top_50_riskiest = df.nlargest(50, 'OverallRiskScore')

# Create a pivot table for the heatmap including the environment attribute
heatmap_data = top_50_riskiest.pivot_table(index='DataClassification', columns='Environment', values='OverallRiskScore', aggfunc='mean', fill_value=0)

# Prepare data for hover tooltips
hover_text = top_50_riskiest.groupby(['DataClassification', 'Environment'])['risks'].apply(lambda x: ', '.join(x)).reset_index()
hover_data = heatmap_data.copy()

for row in hover_data.index:
    for col in hover_data.columns:
        risk_details = hover_text[(hover_text['DataClassification'] == row) & (hover_text['Environment'] == col)]['risks'].values
        if risk_details:
            hover_data.at[row, col] = risk_details[0]
        else:
            hover_data.at[row, col] = ""

# Create the heatmap with Plotly
fig = go.Figure(data=go.Heatmap(
    z=heatmap_data.values,
    x=heatmap_data.columns,
    y=heatmap_data.index,
    colorscale='spectral',
    text=hover_data.values,
    hoverinfo='text',
    hovertemplate='%{text}<extra></extra>'
))

fig.update_layout(
    title='Heatmap of Top 50 Riskiest Assets by Data Classification and Environment',
    xaxis_nticks=36,
    xaxis_title='Environment',
    yaxis_title='Data Classification'
)

# Streamlit app
st.title('Risk Analysis Dashboard')

st.header('Top 10 Riskiest Assets')
st.dataframe(top_10_riskiest)

st.header('Heatmap of Top 50 Riskiest Assets by Data Classification and Environment')
st.plotly_chart(fig)

st.header('Details of Top 50 Riskiest Assets')
st.dataframe(top_50_riskiest)
