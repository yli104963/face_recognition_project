# admin.py
from django.contrib import admin
from django.utils.html import format_html
from .models import Face


class FaceAdmin(admin.ModelAdmin):
    list_display = ('id','name', 'image_url')

    def image_url(self, obj):
        return format_html('<a href="{}">{}</a>', obj.image.url, obj.image.url)

    image_url.short_description = '照片链接'


admin.site.register(Face, FaceAdmin)