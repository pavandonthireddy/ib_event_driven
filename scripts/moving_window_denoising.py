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

st = 0
levels = 9
df = df[:500]

exp_1 = []

exp_2 =[]

exp_3 = []
exp_4 = []
exp_5 = []

window_length = 5#2**levels

df['avg'] = (df['open']+df['close']+df['high']+df['low'])/4

close_values = df['avg'].values

#exp 2
def lowpassfilter(signal, thresh = 0.63, wavelet="db4", mode = "per"):
    thresh = thresh*np.nanmax(signal)
    # print(thresh)
    coeff = pywt.wavedec(signal, wavelet, mode=mode )
    coeff[1:] = (pywt.threshold(i, value=thresh, mode="soft" ) for i in coeff[1:])
    reconstructed_signal = pywt.waverec(coeff, wavelet, mode=mode)


    return reconstructed_signal, coeff[0]





def wavelet_denoising(x, wavelet='db4', level=1):
    coeff = pywt.wavedec(x, wavelet, mode="per")
    sigma = (1/0.6745) * madev(coeff[-level])
    uthresh = sigma * np.sqrt(2 * np.log(len(x)))
    # print(uthresh)
    coeff[1:] = (pywt.threshold(i, value=uthresh, mode='hard') for i in coeff[1:])
    return pywt.waverec(coeff, wavelet, mode='per')



def pywt_swt(data, wavelet, norm, level=5, thresh_coe=10):
    r'''
    Use `pywt`(CPU) to swt_denoise.
    Parameter:
    @data: A numpy.ndarray with shape(N,), the data to be denoised.
    @level: A positive integer not greater than pywt.swt_max_level(len(data)).
    @thresh_coe: A float to control the strictness of denoising.
    Return:
    A numpy.ndarray with the same shape of @data, denoised @data.
    '''
    thresh_coe *= 0.67
    if norm:
        coeffs = pywt.swt(data, wavelet, norm=norm)
    else:
        coeffs = pywt.swt(data, wavelet, level=level)
    coeffs_rec = []
    for i in range(len(coeffs)):
        a_i = coeffs[i][0]
        mad = mead(coeffs[i][1])
        d_i_max = np.max(coeffs[i][1])
        # print(i, thresh_coe*mad)
        thresh = 0.9999*d_i_max#thresh_coe * mad
        d_i = pywt.threshold(coeffs[i][1], thresh , 'hard')
        coeffs_rec.append((a_i, d_i))
    data_rec = pywt.iswt(coeffs_rec, wavelet, norm=norm)
    return data_rec, a_i


def pywt_dwt(data, wavelet, norm, level=5, thresh_coe=10):
    r'''
    Use `pywt`(CPU) to swt_denoise.
    Parameter:
    @data: A numpy.ndarray with shape(N,), the data to be denoised.
    @level: A positive integer not greater than pywt.swt_max_level(len(data)).
    @thresh_coe: A float to control the strictness of denoising.
    Return:
    A numpy.ndarray with the same shape of @data, denoised @data.
    '''

    # cA, cD = pywt.dwt(data, wavelet)
    coeffs_rec = []
    for i in range(level):
        data, cD = pywt.dwt(data, wavelet)
        d_i_max = np.max(cD)
        # print(i, thresh_coe*mad)
        thresh = 0.2*d_i_max#thresh_coe * mad
        d_i = pywt.threshold(cD, thresh , 'hard')
        coeffs_rec.append((data, d_i))

    coeffs_rec = coeffs_rec[::-1]

    data_rec = coeffs_rec[0][0]
    for i in range(level):
        data_rec = pywt.idwt(data_rec, coeffs_rec[i][1], wavelet=wavelet)

    return data_rec



wavelet_list = ["rbio2.2"] #pywt.wavelist()

for wavelet in wavelet_list:
    exp_1 = []

    exp_2 = []

    exp_3 = []
    exp_4 = []
    exp_5 = []

    # diff = {}
    # for x in range(1,11):
    #     diff[str(x/10)] = []
    try:
        for i in range(len(close_values)):
            if i <= window_length:
                # exp_1.append(np.nan)
                exp_2.append(np.nan)
                # exp_3.append(np.nan)
                exp_4.append(np.nan)
                # exp_5.append(np.nan)

            else:
                block = close_values[i-window_length:i]

                #Exp1

                # coeffs_n = pywt.wavedec(block, wavelet)
                # approx_n = coeffs_n[0]
                # details_n = coeffs_n[1:]
                #
                # details_nb = neigh_block(details_n, len(block), 0.4)
                #
                #
                # sig_dop_dn = pywt.waverec([approx_n] + details_nb, wavelet)

                # Exp 2

                thresh_2 = 0.99
                # _, sig_dop_dn_2 = lowpassfilter(block, thresh_2, wavelet=wavelet, mode="per")
                #
                sig_dop_dn_2 = l1_filter(block,500)


                #Exp 3

                # sig_dop_dn_3 = wavelet_denoising(block, wavelet)



                #Exp 4

                # _, sig_dop_dn_4 = pywt_swt(block, wavelet, norm=False, level = levels, thresh_coe= 100)
                #

                #Exp 5

                # sig_dop_dn_5 = pywt_dwt(block, wavelet, norm=False, level = levels, thresh_coe= 100)

                print(f"iteration {i} completed")





                # exp_1.append(sig_dop_dn[-1])

                exp_2.append(sig_dop_dn_2[-1])
                # exp_3.append(sig_dop_dn_3[-1])
                # exp_4.append(sig_dop_dn_4[-1])
                # exp_5.append(sig_dop_dn_5[-1])


        fig, ax= plt.subplots(figsize=(30,10))
        ax.set_title(f"{wavelet} denoised signal vs original signal")
        ax.plot(close_values, label = "Original", )
        ax2 = ax.twinx()
        # ax2.plot(exp_2, label="Original", color="red" )
        ax2.plot(exp_2, label="denoised", color="red" )
        # for x in range(1,11):
        #     plt.plot(diff[str(x / 10)], label = "exp 2, thresh ="+str(x/10))
        # plt.plot(exp_1, label = "Denoised Exp 1")
        # plt.plot(exp_2, label = "Denoised Exp 2")
        # plt.plot(exp_3, label = "Denoised Exp 3")
        # plt.plot(exp_4, label = "Denoised Exp 4")
        # plt.plot(exp_5, label = "Denoised Exp 5")
        # ax2.grid(True)
        # plt.plot(exp_4, label = "Denoised Exp 4")
        #plt.plot(fsig_dop_fden)
        plt.legend(loc="upper left")

        plt.savefig(f"{OUTPUT_RESULTS_DIR}/{wavelet}_5.png", dpi=150)
        plt.show()
        plt.close('all')
    except Exception as e:
        print(e)
        pass


