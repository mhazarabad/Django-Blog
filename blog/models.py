from django.db import models

class Category(models.Model):
    name = models.CharField(max_length=150, db_index=True, unique=True)
    slug = models.SlugField(max_length=159, unique=True, db_index=True)
    
    def __str__(self):
        return self.name
    
class Tag(models.Model):
    name = models.CharField(max_length=150, db_index=True, unique=True)
    
    def __str__(self):
        return self.name

class Post(models.Model):
    title = models.CharField(max_length=150, unique=True, db_index=True)
    slug = models.SlugField(max_length=159, unique=True, db_index=True)
    summary = models.TextField(blank=True, default=None,null=True)
    content = models.TextField()
    STATUS_CHOICES = (
        ('draft', 'Draft'),
        ('published', 'Published'),
    )
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='draft')
    from django.contrib.auth.models import User
    author = models.ForeignKey(to=User, on_delete=models.CASCADE)
    category = models.ForeignKey(to=Category, on_delete=models.CASCADE)
    tags = models.ManyToManyField(to=Tag, blank=True)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.title

class Comment(models.Model):
    post = models.ForeignKey(to=Post, on_delete=models.CASCADE)
    name = models.CharField(max_length=150)
    email = models.EmailField()
    content = models.TextField()
    reply_to = models.ForeignKey(to='self', on_delete=models.CASCADE, blank=True, null=True)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)
    from django.contrib.auth.models import User
    liked_by = models.ManyToManyField(to=User, blank=True, related_name='liked_comments')
    disliked_by = models.ManyToManyField(to=User, blank=True, related_name='disliked_comments')
    
    def __str__(self):
        return self.content[:20]
