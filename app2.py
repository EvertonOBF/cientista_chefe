import pandas as pd
import numpy as np
import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
import plotly.express as px
import gerando_graficos as gg

from diagnostico_rodovia import layout_diagnostico, registrar_callbacks_diagnostico
from classificacao_segmentos_IRI import layout_diag_iri, registrar_callbacks_diagnostico_iri

# Carregando os dados
df_diag = pd.read_csv("dados_dash/diagnostico.csv")
df_fwd = pd.read_csv("dados_dash/fwd_tratado.csv")
df_iri = pd.read_csv("dados_dash/iri_tratado.csv")

# Estilo dos gráficos - Remove a barra de ferramentas e os tooltips
config_grafic = {"displayModeBar": False, "showTips": False}
main_config = {"margin" : {"t":0, "b":0, "l":10, "r":10}}

# Estilo dos cards
cor = "#f0f8ff" # Cor de fundo dos cards
tab_card = {"height": "100%", "padding": "0px"}
tab_card1 = {"height": "100%", "padding": "0px", "backgroundColor": cor}

# Estilos das caixas contendo os gráficos
tabs_styles = {
    'height': '20px'
}
tab_style = {
    'borderBottom': '1px solid #d6d6d6',
    'padding': '5px',
    'backgroundColor': cor,
    'borderLeft': '1px solid #d6d6d6',
    'borderRight': '1px solid #d6d6d6'
}

tab_selected_style = {
    'borderTop': '1px solid #000000',
    'borderLeft': '1px solid #000000',
    'borderRight': '1px solid #000000',
    'borderBottom': '1px solid #000000',
    'backgroundColor': "#d1e9ff" ,
    'padding': '5px'
}

# figuras dos cards
fig_rod_total = gg.gerar_card_1(df_iri)
fig_km_total = gg.gerar_card_2(df_diag)
fig_situacao_trechos = gg.gerar_card_3(df_iri)

lista_vias = ["All"] + df_fwd["VIA"].unique().tolist()
# Instanciando o dash
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.FLATLY], suppress_callback_exceptions=True)

# Tab de Diagnóstico geral
registrar_callbacks_diagnostico(app, df_fwd, df_iri, df_diag)

# Tab de Diagnóstico IRI
registrar_callbacks_diagnostico_iri(app, df_iri)


# Criando o layout do dash
app.layout = dbc.Container(children=[
    dbc.Row([

        # Coluna da esquerda - Menu de navegação
        dbc.Col([
            dbc.Row([
                dbc.Card([
                    dbc.CardBody([
                        
                        html.H5("Highway Monitoring System of Ceará", style={"textAlign": "center", "fontSize":"110%"}),
                        html.Hr(style={"marginBottom":"30px"}),
                        html.H6("Index:"),

                        dcc.RadioItems(["IRI (Profilometer)", "Deflection (FWD)"], 
                                       "Deflection (FWD)", id="index", 
                                       style={"marginBottom":"30px"}, 
                                       labelStyle={"display": "flex", "gap": "8px", "alignItems": "center"}),

                        html.H6("Highway:"),
                        dcc.Dropdown(lista_vias, lista_vias[0], id="rodovia", multi=False, style={"width": "200px", "font-size": "14px"})
                    ])
                ], style=tab_card1)
            ], className ='g-2 my-auto', style={"margin-top": "7px", "height":"96vh"})
        ], sm=2),
        
        # Coluna da direita - Gráficos
        dbc.Col([
            
            # Linha contendo os cards
            dbc.Row([
                
                # Card 1 - Total de rodovias monitoradas
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            dcc.Graph(figure=fig_rod_total, config=config_grafic)
                        ], style={"padding-bottom": "0px", "padding-top": "0px"})
                    ], style=tab_card1)
                ], sm=4),
                
                # Card 2 - Total de km monitorados
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            dcc.Graph(figure=fig_km_total, config=config_grafic)
                        ], style={"padding-bottom": "0px", "padding-top": "0px"})
                    ], style=tab_card1)
                ], sm=4),
                
                # Card 3 - Porcentagem de segmentos classificados como ruins
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            dcc.Graph(figure=fig_situacao_trechos, config=config_grafic)
                        ], style={"padding-bottom": "0px", "padding-top": "0px"})
                    ], style=tab_card1)
                ], sm=4)
            ], className ='g-2 my-auto', style={"margin-top": "7px"}),

            # Linha 2 - Coluna da direita
            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dcc.Tabs(id="tabs-with-props", value='tab-4', children=[
                            dcc.Tab(label=f'Highway Diagnostics', value='tab-4', style=tab_style, selected_style=tab_selected_style),
                            dcc.Tab(label='Pavement condition', value='tab-1', style=tab_style, selected_style=tab_selected_style),
                            dcc.Tab(label=f'Segments Classified (IRI)', value='tab-3', style=tab_style, selected_style=tab_selected_style),
                                
                            
                            ], colors={
                                "border": "white",
                                "primary": "gold",
                                "background": "cornsilk"
                            }),
                            html.Div(id='tabs-content-props-4')
                    ], style=tab_card)
                ])

            ], className ='g-2 my-auto', style={"margin-top": "7px"})
            

        ], sm=10)

    ], className ='g-2 my-auto', style={"margin-top": "7px"})
                            
], fluid=True, style={"height":"100vh"})

# Callbacks para atualizar gráficos e cards:

## Calbak dos gráficos contidos no tab 1, 2 e 3
@app.callback(
        Output('tabs-content-props-4', 'children'),
        [Input('tabs-with-props', 'value'),
         Input("index", "value")]
        )

def render_content(tab, index):
    
    if tab == 'tab-1':

        if ("IRI (Profilometer)" in index):
            df2 = df_iri.copy()
            color_discrete_map={'Excellent': 'green', 'Good': 'lightgreen','Fair': 'yellow',
                 'Poor': 'orange','Very Poor': 'red'}
            category_orders={"Condition": ['Excellent', 'Good', 'Fair', 'Poor', 'Very Poor']}

        elif ("Deflection (FWD)" in index):
            df2 = df_fwd.copy()
            color_discrete_map={'Acceptable': 'green','Unacceptable': 'red'}
            category_orders={"Condition": ['Acceptable', 'Unacceptable']}
        
        fig1 = gg.grafico_tab_1(df2, category_orders, color_discrete_map, index)
        
        return html.Div([
            html.P(
                "Percentage of road segments classified by structural condition based on IRI or Deflection criteria.",
                style={"marginBottom": "20px", "fontSize": "16px", "marginTop": "10px", "marginLeft": "15px"}
            ),

            dcc.Graph(figure=fig1, config=config_grafic)
        ])    

    elif tab == 'tab-3':
        return layout_diag_iri(df_iri)
    
    elif tab == 'tab-4':
       return layout_diagnostico(df_fwd, df_iri)

# Expondo o servidor Flask para o Render
server = app.server

if __name__ == "__main__":
    app.run_server(debug=True)