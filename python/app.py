import pandas as pd
import plotly.express as px
import dash
from dash import dcc, html
from dash.dependencies import Input, Output

# Load the monthly correlation data
df = pd.read_csv("Monthly_Correlation.csv", index_col=0, parse_dates=True)
df.index = pd.to_datetime(df.index.astype(str))  # Ensure index is datetime

# Filter data from March 2024 onwards
df_filtered = df[df.index >= "2024-03"]

#delete the column "Fecha"
if "Fecha" in df_filtered.columns:
    df_filtered = df_filtered.drop(columns=["Fecha"])

# Split columns into two groups
stocks = list(df_filtered.columns)
midpoint = len(stocks) // 2
group1 = stocks[:midpoint]
group2 = stocks[midpoint:]

def plot_heatmap(data, title):
    fig = px.imshow(
        data.T,  # Transpose for better layout
        labels=dict(x="Month", y="Stock", color="Correlation"),
        title=title,
        color_continuous_scale="RdBu_r",
        aspect="auto",
    )
    fig.update_layout(
        autosize=False,
        width=1000,
        height=600,
        xaxis=dict(tickangle=-45),
    )
    return fig

# Dash app setup
app = dash.Dash(__name__)
server = app.server

app.layout = html.Div([
    html.H1("📊 Monthly Correlation Heatmaps", style={'textAlign': 'center'}),
    
    dcc.Dropdown(
        id="group_selector",
        options=[
            {"label": "Group 1", "value": "group1"},
            {"label": "Group 2", "value": "group2"}
        ],
        value="group1",
        clearable=False,
        style={"width": "50%", "margin": "auto"}
    ),
    
    html.Div(
        dcc.Graph(id="heatmap"),
        style={"display": "flex", "justifyContent": "center"}
    )
])

@app.callback(
    Output("heatmap", "figure"),
    Input("group_selector", "value")
)
def update_heatmap(selected_group):
    data = df_filtered[group1] if selected_group == "group1" else df_filtered[group2]
    title = f"📊 Monthly Correlation Heatmap ({selected_group.replace('group', 'Group ')})"
    return plot_heatmap(data, title)

# Run the server locally
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)