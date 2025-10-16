"""
OGA-HDIC 高維度變數選擇方法

此模組實作 Orthogonal Greedy Algorithm with High-Dimensional Information Criterion
適用於變數數量遠大於樣本數的預測問題。
"""

from .method import OGAHDICMethod

__all__ = ['OGAHDICMethod']
