from django import template
register = template.Library()

from datetime import timedelta

@register.filter
def modulo(len_matches, mod):
    return len_matches % mod

@register.filter
def disp_timedelta(value):
    secs = int(value.seconds)
    sec = secs % 60
    min = int((secs - sec) / 60)
    return f'{min:02}:{sec:02}'

@register.filter
def m_result(value):
    return f'{value[0]}:{value[1]}'

@register.filter
def projrr(value):
    if type(value) is type((0, 0)):
        return f'{value[0]:.3f} | {value[1]:.3f}'
    else:
        return f'{value:.3f}'

@register.filter
def rawdate(value):
    return value.replace('T', ' ')
