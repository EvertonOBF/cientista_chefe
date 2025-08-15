import dash
from dash import dcc, html, Input, Output
import dash_bootstrap_components as dbc
import plotly.express as px
import pandas as pd

# Estilo padronizado usado nos outros gráficos
main_config = {"margin": {"t": 10, "b": 0, "l": 10, "r": 10}}
cor = "#f0f8ff"
tab_card1 = {"height": "100%", "padding": "0px", "margin-top":"5px", "margin-left":"1px"}

def layout_diagnostico(df_fwd, df_iri):
    return dbc.Container([

        dbc.Row([

            # Primeira Coluna (Condições da Rodovia, Grpaficos de barra (FWD e IRI)
            dbc.Col([

                # Resumo da rodovia
                dbc.Row([
                    dbc.Card([
                        dbc.CardBody([
                            html.Div(id="resumo-via")
                        ])
                    ])
                ], className='g-0 my-auto', style={"margin-top": "0px"}),
                
                # Gráfico de Barras - Condição FWD
                dbc.Row([
                    dbc.Card([
                        dbc.CardBody([
                            
                            html.P("Condition (FWD)",
                            style={"marginBottom": "0px", "fontSize": "14px", "marginTop": "0px", "marginLeft": "15px"}),
                            dcc.Graph(id='grafico-condicao-fwd', config={"displayModeBar": False})#, style={"height": "120px"})

                        ])
                
                    ], style=tab_card1)
                
                ], className='g-0 my-auto', style={"margin-top": "0px"}),

                # Gráfico de Barras - Condição IRI
                dbc.Row([
                    dbc.Card([
                        dbc.CardBody([
                            html.P("Condition (IRI)",
                            style={"marginBottom": "0px", "fontSize": "14px", "marginTop": "0px", "marginLeft": "15px"}),
                            dcc.Graph(id='grafico-condicao-iri', config={"displayModeBar": False})#, style={"height": "120px"})
                        ])

                    ], style=tab_card1)
                
                ], className='g-0 my-auto', style={"margin-top": "0px"})
            
            ], md=5),

            # Segunda Coluna (Mapa)
            dbc.Col([
                dbc.Row([
                    dbc.Col([
                        dbc.Card([
                            html.Iframe(id="iframe-mapa", style={"width": "100%", "height": "550px", "border": "none"})
                        ])
                    ])

                ], className='g-0 my-auto', style={"margin-top": "5px"})
            
            ], md=7)
            
        ], className='g-2 my-auto', style={"margin-top": "5px"})


    ], fluid=True, style={"height":"81vh"})

