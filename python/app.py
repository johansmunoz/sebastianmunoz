import pandas as pd
import plotly.express as px
import dash
from dash import dcc, html
from dash.dependencies import Input, Output

#FIRST PART --> CREATION OF HEATMAP

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

# SECOND PART --> CREATION OF THE CORRELATION BARCHART

# Load the correlation CSV
df_corr = pd.read_csv("Historical_Correlation.csv", index_col=0, header=None, names=["Stock", "Correlation"],skiprows=1)

#Reset index to have the correct form of the dataframe
df_corr=df_corr.reset_index()

#turn to float the data
df_corr["Correlation"] = df_corr["Correlation"].astype(float)

#order the data according to the correlation
df_corr = df_corr.sort_values("Correlation", ascending=False).reset_index(drop=True)

# Optional: clean column names
df_corr["Stock"] = df_corr["Stock"].str.replace("_Precio cierre", "", regex=False)

def create_bar_chart():
    fig = px.bar(
        df_corr,
        x="Correlation",
        y="Stock",
        orientation="h",
        title="📊 Historical Correlation with COLCAP since 2020",
        color="Correlation",
        color_continuous_scale="RdBu_r",
        range_color=[-1, 1],
        labels={"Correlation": "Correlation Coefficient", "Stock": "Stock"}
    )
    fig.update_layout(
        yaxis=dict(autorange="reversed"),
        height=800,
        xaxis=dict(tickformat=".2f"))
    return fig


# Dash app setup
app = dash.Dash(__name__)
server = app.server

app.layout = html.Div([
    html.H1("📈 Correlation Visualizations", style={'textAlign': 'center'}),
    
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
    ),
    
    dcc.Tab(label="Historical Correlation Bar Chart", children=[
            html.Br(),
            dcc.Graph(figure=create_bar_chart(), style={"margin": "0 auto", "width": "90%"})
        ])
    
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