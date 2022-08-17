from django import template
from tracker.utils import constants
register = template.Library()

@register.simple_tag
def release_version():
    return constants.RELEASE_VERSION