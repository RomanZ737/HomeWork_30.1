import re

from rest_framework import serializers
from urllib.parse import urlparse


def validate_video_url(value):
    if not value:
        return value

    if not value.startswith(('http://', 'https://')):
        raise serializers.ValidationError('URL должен начинаться с http:// или https://')

    try:
        parsed = urlparse(value)
        domain = parsed.netloc.lower()

        if domain.startswith('www.'):
            domain = domain[4:]
    except Exception:
        raise serializers.ValidationError('Некорректный URL.')

    allowed_domains = ['youtube.com', 'www.youtube.com']

    if domain not in allowed_domains and not domain.endswith('.youtube.com'):
        raise serializers.ValidationError(
            "Ссылки на видео разрешены только с youtube.com."
        )

    return value

def validate_description(value):
    if not value:
        return value

    url_pattern = r'https?://[^\s]+'
    urls = re.findall(url_pattern, value)

    for url in urls:
        validate_video_url(url)

    return value
