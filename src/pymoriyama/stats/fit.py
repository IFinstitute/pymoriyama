#! Python 3
import datetime
import math
import numpy as np

from tqdm import tqdm

def nanerror(monthly_stds, axis=None):
    """Compute combined error (sqrt(sum(err_i^2))/N) and preserve xarray DataArray when passed.

    Parameters
    - monthly_stds: array-like 
    - axis: int or tuple of ints (same semantics as numpy)

    Returns
    - numpy.ndarray 
    """

    vals = np.array(monthly_stds)
    num = np.sqrt(np.nansum(vals ** 2, axis=axis))
    den = np.count_nonzero(~np.isnan(vals), axis=axis)
    res = np.where(den != 0, num / den, np.nan)
    return res

def compute_periodic_averages(timestamps: np.ndarray, data: np.ndarray, errs: np.ndarray | None, period='D'):
    """
    観測データを日平均に変換する関数

    Parameters:
    timestamps (np.ndarray): タイムスタンプを含むdatetime64型の配列
    data (np.ndarray): 観測データ (float64型)
    errs (np.ndarray): 観測誤差 (float64型)

    Returns:
    np.ndarray: 1日ごとのタイムスタンプ (datetime型)
    np.ndarray: 日平均された観測データ (float64型)
    np.ndarray: 日平均された観測誤差 (float64型)
    """
    # タイムスタンプを日単位に変換 (例: '2024-01-01' のような日付)
    unique_days = np.unique(timestamps.astype(f"datetime64[{period}]"))

    # 日ごとのデータを格納するためのリスト
    periodic_averages = []
    periodic_errors = []

    # 各日のデータを抽出し、その平均を計算
    for day in tqdm(unique_days):
        # 該当日のデータを抽出
        mask = timestamps.astype(f"datetime64[{period}]") == day
        period_data = data[mask]
        period_errs = errs[mask] if errs is not None else np.zeros_like(period_data) * np.nan

        # 日平均を計算してリストに追加
        if np.all(np.isnan(period_data)):
            periodic_avg = period_data[0]  # または適切なデフォルト値
            periodic_err = period_errs[0]
        else:
            periodic_avg = np.nanmean(period_data, axis=0)
            periodic_err = nanerror(period_errs, axis=0) if errs is not None else np.nanstd(period_data, axis=0) # `errs` が与えられていなければ標準偏差を返す

        periodic_averages.append(periodic_avg)
        periodic_errors.append(periodic_err)

    dtms = np.array(unique_days.astype('datetime64[ns]').tolist(), dtype=object)
    avgs = np.array(periodic_averages, dtype="float64")
    errs = np.array(periodic_errors, dtype='float64')
    return dtms, avgs, errs

def valid_convolve(xx, size):
    '''https://zenn.dev/bluepost/articles/1b7b580ab54e95
    # xxに対してsize個での移動平均を取る
    '''
    b = np.ones(size)/size
    xx_mean = np.convolve(xx, b, mode="same")

    n_conv = math.ceil(size/2)

    # 補正部分
    xx_mean[0] *= size/n_conv
    for i in range(1, n_conv):
        xx_mean[i] *= size/(i+n_conv)
        xx_mean[-i] *= size/(i + n_conv - (size % 2))
	# size%2は奇数偶数での違いに対応するため

    return xx_mean

def calc_correration(x, y):
    x_bar = np.nanmean(x) # 観測データの平均
    y_bar = np.nanmean(y) # 観測データの平均

    s_x = sum((x - x_bar)**2) # 分散 (*n)
    s_y = sum((y - y_bar)**2) # 分散 (*n)
    s_xy = sum((x - x_bar) * (y - y_bar)) # 共分散 (*n)

    cc = s_xy / (np.sqrt(s_x) * np.sqrt(s_y)) # 相関係数
    return cc

def calc_linear_fit(x, y, ey): # y = c + m * x
    err2 = ey ** 2
    s = np.nansum(1 / err2) # U_00
    sumx = np.nansum(x / err2) # U_01
    sumy = np.nansum(y / err2) # v_0
    sumxx = np.nansum(x * x / err2) # U_11
    sumxy = np.nansum(x * y / err2) # v_1
    
    n = len(x) # number of data points  # noqa: F841
    delta = s * sumxx - sumx * sumx # compute the slope and intercept
    m = (s * sumxy - sumx * sumy) / delta # slope
    c = (sumy * sumxx - sumx * sumxy) / delta # intercept
    cov = np.array([[sumxx, -sumx], [-sumx, s]]) / delta
    errm = np.sqrt(s / delta) # noqa: F841
    errc = np.sqrt(sumxx / delta) # noqa: F841
    
    # print(f"slope = {m:10.4f} +/- {errm:7.4f}")
    # print(f"intercept = {c:10.4f} +/- {errc:7.4f}")
    # print(np.sqrt(np.diag(cov)))
    
    # NDF = n - 2 # the number of degree of freedom
    # chisq = np.sum(((y - (m * x + c)) / ey)**2) / NDF
    # print(f"chi squared / NDF = {chisq:7.4f}")

    return (c, m), cov

