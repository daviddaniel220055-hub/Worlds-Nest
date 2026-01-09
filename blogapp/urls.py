from django.urls import include, path
from . import views

urlpatterns = [
    # HOME (LANDING PAGE)
    path('', views.post_list, name='post_list'),   # uses post_list.html
    path('feed/', views.feed_view, name='feed'),   # uses feed.html
    path('settings/', views.settings_view, name='settings'),
    path('post/<int:id>/', views.post_detail, name='post_detail'),

    # AUTH
    path('accounts/signup/', views.signup_view, name='signup'),
    path('accounts/login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),

    # DASHBOARD (PRIVATE)
    path('dashboard/', views.dashboard, name='dashboard'),

    # PROFILE
    path('profile/', views.profile_view, name='profile'),
    path("profile/<str:username>/", views.profile_view, name="user_profile"),
    path('notifications/', views.notifications, name='notifications'),
    path('notification/<int:id>/', views.notification_redirect, name='notification_redirect'),

    # POSTS CRUD
    path('create/', views.create_post, name='create_post'),
    path('my-posts/', views.my_posts, name='my_posts'),
    path('post/<int:post_id>/edit/', views.edit_post_view, name='edit_post'),
    path('delete-post/<int:post_id>/', views.delete_post, name='delete_post'),
    path('post/<int:id>/', views.post_detail, name='post_detail'),
    path('comment/delete/<int:comment_id>/', views.delete_comment, name='delete_comment'),
    path("like/<int:post_id>/", views.like_post, name="like_post"),
    path("search/", views.search_posts, name="search_posts"),
    path("like-toggle/", views.toggle_like, name="toggle_like"),
    

]
