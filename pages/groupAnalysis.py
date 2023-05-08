import dash
import json
from dash import dcc, html, Input, Output
from server import app
import plotly.express as px
import pandas as pd
import plotly.graph_objects as go
import os

#read all of csv files starts with given prefix of individual person
def read_data_with_person_entity(p_name, e_name):
    prefixed = [filename for filename in os.listdir(p_name+'/') if filename.startswith(e_name+'-')]
    df = pd.DataFrame()
    for filename in prefixed:
        temp = pd.read_csv(p_name + '/' + filename)
        df = df.append(temp)
    return df

#for testing read PhysicalActivityTransitionEntity of P0701 and processing data
PATE_p0701_df = read_data_with_person_entity('data/P0701', 'PhysicalActivityTransitionEntity')
PATE_p0701_df['datetime'] = pd.to_datetime(PATE_p0701_df['timestamp'], unit = 'ms')
PATE_p0701_df = PATE_p0701_df.drop_duplicates()
PATE_p0701_df['timedelta'] = PATE_p0701_df['datetime'].diff()
PATE_p0701_df = PATE_p0701_df.loc[PATE_p0701_df['transitionType'].str.startswith('EXIT')]
mov_stats = PATE_p0701_df[['transitionType', 'timedelta']].groupby('transitionType').sum()
mov_stats.index = mov_stats.index.str.replace(r'EXIT_','')
mov_stats = pd.concat([mov_stats, mov_stats['timedelta'].dt.components], axis = 1)

#fig = px.pie(mov_stats, values = 'timedelta', names = mov_stats.index, hole = .9)
fig = go.Figure(data=[go.Pie(labels=mov_stats.index,
                             values=mov_stats['timedelta'], hole = .9)])
fig.update_traces(hoverinfo='label+percent+text', text = (mov_stats['days'] * 24 + mov_stats['hours']).astype(str) + 'h ' + mov_stats['minutes'].astype(str) + 'm ' + mov_stats['seconds'].astype(str) + 's', textinfo = 'label+text',
                  marker=dict(line=dict(color='#000000', width=2)))
fig.update_layout(width = 400, height = 400, legend = {'xanchor':'center', 'yanchor':'middle', 'y':0.5, 'x':0.5})

#for testing tead AppUsageEventEntity of P0701 and processing data
AUEE_P0701_df = read_data_with_person_entity('data/P0701', 'AppUsageEventEntity')
AUEE_P0701_df = AUEE_P0701_df.groupby('packageName').apply(lambda x : x.fillna(x.mode().iloc[0])).reset_index(drop=True)
AUEE_P0701_df['datetime'] = pd.to_datetime(AUEE_P0701_df['timestamp'], unit = 'ms')
AUEE_P0701_df['name'].fillna(AUEE_P0701_df['packageName'], inplace= True)
AUEE_P0701_df = AUEE_P0701_df[(AUEE_P0701_df['type'] == 'MOVE_TO_FOREGROUND')|(AUEE_P0701_df['type'] == 'MOVE_TO_BACKGROUND')]
AUEE_P0701_df.drop_duplicates(inplace = True)
AUEE_P0701_df.sort_values('datetime',inplace=True)

app_usage_stats = AUEE_P0701_df.groupby('name').apply(lambda x: (x.loc[x['type'] == 'MOVE_TO_BACKGROUND']['datetime'].values - x.loc[x['type'] == 'MOVE_TO_FOREGROUND']['datetime'].values).sum())
app_usage_stats.name = 'duration'
app_usage_stats = pd.concat([app_usage_stats, app_usage_stats.dt.components], axis = 1)

fig2 = go.Figure(data=[go.Pie(labels=app_usage_stats.index,
                             values=app_usage_stats['duration'], hole = .9)])
fig2.update_traces(hoverinfo='label+percent+text', text = (app_usage_stats['days'] * 24 + app_usage_stats['hours']).astype(str) + 'h ' + app_usage_stats['minutes'].astype(str) + 'm ' + app_usage_stats['seconds'].astype(str) + 's', textinfo = 'none',
                  marker=dict(line=dict(color='#000000', width=2)))
fig2.update_layout(width = 600, height = 400)

data = {'P': [301, 302, 303, 304], 'mov': [15.1, 16.2, 14.3, 13.2], 'app' : [4.8, 4.2, 4.9, 3.8]}
df = pd.DataFrame.from_dict(data)


layout = html.Div([
    html.Div(html.P(html.B('Group Stats')), className='Header'),
    html.Div(children = [
        dcc.Graph(figure = fig),
        dcc.Graph(figure = fig2)
    ], style={'display':'flex'}),
    html.Div(children = [
        dcc.Dropdown(id = 'x_axis',
                     options = [{'label' : 'movement', 'value' : 'mov'},
                                {'label' : 'AppUsage', 'value' : 'app'}],
                     multi = False,
                     value = 'mov',
                     clearable = False,
                     style = {'width' : '200pt'}),
        dcc.Dropdown(id = 'y_axis',
                     options = [{'label' : 'movement', 'value' : 'mov'},
                                {'label' : 'AppUsage', 'value' : 'app'}],
                     multi = False,
                     value = 'app',
                     clearable = False,
                     style = {'width' : '200pt'})
    ], style = {'display':'flex'}),
    html.Div(children = [
        dcc.Graph(id = 'graph', style = {'width':'600pt', 'height':'300pt'}),
        html.Pre(id = 'click-data', style = {'overflowX':'scroll', 'width':'100pt', 'height':'300pt'}),
        #dcc.Link('test', href = '/indiv')
    ], style = {'display':'flex'}),
    #dash.page_container
])

@app.callback(
    Output('graph', 'figure'),
    Input('x_axis', 'value'),
    Input('y_axis', 'value')
)
def update_graph(x_axis, y_axis):
    fig = px.scatter(df, x=x_axis, y=y_axis)
    fig.update_layout(clickmode = 'event+select')
    return fig

@app.callback(
    Output('click-data', 'children'),
    Input('graph', 'clickData'))
def display_click_data(clickData):
    if clickData == None:
        return None
    return df.loc[clickData['points'][0]['pointIndex']].to_string()

