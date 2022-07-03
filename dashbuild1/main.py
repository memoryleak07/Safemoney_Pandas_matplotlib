# %%
import pandas as pd
import matplotlib as mpl
import matplotlib.pyplot as plt
import matplotlib.dates as md
import numpy as np

datestart = "2020"
dateend = "2021"
colors = ['#ff9999','#66b3ff','#99ff99','#ffcc99']


# %%
## BAR PLOT - AFFLUENZA ORARIA GIORNALIERA
df = pd.read_json('test_daily.json')
## estraggo "transactionsLog" dal json e popolo il dataframe
df = (df["transactionsLog"].apply(pd.Series))
df = df.drop(columns=['Id','Token','ResCode','ResDescription','Levels','User',"TotalRequest","Paid","Dispensed","NotDispensed","TransactionStatus","Total","Description"])
## convert to datetime, set_index on Date and resample to hours
df2 = (
 df.assign(Date=pd.to_datetime(df['Date']))
   .set_index('Date')
   .loc[lambda d: d['TransactionCode'].eq('PAY')]
   .resample('1H').count()
   .rename(columns={"TransactionCode": "Payments"})
)
##
ax = df2.plot(kind="bar", figsize=(16, 8)).set_xticklabels(df2.index.strftime('%H-%M'))
# ax.set_xticklabels(df2.index.strftime('%H-%M'))
plt.title('Hourly turnout of day ' + datestart)
plt.ylabel("Number of Transaction")
plt.xlabel("Hour")
plt.grid(True)
plt.show()


# %%
## BAR PLOT - AFFLUENZA ORARIA PER RANGE DI DATE
df = pd.read_json('test.json')
## estraggo "transactionsLog" dal json e popolo il dataframe
df = (df["transactionsLog"].apply(pd.Series))
df = df.drop(columns=['Id','Token','ResCode','ResDescription','Levels','User',"TotalRequest","Paid","Dispensed","NotDispensed","TransactionStatus","Total","Description"])
df = df.rename(columns={"TransactionCode": "Payments"})
## divido la colonna "Date" in due colonne separate "Date" e "Time"
df['Time'] = pd.to_datetime(df['Date']).dt.time
df['Date'] = pd.to_datetime(df['Date']).dt.date
df['Hour'] = ([time.hour for time in df.loc[:,'Time']])
df['Hour'] = pd.to_datetime(df['Hour'],format='%H').dt.strftime('%H:%M')
df = (df[(df['Payments'] == 'PAY')][['Payments','Hour']].groupby('Hour').count())
###
ax = df.plot(kind='bar', figsize=(16, 8))
plt.title('Hourly turnout from ' + datestart + " to " + dateend)
plt.ylabel('Number of Transaction')
plt.xlabel("Hour")
plt.grid(True)
plt.show()


# %%
## GRAFICO A TORTA - SOMMA TOTALE IN EURO DI PAGAMENTI, PRELIEVI, CARICAMENTI
df = pd.read_json('test.json')
## estraggo "transactionsLog" dal json e popolo il dataframe
df = (df["transactionsLog"].apply(pd.Series))
df = df.drop(columns=['Id','Token','ResCode','ResDescription','Levels','User',"Paid","Dispensed","NotDispensed","TransactionStatus","Description"])
# ## raggruppo per TransactionCode = PAY, WITHDRAWAL e LOAD_CASH e sommo il totale
df = (df[(df['TransactionCode'] == 'PAY') | (df['TransactionCode'] == 'WITHDRAWAL') | (df['TransactionCode'] == 'LOAD_CASH')][['TransactionCode','Total']].groupby('TransactionCode').sum().abs())

# funzione per ritorno valore in € invece che percentuale
def autopct_format(values):
    def my_format(pct):
        total = sum(values)
        val = float(pct*total/100.0)
        return '{v:.2f} €'.format(v=val)
    return my_format


df["Total"].plot(kind='pie',
    figsize=(14, 6),
    autopct = autopct_format(df["Total"]), 
    startangle=90,    
    shadow=False,       
    labels=None, 
    colors = colors,
    fontsize=13              
    )
plt.title('Sum of Totalizer') 
plt.axis('equal') 
plt.legend(labels=df["Total"].index, loc='upper left') 
plt.show()


# %%
## STATISTICHE OPERAZIONI
df = pd.read_json('test.json')
## estraggo "transactionsLog" dal json e popolo il dataframe
df = (df["transactionsLog"].apply(pd.Series))
df = df.drop(columns=['Id','Date','Token','ResCode','ResDescription','Levels','User',"Paid","Dispensed","Total", "Description"])
# estraggo le informazioni
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
print("Totale pagamenti: ", totpay)
print("Totale prelievi: ", totwithdrawal)
print("Totale ricariche: ", totloadcash)
print("Totale svuotamenti: ", totempty)
print("Totale pagamenti abortiti: ", totpayaborted)
print("Totale operazioni in errore: ", toterror)
print("La transazione più alta: ", maxpay, "€")
print("La transazione più bassa: ", minpay, "€")
print("Totale pagamenti\prelievi conlcusi con resto non erogato: ", countnotdisp[True], "su", (totpay + totwithdrawal), "\n[", str(percentage[True]), "]")


# %%
## BAR PLOT - AFFLUENZA GIORNALIERA
df = pd.read_json('test.json')
## estraggo "transactionsLog" dal json e popolo il dataframe
df = (df["transactionsLog"].apply(pd.Series))
df = df.drop(columns=['Id','Token','ResCode','ResDescription','Levels','User',"TotalRequest","Paid","Dispensed","NotDispensed","TransactionStatus","Total","Description"])
df = df.rename(columns={"TransactionCode": "Payments"})
## divido la colonna "Date" in due colonne separate "Date" e "Time"
df['Time'] = pd.to_datetime(df['Date']).dt.time
df['Date'] = pd.to_datetime(df['Date']).dt.date

df = (df[(df['Payments'] == 'PAY')][['Payments','Date']].groupby('Date').count())
highernumberpay = df['Payments'].max()
higherday = df['Payments'].idxmax()
print("Giorno con affluenza maggiore:", higherday)
print("Totale dei pagamenti della giornata:", highernumberpay)

###
ax = df.plot(kind='bar', figsize=(16, 8), color=colors[1])
plt.title('Date turnout from ' + datestart + " to " + dateend)
plt.ylabel('Number of Transaction')
plt.xlabel("Date")
plt.grid(True)
plt.show()

# %%