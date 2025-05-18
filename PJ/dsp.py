import os
from pydub import AudioSegment
import librosa
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd


# 将 m4a 格式转换为 wav 格式
def formatConvert(audio_path, audio_format):
    audio_name = os.path.splitext(audio_path)[0]
    audio = AudioSegment.from_file(audio_path, format=audio_format)
    audio.export(audio_name + ".wav", format="wav")


# 预加重
def preEmphasis(x, alpha=0.97):
    return np.append(x[0], x[1:] - alpha * x[:-1])


# 快速傅里叶变换
def FFT(x):
    x = np.asarray(x, dtype=complex)
    N = len(x)
    assert N > 0 and (N & (N - 1)) == 0, "N must be a power of 2"
    
    if N <= 1:
        return x
    
    # X(k) = G(k) + e^(-2πk/N) H(k)
    G = FFT(x[0::2])     # g(r) = x(2r)
    H = FFT(x[1::2])      # h(r) = x(2r+1)
    
    # 旋转因子列表
    # W1, W2, ..., W(N/2-1)
    W = np.exp(-2j * np.pi * np.arange(N // 2) / N)
    
    # 
    X = np.zeros(N, dtype=complex)
    X[:N//2] = G + W * H
    X[N//2:] = G - W * H
    
    return X


# 计算 STFT
# y: 音频信号
# sr: 采样率
# win: 窗口大小
# step: 步长
def STFT(y, sr, win, step):
    # 分帧
    frames = []
    for i in range(0, len(y) - win, step):
        frame = np.hanning(win) * y[i:i + win]
        frames.append(frame)
    
    # 计算 STFT
    stft = []
    for frame in frames:
        # 计算 FFT
        fft = FFT(frame)
        stft.append(np.abs(fft[:win // 2 + 1])) # 幅值取绝对值，只关心正频率
    
    # 转置为 (频率, 时间) 形式
    return np.array(stft).T


def hz2mel(hz):
    return 2595 * np.log10(1 + hz / 700)

def mel2hz(mel):
    return 700 * (10**(mel / 2595) - 1)


# Mel 滤波器组
def melFilterBank(sr, n_fft, n_filter):
    min_hz = 0
    max_hz = sr / 2

    min_mel = hz2mel(min_hz)
    max_mel = hz2mel(max_hz)

    # 在梅尔刻度上均匀分布
    mel_points = np.linspace(min_mel, max_mel, n_filter + 2)
    hz_points = mel2hz(mel_points)

    indices = np.floor((n_fft + 1) * hz_points / sr).astype(int)    # 在 FFT 结果数组中的索引

    # 空滤波器组
    filterbank = np.zeros((n_filter, n_fft // 2 + 1))

    # 构建每一个滤波器
    for i in range(n_filter):
        left = indices[i]
        center = indices[i+1]
        right = indices[i+2]

        # 三角形滤波器
        for j in range(left, center):
            filterbank[i][j] = (j - left) / (center - left)
        for j in range(center, right):
            filterbank[i][j] = (right - j) / (right - center)

    return filterbank


# 计算 MFCC
# y: 音频信号
# sr: 采样率
# N: 窗口大小
# D: MFCC系数数量，通常为 12~16
# M: Mel 滤波器组数量，通常为 20~40
def computeMFCC(y, sr, N, D=13, M=26):
    # 预加重
    y_ = preEmphasis(y)

    # 分帧 + STFT
    spec = STFT(y_, sr, N, N//2)                # (频率, 窗口)

    # 转换为功率谱
    power_spec = np.square(spec) / N            # (频率, 窗口)

    # 应用 Mel 滤波器组
    filter_bank = melFilterBank(sr, N, M)
    mel_spec = np.dot(filter_bank, power_spec)  # (滤波器数量, 窗口)

    # 离散余弦变换(DCT)
    log_mel_spec = np.log(mel_spec + 1e-10)     # 取对数
    mfcc = np.zeros((D, log_mel_spec.shape[1])) # (系数数量, 窗口数量)
    for i in range(D):
        for j in range(M):
            mfcc[i] += log_mel_spec[j] * np.cos(np.pi * (j - 0.5) * i / M)

    return mfcc