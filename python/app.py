import pandas as pd
import numpy as np
import plotly.express as px
from dash import Dash, dcc, html, Input, Output, dash_table, ctx
import dash
import base64
import io
from flask import Response  # Import Flask's Response

# Load the monthly correlation data
monthly_df = pd.read_csv("Monthly_Correlation.csv", index_col=0, parse_dates=True)
monthly_df.index = pd.to_datetime(monthly_df.index.astype(str))
monthly_df = monthly_df[monthly_df.index >= "2024-03"]
monthly_df.columns = monthly_df.columns.str.replace("_Precio cierre", "", regex=False)

if "Fecha" in monthly_df.columns:
    monthly_df = monthly_df.drop(columns=["Fecha"])

# Split columns into two groups
stocks = list(monthly_df.columns)
midpoint = len(stocks) // 2
group1 = stocks[:midpoint]
group2 = stocks[midpoint:]

def plot_heatmap(data, title):
    avg_corr = data.mean().sort_values(ascending=True)
    sorted_data = data[avg_corr.index]
    fig = px.imshow(
        sorted_data.T,
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
df_corr = pd.read_csv("Historical_Correlation.csv", index_col=0, header=None, names=["Stock", "Correlation"], skiprows=1)
df_corr = df_corr.reset_index()
df_corr["Correlation"] = df_corr["Correlation"].astype(float)
df_corr = df_corr.sort_values("Correlation", ascending=False).reset_index(drop=True)
df_corr["Stock"] = df_corr["Stock"].str.replace("_Precio cierre", "", regex=False)

# Load rolling correlation CSV
rolling_df = pd.read_csv("Rolling_Correlations.csv", index_col=0)
rolling_df = rolling_df.sort_index()
rolling_df.index = rolling_df.index.str.replace("_Precio cierre", "", regex=False)

# App layout
app = dash.Dash(__name__)
server = app.server

app.layout = html.Div([
    html.H1("📈 Correlation Visualizations", style={'textAlign': 'center'}),

    dcc.Tabs([
        dcc.Tab(label="Monthly Heatmap", children=[
            html.Div([
                html.Br(),
                dcc.Dropdown(
                    id="group_selector",
                    options=[
                        {"label": "Group 1", "value": "group1"},
                        {"label": "Group 2", "value": "group2"}
                    ],
                    value="group1",
                    clearable=False,
                    style={"width": "100%", "maxWidth": "600px", "margin": "0 auto"}
                ),
                html.P(
                    "This heatmap shows the monthly correlation between each stock and the COLCAP index since March 2024. "
                    "Red indicates a positive correlation, while blue shows a negative one. Use the dropdown to view different stock groups.",
                    style={"textAlign": "center", "maxWidth": "900px", "margin": "auto"}
                ),
                dcc.Graph(id="heatmap", style={"width": "100%", "maxWidth": "1200px", "margin": "auto"})
            ])
        ]),

        dcc.Tab(label="Historical Correlation Bar Chart", children=[
            html.Br(),
            html.P(
                "This bar chart displays the historical correlation between each stock and the COLCAP index, calculated using data from 2020 onward. "
                "A correlation close to 1 means the stock moves in sync with the index, while values closer to -1 indicate opposite movement.",
                style={"textAlign": "center", "maxWidth": "900px", "margin": "auto"}
            ),
            dcc.Graph(
                figure=px.bar(
                    df_corr,
                    x="Correlation",
                    y="Stock",
                    orientation="h",
                    title="📊 Historical Correlation with COLCAP since 2020",
                    color="Correlation",
                    color_continuous_scale="RdBu_r",
                    range_color=[-1, 1],
                    labels={"Correlation": "Correlation Coefficient", "Stock": "Stock"}
                ).update_layout(
                    yaxis=dict(autorange="reversed"),
                    height=1000,  # Increased from 800 to 1000
                    xaxis=dict(tickformat=".2f")
                ),
                style={"margin": "0 auto", "width": "90%", "height": "1000px"}  # Add fixed height here
            ),

                style={"margin": "0 auto", "width": "100%", "maxWidth": "1200px"}
            ),

            html.H3("Correlation Table", style={"textAlign": "center"}),
            html.Div([
                dash_table.DataTable(
                    id="historical_table",
                    columns=[
                        {"name": "Stock", "id": "Stock"},
                        {"name": "Correlation", "id": "Correlation"}
                    ],
                    data=df_corr.to_dict("records"),
                    style_cell={"textAlign": "center", "padding": "8px"},
                    style_header={"fontWeight": "bold", "backgroundColor": "#f8f8f8"},
                    style_table={"overflowX": "auto"},
                    style_data_conditional=[
                        {
                            "if": {"column_id": "Correlation"},
                            "backgroundColor": "#f0f8ff",
                        }
                    ],
                    page_size=20,
                    sort_action="native",
                    filter_action="native",
                )
            ], style={"width": "100%", "maxWidth": "1200px", "margin": "auto"}),
            html.Br(),
            html.Div([
                html.Label("Select format: "),
                dcc.Dropdown(
                    id="format_selector_hist",
                    options=[
                        {"label": "CSV", "value": "csv"},
                        {"label": "Excel", "value": "excel"},
                    ],
                    value="csv",
                    style={"width": "200px", "margin": "auto"}
                ),
                html.Br(),
                html.A("Download Historical Data", id="download_link_hist", href="/download/historical/csv", download="Historical_Correlation.csv", target="_blank", style={"display": "block", "textAlign": "center"})
            ], style={"textAlign": "center"})
        ]),

        dcc.Tab(label="Rolling Correlation with COLCAP", children=[
            html.Br(),
            html.P(
                "This section shows the rolling correlation between each stock and the COLCAP index over different time windows (e.g., 252 days ≈ 1 year). "
                "Rolling correlation helps track how relationships evolve over time.",
                style={"textAlign": "center", "maxWidth": "900px", "margin": "auto"}
            ),
            dcc.Dropdown(
                id="window_selector",
                options=[{"label": label, "value": label} for label in rolling_df.columns],
                value="252d",
                clearable=False,
                style={"width": "100%", "maxWidth": "600px", "margin": "0 auto"}
            ),
            dcc.Graph(id="bar_chart", style={"width": "100%", "maxWidth": "1200px", "margin": "auto"}),
            html.H3("Correlation Table", style={"textAlign": "center"}),
            html.Div(id="correlation_table", style={"width": "100%", "maxWidth": "1200px", "margin": "auto"}),
            html.Br(),
            html.Div([
                html.Label("Select format: "),
                dcc.Dropdown(
                    id="format_selector_roll",
                    options=[
                        {"label": "CSV", "value": "csv"},
                        {"label": "Excel", "value": "excel"},
                    ],
                    value="csv",
                    style={"width": "200px", "margin": "auto"}
                ),
                html.Br(),
                html.A("Download Rolling Data", id="download_link_roll", href="/download/rolling/csv", download="Rolling_Correlations.csv", target="_blank", style={"display": "block", "textAlign": "center"})
            ], style={"textAlign": "center"})
        ])
    ])
], style={"padding": "1rem"})


