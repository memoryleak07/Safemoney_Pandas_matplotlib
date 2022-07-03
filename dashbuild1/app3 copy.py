import pandas as pd
import plotly.express as px  # (version 4.7.0 or higher)
import plotly.graph_objects as go
from dash import Dash, dcc, html, Input, Output, State  # pip install dash (version 2.0.0 or higher)
from datetime import datetime as dt
import plotly.express as px
import ipaddress


app = Dash(__name__)

# start_date = dt.today()
# end_date = dt.today()


def filterByRangeDate(start_date, end_date):
    # start_date = pd.to_datetime(start_date)
    # end_date = pd.to_datetime(end_date)
    print(start_date, end_date)
    df = pd.read_json('test2.json')
    df = (df["transactionsLog"].apply(pd.Series))
    df = df.drop(columns=['Id','Token','ResCode','ResDescription','Levels','User',"Description"])
    #df['Date'] = pd.to_datetime(df['Date'])
    df = df[(df['Date'] > start_date) & (df['Date'] < end_date)]
    print(df)
    return df


def validateIPAddress(ip):
    print(ip)
    # while True:
    #     try:
    #         ip = ipaddress.ip_address(input('\n[>] Enter Safemoney IP address: '))
    #         break
    #     except ValueError:
    #         print("\n[*] Enter a valid IP address!")
    #         continue



# ------------------------------------------------------------------------------
# App layout
app.layout = html.Div([
    html.H1("Web Application Dashboards with Dash", style={'text-align': 'center'}),
    html.Div(dcc.Input(id='input-on-submit', type='text')),
    html.Button('Submit', id='submit-val', n_clicks=0),
    html.Div(id='container-button-basic', children='Enter a value and press submit'),
    html.Br(),
    dcc.DatePickerRange(
        id='my-date-picker-range',
        min_date_allowed=dt(2020, 12, 31),
        max_date_allowed=dt(2030, 12, 31),
        display_format='MMM Do, YY',
        start_date=dt.today(),
        end_date=dt.today(),

        minimum_nights=0
    ),
    html.Br(),
    html.Div(id='output_container', children=[]),
    html.Br(),
    html.H3("Pie-Chart total sum in €: ", style={'text-align': 'center'}),
    dcc.Graph(id='plot1', figure={}),
    html.Br(),
    html.H3("Bar-Plot hourly turnout: ", style={'text-align': 'center'}),
    dcc.Graph(id='plot2', figure={}),
    html.Br(),
    html.H3("Bar-Plot daily turnout: ", style={'text-align': 'center'}),
    dcc.Graph(id='plot3', figure={}),
    html.Br(),
    html.H3("General statistics:  ", style={'text-align': 'center'}),
    html.Div(id='stat4', children=[]),
    html.Br(),
])

# ------------------------------------------------------------------------------

@app.callback(
    Output('container-button-basic', 'children'),
    Input('submit-val', 'n_clicks'),
    State('input-on-submit', 'value')
)
def update_output(n_clicks, value):
    validateIPAddress(value)
    return 'The input value was "{}" and the button has been clicked {} times'.format(value,n_clicks)

