import base64
from django import template
from django.template.defaultfilters import stringfilter

register = template.Library()


@register.filter
@stringfilter
def encode_base64(image):
    with open(image.path, "rb") as f:
        encoded_string = base64.b64encode(f.read()).decode()
    return f"data:image/png;base64,{encoded_string}"