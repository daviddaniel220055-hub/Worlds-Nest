import json
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db.models import Sum
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.timezone import now

from .models import Post, Profile, Comment
from .forms import PostForm, ProfilePictureForm


# =========================
# HOME (REDIRECT)
# =========================
def home_view(request):
    return render(request, 'blog/post_list.html')
@login_required
def feed_view(request):
    posts = Post.objects.all().order_by('-created_at')
    return render(request, 'blog/feed.html', {'posts': posts})



@login_required
def settings_view(request):
    return render(request, 'settings.html')



# =========================
# PUBLIC FEED (FYP)
# =========================
def post_detail(request, id):
    post = get_object_or_404(Post, id=id)

    # increase views
    post.views += 1
    post.save(update_fields=['views'])

    comments = Comment.objects.filter(
        post=post,
        parent__isnull=True
    ).select_related('user')

    related_posts = Post.objects.exclude(id=post.id)[:5]

    # =====================
    # ADD COMMENT / REPLY
    # =====================
    if request.method == "POST":
        if not request.user.is_authenticated:
            messages.error(request, "You must be logged in to comment.")
            return redirect('login')

        content = request.POST.get("content", "").strip()
        parent_id = request.POST.get("parent_id")

        if not content:
            messages.error(request, "Comment cannot be empty.")
            return redirect('post_detail', id=post.id)

        Comment.objects.create(
            post=post,
            user=request.user,
            content=content,
            parent_id=parent_id if parent_id else None
        )

        return redirect('post_detail', id=post.id)

    return render(request, "blog/post_detail.html", {
        "post": post,
        "comments": comments,
        "related_posts": related_posts,
    })

# =========================
# DELETE COMMENT
# =========================
@login_required
def delete_comment(request, comment_id):
    comment = get_object_or_404(Comment, id=comment_id)

    if request.user == comment.user:
        post_id = comment.post.id
        comment.delete()
        return redirect('post_detail', id=post_id)

    return redirect('post_detail', id=comment.post.id)

# =========================
# AUTH
# =========================
def signup_view(request):
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        email = request.POST.get('email', '').strip()
        password = request.POST.get('password')

        if not username or not password:
            messages.error(request, "All fields are required")
            return redirect('signup')

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists")
            return redirect('signup')

        User.objects.create_user(
            username=username,
            email=email,
            password=password
        )

        messages.success(request, "Account created. Please log in.")
        return redirect('login')

    return render(request, 'accounts/signup.html')

def login_view(request):
    if request.user.is_authenticated:
        return redirect('feed')

    if request.method == 'POST':
        user = authenticate(
            request,
            username=request.POST.get('username'),
            password=request.POST.get('password')
        )

        if user:
            login(request, user)
            return redirect('feed')

        messages.error(request, "Invalid username or password")

    return render(request, 'accounts/login.html')




def logout_view(request):
    logout(request)
    return redirect('login')


# =========================
# DASHBOARD
# =========================
@login_required
def dashboard(request):
    posts = Post.objects.filter(author=request.user)
    total_views = posts.aggregate(total=Sum('views'))['total'] or 0

    context = {
        'posts': posts,
        'total_views': total_views,
        'chart_labels': json.dumps([p.title[:15] for p in posts]),
        'chart_data': json.dumps([p.views for p in posts]),
    }

    return render(request, 'dashboard.html', context)


# =========================
# MY POSTS
# =========================
@login_required
def my_posts(request):
    posts = (
        Post.objects
        .filter(author=request.user)
        .order_by('-created_at')
    )
    return render(request, 'my_posts.html', {'posts': posts})


# =========================
# PROFILE
# =========================


