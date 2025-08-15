#import dash
from dash import dcc, html, Input, Output
import dash_bootstrap_components as dbc
import plotly.express as px
import pandas as pd

# Estilo padronizado usado nos outros gráficos
main_config = {"margin": {"t": 40, "b": 0, "l": 10, "r": 10}}
cor = "#f0f8ff"
tab_card1 = {"height": "100%", "padding": "0px"}

def layout_diag_iri(df_iri):

    return dbc.Container([

        dbc.Row([
            dbc.Col([

                html.P(
                "Proportion of segments rated as poor or very poor based on the IRI (IRI ≥ 3.5 m/km).",
                style={"marginBottom": "20px", "fontSize": "16px", "marginTop": "10px", "marginLeft": "15px"}),

                # Gráfico de barras - Percentual de segmentos classificados como ruins ou péssimos (IRI)
                dcc.Graph(id='grafico-condicao-iri2', config={"displayModeBar": False})
            ], style={"height": "600px"})

        ], className='g-2 my-auto', style={"margin-top": "7px"})

    ], fluid=True, style={"height":"81vh"})

def registrar_callbacks_diagnostico_iri(app, df_iri):
    
    @app.callback(
        Output('grafico-condicao-iri2', 'figure'),
        Input('grafico-condicao-iri2', 'id')
    )

    def update_grafico_condicao_iri(_):
        # Calcula proporções por condição
        condition = df_iri.groupby("VIA")["Condition"].value_counts(normalize=True).reset_index()
        condition["proportion"] = (condition["proportion"] * 100).round(1)
        condition.rename(columns={"proportion": "Proportion (%)"}, inplace=True)

        # Lista de vias que NÃO terão hachura
        CA = ["CE-060", "CE-240", "CE-085", "CE-155", "CE-417", "CE-293"]

        # Agrupa somando apenas Poor e Very Poor
        top_via = condition[condition["Condition"].isin(["Poor", "Very Poor"])]
        top_via = top_via.groupby("VIA")["Proportion (%)"].sum().reset_index()
        top_via = top_via.sort_values("Proportion (%)", ascending=False)

        # Cria coluna de padrão com strings (sem None!)
        top_via["pattern"] = top_via["VIA"].apply(lambda x: "Asphalt concrete" if x in CA else "Surface treatment")

        # Cria gráfico
        fig = px.bar(top_via,
                    x="VIA", 
                    y="Proportion (%)",
                    color="pattern",  # cor fixa
                    pattern_shape="pattern",
                    pattern_shape_sequence=["x", ""],  # normal = "", hachurado = "x"
                    category_orders={"VIA": top_via["VIA"].tolist()},
                    text="Proportion (%)", 
                    template="simple_white",
                    color_discrete_sequence=["#1f77b4"],
                    height=450,
                    hover_data={"VIA": False, "pattern": False, "Proportion (%)": False})

        # Layout
        fig.update_layout(
            xaxis=dict(title=""),
            bargap=0.4,
            margin={'t': 30, 'b': 0},
            legend=dict(
                title_text="",
                #orientation='h',
                yanchor='bottom',
                y=0.9,
                xanchor='center',
                x=0.8,
                font=dict(size=14)
            )
        )

        fig.update_traces(texttemplate="%{text:.1f}%", textposition="outside")
        fig.update_traces(
        hovertemplate="<b>%{x}</b><br>" +  # VIA
                    "Proportion: %{y:.1f}%<extra></extra>",  # Proporção
        customdata=top_via[["pattern"]].values
        )

        return fig
