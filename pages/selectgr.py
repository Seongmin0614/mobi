from dash import dcc, html, Input, Output
import dash_bootstrap_components as dbc
from server import app
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import os

layout = dbc.Container(
    [
        dbc.Row([
            dbc.Col(html.Div("Groups"), width=8, style = {'background-color':'lightcyan'}),
            dbc.Col(html.Div("Selected Groups"), width=4, style = {'background-color':'lightcyan'})])
    ]
)