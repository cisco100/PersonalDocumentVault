from django import forms
from authen.models import PinCode

class PinCodeForm(forms.ModelForm):
    class Meta:
        model = PinCode
        fields = "__all__"

