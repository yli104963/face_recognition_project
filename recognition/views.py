from django.shortcuts import render, redirect
from django.core.files.base import ContentFile
from .models import Face
import face_recognition
import cv2
import numpy as np
import os
import uuid
import base64
from django.conf import settings
import time

# Index page to list all stored faces
def index(request):
    faces = Face.objects.all()
    return render(request, 'recognition/index.html', {'faces': faces})


# Function to capture photo from the webcam
def capture_photo():
    video_capture = cv2.VideoCapture(0)
    ret, frame = video_capture.read()

    if not ret:
        video_capture.release()
        return None, '摄像头打开失败'

    # Generate a unique name for the photo and save it
    photo_name = f"{uuid.uuid4()}.jpg"
    photo_path = os.path.join('faces', photo_name)
    cv2.imwrite(photo_path, frame)
    video_capture.release()

    return photo_path, None


# Function to handle face addition
def detect(request):
    if request.method == "POST":
        name = request.POST.get('name')
        photo_data = request.POST.get('photo_data')

        if not name or not photo_data:
            return render(request, 'recognition/index.html', {'error': '姓名或照片数据缺失'})

        try:
            format, imgstr = photo_data.split(';base64,')
            ext = format.split('/')[-1]
            data = base64.b64decode(imgstr)
        except Exception as e:
            print(f"Error decoding photo data: {e}")
            return render(request, 'recognition/index.html', {'error': '照片数据解码失败'})

        try:
            photo_name = f"{uuid.uuid4()}.{ext}"
            photo_path = os.path.join('faces', photo_name)
            with open(photo_path, 'wb') as f:
                f.write(data)
        except Exception as e:
            print(f"Error saving photo: {e}")
            return render(request, 'recognition/index.html', {'error': '保存照片失败'})

        try:
            with open(photo_path, 'rb') as f:
                image_file = ContentFile(f.read(), name=photo_name)
                face = Face(name=name, image=image_file)
                face.save()
        except Exception as e:
            print(f"Error saving photo to database: {e}")
            os.remove(photo_path)
            return render(request, 'recognition/index.html', {'error': '保存照片到数据库失败'})

        os.remove(photo_path)
        return redirect('index')

    return render(request, 'recognition/index.html')


def recognize(request):
    face_now_dir = os.path.join(settings.MEDIA_ROOT, 'face_now')

    # 创建目录，如果不存在的话
    if not os.path.exists(face_now_dir):
        os.makedirs(face_now_dir)

    # 打开摄像头
    video_capture = cv2.VideoCapture(0)

    # 增加初始化延时，确保摄像头已准备好
    time.sleep(3)

    ret, frame = video_capture.read()
    attempts = 0
    max_attempts = 5

    # 尝试多次读取帧，确保读到有效帧
    while not ret and attempts < max_attempts:
        ret, frame = video_capture.read()
        attempts += 1

    if not ret:
        video_capture.release()
        return render(request, 'recognition/recognize_face.html', {'error': '摄像头打开失败'})

    # 保存抓拍照片
    now_photo_name = f"{uuid.uuid4()}.jpg"
    now_photo_path = os.path.join(face_now_dir, now_photo_name)
    cv2.imwrite(now_photo_path, frame)
    video_capture.release()

    # 生成照片的 URL
    now_photo_url = request.build_absolute_uri(os.path.join(settings.MEDIA_URL, 'face_now', now_photo_name))

    # 将图像转换为 RGB 格式
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    # 加载已知人脸数据
    known_face_encodings = []
    known_face_names = []
    known_face_images = []

    for face in Face.objects.all():
        image = face_recognition.load_image_file(face.image.path)
        encodings = face_recognition.face_encodings(image)
        if encodings:
            known_face_encodings.append(encodings[0])
            known_face_names.append(face.name)
            known_face_images.append(face.image.url)

    try:
        # 查找图像中的所有人脸
        face_locations = face_recognition.face_locations(rgb_frame)
        face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)
    except Exception as e:
        print(f"Error during face recognition: {e}")
        return render(request, 'recognition/recognize_face.html', {'error': '人脸识别过程中发生错误'})

    face_results = []
    for face_encoding, face_location in zip(face_encodings, face_locations):
        if known_face_encodings:
            matches = face_recognition.compare_faces(known_face_encodings, face_encoding)
            face_distances = face_recognition.face_distance(known_face_encodings, face_encoding)
            best_match_index = np.argmin(face_distances)

            if matches[best_match_index]:
                name = known_face_names[best_match_index]
                similarity = 1 - face_distances[best_match_index]
                face_results.append({
                    'name': name,
                    'image_url': known_face_images[best_match_index],
                    'similarity': similarity,
                    'location': face_location
                })
            else:
                face_results.append({
                    'name': "无相关人物信息",
                    'image_url': None,
                    'similarity': None,
                    'location': face_location
                })

    return render(request, 'recognition/recognize_face.html', {
        'current_image_url': now_photo_url,
        'face_results': face_results,
        'no_match': not any(result['name'] != "无相关人物信息" for result in face_results)
    })

def recognize_image(request):
    if request.method == 'POST' and request.FILES.get('image'):
        uploaded_image = request.FILES['image']
        image_path = os.path.join(settings.MEDIA_ROOT, 'uploaded_images', uploaded_image.name)

        # 创建目录，如果不存在的话
        if not os.path.exists(os.path.dirname(image_path)):
            os.makedirs(os.path.dirname(image_path))

        # 保存上传的图片到指定目录
        with open(image_path, 'wb+') as f:
            for chunk in uploaded_image.chunks():
                f.write(chunk)

        # 加载上传的图片进行面部识别
        image = face_recognition.load_image_file(image_path)
        face_locations = face_recognition.face_locations(image)
        face_encodings = face_recognition.face_encodings(image, face_locations)

        known_face_encodings = []
        known_face_names = []
        known_face_images = []

        # 加载数据库中的已知人脸
        for face in Face.objects.all():
            known_image = face_recognition.load_image_file(face.image.path)
            known_encodings = face_recognition.face_encodings(known_image)
            if known_encodings:
                known_face_encodings.append(known_encodings[0])
                known_face_names.append(face.name)
                known_face_images.append(face.image.url)

        face_results = []
        for face_encoding in face_encodings:
            matches = face_recognition.compare_faces(known_face_encodings, face_encoding)
            face_distances = face_recognition.face_distance(known_face_encodings, face_encoding)
            best_match_index = np.argmin(face_distances)

            if matches[best_match_index]:
                name = known_face_names[best_match_index]
                face_results.append({
                    'name': name,
                    'distance': face_distances[best_match_index],
                    'image_url': known_face_images[best_match_index]
                })

        # 生成上传图片的完整 URL
        uploaded_image_url = request.build_absolute_uri(os.path.join(settings.MEDIA_URL, 'uploaded_images', uploaded_image.name))

        return render(request, 'recognition/recognize_image.html', {
            'uploaded_image_url': uploaded_image_url,
            'face_results': face_results,
            'no_match': not face_results
        })

    return render(request, 'recognition/recognize_image.html')
