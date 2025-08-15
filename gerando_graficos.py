from altair import condition
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
import warnings
warnings.filterwarnings("ignore")

# Estilo dos gráficos - Remove a barra de ferramentas e os tooltips
config_grafic = {"displayModeBar": False, "showTips": False}
main_config = {"margin" : {"t":0, "b":0, "l":10, "r":10}}
cor =  "#f0f8ff"

# Estilo dos cards
tab_card = {"height": "100%", "padding": "0px"}
tam_font = 20

## Card Monitored Highways

# Card Total de rodovias monitoradas
def gerar_card_1(df_iri):
    df_iri = df_iri[df_iri["Condition"] != "No Data"]
    fig_rod_total = go.Figure()
    fig_rod_total.add_trace(go.Indicator(
        mode='number',
            title={"text": "Monitored Highways", "font":{"size":15, "color":"#000000"}},
        value = df_iri["VIA"].nunique(),
        number = {'suffix': '', 'font': {'size': tam_font, "color":"#000000"}},
    ))
    fig_rod_total.update_layout(main_config, height=64)
    fig_rod_total.update_layout({'margin':{'l':0, 'r':0 , 't':20, 'b':0}}, paper_bgcolor=cor, plot_bgcolor=cor)

    return fig_rod_total

# Card Total de km monitorados
def gerar_card_2(df_diag):
    df_diag = df_diag[df_diag["via"] != "All"]
    fig_km_total = go.Figure()
    fig_km_total.add_trace(go.Indicator(
        mode='number',
            title={"text": "Monitored Distance", "font":{"size":15, "color":"#000000"}},
        value=df_diag["extensão(km)"].sum()*2,
        number={'suffix': ' km', 'font': {'size': tam_font, "color":"#000000"}},
    ))
    fig_km_total.update_layout(main_config, height=64)
    fig_km_total.update_layout({'margin':{'l':0, 'r':0 , 't':20, 'b':0}}, paper_bgcolor=cor, plot_bgcolor=cor)
    return fig_km_total

# Card Porcentagem de segmentos ruins
def gerar_card_3(df_iri):
    valor_trechos_ruins = df_iri[df_iri["Condition"].isin(["Poor", "Very Poor"])].shape[0] / df_iri.shape[0] * 100
    fig_situacao_trechos = go.Figure()
    fig_situacao_trechos.add_trace(go.Indicator(
        mode='number',
            title={"text": "Poor Segments (IRI)", "font":{"size":15, "color":"#000000"}},
        value=round(valor_trechos_ruins,2),
        number={'suffix': ' %', 'font': {'size': tam_font, "color":"#000000"}},
    ))
    fig_situacao_trechos.update_layout(main_config, height=64)
    fig_situacao_trechos.update_layout({'margin':{'l':0, 'r':0 , 't':20, 'b':0}}, paper_bgcolor=cor, plot_bgcolor=cor)
    return fig_situacao_trechos

# Gráfico - Classificação das rodovias de acordo com o IRI ou FWD (Tab 1)

def grafico_tab_1(df2, category_orders, color_discrete_map, index):
    CA = ["CE-060", "CE-240", "CE-085", "CE-155", "CE-417", "CE-293"]

    condition = (df2.groupby("VIA")["Condition"].value_counts(normalize=True)*100).round(2).reset_index()
    condition.rename(columns={"proportion":"Proportion (%)"}, inplace=True)
    condition.sort_values(by=["Condition", "Proportion (%)"], ascending=False, inplace=True)

    #vias_com_asterisco = {
    #via: f"{via}*" if via not in CA else via
    #for via in condition['VIA'].unique()}

    # Aplica renomeação no DataFrame (sem alterar o original)
    #condition_plot = condition.copy()
    #condition_plot['VIA'] = condition_plot['VIA'].map(vias_com_asterisco)

    condition["Pavement type"] = np.where(condition["VIA"].isin(CA), "Asphalt concrete", "Surface treatment")

    fig = px.bar(condition, 
                x="VIA", y="Proportion (%)", 
                color="Condition",
                category_orders=category_orders,
                color_discrete_map=color_discrete_map,
                hover_name='VIA',
                hover_data={'Condition': True, 'Proportion (%)': True, 'VIA':False, "Pavement type":True}, template="simple_white", height=500)

    fig.update_layout(
        legend=dict(title=index, orientation="h", y=1, yanchor="bottom", x=0.5, xanchor="center"),
        xaxis = dict(title=""), bargap=0.3)

    fig.update_layout({'margin':{'t':50, 'b':0}},
                      #annotations=[
        #dict(text="*  Surface treatment", xref="paper",
        #    yref="paper", x=0.0, y=1.1, showarrow=False, font=dict(size=14), align="left")]
                      )
    
    return fig

