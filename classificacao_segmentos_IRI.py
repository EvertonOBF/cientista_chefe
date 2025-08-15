from dash import dcc, html
import dash_bootstrap_components as dbc
import plotly.express as px
import pandas as pd

# Estilo padronizado usado nos outros gráficos (mantido)
main_config = {"margin": {"t": 40, "b": 0, "l": 10, "r": 10}}
cor = "#f0f8ff"
tab_card1 = {"height": "100%", "padding": "0px"}

def _build_iri_static_figure(df_iri: pd.DataFrame):
    """
    Reproduz exatamente o gráfico anterior, mas gera UMA VEZ (sem callback).
    """
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

    # Coluna de padrão (strings)
    top_via["pattern"] = top_via["VIA"].apply(lambda x: "Asphalt concrete" if x in CA else "Surface treatment")

    # === FIGURA (mantidos cor, padrões, margens, alturas etc.) ===
    fig = px.bar(
        top_via,
        x="VIA",
        y="Proportion (%)",
        color="pattern",                 # cor fixa por padrão
        pattern_shape="pattern",
        pattern_shape_sequence=["x", ""],  # normal = "", hachurado = "x" (mantido)
        category_orders={"VIA": top_via["VIA"].tolist()},
        text="Proportion (%)",
        template="simple_white",
        color_discrete_sequence=["#1f77b4"],
        height=500,
        hover_data={"VIA": False, "pattern": False, "Proportion (%)": False},
    )

    # Layout (mantido)
    fig.update_layout(
        xaxis=dict(title=""),
        bargap=0.4,
        margin={"t": 30, "b": 0, 'l':120},
        legend=dict(
            title_text="",
            # orientation='h',  # (deixado como antes, comentado)
            yanchor="bottom",
            y=0.9,
            xanchor="center",
            x=0.8,
            font=dict(size=14),
        ),
    )

    # Traces (mantidos)
    fig.update_traces(texttemplate="%{text:.1f}%", textposition="outside")
    fig.update_traces(
        hovertemplate="<b>%{x}</b><br>Proportion: %{y:.1f}%<extra></extra>",
        customdata=top_via[["pattern"]].values,
    )

    return fig

def layout_diag_iri(df_iri: pd.DataFrame):
    """
    Layout da aba IRI: devolve um Graph já com a figure estática.
    Nada de callback aqui — a figura é criada 1x na montagem da aba.
    """
    iri_fig = _build_iri_static_figure(df_iri)
    return dbc.Container([
        dbc.Row([
            dbc.Col([
                html.P(
                    "Proportion of segments rated as poor or very poor based on the IRI (IRI ≥ 3.5 m/km).",
                    style={"marginBottom": "20px", "fontSize": "16px", "marginTop": "10px", "marginLeft": "15px"},
                ),
                dcc.Graph(id="grafico-condicao-iri2", figure=iri_fig, config={"displayModeBar": False}),
            ], style={"height": "550px"})
        ], className="g-2 my-auto", style={"margin-top": "7px"})
    ], fluid=True, style={"height": "81vh"})
