from django import forms 
from django.contrib.auth.models import User
from django.contrib.auth import authenticate

from blog.models import Category, Post


class ContactForm(forms.Form):
    name=forms.CharField(label="Name",max_length=100,required=True)
    email=forms.EmailField(label="Email",required=True)
    message=forms.CharField(required=True)

class RegisterForm(forms.ModelForm):
    username=forms.CharField(label="Username",max_length=100,required=True)
    email=forms.EmailField(label="email",max_length=100,required=True)
    password=forms.CharField(label="password",max_length=100,required=True)
    password_confirm=forms.CharField(label="password_confirm",max_length=100,required=True)

    class Meta:
        model = User
        fields=['username','email','password']

    def clean(self):
        cleaned_data= super().clean()
        password=cleaned_data.get('password')
        password_confirm=cleaned_data.get('password_confirm')

        if password and password_confirm and password != password_confirm:  # For checking passwords
            raise forms.ValidationError("Passwords do not match")

class LoginForm(forms.Form):
    username=forms.CharField(label="Username",max_length=100,required=True)
    password=forms.CharField(label="Password",max_length=100,required=True)

    def clean(self):
        cleaned_data= super().clean()
        username=cleaned_data.get('username')
        password=cleaned_data.get('password')

        if username and password:
            user=authenticate(username=username,password=password)
            if user is None:
                raise forms.ValidationError("Invalid Username and Password :(")
            
class ForgotPasswordForm(forms.Form):
    email=forms.EmailField(label="Email",max_length=100,required=True)

    def clean(self):
        cleaned_data= super().clean()
        email= cleaned_data.get('email')
        if not User.objects.filter(email=email):
            raise forms.ValidationError("No User Registered With This Email !!")
        
class ResetPasswordForm(forms.Form):
    new_password=forms.CharField(label="New Password",min_length=8,required=True)
    confirm_password=forms.CharField(label="Confirm Password",min_length=8,required=True)

    def clean(self):
        cleaned_data = super().clean()
        new_password = cleaned_data.get('new_password')
        confirm_password = cleaned_data.get('confirm_password')

        if new_password and confirm_password and new_password != confirm_password:
            raise forms.ValidationError("Password do not match")
        
class PostForm(forms.ModelForm):
    title =forms.CharField(label="Title",max_length=100,required=True)
    content =forms.CharField(label="Content",max_length=400,required=True)
    category=forms.ModelChoiceField(label="Category",queryset=Category.objects.all(),required=True)
    img_url=forms.ImageField(label="Image",required=False)

    class Meta:
        model = Post
        fields=['title','content','category','img_url']

    def clean(self):
        cleaned_data = super().clean()
        title = cleaned_data.get('title')
        content =cleaned_data.get('content')

        if title and len(title)<5:
            raise forms.ValidationError("Title must be atleast 5 characters long")
        
        if content and len(content)<10:
            raise forms.ValidationError("Content must be atleast 10 characters long")
        
    def save(self, commit = ...):
        post = super().save(commit)
        cleaned_data = super().clean()

        if cleaned_data.get('img_url'):
            post.img_url = cleaned_data.get('img_url')
        else:
            img_url = "https://upload.wikimedia.org/wikipedia/commons/thumb/a/ac/No_image_available.svg/600px-No_image_available.svg.png"
            post.img_url = img_url

        if commit:
            post.save()
        return post

        
    