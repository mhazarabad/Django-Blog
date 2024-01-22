from django.db import models
from ckeditor.fields import RichTextField

class Category(models.Model):
    name = models.CharField(max_length=150, db_index=True, unique=True)
    slug = models.SlugField(max_length=150, unique=True, db_index=True)

    @property
    def response(self):
        return {
            'name': self.name,
            'slug': self.slug,
        }
    
    @classmethod
    def get_used_categories(cls):
        from .models import Post
        return cls.objects.filter(id__in=set(Post.objects.values_list('id', flat=True)))
    
    def __str__(self):
        return self.name
    
class Tag(models.Model):
    name = models.CharField(max_length=150, db_index=True, unique=True)
    slug = models.SlugField(max_length=150, unique=True, db_index=True)
    
    @property
    def response(self):
        return {
            'name': self.name,
            'slug': self.slug,
        }

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
    def full_data_response(self):
        return {
            'id': self.id, # for APIs
            'header_image_url': self.header_image.url,
            'title': self.title,
            'slug': self.slug,
            'summary': self.summary,
            'content': self.content,
            'status': self.status,
            'status_text': self.get_status_display(),
            'author': self.author.get_full_name(),
            'category': self.category.response,
            'tags': [tag.response for tag in self.tags.all()],
            'created': self.created.strftime('%Y-%m-%d %H:%M:%S'),
            'total_likes': self.total_likes,
            'total_dislikes': self.total_dislikes,
            'total_comments': self.total_comments,
            'comments': [comment.full_data_response for comment in self.comment_set.all()],
        }
    
    @property
    def preview_response(self):
        return {
            'id': self.id, # for APIs
            'header_image_url': self.header_image.url,
            'title': self.title,
            'slug': self.slug,
            'summary': self.summary,
            'category': self.category.response,
            'created': self.created.strftime('%Y-%m-%d %H:%M:%S'),
        }

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
        if self.id and self.check_duplicate_in_liked_and_disliked:
            self.disliked_by.remove(self.liked_by.get(id__in=self.disliked_by.values_list('id', flat=True)))# or raise Exception('duplicate')
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title

class Comment(models.Model):
    post = models.ForeignKey(to=Post, on_delete=models.CASCADE)
    name = models.CharField(max_length=150)
    email = models.EmailField()
    email_hash = models.CharField(max_length=150, blank=True, null=True)
    content = models.TextField()
    reply_to = models.ForeignKey(to='self', on_delete=models.CASCADE, blank=True, null=True)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)
    from django.contrib.auth.models import User
    liked_by = models.ManyToManyField(to=User, blank=True, related_name='liked_comments')
    disliked_by = models.ManyToManyField(to=User, blank=True, related_name='disliked_comments')
    hided = models.BooleanField(default=False)

    @property
    def full_data_response(self):
        return {
            'id': self.id, # for APIs
            'name': self.name,
            'content': self.content,
            'replies': self.get_all_replies,
            'created': self.created.strftime('%Y-%m-%d %H:%M:%S'),
            'total_likes': self.total_likes,
            'total_dislikes': self.total_dislikes,
        }
    
    @property
    def get_all_replies(self):
        return [reply.full_data_response for reply in self.comment_set.filter(hided=False)]

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
        if self.id and self.check_duplicate_in_liked_and_disliked:
            self.disliked_by.remove(self.liked_by.get(id__in=self.disliked_by.values_list('id', flat=True)))# or raise Exception('duplicate')
        from hashlib import sha256
        self.email_hash = sha256(self.email.encode()).hexdigest()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.content[:20]