@login_required
def profile_view(request, username=None):

    # 🔹 If username exists → view someone else
    if username:
        user_obj = get_object_or_404(User, username=username)
    else:
        user_obj = request.user

    profile = user_obj.profile
    posts = Post.objects.filter(author=user_obj).order_by('-created_at')

    # 🔹 Only allow edit if it is YOUR profile
    if request.method == "POST" and user_obj == request.user:

        username_input = request.POST.get("username")
        email = request.POST.get("email")

        if username_input:
            user_obj.username = username_input.strip()

        if email:
            user_obj.email = email.strip()

        user_obj.save()

        if "profile_picture" in request.FILES:
            profile.profile_picture = request.FILES["profile_picture"]
            profile.save()

        messages.success(request, "Profile updated successfully.")

    return render(request, "profile.html", {
        "profile": profile,
        "posts": posts,
        "is_own_profile": user_obj == request.user
    })

# =========================
# CREATE / EDIT / DELETE POST
# =========================
@login_required
def create_post(request):
    form = PostForm(request.POST or None, request.FILES or None)

    if form.is_valid():
        post = form.save(commit=False)
        post.author = request.user
        post.save()
        return redirect('dashboard')

    return render(request, 'create_post.html', {'form': form})


@login_required
def edit_post_view(request, post_id):
    post = get_object_or_404(Post, id=post_id, author=request.user)
    form = PostForm(
        request.POST or None,
        request.FILES or None,
        instance=post
    )

    if form.is_valid():
        form.save()
        return redirect('my_posts')

    return render(request, 'edit_post.html', {'form': form})


@login_required
def delete_post(request, post_id):
    post = get_object_or_404(Post, id=post_id, author=request.user)

    if request.method == 'POST':
        post.delete()

    return redirect('my_posts')


# =========================
# AUTO CREATE PROFILE
# =========================
@receiver(post_save, sender=User)
def create_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)



def post_list(request):
    posts = Post.objects.select_related("author").order_by("-created_at")
    return render(request, "blog/post_list.html", {
        "posts": posts
    })



from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from .models import Post


# blogapp/views.py
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from django.views.decorators.http import require_POST

@login_required
@require_POST
def toggle_like(request):
    data = json.loads(request.body)
    post_id = data.get("post_id")

    post = Post.objects.get(id=post_id)

    if request.user in post.likes.all():
        post.likes.remove(request.user)
        liked = False
    else:
        post.likes.add(request.user)
        liked = True

    return JsonResponse({
        "liked": liked,
        "likes_count": post.likes.count()
    })





from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Notification

@login_required
def notifications(request):
    notifications = Notification.objects.filter(
        user=request.user
    ).order_by("-created_at")

    # mark as read
    notifications.filter(is_read=False).update(is_read=True)

    return render(request, "blog/notifications.html", {
        "notifications": notifications
    })


@login_required
def notification_redirect(request, id):
    notification = get_object_or_404(
        Notification,
        id=id,
        user=request.user
    )

    # mark as read
    notification.is_read = True
    notification.save()

    # redirect to related post
    if notification.post:
        return redirect('post_detail', notification.post.id)

    return redirect('notifications')


@login_required
def like_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    user = request.user

    if user in post.likes.all():
        post.likes.remove(user)
        liked = False
    else:
        post.likes.add(user)
        liked = True

    return JsonResponse({
        "liked": liked,
        "likes_count": post.likes.count()
    })


from django.db.models import Q
def search_posts(request):
    query = request.GET.get("q", "").strip()

    # 🔹 If username exists → go to profile
    try:
        user = User.objects.get(username__iexact=query)
        return redirect("user_profile", username=user.username)
    except User.DoesNotExist:
        pass

    # 🔹 Else search posts
    posts = Post.objects.filter(title__icontains=query)

    return render(request, "search_results.html", {
        "query": query,
        "posts": posts
    })


def user_profile(request, username):
    user = get_object_or_404(User, username=username)
    posts = Post.objects.filter(author=user).order_by('-created_at')

    return render(request, 'profile_detail.html', {
        'profile_user': user,
        'posts': posts,
    })



# =========================
# CUSTOM 404
# =========================
def custom_404_view(request, exception):
    return render(request, '404.html', status=404)
