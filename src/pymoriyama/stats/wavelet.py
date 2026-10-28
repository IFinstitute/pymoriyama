import numpy as np


def compute_cwt(signal, dt, dj=0.125, omega0=6.0, s0=None):
    """
    連続ウェーブレット変換を計算する関数
    
    Parameters
    ----------
    signal : ndarray
        入力信号
    dt : float
        サンプリング間隔
    dj : float, optional
        スケール間隔 (default: 0.125)
    omega0 : float, optional
        Morlet ウェーブレットのパラメータ (default: 6.0)
    s0 : float, optional
        最小スケール (default: 2.0*dt)
    
    Returns
    -------
    cwt : ndarray
        ウェーブレット係数 (複素数配列)
    freq_cwt : ndarray
        対応する周波数配列
    s_to_f : float
        スケール-周波数変換係数
    """
    if s0 is None:
        s0 = 2.0 * dt
    
    # n_cwt をlen(signal)よりも大きな2のべき乗の数になるように設定
    n_cwt = int(2**(np.ceil(np.log2(len(signal)))))
    
    # パラメータ定義
    J = int(np.log2(n_cwt*dt/s0)/dj)
    
    # スケール配列
    s = s0 * 2.0**(dj*np.arange(0, J+1, 1))
    
    # ゼロパディングとDC成分除去
    x = np.zeros(n_cwt, dtype=complex)
    x[0:len(signal)] = signal[0:len(signal)] - np.mean(signal)
    
    # omega配列
    omega = 2.0*np.pi*np.fft.fftfreq(n_cwt, dt)
    
    # FFTを使ったウェーブレット変換
    X = np.fft.fft(x)
    cwt = np.zeros((J+1, n_cwt), dtype=complex)
    psi = np.zeros((J+1, n_cwt), dtype=complex)
    Hev = np.array(omega > 0.0)
    
    for j in range(J+1):
        psi[j, :] = (
            np.sqrt(2.0*np.pi*s[j]/dt)
            *np.pi**(-0.25)
            *np.exp(-0.5*(s[j]*omega-omega0)**2)
            *Hev
            )
        cwt[j, :] = np.fft.ifft(X*np.conjugate(psi[j, :]))
    
    # スケール-周波数変換
    s_to_f = (omega0 + np.sqrt(2.0 + omega0**2)) / (4.0*np.pi)
    freq_cwt = s_to_f / s
    cwt = cwt[:, 0:len(signal)]
    # psi = psi[:, 0:len(signal)]
    
    return cwt, freq_cwt, s_to_f, psi, omega


def compute_coi(time_array, dt, s_to_f):
    """
    Cone of Influence (COI) を計算する関数
    
    Parameters
    ----------
    time_array : ndarray
        時間配列
    dt : float
        サンプリング間隔
    s_to_f : float
        スケール-周波数変換係数
    
    Returns
    -------
    COI : ndarray
        Cone of Influence
    """
    COI = np.zeros_like(time_array)
    COI[0] = 0.5/dt
    COI[1:len(time_array)//2] = np.sqrt(2)*s_to_f/time_array[1:len(time_array)//2]
    COI[len(time_array)//2:-1] = np.sqrt(2)*s_to_f/(time_array[-1]-time_array[len(time_array)//2:-1])
    COI[-1] = 0.5/dt
    
    return COI


def fast_s_transform(signal, dt):
    """
    FFTベースの高速S変換を計算する関数
    
    Parameters
    ----------
    signal : ndarray
        入力信号
    dt : float
        サンプリング間隔
    
    Returns
    -------
    S : ndarray
        Stockwell 係数 (複素数配列)
    freqs : ndarray
        対応する周波数配列
    t : float
        対応する時系列
    """
    N = len(signal)
    t = np.arange(N) * dt
    freqs = np.fft.fftfreq(N, d=dt)

    X = np.fft.fft(signal)
    S = np.zeros((N, N), dtype=np.complex128)
    g_centered = np.zeros((N, N), dtype=float)

    for k, f in enumerate(freqs):
        if f == 0:
            S[k, :] = np.mean(signal)  # DC成分
            continue
        
        # 1. 周波数スペクトルを -k だけシフト (S変換の正規手順)
        X_shifted = np.roll(X, -k)
        
        # 2. 正確な S 変換用ガウス窓 (-2 * pi^2 を適用)
        g_centered[k, :] = np.exp(-2 * (np.pi**2) * (freqs / f)**2)
        
        # 3. 逆FFTにより局所複素包絡線を計算
        S[k, :] = np.fft.ifft(X_shifted * g_centered[k, :])
    
    pos_mask = freqs >= 0
    return S[pos_mask, :], freqs[pos_mask], t


def compute_coi_stockwell(time_array):
    """
    S変換用の COI (e-folding distance) を計算する関数
    """
    # 両端からの最短距離 tau を計算
    t_from_start = time_array - time_array[0]
    t_from_end = time_array[-1] - time_array
    tau = np.minimum(t_from_start, t_from_end)
    
    # 始点・終点でのゼロ除算を回避
    tau[tau == 0] = 1e-10
    
    # f_COI = sqrt(2) / tau
    COI = np.sqrt(2) / tau
    return COI
