# consumers.py
import json
from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer
from django.contrib.auth.models import User
from .models import Message

from django.db.models import Q


from channels.generic.websocket import WebsocketConsumer
from asgiref.sync import async_to_sync
import json
from django.contrib.auth.models import User
from .models import Message
from django.db.models import Q

class ChatConsumer(WebsocketConsumer):
    def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['recipient_id']
        self.room_group_name = f'chat_{self.room_name}'

        # Join room group
        async_to_sync(self.channel_layer.group_add)(
            self.room_group_name,
            self.channel_name
        )

        self.accept()

    def disconnect(self, close_code):
        # Leave room group
        async_to_sync(self.channel_layer.group_discard)(
            self.room_group_name,
            self.channel_name
        )

    def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']
        sender_id = self.scope['user'].id
        recipient_id = self.room_name

        sender = User.objects.get(id=sender_id)
        recipient = User.objects.get(id=recipient_id)

        Message.objects.create(sender=sender, recipient=recipient, content=message)

        # Send message to room group
        async_to_sync(self.channel_layer.group_send)(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message,
                'sender': sender.username
            }
        )

    def chat_message(self, event):
        message = event['message']
        sender = event['sender']

        # Send message to WebSocket
        self.send(text_data=json.dumps({
            'message': message,
            'sender': sender
        }))
    
    def load_chat_history(self, event):
        sender_id = event['sender_id']
        recipient_id = event['recipient_id']

        sender = User.objects.get(id=sender_id)
        recipient = User.objects.get(id=recipient_id)

        # Récupérer l'historique des messages entre l'expéditeur et le destinataire
        messages_sent_by_sender = Message.objects.filter(sender=sender, recipient=recipient).order_by('timestamp')[:10]
        messages_sent_to_sender = Message.objects.filter(sender=recipient, recipient=sender).order_by('timestamp')[:10]

       # Envoyer les messages à WebSocket avec les détails nécessaires
        for message in messages_sent_by_sender:
          self.send(text_data=json.dumps({
            'message': message.content,
            'sender': message.sender.username,
            'timestamp': message.timestamp.strftime('%I:%M %p, %b %d'),
            'sender_image': message.sender.profile_image.url  # URL de l'image du sender
          }))

        for message in messages_sent_to_sender:
          self.send(text_data=json.dumps({
            'message': message.content,
            'sender': message.sender.username,
            'timestamp': message.timestamp.strftime('%I:%M %p, %b %d'),
            'sender_image': message.sender.profile_image.url  # URL de l'image du sender
          }))
