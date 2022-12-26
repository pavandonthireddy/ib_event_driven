import datetime
from ib_insync import *

ib = IB()
ib.connect('127.0.0.1', 7496, clientId=5)

contract = Forex('EURUSD')


summary = ib.accountSummary()
bars = ib.reqHistoricalData(
    contract,
    endDateTime='',
    durationStr='22 Y',
    barSizeSetting='1 day',
    whatToShow='MIDPOINT',
    useRTH=True,
    formatDate=1)

# save to CSV file

df = util.df(bars)
df.to_csv('../data/'+contract.symbol + '.csv', index=False)
print("Check")