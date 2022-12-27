import datetime
from ib_insync import *
from src.settings import ENVIRONMENTS, DATA_DIR

ib = IB()
env = ENVIRONMENTS["IB_SIMULATED"]

ib.connect(env['HOST'], env['PORT'], clientId=env['CLIENT_ID'])

contract = Forex('EURUSD')


summary = ib.accountSummary()
bars = ib.reqHistoricalData(
    contract,
    endDateTime='',
    durationStr='5 D',
    barSizeSetting='1 min',
    whatToShow='MIDPOINT',
    useRTH=True,
    formatDate=1)

# save to CSV file

df = util.df(bars)
df.to_csv(DATA_DIR+contract.symbol + '.csv', index=False)
print("Check")