def registrar_callbacks_diagnostico(app, fwd_df, iri_df, df_diag):

    @app.callback(
        Output('resumo-via', 'children'),
        Output('grafico-condicao-fwd', 'figure'),
        Output('grafico-condicao-iri', 'figure'),
        Output('iframe-mapa', 'src'),
        Input('rodovia', 'value'),
        Input("index", "value")
    )
    def atualizar_diagnostico(via, index):
        if not via:
            return dash.no_update, dash.no_update, dash.no_update, dash.no_update

        if via == "All":
            fwd = fwd_df.copy()
            iri = iri_df.copy()

        else:
            fwd = fwd_df[fwd_df['VIA'] == via]
            iri = iri_df[iri_df['VIA'] == via]
        
        diag = df_diag[df_diag['via'] == via]

        data = diag['data'].values[0]
        extension = diag['extensão(km)'].values[0]
        pavimento = diag['pavimentação'].values[0]
        fator = diag['fator_adimissão'].values[0]

        #total_fwd = len(fwd)
        #total_iri = len(iri)
        fwd_crit = (fwd['Condition'] == 'Unacceptable').mean() * 100
        iri_crit = ((iri['Condition'] == 'Very Poor') | (iri['Condition'] == 'Poor')).mean() * 100
        
        # Resumo da condição da rodovia
        resumo = html.Div([
                 html.H5(f"Highway: {via}", style={"marginTop": "0px", "marginBottom": "5px", "fontSize": "18px", "fontWeight": "bold"}),
                 html.Hr(style={"marginTop": "5px", "marginBottom": "5px"}),

                html.Ul([
                    html.Li(f'Study period: {data}'),
                    html.Li(f"Segment length: {extension} km"),
                    html.Li(f"Pavement type: {pavimento}"),
                    html.Li(f"Admission Factor (FWD): {fator} × 10⁻² mm"),
                    
                    #html.Li(f"Total segments evaluated (FWD): {total_fwd}"),
                    #html.Li(f"Total segments evaluated (IRI): {total_iri}"),
                    html.Li(f"FWD - % of segments classified as Unacceptable: {fwd_crit:.1f}%"),
                    html.Li(f"IRI - % of segments classified as Poor or Very Poor: {iri_crit:.1f}%"),
                ], style={"paddingLeft": "30px", "marginBottom": "0", "marginTop": "0", "fontSize": "15px"})
            ])

        # Gráfico de barras condição da rodovia - FWD
        color_discrete_map={'Acceptable': 'green','Unacceptable': 'red'}
        category_orders={"Condition": ['Acceptable', 'Unacceptable']}
        
        fwd_counts = fwd['Condition'].value_counts(normalize=True).mul(100).reset_index()
        fwd_counts.columns = ['ConditionLabel', 'proportion']
        fig_fwd = px.bar(
            fwd_counts,
            color='ConditionLabel',
            color_discrete_map=color_discrete_map,
            category_orders=category_orders,  
            x='ConditionLabel', y='proportion',
            labels={'ConditionLabel': 'Condition', 'proportion': '%'},
            template="simple_white"
        )
        
        fig_fwd.update_traces(
            hovertemplate='%{x}<br>%{y:.1f}%<extra></extra>'
        )

        fig_fwd.update_layout({'margin':{'t':10, 'b':5}})
        fig_fwd.update_layout(
            showlegend=False,
            height=110,#238, 
            bargap=0.4,
            xaxis = dict(title=None))

        # Gráfico de barras condição da rodovia - IRI
        color_discrete_map={'Excellent': 'green', 'Good': 'lightgreen','Fair': 'yellow',
                 'Poor': 'orange','Very Poor': 'red'}
        category_orders={"Condition": ['Excellent', 'Good', 'Fair', 'Poor', 'Very Poor']}

        iri_counts = (
            iri['Condition']
            .value_counts(normalize=True)
            .mul(100)
            .reindex(['Excellent', 'Good', 'Fair', 'Poor', 'Very Poor']) 
            .reset_index()
        )
        
        iri_counts.columns = ['ConditionLabel', 'proportion']
        fig_iri = px.bar(
            iri_counts,
            x='ConditionLabel', y='proportion',
            labels={'ConditionLabel': 'Condition', 'proportion': '%'},
            color='ConditionLabel',
            template="simple_white",
            category_orders=category_orders,
            color_discrete_map=color_discrete_map,
        )
        
        fig_iri.update_traces(
            hovertemplate='%{x}<br>%{y:.1f}%<extra></extra>'
        )

        fig_iri.update_layout({'margin':{'t':10, 'b':5}})
        fig_iri.update_layout(
            showlegend=False,
            height=118,#238, 
            bargap=0.4, 
            xaxis=dict(title=None))
        
        # mapa
        # if  ("Profilometer (IRI)" in index):
        #     if via == "CE-155 - (II)":
        #         src_mapa = "/assets/mapa_ce_155 - (II)_iri.html"
        #     else:
        #         src_mapa = f"/assets/mapa_ce_{via.split('-')[1]}_iri.html"
        
        # else:
        #     if via == "CE-155 - (II)":
        #         src_mapa = "/assets/mapa_ce_155_II.html"
        #     else:
        #         src_mapa = f"/assets/mapa_ce_{via.split('-')[1]}.html"

        if via == "All":
            src_mapa = "/assets/mapa_ce_all.html"  # ou use um mapa genérico
        
        else:
            if  ("IRI (Profilometer)" in index):
                if via == "CE-155 - (II)":
                    src_mapa = "/assets/mapa_ce_155 - (II)_iri.html"
                else:
                    src_mapa = f"/assets/mapa_ce_{via.split('-')[1].strip()}_iri.html"
            else:
                if via == "CE-155 - (II)":
                    src_mapa = "/assets/mapa_ce_155_II.html"
                else:
                    src_mapa = f"/assets/mapa_ce_{via.split('-')[1].strip()}.html"

        return resumo, fig_fwd, fig_iri, src_mapa