from django.shortcuts import get_object_or_404, render,redirect
from django.http import HttpResponse,Http404
from django.urls import reverse
import logging
from .models import Category, Post,AboutUs
from django.core.paginator import Paginator
from .forms import ContactForm, ForgotPasswordForm, LoginForm, PostForm,RegisterForm, ResetPasswordForm
from django.contrib import messages
from django.contrib.auth import authenticate,login as auth_login,logout as auth_logout

from django.contrib.auth.models import User
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode,urlsafe_base64_decode
from django.contrib.sites.shortcuts import get_current_site
from django.utils.encoding import force_bytes
from django.template.loader import render_to_string
from django.core.mail import send_mail
from django.contrib.auth.decorators import login_required,permission_required
from django.contrib.auth.models import Group

# Static demo data
# posts=[{'id':1,'title':'Post 1','content':'Contents of post 1'},
#        {'id':2,'title':'Post 2','content':'Contents of post 2'},
#        {'id':3,'title':'Post 3','content':'Contents of post 3'},
#        {'id':4,'title':'Post 4','content':'Contents of post 4'}
# ]

def index(request):
    blog_title_name="Latest Post"
    #getting posts from model
    all_posts = Post.objects.filter(is_published=True)
    # Pagination
    paginator=Paginator(all_posts,5)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request,'index.html',{'blog_title':blog_title_name,'page_obj':page_obj})

def detail(request,slug):
    if request.user and not request.user.has_perm('blog.view_post'):
        messages.error(request,"Sorry, you have no permission to view any posts")
        return redirect('blog:index')
    # static data
    # post=next((items for items in posts if items['id'] == post_id),None)
    try:
        # Getting data from post_id
        post=Post.objects.get(slug=slug)
        related_posts=Post.objects.filter(category = post.category ).exclude(pk=post.id)
    except Post.DoesNotExist:
        raise Http404("Page Does Not Exit :(")
        # return redirect(reverse('blog:index'))
    # logger=logging.getLogger('TESTING')
    # logger.debug(f'Your Post Variable is {post}')
    return render(request,'detail.html',{'post':post,'related_posts':related_posts})

def welcome(request):
    return HttpResponse("Welcome Rockstar!!")

def old_url_redirects(request):
    return redirect(reverse('blog:new_url'))

def new_url_view(request):
    return HttpResponse("This is REDIRECTED new URL")

def contact(request):
    if request.method=="POST":
        form=ContactForm(request.POST)
        name=request.POST.get('name')
        email=request.POST.get('email')
        message=request.POST.get('mesaage')
        logger=logging.getLogger('TESTING')
        if form.is_valid():
            logger.debug(f' Post data is {form.cleaned_data['name']} {form.cleaned_data['email']} {form.cleaned_data['message']}')
            success_message="Form has been Submitted Successfully!!"
            return render(request,'contact.html',{'form':form,'success_message':success_message})
        else:
            logger.debug("Form Validation Failure")
        return render(request,'contact.html',{'form':form,'name':name,'email':email,'message':message})
    return render(request,'contact.html')

def about(request):
    about_content=AboutUs.objects.first()
    if about_content is None or not about_content.content:
        about_content="No Contents Right Here..!!"
    else:
        about_content=about_content.content
    return render(request,'about.html',{'about_content':about_content})

def register(request):
    form=RegisterForm()
    if request.method == "POST":
        form=RegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])  # for password hashing
            user.save()
            # Add users to group
            readers_group,created=Group.objects.get_or_create(name="Readers")
            user.groups.add(readers_group)
            messages.success(request,"Registration Successful! You Can Login In.")
            return redirect(reverse('blog:login'))
    return render(request,'register.html',{'form':form})

def login(request):
    form=LoginForm()
    if request.method == "POST":
        form=LoginForm(request.POST)
        if form.is_valid():
            username=form.cleaned_data['username']
            password=form.cleaned_data['password']
            user=authenticate(username=username,password=password)
            if user is not None:
                auth_login(request,user)
                return redirect(reverse('blog:dashboard'))

    return render(request,'login.html',{'form':form})

def dashboard(request):
    blog_title="My Posts"
    all_posts = Post.objects.filter(user=request.user)
    paginator=Paginator(all_posts,5)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request,'dashboard.html',{'blog_title':blog_title,'page_obj':page_obj})

def logout(request):
    auth_logout(request)
    return redirect('blog:index')

def forgot_password(request):
    form = ForgotPasswordForm()
    if request.method == "POST":
        form=ForgotPasswordForm(request.POST)
        if form.is_valid():
            email =form.cleaned_data['email']
            user = User.objects.get(email=email)
            # send email to reset password
            token=default_token_generator.make_token(user)
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            current_site = get_current_site(request)
            domain = current_site.domain
            subject = "Reset Password Requested"
            message = render_to_string('reset_password_email.html',{'domain':domain,'uid':uid,'token':token})
            send_mail(subject,message,'noreply@blog.com',[email])
            messages.success(request,'Email has been sent!!')
    return render(request,'forgot_password.html',{'form':form})

def reset_password(request,uidb64,token):
    form = ResetPasswordForm()
    if request.method == "POST":
        form=ResetPasswordForm(request.POST)
        if form.is_valid():
            new_password=form.cleaned_data['new_password']
            try:
                uid=urlsafe_base64_decode(uidb64)
                user=User.objects.get(pk=uid)
            except(TypeError,OverflowError,ValueError,User.DoesNotExist):
                user=None
            if user is not None and default_token_generator.check_token(user,token):
                user.set_password(new_password)
                user.save()
                messages.success(request,"Your password has been reset Successfully!!")
                return redirect(reverse('blog:login'))
            else:
                messages.error(request,"The password reset link is invalid !")
    return render(request,'reset_password.html',{'form':form})

@login_required
@permission_required('blog.add_post',raise_exception=True)
def new_post(request):
    categories=Category.objects.all()
    form=PostForm()
    if request.method =="POST":   
        form=PostForm(request.POST,request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.user = request.user
            post.save()
            return redirect('blog:dashboard')
    return render(request,'new_post.html',{'form':form,'categories':categories})

@login_required
@permission_required('blog.change_post',raise_exception=True)
def edit_post(request,post_id):
    categories=Category.objects.all()
    post = get_object_or_404(Post,id=post_id)
    form=PostForm()
    if request.method == "POST":
        form=PostForm(request.POST,request.FILES,instance=post)
        if form.is_valid():
            form.save()
            messages.success(request,"Post Updated Successfully")
            return redirect('blog:dashboard')
    return render(request,'edit_post.html',{'categories':categories,'form':form,'post':post})

@login_required
@permission_required('blog.delete_post',raise_exception=True)
def delete_post(request,post_id):
    post = get_object_or_404(Post,id=post_id)
    post.delete()
    messages.success(request,"Post Deleted Successfully")
    return redirect('blog:dashboard')

@login_required
@permission_required('blog.can_publish',raise_exception=True)
def publish_post(request,post_id):
    post=get_object_or_404(Post,id=post_id)
    post.is_published=True
    post.save()
    messages.success(request,"Post Published Successfully")
    return redirect('blog:dashboard')