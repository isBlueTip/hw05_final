from django.core.paginator import Paginator
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import Post, Group, User, Follow
from .forms import PostForm, CommentForm

POSTS_DSPL = 10

import logging  # TODO delete logger before final commit
logging.basicConfig(level=logging.DEBUG,
                    filename='views.log',
                    format='%(asctime)s | %(levelname)s | %(message)s')


def index(request):
    template = 'posts/index.html'
    title = 'Последние обновления на сайте'
    posts = Post.objects.all()
    paginator = Paginator(posts, POSTS_DSPL)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'title': title,
        'page_obj': page_obj,
    }
    return render(request, template, context)


def group_list(request, pk):
    template = 'posts/group_list.html'
    group = get_object_or_404(Group, slug=pk)
    posts = group.posts.all()
    paginator = Paginator(posts, POSTS_DSPL)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'group': group,
        'page_obj': page_obj,
    }
    return render(request, template, context)


def profile(request, username):
    template = 'posts/profile.html'
    author = get_object_or_404(User, username=username)
    posts = author.posts.all()
    paginator = Paginator(posts, POSTS_DSPL)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    title = ('Профиль пользователя ' + str(author.get_full_name()))
    current_user = User.objects.get(username=request.user)
    follow = Follow.objects.filter(user=current_user).filter(author=author)
    logging.debug(follow)
    if Follow.objects.filter(user=current_user, author=author):
        following = True
    else:
        following = False
    logging.debug(following)
    context = {'title': title,
               'author': author,
               'posts': posts,
               'page_obj': page_obj,
               'following': following,
               }
    return render(request, template, context)


def post_detail(request, post_id):
    template = 'posts/post_detail.html'
    post = get_object_or_404(Post, pk=post_id)
    form = CommentForm
    title = 'Пост ' + post.text[:30]
    comments = post.comments.all()
    context = {
        'title': title,
        'post': post,
        'form': form,
        'comments': comments
    }
    return render(request, template, context)


@login_required
def post_create(request):
    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
    )
    if form.is_valid():
        new_post = form.save(commit=False)
        new_post.author = request.user
        new_post.save()
        return redirect(to='posts:profile', username=request.user)
    template = 'posts/create_post.html'
    title = 'Создать новый пост'
    context = {
        'title': title,
        'form': form,
    }
    return render(request, template, context)


@login_required
def post_edit(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    # condition to prevent editing post of another author via direct link
    if post.author != request.user:
        return redirect(to='posts:index')
    # edit and save DB post entry
    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
        instance=post,
    )
    if form.is_valid():
        post = form.save()
        return redirect(to='posts:post_detail', post_id=post.pk)
    template = 'posts/create_post.html'
    title = 'Редактировать пост'
    form = PostForm(instance=post)
    is_edit = True
    context = {
        'title': title,
        'post': post,
        'is_edit': is_edit,
        'form': form,
    }
    return render(request, template, context)


@login_required
def add_comment(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
        return redirect('posts:post_detail', post_id=post_id)


@login_required
def follow_index(request):
    template = 'posts/follow.html'
    title = 'Посты любимых авторов'
    current_user_pk = User.objects.get(username=request.user).pk
    followings = Follow.objects.filter(user=current_user_pk)
    author_list = followings.values_list('author', flat=True)
    posts = Post.objects.filter(author__in=author_list)
    paginator = Paginator(posts, POSTS_DSPL)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'title': title,
        'page_obj': page_obj,
    }
    return render(request, template, context)


@login_required
def profile_follow(request, username):
    # logging.debug(f'current user = {request.user}')
    # logging.debug(f'current user = {str(request.user)}')
    # logging.debug(f'current author = {username}')
    # logging.debug(f'current author = {type(username)}')
    if username != str(request.user):
        current_user = User.objects.get(username=request.user)
        Follow.objects.create(
            user=current_user,
            author=User.objects.get(username=username),
        )
    return redirect('posts:profile', username=username)


@login_required
def profile_unfollow(request, username):
    current_author = User.objects.get(username=username)
    current_user = User.objects.get(username=request.user)
    Follow.objects.filter(user=current_user, author=current_author).delete()

    return redirect('posts:profile', username=username)
