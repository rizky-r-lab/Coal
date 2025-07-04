from dash import Dash, html, dcc, callback, Output, Input
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.express as px
from datetime import datetime 
import numpy as np

import pandas as pd

buses = pd.read_csv('tes/buses.csv',index_col=0)
stores = pd.read_csv('tes/stores.csv',index_col=0)
loads = pd.read_csv('tes/loads.csv',index_col=0)
loads_p_set = pd.read_csv('tes/loads-p_set.csv', index_col=0)
links = pd.read_csv('tes/links.csv',index_col=0)
links_p0 = pd.read_csv('tes/links-p0.csv',index_col=0)
snapshot = pd.read_csv('tes/snapshots.csv',index_col=0)


app = Dash()

demand = loads.index.values.tolist()
demand.insert(0,'All')

source = stores.index.values.tolist()
source.insert(0,'All')

mt = pd.to_datetime(snapshot['snapshot'])
loads_p_set.index = mt
links_p0.index = mt
dict_mt = {i:val for i,val in enumerate(mt)}
dict_name = {i: val.strftime("%b %y") for i,val in enumerate(mt)}

app.layout = [
    html.H1(children='Jalur pengiriman Batubara', style={'textAlign':'center'}),
    html.Div([html.Div([dcc.Dropdown(demand, 'All', id='demand')], style={'width': '48%', 'display': 'inline-block'}),
              html.Div([dcc.Dropdown(source, 'All', id='source')], style={'width': '48%', 'display': 'inline-block'})
            ]),
    html.Div([dcc.Slider(0, len(mt),marks=dict_name,step=None, value=0, id = 'date_val')]),
    html.Div([dcc.Graph(id='graph-content1')]),
    html.Div([dcc.Graph(id='graph-content2')])
]

