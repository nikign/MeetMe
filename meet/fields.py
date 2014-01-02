from django import forms
from templatetags import i18n

class PersianTimeField(forms.TimeField):
    "A time field accepting Persian/Arabic digits in addition to Latin digits."

    def __init__(self, initial=None, *args, **kwargs):
        if initial:
            initial = i18n.localize_digits(initial)
        super(PersianTimeField, self).__init__(initial=initial, *args, **kwargs)

    def clean(self, value):
        value = i18n.convert_iranian_digits_to_latin(value)
        return super(PersianTimeField, self).clean(value)

    def to_python(self, value):
        value = i18n.convert_iranian_digits_to_latin(value)
        return super(PersianTimeField, self).to_python(value)

