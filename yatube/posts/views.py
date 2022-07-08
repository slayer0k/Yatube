from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.core.cache import caches
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render

from .forms import CommentForm, PostForm
from .models import Follow, Group, Post, User


def paginator(posts, page_numb):
    pagin = Paginator(posts, settings.LIMIT)
    return pagin.get_page(page_numb)


def index(request):
    posts = caches['default'].get('posts')
    if posts is None:
        posts = Post.objects.select_related('author', 'group')
        caches['default'].set('posts', posts, 20)
    page_obj = paginator(posts, request.GET.get('page'))
    return render(request, "posts/index.html",
                  {"page_obj": page_obj})


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    posts = group.posts.select_related('author')
    page_obj = paginator(posts, request.GET.get('page'))
    context = {'group': group,
               'page_obj': page_obj, }
    return render(request, 'posts/group_list.html', context)


def profile(request, username):
    author = get_object_or_404(User, username=username)
    posts = author.posts.select_related('group')
    page_obj = paginator(posts, request.GET.get('page'))
    count = page_obj.paginator.count
    if request.user.is_authenticated:
        following = Follow.objects.filter(
            author=author).filter(user=request.user).exists()
    else:
        following = False
    context = {
        'following': following,
        'author': author,
        'page_obj': page_obj,
        'count': count
    }
    return render(request, 'posts/profile.html', context)


def post_detail(request, post_id):
    post = get_object_or_404(Post.objects.select_related(
        'author'), pk=post_id)
    count = post.author.posts.count
    comments = post.comments.select_related('author')
    form = CommentForm()
    context = {
        'post': post,
        'count': count,
        'comments': comments,
        'form': form
    }
    return render(request, 'posts/post_detail.html', context)


@login_required
def post_create(request):
    form = PostForm(
        request.POST or None,
        files=request.FILES or None)

    if form.is_valid():
        post = form.save(commit=False)
        post.author = request.user
        post.save()
        return redirect('posts:profile', post.author.username)
    context = {
        'form': form,
    }

    return render(request, "posts/create_post.html", context)


def post_edit(request, post_id):
    post = get_object_or_404(Post, pk=post_id)

    if request.user != post.author:
        return redirect('posts:post', post_id)

    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
        instance=post)

    if form.is_valid():
        form.save()
        return redirect('posts:post', post_id)

    context = {
        'post': post,
        'form': form,
        'is_edit': True,
    }

    return render(request, 'posts/create_post.html', context)


@login_required
def add_comment(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
    return redirect('posts:post', post_id=post_id)


@login_required
def profile_follow(request, username):
    author = get_object_or_404(User, username=username)
    if author == request.user:
        return redirect('posts:profile', username)
    if not Follow.objects.filter(author=author, user=request.user).exists():
        Follow.objects.create(author=author, user=request.user)
    return redirect('posts:profile', username)


@login_required
def profile_unfollow(request, username):
    author = get_object_or_404(User, username=username)
    if Follow.objects.filter(author=author, user=request.user).exists():
        Follow.objects.filter(author=author, user=request.user).delete()
    return redirect('posts:profile', username)


@login_required
def follow_index(request):
    authors = [object.author for object in request.user.follower.all()]
    posts = Post.objects.select_related('group').filter(author__in=authors)
    page_obj = paginator(posts, request.GET.get('page'))
    context = {
        'page_obj': page_obj,
    }
    return render(request, 'posts/follow.html', context)
