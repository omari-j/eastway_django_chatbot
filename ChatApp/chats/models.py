from django.db import models
from django.contrib.auth.models import User
import uuid


# Create your models here.
class Chat(models.Model):
    """Represents a conversation thread."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=255, default="New Chat")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Chat {self.id} - {self.user.username}"

    def return_room_messages(self):
        return Message.objects.filter(chat=self)

    def create_new_chat_message(self, user, message, ai_response):
        new_message = Message(chat=self, user=user, message=message, ai_response=ai_response)
        new_message.save()


class Message(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    chat = models.ForeignKey(Chat, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.TextField()
    ai_response = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Message in {self.chat.id} - {self.user.username}"
