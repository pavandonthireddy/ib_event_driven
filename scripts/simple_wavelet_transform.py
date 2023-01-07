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

df = pd.read_csv("../data/EUR.csv", header=0, parse_dates=True)

window_levels = 12

df = df[:2**window_levels]

exp_1 = []

exp_2 =[]

exp_3 = []
exp_4 = []


df['avg'] = (df['open']+df['close']+df['high']+df['low'])/4

close_values = df['avg'].values



data = close_values
waveletname = 'sym5'

for waveletname in ["rbio2.2"]:#pywt.wavelist():
    try:

        # fig, axarr = plt.subplots(nrows=window_levels, ncols=2, figsize=(6, 6))
        coeffs = pywt.dwt(data, waveletname) #pywt.swt(data, waveletname)

        levels = {}

        modified = []
        mod_dict = {}
        denoised_dict = {}
        for i in range(1, 11):
            mod_dict[str(i / 10)] = []


        for i in range(window_levels):
            cA = coeffs[i][0]
            cD = coeffs[i][1]
            thresh_D = 0.15*np.max(cD)
            thresh_A = 0.5*np.max(cA)
            cD_m = pywt.threshold(cD, thresh_D , 'soft')
            for i in range(1,11):
                cD_i = pywt.threshold(cD, (i/10)*np.max(cD), 'hard')
                mod_dict[str(i/10)].append((cA,cD_i) )

            if i<0:
                cA_m = pywt.threshold(cA, thresh_A , 'soft')
            else:
                cA_m = cA
            modified.append((cA_m, cD_m))


        # for ii in range(window_levels):
        #     # (data, coeff_d) = pywt.dwt(data, waveletname)
        #
        #
        #     data = coeffs[ii][0]
        #     coeff_d = coeffs[ii][1]
        #     axarr[ii, 0].plot(data, 'r', label ="original")
        #     axarr[ii, 0].plot(modified[ii][0], color = 'blue', label ="modified")
        #
        #     axarr[ii, 1].plot(coeff_d, 'g', label="original")
        #     axarr[ii, 1].plot(modified[ii][1], color = 'black', label="modified")
        #
        #
        #     # axarr[ii, 0].set_ylabel("Level {}".format(ii + 1), fontsize=14, rotation=90)
        #     # axarr[ii, 0].set_yticklabels([])
        #     if ii == 0:
        #         axarr[ii, 0].set_title("Approximation coefficients", fontsize=14)
        #         axarr[ii, 1].set_title("Detail coefficients", fontsize=14)
        #     # axarr[ii, 1].set_yticklabels([])
        #
        # plt.grid(True)
        # plt.legend(loc="upper left")
        # plt.tight_layout()
        # plt.show()

        denoised = pywt.iswt(modified, waveletname)

        for i in range(1, 11):
            denoised_dict[str(i / 10)] = pywt.iswt(mod_dict[str(i/10)], waveletname)

        # fig, ax = plt.subplots(nrows=6, ncols=1, figsize=(10, 10))
        # for i in range(6):
        #     if i ==0:
        #         ax[i].plot(close_values)
        #     else:
        #         ax[i].plot(coeffs[i-1][0], label = f"Approximate level {i-1}")
        #
        #
        # plt.show()
        fig, ax = plt.subplots(figsize=(20, 10))
        ax.set_title(f"{waveletname}")
        # ax.plot(close_values, label = "Original", color="red")
        ax2 = ax.twinx()
        ax2.plot(modified[-1][0], label = "Last ")
        # for i in range(1,11):
        #     ax2.plot(denoised_dict[str(i/10)], label = f"Denoised {i/10}")
        ax.plot(denoised, label="denoised", color = "black")
        plt.grid(True)
        plt.legend(loc="upper left")
        # plt.show()
        plt.savefig(f"{OUTPUT_RESULTS_DIR}/{waveletname}_chk.png", dpi=150)
        plt.close('all')
    except:
        pass