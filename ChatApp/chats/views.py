from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from .models import Chat, Message
from langchain.schema import HumanMessage, AIMessage
from .functions import generate_response, gr
from django.contrib.auth.models import User
import datetime
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.chat_history import BaseChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory
from django.core import serializers

# Create your views here.

store = {}

@login_required()
def create_chat(request, username):
    user = get_object_or_404(User, username=username)
    chat = Chat(user=user, title=f'{user.username} chat create at: {datetime.datetime.now()}')
    return render(request, 'chats/chat_interface.html', {
        'user': user,
        'username': username,
        'id': chat.id,
        'chat': chat,
    })

@login_required
@csrf_exempt
def load_chat(request, id):
    if request.method == "POST":
        question = request.POST.get('msg')
        if not question:
            return JsonResponse({"error": "Missing question"}, status=400)

        chat_id = request.POST.get('id')
        chat = get_object_or_404(Chat, id=id)
        past_messages = Message.objects.filter(id=id).order_by('created_at')
        if not past_messages:
            request.session['history'] = {}
        else:
            if 'history' not in request.session:
                 store[chat_id]= ChatMessageHistory(
                    [HumanMessage(content=msg.message) if msg.message else AIMessage(content=msg.ai_response) for msg in past_messages if msg.message or msg.ai_response]
                )

            else:
                pass

        def get_session_history(session_id: str) -> BaseChatMessageHistory:
            if session_id not in store:
                store[session_id] = ChatMessageHistory()
            return store[session_id]

        ai_response = gr(question, chat_id, get_session_history)['answer']
        chat.create_new_chat_message(user=request.user, message=question, ai_response=ai_response)

        return JsonResponse({"response": ai_response})

    # GET request: load chat history
    if id:
        chat, _ = Chat.objects.get_or_create(id=id)
        messages = chat.return_room_messages().order_by('created_at')

    return render(request, 'chats/chat_interface.html', {'chat': chat, 'messages': messages})


@login_required()
def delete_chat(request, id):
    if request.method == 'POST':
        chat = get_object_or_404(Chat, id=id)
        chat.delete()
        return redirect('main:user_dashboard', username=request.user.username)
