import datetime as dt
from ib_insync import *
from src.settings import ENVIRONMENTS, DATA_DIR
import pywt

import matplotlib.pyplot as plt
from trend_scanning_label import getBinsFromTrend
import numpy as np
import pandas as pd


# ib = IB()
# env = ENVIRONMENTS["IB_LIVE"]
#
# ib.connect(env['HOST'], env['PORT'], clientId=env['CLIENT_ID'])
#
# contract = Forex('EURUSD')
# contract = CFD(symbol = 'IBUS500', currency= 'USD', exchange='SMART')
# contract = Stock(symbol="TSLA", exchange="SMART", currency="USD")
# print(contract)
# print("Description", contract.description)
#
# ib.qualifyContracts(contract)
#
# order = MarketOrder('BUY', 20000)
#
# trade = ib.placeOrder(contract, order)


# summary = ib.accountSummary()
# bars = ib.reqHistoricalData(
#     contract,
#     endDateTime='',
#     durationStr='2 D',
#     barSizeSetting='1 min',
#     whatToShow='MIDPOINT',
#     useRTH=True,
#     formatDate=1)

# ticks =  ib.reqHistoricalTicks(
#     contract,
#     startDateTime= dt.date(2022,12,27),
#     endDateTime=dt.date(2022,12,28),
#     whatToShow='MIDPOINT',
#     numberOfTicks=1000,
#     useRth = True)
# save to CSV file

df = pd.read_csv("../data/EUR.csv", header=0, parse_dates=True)

df = df[:1000]
# df = util.df(bars)

close = df['close'].values
close_bkp = df['close'].copy()

cA, cD = pywt.dwt(close, "sym12", mode="zero")


coeffs_n = pywt.wavedec(close, "sym12")
approx_n = coeffs_n[0]
details_n = coeffs_n[1:]

def neigh_block(details, n, sigma):
    res = []
    L0 = int(np.log2(n) // 2)
    L1 = max(1, L0 // 2)
    L = L0 + 2 * L1
    def nb_beta(sigma, L, detail):
        S2 = np.sum(detail ** 2)
        lmbd = 4.2 # solution of lmbd - log(lmbd) = 3
        beta = (1 - lmbd * L * sigma**2 / S2)
        return max(0, beta)
    for d in details:
        d2 = d.copy()
        for start_b in range(0, len(d2), L0):
            end_b = min(len(d2), start_b + L0)
            start_B = start_b - L1
            end_B = start_B + L
            if start_B < 0:
                end_B -= start_B
                start_B = 0
            elif end_B > len(d2):
                start_B -= end_B - len(d2)
                end_B = len(d2)
            assert end_B - start_B == L
            d2[start_b:end_b] *= nb_beta(sigma, L, d2[start_B:end_B])
        res.append(d2)
    return res

details_nb = neigh_block(details_n, len(close), 0.1)

sig_dop_dn = pywt.waverec([approx_n] + details_nb, "sym12")
plt.figure(figsize=(15,4))
plt.title("denoised signal vs original signal")
plt.plot(close)
plt.plot(sig_dop_dn)
#plt.plot(fsig_dop_fden)
plt.show()

close = pd.DataFrame(sig_dop_dn)



idx_range_from = 5
idx_range_to = 55
df1 = getBinsFromTrend(close_bkp.index, close_bkp,  [idx_range_from, idx_range_to, 10])

tValues = df1['tVal'].values  # tVal

doNormalize = True
# normalise t-values to -1, 1
if doNormalize:
    np.min(tValues)
    minusArgs = [i for i in range(0, len(tValues)) if tValues[i] < 0]
    tValues[minusArgs] = tValues[minusArgs] / (np.min(tValues) * (-1.0))

    plus_one = [i for i in range(0, len(tValues)) if tValues[i] > 0]
    tValues[plus_one] = tValues[plus_one] / np.max(tValues)



classes = np.where(tValues<0,-1,1)

plt.scatter(df1.index, close_bkp.loc[df1.index].values, c=classes, cmap='viridis')  # df1['tVal'].values, cmap='viridis')
# plt.plot(close.index, close.values, color='gray')
# plt.plot(close_bkp.index, close_bkp.values, color = 'gray')
plt.colorbar()
plt.show()




# util.barplot(bars, title='', upColor='blue', downColor='red')
# plt.show()
# df.to_csv(DATA_DIR+contract.symbol + '.csv', index=False)


# df_ticks = util.df(ticks)
# df_ticks.to_csv(DATA_DIR+contract.symbol + 'ticks.csv', index=False)
# print("Check")