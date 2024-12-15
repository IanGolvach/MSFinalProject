from dash import Dash, dcc, html, Input, Output, State, callback, dash_table, ctx, no_update
from dash.exceptions import PreventUpdate
import plotly.express as px
from io import StringIO
import pandas as pd
import numpy as np

usernames = ['Joe','Bob','Phil','Trent','Ross','Mary']
passwords = ['123','wordpass','compromise','razzle','password','abacus']
access_levels = [0,0,0,0,0,1]

app = Dash()
app.layout = [html.Div(
    [
        dcc.Store(id='access_level',data=-1),
        dcc.Store(id='tickers_available',data=[]), # Actually the ticker names
        html.Div(
            [
                html.H1("!!STOCK ANALYZER!!"),
                html.P("TICKERS TICKERS AND MORE TICKERS")
            ]
        ),
        dcc.Tabs(
            id='tab_bar',
            value='login',
            children=[
                dcc.Tab(
                    label='Login',
                    value='login',
                    id='login_tab'
                ),
                dcc.Tab(
                    label='Tickers',
                    value='tickers',
                    id='tickers_tab'
                ),
                dcc.Tab(
                    label='Statistics',
                    value='stats',
                    id='stats_tab'
                ),
                dcc.Tab(
                    label='Predictions',
                    value='preds',
                    id='preds_tab'
                ),
                dcc.Tab(
                    label='Admin Tools',
                    value='admin',
                    id='admin_tab'
                )
            ]
        ),
        html.Div(
            id='login_screen',
            children=[
                html.H2("Please enter your username and password", style={'margin':'auto','textalign':'center'}),
                html.P("Username", style={'margin':'auto'}),
                dcc.Input(
                    id='login_username',
                    type='text',
                    placeholder='username'
                ),
                html.P("Password",style={'margin':'auto'}),
                dcc.Input(
                    id='login_password',
                    type='text',
                    placeholder='password'
                ),
                html.Button(
                    id='login_btn',
                    children='Login',
                    style={'margin':'auto'}
                )
            ], style={'textalign':'center','width':'100%','height':'100%'}
        ),
        html.Div(
            id='tickers_screen',
            children=[
                html.H2("Choose tickers to review."),
                html.Button(id='tickers_refresh_btn',children='Refresh Available Tickers'),
                dcc.Dropdown(
                    [],
                    multi=True,
                    placeholder="Choose stocks to observe"
                ),
                dcc.Checklist(
                    id='ticker_features_checklist',
                    options=['close','open','high','low'],
                    inline=True
                ),
                dcc.Graph(
                    id='ticker_loch_graph', figure=px.line()
                ),
                html.H2("Ticker Volume"),
                dcc.Graph(
                    id='ticker_volume_graph', figure=px.line()
                )
            ]
        ),
        html.Div(
            id='stats_screen',
            children=[
                
            ]
        ),
        html.Div(
            id='preds_screen',
            children=[
                
            ]
        ),
        html.Div(
            id='admin_screen',
            children=[
                
            ]
        )

    ]
)]

###################################################################################################
#
# L O G I N  S C R E E N  C A L L B A C K S
#
###################################################################################################

@callback(
    Output('login_screen','hidden'),
    Output('tickers_screen','hidden'),
    Output('stats_screen','hidden'),
    Output('preds_screen','hidden'),
    Output('admin_screen','hidden'),
    Input('tab_bar','value')
)
def show_screen(screen_selected):
    if screen_selected == 'login':
        return [False,True,True,True,True]
    elif screen_selected == 'tickers':
        return [True,False,True,True,True]
    elif screen_selected == 'stats':
        return [True,True,False,True,True]
    elif screen_selected == 'preds':
        return [True,True,True,False,True]
    elif screen_selected == 'admin':
        return [True,True,True,True,False]

@callback(
    Output('login_tab','disabled'),
    Output('tickers_tab','disabled'),
    Output('stats_tab','disabled'),
    Output('preds_tab','disabled'),
    Output('admin_tab','disabled'),
    Input('access_level','data')
)
def tab_access_level_handling(level):
    if level == -1:
        return [True,True,True,True,True]
    if level == 0:
        return [False,False,False,False,True]
    if level == 1:
        return [False,False,False,False,False]
    
@callback(
    Output('access_level','data'),
    State('login_username','value'),
    State('login_password','value'),
    Input('login_btn','n_clicks')
)
def login(username, password, n_clicks):
    if n_clicks == 0:
        raise PreventUpdate
    if username in usernames:
        if passwords[usernames.index(username)] == password:
            return access_levels[usernames.index(username)]
    return -1

###################################################################################################
#
# T I C K E R  S C R E E N  C A L L B A C K S
#
###################################################################################################

###################################################################################################
#
# S T A T I S T I C S  S C R E E N  C A L L B A C K S
#
###################################################################################################

###################################################################################################
#
# P R E D I C T I O N S  S C R E E N  C A L L B A C K S
#
###################################################################################################

###################################################################################################
#
# A D M I N  S C R E E N  C A L L B A C K S
#
###################################################################################################

if __name__ == '__main__':
    app.run(debug=True)