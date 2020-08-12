import pandas as pd
import psycopg2
import sys
sys.path.append('../../ETLPipelines')
from InsertData import *


# Function to calculate marketshare
def get_mkcap(ticker, price, ticker2shares):
	shares = ticker2shares[ticker]
	return price*shares


# Connect to database
conn = psycopg2.connect(host='localhost', port=5432, database='postgres')

# Obtain Share Outstanding list
query_shares = """select l.ticker, l.shareoutstanding
                  from stock.stockshareoutstanding as l
                  left join
                  stock.stockmeta as r
                  on l.ticker = r.ticker
                  where r.indexcomponent = 'S&P 500'; """

shares_list = pd.io.sql.read_sql(query_shares, conn)
tickers = shares_list['ticker'].tolist()

ticker2shares = {}
for index, row in shares_list.iterrows():
	ticker2shares[row['ticker']] = row['shareoutstanding']

# Obtain testing data of stock price
query_prices = """select ticker, tradedate, closeprice
                  from stock.stockprice
                  where date_part('year', tradedate) 
                  between 2019 and 2020
                  and ticker in (
                  select ticker from stock.stockmeta
                  where indexcomponent = 'S&P 500')"""

df_price_test = pd.io.sql.read_sql(query_prices, conn)

# Obtain predicted stock price for all predicted
query_prices = """select * from stock.pred_proto_staging
                  where date_part('year', tradedate) > 2018;"""

df_price_pred = pd.io.sql.read_sql(query_prices, conn)


# Calculate testing data of market cap
df_price_test['mkcap_daily_test'] = df_price_test.apply(lambda row: get_mkcap(row.ticker, 
	                                                           row.closeprice,
	                                                           ticker2shares),
                                                               axis=1)
sp500_test = df_price_test[['tradedate','mkcap_daily_test']].groupby('tradedate').sum()
sp500_test = sp500_test.reset_index()

# Calculate predicted market cap
df_price_pred['mkcap_daily_pred'] = df_price_pred.apply(lambda row: get_mkcap(row.ticker, 
	                                                           row.closeprice,
	                                                           ticker2shares),
                                                               axis=1)
sp500_pred = df_price_pred[['tradedate','mkcap_daily_pred']].groupby('tradedate').sum()
sp500_pred = sp500_pred.reset_index()

# Obtain sp500_pred Divisor
query_divisor = """ select l.tradedate, r.divisor 
					from
					    (select tradedate, 
					    date_part('quarter', tradedate) as tradequarter,
					    date_part('year', tradedate) as tradeyear
					    from (select distinct(tradedate) from
					    stock.pred_proto_staging
					    where date_part('year',tradedate) 
					    > 2018) as i
					    ) as l
					left join (
					    select *, 
					    date_part('quarter', tradedate) as tradequarter,
					    date_part('year', tradedate) as tradeyear
					    from stock.sp500divisor) as r
					on l.tradequarter = r.tradequarter and 
					    l.tradeyear = r.tradeyear
					order by 1;"""
df_divisor = pd.io.sql.read_sql(query_divisor, conn)
df_divisor = df_divisor.fillna(method='ffill')

sp500 = pd.merge(sp500_pred, df_divisor, how='inner', on='tradedate')
sp500 = pd.merge(sp500, sp500_test, how='left', on='tradedate')


sp500['sp500_pred'] = sp500['mkcap_daily_pred']/(1.0*sp500['divisor'])
sp500['sp500_test'] = sp500['mkcap_daily_test']/(1.0*sp500['divisor'])


for index, row in sp500.iterrows():
	insert_sp500_protodb(conn, row)
