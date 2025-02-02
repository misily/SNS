from django.http import HttpResponseRedirect, Http404
from django.urls import reverse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login
from .forms import SignUpForm
from .models import User as models_user
from django.contrib import auth, messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from .forms import UserUpdateForm
from post.forms import CommentForm
from post.serializers import PostSerializer

from post import models


def main(request):
    if request.method == 'GET':
        if request.user.is_authenticated:
            return HttpResponseRedirect(reverse('post:feed'))

    elif request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse('post:feed'))

    return render(request, 'user/main.html')


def signup(request):
    if request.method == 'GET':
        form = SignUpForm()

        return render(request, 'user/signup.html', {'form': form})

    elif request.method == 'POST':
        form = SignUpForm(request.POST)

        if form.is_valid():
            form.save()

            username = form.cleaned_data['username']
            password = form.cleaned_data['password']

            user = authenticate(request, username=username, password=password)

            if user is not None:
                login(request, user)
                return HttpResponseRedirect(reverse('post:feed'))

        return render(request, 'user/main.html')


@login_required
def logout(request):
    auth.logout(request)
    return render(request, 'user/main.html')


@login_required
def my_posts(request):
    if request.method == 'GET':
        comment_form = CommentForm()
        user = get_object_or_404(models_user, pk=request.user.id)
        post_list = models.Post.objects.filter(author=user).order_by('-id')
        serializer = PostSerializer(post_list, many=True)
        
        return render(request, 'post/posts.html', {'posts': serializer.data, 'comment_form': comment_form, 'user': user})


@login_required
def profile_update(request):
    if request.method == 'POST':
        form = UserUpdateForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, '프로필 업데이트 완료')
            return redirect('user:my-posts')
    return render(request, 'user/profile_update.html')


@login_required
def edit_profile(request, user_id):
    user = get_object_or_404(models_user, pk=user_id)
    if user:
        # 로그인한 유저가 맞다면
        if request.method == "GET":
            form = UserUpdateForm(instance=user)
            return render(request, 'user/profile_edit.html', {"form": form})
        elif request.method == "POST":
            forms = UserUpdateForm(request.POST, request.FILES, instance=user)
            if forms.is_valid():
                forms.save()

            return redirect(reverse('post:feed'))

    else:
        # 로그인한 유저와 다르면
        return redirect('post:feed')
