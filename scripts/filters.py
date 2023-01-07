import datetime as dt
from ib_insync import *
from src.settings import ENVIRONMENTS, DATA_DIR
import pywt
from src.settings import OUTPUT_RESULTS_DIR
from scripts.helper import *
import matplotlib.pyplot as plt
from trend_scanning_label import getBinsFromTrend
import numpy as np
import pandas as pd
from modwtpy import modwt, imodwt
from scipy import stats
from scipy.signal import savgol_filter

df = pd.read_csv("../data/EUR.csv", header=0, parse_dates=True)


df = df[:500]

window_length = 20

# df['avg'] = (df['open']+df['close']+df['high']+df['low'])/4

df['avg'] = df['close'].copy()



df['avg_w'] = df['avg'].shift(int((window_length-1)/2))
df['non'] = 2*df['avg'] - df['avg_w']
df['non_zlema'] = df['non'].ewm(alpha = 2/(window_length+1), ignore_na=True).mean()



close_values = df['non_zlema'].values
df['ewma'] = df['close'].ewm(alpha = 2/(window_length+1), ignore_na=True).mean()


df['non_zlema_w'] = df['non_zlema'].shift(int((window_length-1)/2))
df['non_zlema_dif'] = 2*df['non_zlema'] - df['non_zlema_w']
df['non_zlema_2'] = df['non_zlema_dif'].ewm(alpha = 2/(window_length+1), ignore_na=True).mean()







# filt1 = savgol_filter(close_values, 50, 6)
# filt1 = smooth(close_values,20, window='gaussian')



df0 = pd.Series(close_values)

idx_range_from = 5
idx_range_to = 50

trends = False
if trends:
    df1 = getBinsFromTrend(df0.index, df0, [idx_range_from, idx_range_to, 2])  # [3,10,1] = range(3,10)
    tValues = df1['tVal'].values  # tVal

    doNormalize = False
    # normalise t-values to -1, 1
    if doNormalize:
        np.min(tValues)
        minusArgs = [i for i in range(0, len(tValues)) if tValues[i] < 0]
        tValues[minusArgs] = tValues[minusArgs] / (np.min(tValues) * (-1.0))

        plus_one = [i for i in range(0, len(tValues)) if tValues[i] > 0]
        tValues[plus_one] = tValues[plus_one] / np.max(tValues)
    tValues = np.where(tValues<0, -1, 1)

fig, ax = plt.subplots(figsize=(30, 10))
ax.set_title(f"Denoised")
ax.plot(close_values, label="zlema", color = "black")
# ax.plot(filt1, label="Denoised", )
if trends:
    ax.scatter(df1.index, df0.loc[df1.index].values, c=tValues, s = 5, cmap='viridis')
else:
    ax.plot(df['close'].values, label = 'Close')
    # ax.plot(df['ewma'].values, label='EWMA')
    ax.plot(df['non_zlema_2'].values, label='zlema_2')

ax.grid(True)
plt.legend(loc="upper left")
plt.show()



