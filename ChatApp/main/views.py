from django.shortcuts import render, redirect, get_object_or_404
from .forms import SignupForm, LoginForm
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import Http404
from chats.models import Chat
from chats.forms import ChatForm


def login_user(request):
    if request.method == 'POST':
        form = LoginForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('main:user_dashboard', username=user.username)
        else:
            messages.success(request, 'There has been an error, please retry.')
            return redirect('/')
    else:
        form = LoginForm()

    return render(request, 'main/login.html', {
        'form': form
    })


def signup_user(request):
    if request.method == 'POST':
        # if form is submitted create new instance of the form with all of the information from the form (request.POST)
        form = SignupForm(request.POST)
        # check if form is valid
        if form.is_valid():
            # save user in the database
            form.save()
            messages.success(request, "You are now signed up, please login to use your account")
            return redirect('/')

    else:

        form = SignupForm()
    return render(request, 'main/signup.html', {
        'form': form
    })


@login_required
def user_dashboard(request, username):
    user = get_object_or_404(User, username=username)

    # Check if the logged-in user matches the requested username
    if request.user != user:
        raise Http404("You don't have access to this dashboard.")

    chats = Chat.objects.filter(user=user)
    form = ChatForm()

    if request.method == 'POST':
        form = ChatForm(request.POST)
        if form.is_valid():
            new_chat = form.save(commit=False)  # Don't save yet
            new_chat.user = request.user        # Associate with user
            new_chat.save()
            return redirect('chats:load_chat', new_chat.id)  # Redirect to the new chat

    return render(request, 'main/dashboard.html', {
        'chats': chats,
        'user': user,
        'form': form,
    })


# @login_required
# def user_dashboard(request, username):
#     user = get_object_or_404(User, username=username)
#
#     # Check if the logged-in user matches the requested username
#     if request.user != user:
#         raise Http404("You don't have access to this dashboard.")
#
#     chats = Chat.objects.filter(user=user)
#     form = ChatForm()
#
#     if request.method == 'POST':
#         form = ChatForm(request.POST)
#         if form.is_valid():
#             new_chat = form.save(commit=False)  # Don't save yet
#             new_chat.user = request.user        # Associate with user
#             new_chat.save()
#             return redirect('chat_detail', new_chat.id)  # Redirect to the new chat
#
#     return render(request, 'dashboard.html', {
#         'chats': chats,
#         'user': user,
#         'form': form,
#     })


def logout_user(request):
    if request.method == 'POST':
        logout(request)
        return redirect('main:login')
    else:
        # Handle GET request
        return redirect('main:login')

