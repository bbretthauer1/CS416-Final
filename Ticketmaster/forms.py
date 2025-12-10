from django import forms
from .models import User, Comments


class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = "__all__"
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'password': forms.PasswordInput(attrs={'class': 'form-control mb-2'}),
        }

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comments
        fields = ('comment','event', 'user')
        widgets = {
            'event': forms.HiddenInput(),
            'user': forms.HiddenInput(),
            'comment': forms.TextInput(attrs={'class': 'form-control'}),
        }