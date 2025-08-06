from django.urls import path
from . import views

app_name='blog'
#URLs Configurations
urlpatterns=[
    path('',views.index,name="index"),
    path('detail/<str:slug>',views.detail,name="detail"),
    path("welcome",views.welcome,name="welcome"),
    path("old_url",views.old_url_redirects,name="old_url"),
    path("new_changed_url",views.new_url_view,name="new_url"),
    path("contact",views.contact,name="contact"),
    path("about",views.about,name="about"),
    path("register",views.register,name="register"),
    path("login",views.login,name="login"),
    path("dashboard",views.dashboard,name="dashboard"),  
    path("logout",views.logout,name="logout"),
    path("forgotpassword",views.forgot_password,name="forgotpassword"),
    path("resetpassword/<uidb64>/<token>/",views.reset_password,name="resetpassword"),
    path("newpost",views.new_post,name="newpost"),
    path("editpost/<int:post_id>",views.edit_post,name="editpost"),
    path("deletepost/<int:post_id>",views.delete_post,name="deletepost"),
    path("publishpost/<int:post_id>",views.publish_post,name="publishpost")
]