@app.callback(
    [Output(component_id='output_container', component_property='children'),
    Output(component_id='plot1', component_property='figure'),
    Output(component_id='plot2', component_property='figure'),
    Output(component_id='plot3', component_property='figure'),
    Output(component_id='stat4', component_property='children')],
    # [Input(component_id='slct_year', component_property='value')]
    Input('my-date-picker-range', 'start_date'),
    Input('my-date-picker-range', 'end_date')
)
def update_graph(start_date, end_date):
    # print(start_date, end_date)
    df = filterByRangeDate(start_date, end_date)

    container = "The range date chosen by user is from {} to {}".format(start_date, end_date)

    # # PLOT1 - PIE CHART
    dff2 = df.copy()
    dff2 = dff2.drop(columns=["Paid","Dispensed","NotDispensed","TransactionStatus"]) 
    # raggruppo per TransactionCode = PAY, WITHDRAWAL e LOAD_CASH e sommo il totale
    dff2 = (dff2[(dff2['TransactionCode'] == 'PAY') | (dff2['TransactionCode'] == 'WITHDRAWAL') | (dff2['TransactionCode'] == 'LOAD_CASH')][['TransactionCode','Total']].groupby('TransactionCode').sum().abs())
    fig1 = go.Figure(data=[go.Pie(values=dff2["Total"], labels=dff2.index, textinfo='percent+value')])


    # # PLOT2 - AFFLUENZA ORARIA
    dff = df.copy()
    dff = (
    dff.assign(Date=pd.to_datetime(df['Date']))
    .set_index('Date')
    .loc[lambda d: d['TransactionCode'].eq('PAY')]
    .resample('1H').count()
    .rename(columns={"TransactionCode": "Payments"})
    )
    fig2 = px.bar(dff, x=(dff.index.strftime('%H-%M')), y="Payments")


    # # PLOT3 - AFFLUENZA GIORNALIERA
    dff3 = df.copy()
    dff3 = dff3.rename(columns={"TransactionCode": "Payments"})
    ## divido la colonna "Date" in due colonne separate "Date" e "Time"
    dff3['Time'] = pd.to_datetime(dff3['Date']).dt.time
    dff3['Date'] = pd.to_datetime(dff3['Date']).dt.date
    dff3 = (dff3[(dff3['Payments'] == 'PAY')][['Payments','Date']].groupby('Date').count())
    highernumberpay = dff3['Payments'].max()
    higherday = dff3['Payments'].idxmax()
    print("Giorno con affluenza maggiore:", higherday)
    print("Totale dei pagamenti della giornata:", highernumberpay)

    fig3 = px.bar(dff3, y="Payments")


    # # DIV4 - STATISTISCHE
    totpay =  (((df['TransactionCode'] == 'PAY')).sum())
    totwithdrawal = (((df['TransactionCode'] == 'WITHDRAWAL')).sum())
    totloadcash = (((df['TransactionCode'] == 'LOAD_CASH')).sum())
    totempty = (((df['TransactionCode'] == 'EMPTY_CASH_TOTAL_SET')).sum())
    totpayaborted =  ((df['TransactionCode'] == 'PAY') & (df['TransactionStatus'] == 'ABORTED')).sum()
    toterror = (((df['TransactionCode'] == 'PAY') | (df['TransactionCode'] == 'WITHDRAWAL') | (df['TransactionCode'] == 'LOAD_CASH')) & (df['TransactionStatus'] == 'ERROR')).sum()
    maxpay = (df[(df['TransactionCode'] == 'PAY') & (df['TransactionStatus'] == 'TERMINATED')]['TotalRequest'].max())
    minpay = (df[(df['TransactionCode'] == 'PAY') & (df['TransactionStatus'] == 'TERMINATED')  & (df['TotalRequest'] > 0)]['TotalRequest'].min())
    # creo una nuova colonna bool IsChangeNotDispensed
    df['IsChangeNotDispensed'] = ((df['NotDispensed'] > 0) & ((df['TransactionCode'] == 'PAY') | (df['TransactionCode'] == 'WITHDRAWAL')))
    df = (df[(df['TransactionCode'] == 'PAY') | (df['TransactionCode'] == 'WITHDRAWAL') & (df['TransactionStatus'] == 'TERMINATED')][['TransactionCode','TransactionStatus','NotDispensed' ,'IsChangeNotDispensed']])
    countnotdisp = ((df['NotDispensed'] > 0) & (df['TransactionStatus'] == 'TERMINATED')).value_counts()
    percentage = df['IsChangeNotDispensed'].value_counts(normalize=True).mul(100).astype(str)+' %'
    # printo i risultati
    # print("Totale pagamenti: ", totpay)
    # print("Totale prelievi: ", totwithdrawal)
    # print("Totale ricariche: ", totloadcash)
    # print("Totale svuotamenti: ", totempty)
    # print("Totale pagamenti abortiti: ", totpayaborted)
    # print("Totale operazioni in errore: ", toterror)
    # print("La transazione più alta: ", maxpay, "€")
    # print("La transazione più bassa: ", minpay, "€")
    # print("Totale pagamenti\prelievi conlcusi con resto non erogato: ", countnotdisp[True], "su", (totpay + totwithdrawal), "\n[", str(percentage[True]), "]")
    stat4 = ("Totale pagamenti: ", totpay, html.Br(),
            "Totale prelievi: ", totwithdrawal, html.Br(),
            "Totale ricariche: ", totloadcash, html.Br(),
            "Totale svuotamenti: ", totempty, html.Br(),
            "Totale pagamenti abortiti: ", totpayaborted, html.Br(),
            "Totale operazioni in errore: ", toterror, html.Br(),
            "La transazione più alta: ", maxpay, "€", html.Br(),
            "La transazione più bassa: ", minpay, "€", html.Br(),
            "Totale pagamenti\prelievi conlcusi con resto non erogato: ", countnotdisp[True], " su ", (totpay + totwithdrawal), html.Br(), str(percentage[True]))
                

    return container, fig1, fig2, fig3, stat4

    # ------------------------------------------------------------------------------
   





if __name__ == '__main__':
    app.run_server(debug=True)

