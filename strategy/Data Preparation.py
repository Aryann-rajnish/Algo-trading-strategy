# This code is part of free course - Python For Algo Trading. Enroll at https://algoji.com/pro
# Copyright AlgoJi.com, all rights reserved

import pandas as pd

#read from csv
df = pd.read_csv("Data//BankNifty.csv")

#delete column
df = df.drop('Turnover (Rs. Cr)', 1)

#rename column
old_names = ['Date','Open','High','Low','Close','Shares Traded']
header_list = ['Date Time', 'Open', 'High', 'Low', 'Close', 'Volume']
df.rename(columns=dict(zip(old_names, header_list)), inplace=True)

#add column
df['Adj Close'] = ''

#write back to csv
df.to_csv("Data//BankNifty.csv", na_rep = 100, index= False)
