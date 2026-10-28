#! Python 3
#* https://zenn.dev/watarungurunnn/articles/3c8deeff7ab772
import numpy as np
from itertools import chain, islice
from collections import deque
from typing import Iterable, Union
from .fit import nanerror

def running_mean(iterable: Iterable[float], n: int, axis=None) -> Iterable[float]:
    it = iter(iterable) # データをイテレータに変換して呼び出せる状態にする
    d = deque(islice(it, n-1)) # islice でイテレータの先頭から n-1 個の要素を deque
    d.appendleft(0) # d のサイズが n になるように左端に詰め物 (なんでもいいから 0)
    # s = sum(d) # 平均計算の分子の合計値
    for elem in it:
        # print(elem, d_pop := d.popleft(), d)
        # s += elem - d_pop # d.popleft()
        # d.append(elem)
        # yield float(s / n)

        # print(d)
        d.popleft() # 左端の要素を取り出して削除
        # print(d)
        d.append(elem) # イテレータから取り出した要素を右端に追加 -> 窓の移動
        # print(d)
        ma = np.nanmean(d, axis=axis) # 平均計算
        # print(ma)
        yield float(ma)

def stream_running_mean(stream: Iterable[Union[int, float]], window_size: int, axis=None) -> Iterable[float]:
    return chain(
        [float('nan')] * (window_size // 2),
        running_mean(stream, window_size, axis),
        [float('nan')] * (window_size - 1 - window_size // 2)
    )

def moving_average(data, size, axis=None):
    """
    data: (n, d)
    size: 移動平均のサイズ
    return: data[i-size:i]のデータの平均。i < sizeの場合は最初からi行目までで計算。
    """
    result = []
    # 1次元データの場合の分岐
    if data.ndim == 1:
        xx_mean = np.array(list(stream_running_mean(data, size, axis)))
        return xx_mean
    
    for i in range(data.shape[1]):
        xx = data[:, i]
        # b = np.ones(size)/size
        xx_mean = np.array(list(stream_running_mean(xx, size, axis)))
        # # 補正部分
        # for j in range(min(size-1, len(xx))):
        #     xx_mean[j] *= size/(j + 1)
        result.append(xx_mean.reshape(-1, 1))
    return np.hstack(result)

def running_error(iterable: Iterable[float], n: int, axis=None) -> Iterable[float]:
    it = iter(iterable) # データをイテレータに変換して呼び出せる状態にする
    d = deque(islice(it, n-1)) # islice でイテレータの先頭から n-1 個の要素を deque
    d.appendleft(0) # d のサイズが n になるように左端に詰め物 (なんでもいいから 0)
    # s = sum(d) # 平均計算の分子の合計値
    for elem in it:
        # print(elem, d_pop := d.popleft(), d)
        # s += elem - d_pop # d.popleft()
        # d.append(elem)
        # yield float(s / n)

        # print(d)
        d.popleft() # 左端の要素を取り出して削除
        # print(d)
        d.append(elem) # イテレータから取り出した要素を右端に追加 -> 窓の移動
        # print(d)
        ma = nanerror(d, axis=axis) # 平均計算
        # print(ma)
        yield float(ma)

def stream_running_error(stream: Iterable[Union[int, float]], window_size: int, axis=None) -> Iterable[float]:
    return chain(
        [float('nan')] * (window_size // 2),
        running_error(stream, window_size, axis),
        [float('nan')] * (window_size - 1 - window_size // 2)
    )

def moving_error(data, size, axis=None):
    """
    data: (n, d)
    size: 移動平均のサイズ
    return: data[i-size:i]のデータの平均。i < sizeの場合は最初からi行目までで計算。
    """
    result = []
    for i in range(data.shape[1]):
        xx = data[:, i]
        # b = np.ones(size)/size
        xx_error = np.array(list(stream_running_error(xx, size, axis)))
        # # 補正部分
        # for j in range(min(size-1, len(xx))):
        #     xx_mean[j] *= size/(j + 1)
        result.append(xx_error.reshape(-1, 1))
    return np.hstack(result)


def moving_std(data, size, return_average=True):
    """
    data: (n, d)
    size: 移動平均のサイズ
    return_average: 平均も返すかどうか
    return: data[i-size:i]のデータの標準偏差(と平均)。i < sizeの場合は最初からi行目までで計算。
        (n, d) or (n, d) * 2
    """
    result = []
    ma = moving_average(data, size)
    
    for i in range(data.shape[1]):
        xx = data[:, i]
        xx_std = np.zeros(len(xx))
        
        # 各点での移動標準偏差を計算
        for j in range(len(xx)):
            if j < size:
                # ウィンドウサイズより小さい場合は、最初からj+1個のデータで計算
                window_data = xx[:j+1]
                xx_std[j] = np.std(window_data, ddof=0)  # ddof=0で母標準偏差
            else:
                # ウィンドウサイズ以上の場合は、直前size個のデータで計算
                window_data = xx[j-size+1:j+1]
                xx_std[j] = np.std(window_data, ddof=0)
        
        result.append(xx_std.reshape(-1, 1))
    
    ms = np.hstack(result)
    if return_average:
        return ms, ma
    else:
        return ms

def moving_std_fast(data, size, return_average=True):
    """
    高速版の移動標準偏差計算（畳み込みを使用）
    data: (n, d)
    size: 移動平均のサイズ
    return_average: 平均も返すかどうか
    return: data[i-size:i]のデータの標準偏差(と平均)。
    """
    result = []
    ma = moving_average(data, size)
    
    for i in range(data.shape[1]):
        xx = data[:, i]
        xx_mean = ma[:, i]
        
        # E[X^2]を計算
        b = np.ones(size)/size
        xx_squared_mean = np.convolve(xx**2, b, mode="full")[:len(xx)]
        
        # 補正部分（最初のsize-1個）
        for j in range(min(size-1, len(xx))):
            xx_squared_mean[j] *= size/(j + 1)
        
        # Var(X) = E[X^2] - E[X]^2
        variance = xx_squared_mean - xx_mean**2
        
        # 数値誤差で負になることがあるので、0でクリップ
        variance = np.maximum(variance, 0)
        
        xx_std = np.sqrt(variance)
        result.append(xx_std.reshape(-1, 1))
    
    ms = np.hstack(result)
    if return_average:
        return ms, ma
    else:
        return ms

def moving_standardization(data, size, return_full=True):
    """
    data: (n, d)
    size: 移動平均のサイズ
    return_full: Trueの場合、返り値のサイズはdataと一致する。
    return: (n, d)
    """
    ms, ma = moving_std_fast(data, size)
    
    if return_full:
        # 各データポイントを、その直前のウィンドウの統計量で標準化
        result = np.zeros_like(data)
        
        for i in range(len(data)):
            if i == 0:
                # 最初のデータはそのまま
                result[i] = data[i]
            else:
                # i番目のデータは、i-1番目までのデータの統計量で標準化
                # 標準偏差が0の場合は標準化しない
                mask = ms[i-1] > 1e-10
                result[i] = np.where(mask, (data[i] - ma[i-1]) / ms[i-1], data[i] - ma[i-1])
        
        return result
    else:
        # size以降のデータのみ返す
        mask = ms[size-1:-1] > 1e-10
        return np.where(mask, (data[size:] - ma[size-1:-1]) / ms[size-1:-1], 
                       data[size:] - ma[size-1:-1])

# 使用例とテスト
if __name__ == "__main__":
    # 1次元データでのテスト
    print("=== 1次元データのテスト ===")
    # data = np.arange(10).reshape(10, 1).astype(float)
    data = np.array([1, 2, 3, 4, 5, np.nan, 7, 8, 9, 10]).reshape(10, 1).astype(float)
    print("元データ:")
    print(data.flatten())

    window_size = 3
    print(f"{window_size}点移動平均:")
    # print(list(running_mean(data, window_size)))
    result = np.array(list(stream_running_mean(data, window_size)))
    # print(result)
    for i, value in enumerate(result):
        print(f"  位置 {i}: {value:.2f}")

    # 移動平均のテスト
    ma = moving_average(data, 3)
    print("\n移動平均 (window size=3):")
    print(ma.flatten())

    # 移動標準偏差のテスト
    ms, _ = moving_std_fast(data, 3)
    print("\n移動標準偏差 (window size=3):")
    print(ms.flatten())

    # 標準化のテスト
    data_standardized = moving_standardization(data, 3)
    print("\n標準化後:")
    print(data_standardized.flatten())

    # 多次元データでのテスト
    print("\n\n=== 多次元データのテスト ===")
    np.random.seed(42)
    data_2d = np.random.randn(100, 3) * np.array([1, 5, 10]) + np.array([0, 10, -5])

    data_2d_standardized = moving_standardization(data_2d, 10)

    print(f"元データの形状: {data_2d.shape}")
    print(f"標準化後の形状: {data_2d_standardized.shape}")
    print("\n元データの統計量:")
    print(f"平均: {np.mean(data_2d, axis=0)}")
    print(f"標準偏差: {np.std(data_2d, axis=0)}")

    print("\n標準化後のデータ（最後の10行）の統計量:")
    print(f"平均: {np.mean(data_2d_standardized[-10:], axis=0)}")
    print(f"標準偏差: {np.std(data_2d_standardized[-10:], axis=0)}")

    # オンライン異常検知の使用例
    print("\n\n=== オンライン異常検知の例 ===")
    # 正常データ
    normal_data = np.random.randn(50, 1)
    # 異常データ（外れ値）
    anomaly_data = np.array([[10], [-8], [0.5]])

    # 正常データで移動統計量を計算
    window_size = 20
    ms, ma = moving_std_fast(normal_data, window_size)

    # 最後のウィンドウの統計量を使って異常データを標準化
    last_mean = ma[-1, 0]
    last_std = ms[-1, 0]

    standardized_anomaly = (anomaly_data - last_mean) / last_std

    print("正常データの最後のウィンドウの統計量:")
    print(f"平均: {last_mean:.3f}, 標準偏差: {last_std:.3f}")
    print(f"\n異常データ: {anomaly_data.flatten()}")
    print(f"標準化後: {standardized_anomaly.flatten()}")
    print("\n|z-score| > 3 の異常判定:")
    for i, z in enumerate(standardized_anomaly.flatten()):
        is_anomaly = abs(z) > 3
        print(f"データ{i+1}: z-score = {z:.3f}, 異常: {is_anomaly}")
