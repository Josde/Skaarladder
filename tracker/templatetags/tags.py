from django import template
from django.utils.html import format_html


from tracker.utils import constants


register = template.Library()


@register.simple_tag
def release_version():
    return constants.RELEASE_VERSION
