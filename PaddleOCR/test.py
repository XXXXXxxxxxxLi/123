import cv2
import matplotlib.pyplot as plt
import numpy as np
import os

# 选择2张图像可视化
img1 = cv2.imread("doc/imgs/00006737.jpg")
img2 = cv2.imread("doc/imgs/00056221.jpg")
plt.figure(figsize=(15, 6))
plt.subplot(1, 2, 1)  # 定义 1行2列
plt.imshow(img1[:, :, ::-1])  # 第1列 放 img1 ，::-1 => axis 3 倒序
plt.subplot(1, 2, 2)  # 定义 1行2列
plt.imshow(img2[:, :, ::-1])  # 第2列 放 img1
plt.show()

