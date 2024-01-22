from django.contrib import admin
from .models import Post, Comment, Category, Tag

def delete_selected(modeladmin, request, queryset):
    """
    to delete selected posts and avoid database overload
    """
    queryset_ids = queryset.values_list('id', flat=True)
    for group_idx in range(0, len(queryset_ids), 100):
        queryset.filter(id__in=queryset_ids[group_idx:group_idx+100]).delete()

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    list_display_links = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}
    actions = [delete_selected]


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    list_display_links = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}
    actions = [delete_selected]

from django import forms
from ckeditor.widgets import CKEditorWidget

class PostAdminForm(forms.ModelForm):
    content = forms.CharField(widget=CKEditorWidget())
    class Meta:
        model = Post
        fields = '__all__'

def make_published(modeladmin, request, queryset):
    """
    to publish selected posts and avoid database overload
    """
    queryset_ids = queryset.values_list('id', flat=True)
    for group_idx in range(0, len(queryset_ids), 100):
        queryset.filter(id__in=queryset_ids[group_idx:group_idx+100]).update(status='published')

def make_draft(modeladmin, request, queryset):
    """
    to draf selected posts and avoid database overload
    """
    queryset_ids = queryset.values_list('id', flat=True)
    for group_idx in range(0, len(queryset_ids), 100):
        queryset.filter(id__in=queryset_ids[group_idx:group_idx+100]).update(status='draft')

@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    form = PostAdminForm
    list_display = ('title', 'slug', 'status', 'created', 'modified', 'author')
    list_display_links = ('title', 'slug', 'status', 'created', 'modified', 'author')
    list_filter = ('status',)
    search_fields = ('title', 'content')
    prepopulated_fields = {'slug': ('title',)}
    date_hierarchy = 'modified'
    ordering = ('created', 'modified')
    filter_horizontal = ('tags','liked_by','disliked_by')
    read_only = ('author',)
    actions = [make_published, make_draft, delete_selected]
    show_facets = admin.ShowFacets.ALWAYS

    def add_view(self, request, form_url='', extra_context=None):
        self.exclude = ('author','liked_by','disliked_by')
        return super().add_view(request, form_url, extra_context)
    
    # asign the current user as the author of the post
    def save_model(self, request, obj, form, change):
        obj.author = request.user
        obj.save()

def make_hidden(modeladmin, request, queryset):
    """
    to hide selected comments and avoid database overload
    """
    queryset_ids = queryset.values_list('id', flat=True)
    for group_idx in range(0, len(queryset_ids), 100):
        queryset.filter(id__in=queryset_ids[group_idx:group_idx+100]).update(hided=True)

def make_visible(modeladmin, request, queryset):
    """
    to show selected comments and avoid database overload
    """
    queryset_ids = queryset.values_list('id', flat=True)
    for group_idx in range(0, len(queryset_ids), 100):
        queryset.filter(id__in=queryset_ids[group_idx:group_idx+100]).update(hided=False)

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'post', 'created', 'modified', 'hided')
    list_display_links = ('name', 'email', 'post', 'created', 'modified', 'hided')
    search_fields = ('name', 'email', 'content')
    date_hierarchy = 'created'
    ordering = ('created', 'modified')
    actions = [make_hidden, make_visible, delete_selected]
    filter_horizontal = ('liked_by', 'disliked_by')
    list_filter = ('hided',)
    show_facets = admin.ShowFacets.ALWAYS

    exclude = ('email_hash',)

    def add_view(self, request, form_url='', extra_context=None):
        self.exclude = ('hided','liked_by','disliked_by','email_hash')
        return super().add_view(request, form_url, extra_context)
# Register your models here.
