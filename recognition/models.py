# models.py
from django.db import models
from django.db.models.signals import post_delete
from django.dispatch import receiver
import os

class Face(models.Model):
    name = models.CharField(max_length=100)
    image = models.ImageField(upload_to='faces/')

    class Meta:
        verbose_name = '人脸识别'
        verbose_name_plural = verbose_name

@receiver(post_delete, sender=Face)
def auto_delete_file_on_delete(sender, instance, **kwargs):
    """确保删除模型实例时也删除相关的文件"""
    if instance.image:
        if os.path.isfile(instance.image.path):
            os.remove(instance.image.path)