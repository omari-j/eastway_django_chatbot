from django.apps import AppConfig


class ChatsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'chats'

    def ready(self):
        from django.conf import settings
        from .functions import create_rag_pipeline

        # Initialize the RAG pipeline and store it in the app config
        if not hasattr(settings, 'RAG_CHAIN'):
            settings.RAG_CHAIN = create_rag_pipeline()
