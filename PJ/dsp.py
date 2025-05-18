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


# 计算单帧信号的过零率
def zero_crossing_rate(frame):
    signs = np.sign(frame)
    diffs = np.abs(signs[1:] - signs[:-1]) / 2
    zcr = np.sum(diffs)
    return zcr / len(frame)


# 计算短时过零率
# y: 信号
# win: 窗口大小（帧长）
# step: 步长
def short_time_zcr(y, win, step):
    zcrs = []
    for i in range(0, len(y) - win + 1, step):
        frame = y[i:i + win]
        zcr = zero_crossing_rate(frame)
        zcrs.append(zcr)
    return np.array(zcrs)


# 计算短时能量
# y: 信号
# win: 窗口大小（帧长）
# step: 步长
def short_time_energy(y, win, step):
    energy = []
    for i in range(0, len(y) - win + 1, step):
        frame = y[i:i + win]
        energy.append(np.sum(frame ** 2))  # 平方和计算能量
    return np.array(energy)


# 基于双门限法的语音端点检测 (voice activity detection)
# y: 输入音频信号
# sr: 采样率
# win: 帧长
# step: 帧移(ms)
# energy_ratio: 能量阈值（相对于最大能量的比例）
# zcr_thresh: 过零率阈值（绝对阈值）
# silence_duration: 静音持续时间（秒）
# 语音段起止索引列表 [(start1, end1), (start2, end2), ...]
def vad(y, sr, win, step, energy_ratio=0.2, zcr_thresh=0.15, silence_duration=0.2):
    # 计算短时能量和过零率
    energy = short_time_energy(y, win, step)
    zcrs = short_time_zcr(y, win, step)

    # 正则化能量到[0, 1]
    if np.max(energy) > 0:
        energy = energy / np.max(energy)

    # 设置能量阈值
    high_thresh = energy_ratio
    low_thresh = energy_ratio * 0.5

    # 计算静音持续需要的帧数
    silence_frames = int(silence_duration * sr / step)

    segments = []       # 语音段列表
    inSpeech = False    # 是否在语音段中
    start = 0           # 语音段开始索引
    silenceCount = 0   # 静音帧计数

    # 遍历每一帧
    for i in range(len(energy)):
        if not inSpeech:
            # 使用高能量阈值和过零率来检测语音开始
            if energy[i] > high_thresh:
                inSpeech = True
                silenceCount = 0
                # 往回看，使用低能量阈值和过零率来检测语音开始
                for j in range(i-1, -1, -1):
                    if energy[j] < low_thresh and zcrs[j] < zcr_thresh:
                        start = j + 1
                        break
                else:
                    start = i
        else:
            # 使用低能量阈值和过零率来检测静音帧
            if energy[i] < low_thresh and zcrs[i] < zcr_thresh:
                silenceCount += 1
                # 只有当静音持续足够长时间时，才认为语音结束
                if silenceCount >= silence_frames:
                    inSpeech = False
                    # 结束点是静音开始的地方
                    end = i - silenceCount + 1
                    segments.append((start * step, end * step))
                    silenceCount = 0
            else:
                # 重置静音计数
                silenceCount = 0

    # 处理语音段到达音频末尾的情况
    if inSpeech:
        segments.append((start * step, len(energy) * step))

    return segments