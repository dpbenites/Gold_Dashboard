import dash
from dash import html, dcc, Output, Input
import plotly.express as px
import pandas as pd
import dash_bootstrap_components as dbc
from dash_bootstrap_templates import load_figure_template

load_figure_template("vapor")
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.VAPOR])

# ====================== Data Frame classe =========== ##
class GoldData:
    def __init__(self, file_gold_production, file_gold_price, start_year, end_year, n_top_producers):
        self.df_gold = pd.read_csv(file_gold_production)
        self.df_gold.rename(columns={'Gold Production (Clio-Infra & USGS)': 'Gold Production'}, inplace=True)
        self.df_price = pd.read_csv(file_gold_price)
        self.df_price['Date'] = pd.to_datetime(self.df_price['Date'])
        self.start_year = start_year
        self.end_year = end_year
        self.n_top_producers = n_top_producers

    def ranking(self):
        df_filtered = self.df_gold[(self.df_gold['Year'] >= self.start_year) & (self.df_gold['Year'] <= self.end_year)]
        df_grouped = df_filtered.groupby('Entity')['Gold Production'].sum().reset_index()
        df_grouped.rename(columns={'Gold Production': 'Total Gold Production'}, inplace=True)
        df_ranked = df_grouped.sort_values(by='Total Gold Production', ascending=False).reset_index(drop=True)
        df_ranked = df_ranked.iloc[:self.n_top_producers + 1]

        total_top_countries = df_ranked.loc[1:, 'Total Gold Production'].sum()
        rest_of_world_production = df_ranked.loc[0, 'Total Gold Production'] - total_top_countries
        rest_of_world_df = pd.DataFrame({'Entity': ['Rest of World'], 'Total Gold Production': [rest_of_world_production]})
        df_ranked = pd.concat([df_ranked, rest_of_world_df], ignore_index=True)
        return df_ranked

    def gold_hist(self):
        top_countries = self.ranking()['Entity'].tolist()
        top_countries.pop(0)
        top_countries.pop(-1)

        df_filtered = self.df_gold[self.df_gold['Entity'].isin(top_countries)]
        df_filtered = df_filtered[(self.df_gold['Year'] >= self.start_year) & (self.df_gold['Year'] <= self.end_year)]
        return df_filtered
    
    def gold_price(self):
        df_price = self.df_price
        return df_price

# ==================== Layout ================= #
app.layout = dbc.Container([
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H4('Dashboard de Produção de Ouro', className='card-title'),
                    html.H4('FinancEEL Quant'),
                    html.P('Selecione o intervalo de datas e o número de maiores produtores para análise.', className='card-text'),
                    html.Label('Data Inicial:'),
                    dcc.Input(id='start-date', type='number', value=1940, className='form-control'),
                    html.Label('Data Final:'),
                    dcc.Input(id='end-date', type='number', value=2000, className='form-control'),
                    html.Label('Número de maiores produtores:'),
                    dcc.Input(id='top-n', type='number', value=5, className='form-control')
                ])
            ], style={'height': '100%', 'margin': '20px', 'padding': '10px'})
        ], width=3),

        dbc.Col([
            dbc.Row([
                dbc.Col(dcc.Graph(id='pie-chart'), width=6),
                dbc.Col(dcc.Graph(id='bar-chart'), width=6)
            ])
        ], width=9)
    ], style= {'margin': '20px', 'padding':'10px' } ),
    
    dbc.Row([
        dbc.Col(dcc.Graph(id='line-chart'), width=6),
        dbc.Col(dcc.Graph(id='gold-price-chart'), width=6)
    ], style={'margin-top': '20px', 'height': '100%' })
], fluid=True)

# Callbacks
@app.callback(
    [Output('pie-chart', 'figure'),
     Output('bar-chart', 'figure'),
     Output('line-chart', 'figure'),
     Output('gold-price-chart', 'figure')],
    [Input('start-date', 'value'),
     Input('end-date', 'value'),
     Input('top-n', 'value')]
)
def update_charts(start_year, end_year, top_n):
    gold_data = GoldData('gold-production.csv', 'Gold_price.csv', start_year, end_year, top_n)

    df_ranked = gold_data.ranking()
    df_filtered = gold_data.gold_hist()

    # Pie Chart
    pie_fig = px.pie(df_ranked[1:], values='Total Gold Production', names='Entity', title=f'Proporção dos Maiores Produtores de Ouro ({start_year}-{end_year})')

    # Bar Chart
    bar_fig = px.bar(df_ranked[1:], x='Entity', y='Total Gold Production', title=f'Produção Total dos Maiores Produtores de Ouro ({start_year}-{end_year})')

    # Line Chart
    line_fig = px.line(df_filtered, x='Year', y='Gold Production', color='Entity', title='Produção de Ouro ao Longo do Tempo')

    # Gold Price Chart
    df_gold_price = gold_data.gold_price()
    gold_price_fig = px.line(df_gold_price, x='Date', y='Price(USD)', title='Preço do Ouro')

    return pie_fig, bar_fig, line_fig, gold_price_fig

# Run the app
if __name__ == '__main__':
    app.run_server(debug=True, host='127.0.0.1')
