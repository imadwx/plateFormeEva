from django.db import models
from django.contrib.auth.models import User


def user_directory_path(instance, filename):
    # File will be uploaded to MEDIA_ROOT/user_<id>/<filename>
    return f'user_{instance.user.id}/{filename}'




from django.db import models
from django.contrib.auth.models import User
import json
from django.utils import timezone

def user_directory_path(instance, filename):
    # File will be uploaded to MEDIA_ROOT/user_<id>/<filename>
    return f'user_{instance.user.id}/{filename}'



    

class QuestionType(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name

class EvaluationMultQ(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    uploaded_files = models.FileField(upload_to=user_directory_path)
    question_types = models.ManyToManyField(QuestionType)
    additional_module = models.CharField(max_length=255, blank=True, default='')
    created_at = models.DateTimeField(default=timezone.now, blank=True)

    def __str__(self):
        return f'Évaluation {self.id} - User: {self.user.username}'



class ProfileUser(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    profile_image = models.ImageField(upload_to=user_directory_path, blank=True, null=True)
    
    def __str__(self):
        return f'Profile of {self.user.username}'
    

class Message(models.Model):
    sender = models.ForeignKey(User, related_name='sent_messages', on_delete=models.CASCADE)
    recipient = models.ForeignKey(User, related_name='received_messages', on_delete=models.CASCADE)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Message from {self.sender.username} to {self.recipient.username}'

    class Meta:
        ordering = ['-timestamp']