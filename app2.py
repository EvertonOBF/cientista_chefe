import pandas as pd
import numpy as np
import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
import plotly.express as px

# =====================
# Funções internas
# =====================
import gerando_graficos as gg
from diagnostico_rodovia import layout_diagnostico, registrar_callbacks_diagnostico 
from classificacao_segmentos_IRI import layout_diag_iri

# =====================
# Carregando os dados
# =====================
df_diag = pd.read_csv("dados_dash/diagnostico.csv")
df_fwd = pd.read_csv("dados_dash/fwd_tratado.csv")
df_iri = pd.read_csv("dados_dash/iri_tratado.csv")

# =====================
# Estilos / Configs
# =====================
config_grafic = {"displayModeBar": False, "showTips": False}
main_config = {"margin": {"t": 0, "b": 0, "l": 10, "r": 10}}

cor = "#f0f8ff"  # Cor de fundo dos cards
tab_card = {"height": "100%", "padding": "0px"}
tab_card1 = {"height": "100%", "padding": "0px", "backgroundColor": cor}

tabs_styles = {"height": "20px"}
tab_style = {
    "borderBottom": "1px solid #d6d6d6",
    "borderTop": "1px solid #d6d6d6",
    "padding": "5px",
    "backgroundColor": cor,
    "borderLeft": "1px solid #d6d6d6",
    "borderRight": "1px solid #d6d6d6",
}
tab_selected_style = {
    "borderTop": "1px solid #000000",
    "borderLeft": "1px solid #000000",
    "borderRight": "1px solid #000000",
    "borderBottom": "1px solid #000000",
    "backgroundColor": "#d1e9ff",
    "padding": "5px",
}

# =====================
# Figuras dos cards (geradas 1x)
# =====================
fig_rod_total = gg.gerar_card_1(df_iri)
fig_km_total = gg.gerar_card_2(df_diag)
fig_situacao_trechos = gg.gerar_card_3(df_iri)

lista_vias = ["All"] + df_fwd["VIA"].unique().tolist()

# =====================
# App Dash
# =====================
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.FLATLY], suppress_callback_exceptions=True)

# Callbacks do diagnóstico geral (tab 4)
registrar_callbacks_diagnostico(app, df_fwd, df_iri, df_diag)

# =====================
# Layouts prontos das abas
# =====================
tab1_layout = html.Div([
    html.P(
        "Percentage of road segments classified by structural condition based on IRI or Deflection criteria.",
        style={"marginBottom": "20px", "fontSize": "16px", "marginTop": "10px", "marginLeft": "15px"},
    ),
    dcc.Graph(id="fig-tab1", config=config_grafic),
])

# Segments Classified (IRI) agora estático (figura criada dentro do módulo)
tab3_layout = layout_diag_iri(df_iri)

# Highway Diagnostics (mantém callbacks internos do módulo correspondente)
tab4_layout = layout_diagnostico(df_fwd, df_iri)

# =====================
# Layout principal
# =====================
app.layout = dbc.Container(children=[
    dbc.Row([
        # Coluna esquerda - filtros
        dbc.Col([
            dbc.Row([
                dbc.Card([
                    dbc.CardBody([
                        html.H5("Highway Monitoring System of Ceará", style={"textAlign": "center", "fontSize": "110%"}),
                        html.Hr(style={"marginBottom": "30px"}),

                        html.H6("Highway:"),
                        dcc.Dropdown(
                            lista_vias, lista_vias[0], id="rodovia", multi=False,
                            style={"width": "200px", "font-size": "14px", "marginBottom": "30px"},
                        ),

                        html.H6("Parameters:"),
                        dcc.RadioItems(
                            ["IRI (Profilometer)", "Deflection (FWD)"],
                            "Deflection (FWD)",
                            id="index",
                            style={"marginBottom": "30px"},
                            labelStyle={"display": "flex", "gap": "8px", "alignItems": "center"},
                        ),
                    ])
                ], style=tab_card1)
            ], className='g-1 my-auto', style={"margin-top": "7px", "height": "98.2vh"})
        ], sm=2),

        # Coluna direita - conteúdo
        dbc.Col([
            # Linha dos cards
            dbc.Row([
                dbc.Col([dbc.Card([dbc.CardBody([dcc.Graph(figure=fig_rod_total, config=config_grafic)], style={"padding-bottom": "0px", "padding-top": "0px"})], style=tab_card1)], sm=4),
                dbc.Col([dbc.Card([dbc.CardBody([dcc.Graph(figure=fig_km_total,  config=config_grafic)], style={"padding-bottom": "0px", "padding-top": "0px"})], style=tab_card1)], sm=4),
                dbc.Col([dbc.Card([dbc.CardBody([dcc.Graph(figure=fig_situacao_trechos, config=config_grafic)], style={"padding-bottom": "0px", "padding-top": "0px"})], style=tab_card1)], sm=4),
            ], className='g-1 my-auto', style={"margin-top": "0px"}),

            # Linha com as abas
            dbc.Row([
                dbc.Col([
                    dcc.Tabs(
                        id="tabs-with-props", value="tab-4",
                        children=[
                            dcc.Tab(label="Highway Diagnostics", value="tab-4", style=tab_style, selected_style=tab_selected_style),
                            dcc.Tab(label="Pavement Condition", value="tab-1", style=tab_style, selected_style=tab_selected_style),
                            dcc.Tab(label="Segments Classified (IRI)", value="tab-3", style=tab_style, selected_style=tab_selected_style),
                        ],
                        colors={"border": "white", "primary": "gold", "background": "cornsilk"},
                    ),
                    html.Div(id="tabs-content-props-4"),
                ])
            ], className='g-1 my-auto', style={"margin-top": "7px", "height": "89vh"}),
        ], sm=10),
    ], className='g-2 my-auto', style={"margin-top": "-20px"})
], fluid=True, style={"height": "100vh", "margin-top": "-8px"})

# =====================
# Callbacks
# =====================

# A) Callback de abas: apenas alterna entre layouts prontos
@app.callback(
    Output("tabs-content-props-4", "children"),
    Input("tabs-with-props", "value"),
)
def render_content(tab):
    if tab == "tab-1":
        return tab1_layout
    elif tab == "tab-3":
        return tab3_layout
    elif tab == "tab-4":
        return tab4_layout
    return tab4_layout

# B) Pavement Condition: atualiza a figura SOMENTE quando o RadioItems muda
@app.callback(
    Output("fig-tab1", "figure"),
    Input("index", "value"),
)
def update_tab1_figure(index):
    if "IRI (Profilometer)" in index:
        df2 = df_iri.copy()
        color_discrete_map = {
            "Excellent": "green",
            "Good": "lightgreen",
            "Fair": "yellow",
            "Poor": "orange",
            "Very Poor": "red",
        }
        category_orders = {"Condition": ["Excellent", "Good", "Fair", "Poor", "Very Poor"]}
    else:
        df2 = df_fwd.copy()
        color_discrete_map = {"Acceptable": "green", "Unacceptable": "red"}
        category_orders = {"Condition": ["Acceptable", "Unacceptable"]}

    fig1 = gg.grafico_tab_1(df2, category_orders, color_discrete_map, index)
    return fig1

# =====================
# Expondo o servidor Flask para o Render
# =====================
server = app.server

if __name__ == "__main__":
    app.run_server(debug=True)