@callback(
    Output('graph-content1', 'figure',allow_duplicate=True),
    Input('demand','value'),
    Input('source','value'),
    Input('date_val','value'),
    prevent_initial_call=True# jika 3 input bagaimana?
)
def update_graph(demand, source, date_val):
    date_val = dict_mt[date_val]
    if source == 'All':
        dff_source = stores
        dff_branch = links
    else:
        dff_source = stores.loc[source,]
        dff_branch = links[links['bus0']==stores.loc[source,'bus']]
    
    if demand == 'All':
        dff_load = loads
        #dff_branch = dff_branch
    else:
        dff_load = loads.loc[demand,]
        dff_branch = dff_branch[dff_branch['bus1']==loads.loc[demand,'bus']]
    
    #print(dff_branch)
    #return dff_source,dff_load,dff_branch
    df_source_val = links_p0.groupby(links['bus0'].get(links_p0.columns),axis=1).sum()#.loc[:,links['bus0'].unique()].transpose()
    
    fig = make_subplots(rows=1,cols=1,
                        specs=[[{"type": "scattermap"}]])
    
    #add trace of source
    
    if source == 'All':
        for i in dff_source.index:
            fig.add_trace(go.Scattermap(lon=[buses.loc[dff_source.loc[i,'bus'],'x'],], lat=[buses.loc[dff_source.loc[i,'bus'],'y'],], name=i,
                                    mode='markers', marker=go.scattermap.Marker(size=14, color= 'red'), 
                                    #customdata = [[i, dff_source.loc[i,'caloric_value'], df_source_val.loc[date_val,dff_source.loc[i,'bus']]]],
                                    #hovertemplate = "Source : %{customdata[0]} \nCaloric Value :%{customdata[1]} kcal/kg\nProduction = %{customdata[2]:.2f} ribu Ton"
                                    ),
                        row=1,col=1
                        )
            #fig.update_traces(customdata = [i, dff_source.loc[i,'caloric_value']])#, df_source_val.loc[date_val,dff_source.loc[i,'bus']]])
    else:
        fig.add_trace(go.Scattermap(lon=[buses.loc[dff_source.loc['bus'],'x'],], lat=[buses.loc[dff_source.loc['bus'],'y'],], name=source,
                                    mode='markers', marker=go.scattermap.Marker(size=14, color= 'red'), 
                                    #customdata = [[source, dff_source.loc['caloric_value'], df_source_val.loc[date_val,dff_source.loc['bus']]]],
                                    #hovertemplate = "Source : %{customdata[0]} \nCaloric Value :%{customdata[1]} kcal/kg,\nProduction = %{customdata[2]:.2f} ribu Ton"
                                    ),
                        row=1,col=1
                        )
        #fig.update_traces(customdata = [source, dff_source.loc['caloric_value']])#, df_source_val.loc[date_val,dff_source.loc['bus']]])
    
    #add trace of source
    if demand == 'All':
        for i in dff_load.index:
            fig.add_trace(go.Scattermap(lon=[buses.loc[dff_load.loc[i,'bus'],'x'],], lat=[buses.loc[dff_load.loc[i,'bus'],'y'],], name=i,
                                    mode='markers', marker=go.scattermap.Marker(size=14, color= 'green'), 
                                    #customdata = [[i, 
                                    #            dff_load.loc[i,'caloric_value'], 
                                    #            loads_t['p_set'].loc[date_val,i]
                                    #            ]],
                                    #hovertemplate = "PLTU : %{customdata[0]}, Target Caloric Value : %{customdata[1]} kcal/kg, Kebutuhan = %{customdata[2]:.2f} ribu Ton"
                                    ),
                        row=1,col=1
                        )
    else:
        fig.add_trace(go.Scattermap(lon=[buses.loc[dff_load.loc['bus'],'x'],], lat=[buses.loc[dff_load.loc['bus'],'y'],], name=demand,
                                    mode='markers', marker=go.scattermap.Marker(size=14, color= 'green'),
                                    #customdata = [[demand, 
                                    #            dff_load.loc['caloric_value'], 
                                    #            loads_t['p_set'].loc[date_val,demand]
                                    #            ]],
                                    #hovertemplate = "PLTU : %{customdata[0]}, Target Caloric Value : %{customdata[1]} kcal/kg, Kebutuhan = %{customdata[2]:.2f} ribu Ton"
                                    ),
                        row=1,col=1
                        )
    
    #add trace of links
    #if source == 'All' or demand == 'All':
    
    for i in dff_branch.index:
        sumber = stores[stores['bus']==dff_branch.loc[i,'bus0']].index[0]
        ld = loads[loads['bus']==dff_branch.loc[i,'bus1']].index[0]
        fig.add_trace(go.Scattermap(lon=[buses.loc[dff_branch.loc[i,'bus0'],'x'],buses.loc[dff_branch.loc[i,'bus1'],'x']],
                                    lat=[buses.loc[dff_branch.loc[i,'bus0'],'y'],buses.loc[dff_branch.loc[i,'bus1'],'y']], name=i,
                                mode='lines', line=go.scattermap.Line(width=links_p0.loc[date_val,i]/100+1, color= 'black' if links_p0.loc[date_val,i]/100>0 else 'yellow'),
                                customdata = [
                                    [sumber,stores.loc[sumber,'caloric_value'],df_source_val.loc[date_val,dff_branch.loc[i,'bus0']], links_p0.loc[date_val,i]],
                                    [ld, loads.loc[ld,'caloric_value'], loads_p_set.loc[date_val,ld],links_p0.loc[date_val,i]]          
                                              ],
                                hovertemplate = "%{customdata[0]} : %{customdata[1]}kcal/kg, Prod/Demadn = %{customdata[2]:.2f}ribu Ton, send/rec:%{customdata[3]:.2f} ribu Ton"
                                ),
                    row=1,col=1
                    )
    
    fig.update_layout(map=dict(
        bearing=0,
        center=dict(
            lat=np.mean(buses['y']),
            lon=np.mean(buses['x'])
        ),
        zoom = 3)
    )
    return fig
@callback(
    Output('graph-content2', 'figure',allow_duplicate=True),
    Input('demand','value'),
    Input('source','value'),
    #Input('date_val','value'),
    prevent_initial_call=True# jika 3 input bagaimana?
)
def update_graph2(demand, source):
    fig = make_subplots(rows=1,cols=1)
    dff_val = pd.DataFrame()
    for i in links_p0.index:
        for col in links_p0.columns:
            data = {'Waktu':[i.strftime("%b %y"),],
                    'Source' : [links.loc[col,'bus0'],],
                    'Load' : [links.loc[col,'bus1'],],
                    'Value' : [links_p0.loc[i,col],],
            }
            dff_val=pd.concat([dff_val,pd.DataFrame(data)])
    if source == 'All' and demand == 'All':
        pass
    elif source != 'All' and demand == 'All' :
       fig=px.bar(dff_val[dff_val['Source']==stores.loc[source,'bus']],x='Waktu',y='Value',color='Load', title=f'Produksi {source}')
        #fig.update_layout(Title)
    elif source == 'All' and demand != 'All' :
        fig=px.bar(dff_val[dff_val['Load']==loads.loc[demand,'bus']],x='Waktu',y='Value',color='Source',title=f'{demand}')
    else:
        dff = dff_val[(dff_val['Source']==stores.loc[source,'bus'])&(dff_val['Load']==loads.loc[demand,'bus'])]
        fig=px.bar(dff,x='Waktu',y='Value', title=f'{source} - {demand}')#, color = dff['Load']))
        
    
    
    return fig

if __name__ == '__main__':
    app.run(debug=True)