@app.callback(
    Output("heatmap", "figure"),
    Input("group_selector", "value")
)
def update_heatmap(selected_group):
    data = monthly_df[group1] if selected_group == "group1" else monthly_df[group2]
    title = f"\ud83d\udcc8 Monthly Correlation Heatmap ({selected_group.replace('group', 'Group ')})"
    return plot_heatmap(data, title)

@app.callback(
    [Output("bar_chart", "figure"), Output("correlation_table", "children")],
    Input("window_selector", "value")
)
def update_rolling_output(selected_window):
    corr_series = rolling_df[selected_window].dropna().sort_values(ascending=False)

    fig = px.bar(
    x=corr_series.index,
    y=corr_series.values,
    labels={"x": "Stock", "y": f"Correlation ({selected_window})"},
    title=f"Rolling Correlation with COLCAP ({selected_window})",
    color=corr_series.index,  # Make each stock have a unique color
    color_discrete_sequence=px.colors.qualitative.Safe  # Or Vibrant, Dark2, Set3, etc.
)


    fig.update_layout(xaxis_tickangle=-45, height=500)

    table = dash_table.DataTable(
    columns=[
        {"name": "Stock", "id": "Stock"},
        {"name": f"Correlation ({selected_window})", "id": "Correlation"}
    ],
        data=[{"Stock": stock, "Correlation": round(corr, 4)} for stock, corr in corr_series.items()],
        style_cell={"textAlign": "center", "padding": "8px"},
        style_header={"fontWeight": "bold", "backgroundColor": "#f8f8f8"},
        style_table={"overflowX": "auto"},
        style_data_conditional=[
            {
                "if": {"column_id": "Correlation"},
                "backgroundColor": "#f0f8ff",
            }
        ],
        page_size=20,
        sort_action="native",
        filter_action="native",
    )

    return fig, table

@app.callback(
    Output("download_link_hist", "href"),
    Input("format_selector_hist", "value")
)
def update_download_link_hist(format_value):
    return f"/download/historical/{format_value}"

@app.callback(
    Output("download_link_roll", "href"),
    Input("format_selector_roll", "value")
)
def update_download_link_roll(format_value):
    return f"/download/rolling/{format_value}"

@app.server.route("/download/<file_type>/<fmt>")
def download_file(file_type, fmt):
    if file_type == "historical":
        df = df_corr
    elif file_type == "rolling":
        df = rolling_df
    else:
        return Response("Invalid file type", status=400)

    if fmt == "csv":
        buffer = df.to_csv(index=False if file_type == "historical" else True)
        mimetype = "text/csv"
        filename = f"{file_type}_correlation.csv"
    # elif fmt == "excel":
    #     output = io.BytesIO()
    #     with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
    #         df.to_excel(writer, index=False if file_type == "historical" else True)
    #     buffer = output.getvalue()
    #     mimetype = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    #     filename = f"{file_type}_correlation.xlsx"
    else:
        return Response("Invalid format", status=400)

    # Correct the Content-Disposition header based on format
    return Response(
        buffer,
        mimetype=mimetype,
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )
# Run the server locally
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)