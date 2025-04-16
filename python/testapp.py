import pandas as pd
import numpy as np
import plotly.express as px
from dash import Dash, dcc, html, Input, Output
import dash

# Load the monthly correlation data
monthly_df = pd.read_csv("TEST_APP_DASH/Monthly_Correlation.csv", index_col=0, parse_dates=True)
monthly_df.index = pd.to_datetime(monthly_df.index.astype(str))
monthly_df = monthly_df[monthly_df.index >= "2024-03"]
if "Fecha" in monthly_df.columns:
    monthly_df = monthly_df.drop(columns=["Fecha"])

# Split columns into two groups
stocks = list(monthly_df.columns)
midpoint = len(stocks) // 2
group1 = stocks[:midpoint]
group2 = stocks[midpoint:]

def plot_heatmap(data, title):
    fig = px.imshow(
        data.T,
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

# Load the historical correlation CSV
df_corr = pd.read_csv("TEST_APP_DASH/Historical_Correlation.csv", index_col=0, header=None, names=["Stock", "Correlation"], skiprows=1)
df_corr = df_corr.reset_index()
df_corr["Correlation"] = df_corr["Correlation"].astype(float)
df_corr = df_corr.sort_values("Correlation", ascending=False).reset_index(drop=True)
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

# Load rolling correlation CSV
rolling_df = pd.read_csv("TEST_APP_DASH/Rolling_Correlations.csv", index_col=0)
rolling_df = rolling_df.sort_index()

# App layout
app = dash.Dash(__name__)
server = app.server

app.layout = html.Div([
    html.H1("📈 Correlation Visualizations", style={'textAlign': 'center'}),

    dcc.Tabs([
        dcc.Tab(label="Monthly Heatmap", children=[
            html.Br(),
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
            html.Div(dcc.Graph(id="heatmap"), style={"display": "flex", "justifyContent": "center"})
        ]),

        dcc.Tab(label="Historical Correlation Bar Chart", children=[
            html.Br(),
            dcc.Graph(figure=create_bar_chart(), style={"margin": "0 auto", "width": "90%"})
        ]),

        dcc.Tab(label="Rolling Correlation with COLCAP", children=[
            html.Br(),
            dcc.Dropdown(
                id="window_selector",
                options=[{"label": label, "value": label} for label in rolling_df.columns],
                value="252d",
                clearable=False,
                style={"width": "50%", "margin": "auto"}
            ),
            dcc.Graph(id="bar_chart"),
            html.H3("Correlation Table", style={"textAlign": "center"}),
            html.Div(id="correlation_table", style={"width": "80%", "margin": "auto"})
        ])
    ])
])

@app.callback(
    Output("heatmap", "figure"),
    Input("group_selector", "value")
)
def update_heatmap(selected_group):
    data = monthly_df[group1] if selected_group == "group1" else monthly_df[group2]
    title = f"📊 Monthly Correlation Heatmap ({selected_group.replace('group', 'Group ')})"
    return plot_heatmap(data, title)

@app.callback(
    [Output("bar_chart", "figure"), Output("correlation_table", "children")],
    Input("window_selector", "value")
)
def update_rolling_output(selected_window):
    corr_series = rolling_df[selected_window].dropna()

    fig = px.bar(
        x=corr_series.index,
        y=corr_series.values,
        labels={"x": "Stock", "y": f"Correlation ({selected_window})"},
        title=f"Rolling Correlation with COLCAP ({selected_window})",
        color=corr_series.values,
        color_continuous_scale="RdBu",
        range_color=[-1, 1]
    )
    fig.update_layout(xaxis_tickangle=-45, height=500)

    table = html.Table([
        html.Thead([
            html.Tr([html.Th("Stock"), html.Th(f"Correlation ({selected_window})")])
        ]),
        html.Tbody([
            html.Tr([html.Td(stock), html.Td(round(corr, 4))])
            for stock, corr in corr_series.items()
        ])
    ])

    return fig, table

# Run the server locally
if __name__ == "__main__":
    app.run(debug=True)
    
    # Run the server locally
# if __name__ == "__main__":
#     app.run(host="0.0.0.0", port=8080)