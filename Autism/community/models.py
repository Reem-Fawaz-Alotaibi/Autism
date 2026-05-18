from django.db import models

# Create your models here.
from django.db import models
from django.contrib.auth.models import User


class Post(models.Model):

    CATEGORY_CHOICES = [
        ('sleep', 'النوم'),
        ('food', 'التغذية'),
        ('play', 'اللعب'),
        ('education', 'التعليم'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    category = models.CharField(max_length=20,choices=CATEGORY_CHOICES)
    content = models.TextField()
    tags = models.CharField(max_length=200,blank=True)
    created_at = models.DateTimeField(auto_now_add=True )

    def __str__(self):
        return self.title
    

class Comment(models.Model):

    post = models.ForeignKey(Post,on_delete=models.CASCADE,related_name='comments')
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user.username
    

class Like(models.Model):

    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='likes')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    class Meta:
        unique_together = ['post', 'user']


class CommentLike(models.Model):
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE, related_name='comment_likes')
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    class Meta:
        unique_together = ['comment', 'user']

    def __str__(self):
        return f"{self.user.username} liked {self.comment.id}"
    
    
class Report(models.Model):

    REASONS = [
        ('spam', 'محتوى مزعج'),
        ('bullying', 'تنمر'),
        ('false', 'معلومات خاطئة'),
        ('other', 'سبب آخر'),
    ]

    STATUS_CHOICES = [
    ('pending', 'قيد المراجعة'),
    ('solved', 'تم الحل'),
]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    reason = models.CharField(max_length=50, choices=REASONS)
    status = models.CharField(max_length=20,choices=STATUS_CHOICES,default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
