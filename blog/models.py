from django.db import models
from ckeditor.fields import RichTextField

class Category(models.Model):
    name = models.CharField(max_length=150, db_index=True, unique=True)
    slug = models.SlugField(max_length=150, unique=True, db_index=True)
    
    def __str__(self):
        return self.name
    
class Tag(models.Model):
    name = models.CharField(max_length=150, db_index=True, unique=True)
    slug = models.SlugField(max_length=150, unique=True, db_index=True)
    
    def __str__(self):
        return self.name

class Post(models.Model):
    header_image = models.ImageField(upload_to='post_images')
    title = models.CharField(max_length=150, unique=True, db_index=True)
    slug = models.SlugField(max_length=150, unique=True, db_index=True)
    summary = models.TextField(blank=True, default=None,null=True)
    content = RichTextField()
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
    from django.contrib.auth.models import User
    liked_by = models.ManyToManyField(to=User, blank=True, related_name='liked_posts')
    disliked_by = models.ManyToManyField(to=User, blank=True, related_name='disliked_posts')
    
    @property
    def total_likes(self):
        return self.liked_by.count()
    
    @property
    def total_dislikes(self):
        return self.disliked_by.count()

    @property
    def total_comments(self):
        return self.comment_set.count()
    
    @property
    def check_duplicate_in_liked_and_disliked(self):
        return True if self.liked_by.filter(id__in=self.disliked_by.values_list('id', flat=True)).exists() else False
        
    def save(self, *args, **kwargs):
        if self.check_duplicate_in_liked_and_disliked:
            self.disliked_by.remove(self.liked_by.get(id__in=self.disliked_by.values_list('id', flat=True)))# or raise Exception('duplicate')
        self.summary = self.content[:200]+' ...'
        super().save(*args, **kwargs)

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
    hided = models.BooleanField(default=False)

    @property
    def total_likes(self):
        return self.liked_by.count()
    
    @property
    def total_dislikes(self):
        return self.disliked_by.count()

    @property
    def check_duplicate_in_liked_and_disliked(self):
        return True if self.liked_by.filter(id__in=self.disliked_by.values_list('id', flat=True)).exists() else False
        
    def save(self, *args, **kwargs):
        if self.check_duplicate_in_liked_and_disliked:
            self.disliked_by.remove(self.liked_by.get(id__in=self.disliked_by.values_list('id', flat=True)))# or raise Exception('duplicate')
        super().save(*args, **kwargs)

    def __str__(self):
        return self.content[:20]
