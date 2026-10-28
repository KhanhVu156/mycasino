from django import forms
from django.contrib.auth.forms import AuthenticationForm

class CustomAuthenticationForm(AuthenticationForm):
    remember_me = forms.BooleanField(
        required=False,
        initial=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )

class SpinForm(forms.Form):
    """
    Form dùng để validate dữ liệu cược từ Client gửi lên.
    Tránh việc người dùng gửi số tiền âm hoặc số tiền quá lớn.
    """
    bet = forms.IntegerField(min_value=1, required=True)