from django.urls import path
from . import views

urlpatterns = [
    path('', views.post_list, name='post_list'),
    path('feed/', views.feed_view, name='feed'),
    path('settings/', views.settings_view, name='settings'),
    path('accounts/signup/', views.signup_view, name='signup'),
    path('accounts/login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('profile/', views.profile_view, name='profile'),
    path("profile/<str:username>/", views.profile_view, name="user_profile"),
    path('notifications/', views.notifications, name='notifications'),
    path('notification/<int:id>/', views.notification_redirect, name='notification_redirect'),
    path('create/', views.create_post, name='create_post'),
    path('my-posts/', views.my_posts, name='my_posts'),
    path('post/<int:id>/', views.post_detail, name='post_detail'),
    path('post/<int:post_id>/edit/', views.edit_post_view, name='edit_post'),
    path('delete-post/<int:post_id>/', views.delete_post, name='delete_post'),
    path('comment/delete/<int:comment_id>/', views.delete_comment, name='delete_comment'),
    path("like/<int:post_id>/", views.like_post, name="like_post"),
    path("like-toggle/", views.toggle_like, name="toggle_like"),
    path("search/", views.search_posts, name="search_posts"),
]