from django.contrib.auth import authenticate
from django import forms
from .models import User, Player


class LogForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)

    def clean(self):
        email = self.cleaned_data.get('email')
        password = self.cleaned_data.get('password')
        user = authenticate(username=email, password=password)
        if not user or not user.is_active:
            raise forms.ValidationError("Sorry, that login was invalid. Please try again.")
        return self.cleaned_data

    def login(self, request):
        email = self.cleaned_data.get('email')
        password = self.cleaned_data.get('password')
        user = authenticate(username=email, password=password)
        return user

    class Meta:
        model = User
        fields = ['email', 'password']


class RegForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)

    def clean(self):
        email = self.cleaned_data.get('email')
        if User.objects.exclude(pk=self.instance.pk).filter(email=email).exists():
            raise forms.ValidationError("Sorry, user blah blah blah")
        return self.cleaned_data

    def save(self, email):
        instance = super().save(commit=False)
        instance.username = email
        return instance

    def register(self):
        email = self.cleaned_data.get('email')
        password = self.cleaned_data.get('password')
        user = self.save(email)
        user.set_password(password)
        user.save()
        user = authenticate(username=email, password=password)
        return user

    class Meta:
        model = User
        fields = ['email', 'password']


class PlayerRequestForm(forms.ModelForm):

    def clean(self):
        name = self.cleaned_data.get('name')
        if Player.objects.filter(name=name).exists():
            raise forms.ValidationError("Sorry, user blah blah blah")
        return self.cleaned_data

    class Meta:
        model = Player
        fields = ['name']

