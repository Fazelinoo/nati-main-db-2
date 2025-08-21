from django import template
import jdatetime
from django.utils.safestring import mark_safe

register = template.Library()

@register.filter
def to_jalali(value):
    """
    تبدیل تاریخ میلادی (datetime.date یا datetime.datetime) به شمسی (جلالی)
    """
    if not value:
        return ''
    try:
        if hasattr(value, 'date'):
            value = value.date()
        jdate = jdatetime.date.fromgregorian(date=value)
        return f"{jdate.year}/{jdate.month:02}/{jdate.day:02}"
    except Exception:
        return str(value)
