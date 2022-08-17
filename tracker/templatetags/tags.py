from django import template
from django.utils.html import format_html
from tracker.utils import constants


register = template.Library()


@register.simple_tag
def release_version():
    return constants.RELEASE_VERSION


@register.simple_tag
def copy_on_click(content: str, css_class: str = ""):
    """Tag that creates some HTML text that will be copied on click.

    Args:
        content (str): The content that you want to show and copy.
        css_class (str, optional): The TailwindCSS class to apply to this element. Defaults to "".

    Returns:
        str: The HTML tag that will be rendered in the browser.
    """
    return format_html(
        """<a class={0} _='on click writeText({1}) into the {2} clipboard 
                        then set {3} on #copied
                        then show #copied with *opacity 
                        then wait 1s 
                        then hide #copied with *opacity
                        then wait 700ms
                        then set {4} on #copied'>{1}</a> <em class='hidden transition-all duration-700 ease-in-out opacity-0' id='copied'>copied!</em>""",
        css_class,
        content,
        "navigator's",  # these few are part of the format due to string escaping fuckery
        "{style: 'display:inline'}",
        "{style: 'display:none'}",
    )


@register.simple_tag
def help_button(content: str):
    """Tag that creates a help button that when hovered will show whichever information you passed to it.

    Args:
        content (str): The information to show

    Returns:
        str: The HTML tag that will be rendered in the browser.
    """
    
    return ""
