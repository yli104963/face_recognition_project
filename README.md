# 人脸识别项目

## 项目概述

这个项目是一个人脸识别系统，利用 Django 框架结合 `face_recognition` 库实现了人脸的捕捉、存储、识别及管理功能。用户可以通过摄像头实时抓拍照片，将其与数据库中的人脸数据进行比对，并显示识别结果。

## 目录

- [功能](#功能)
- [技术栈](#技术栈)
- [安装指南](#安装指南)
- [配置](#配置)
- [使用说明](#使用说明)
  - [新增人脸](#新增人脸)
  - [人脸识别](#人脸识别)
  - [图片上传识别](#图片上传识别)
- [文件结构](#文件结构)
- [常见问题](#常见问题)
- [贡献](#贡献)
- [许可证](#许可证)

## 功能

- **新增人脸**：通过摄像头拍摄并存储人脸图像到数据库。
- **人脸识别**：实时识别摄像头拍摄到的人脸，并与数据库中的人脸进行比对。
- **图片上传识别**：支持上传图片进行人脸识别，并显示识别结果。

## 技术栈

- **Django**：Web框架
- **face_recognition**：人脸识别库
- **OpenCV**：计算机视觉库
- **Python**：编程语言
- **Bootstrap**：前端样式框架

## 安装指南

1. **克隆项目**

    ```bash
    git clone https://github.com/yourusername/face_recognition_project.git
    cd face_recognition_project
    ```

2. **创建虚拟环境**

    ```bash
    python -m venv venv
    source venv/bin/activate  # 在 Windows 上使用 `venv\Scripts\activate`
    ```

3. **安装依赖**

    ```bash
    pip install -r requirements.txt
    ```

4. **运行迁移**

    ```bash
    python manage.py makemigrations
    python manage.py migrate
    ```

5. **创建超级用户**

    ```bash
    python manage.py createsuperuser
    ```

6. **运行开发服务器**

    ```bash
    python manage.py runserver
    ```

## 配置

### `settings.py`

确保在 `settings.py` 中配置了媒体文件的路径：

```python
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
```

## 使用说明

### 新增人脸

	1.	访问 / 路由。
	2.	输入姓名并拍摄照片，点击“新增人脸”按钮。
	3.	照片将被保存到数据库，并与姓名关联。

### 人脸识别

	1.	访问 /recognize/ 路由。
	2.	摄像头将自动打开并拍摄当前画面。
	3.	系统将识别拍摄到的人脸，并与数据库中的人脸数据进行比对。
	4.	识别结果将显示在页面上，包括抓拍照片和数据库中的匹配照片。

### 图片上传识别

	1.	访问 /rec-img/ 路由。
	2.	上传一张图片进行识别。
	3.	系统将对上传的图片进行人脸识别，并显示识别结果。


