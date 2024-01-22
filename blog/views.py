
def Landing(request,category_slug=None,tag_slug=None):
    if request.method != 'GET':
        from django.http.response import HttpResponseNotAllowed
        return HttpResponseNotAllowed(['GET'])
        
    from django.shortcuts import render
    from .models import Post, Category
    from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
    from django.db.models import Q
    q_category = Q(category__slug=category_slug) if category_slug else Q()
    q_tag = Q(tags__slug=tag_slug) if tag_slug else Q()
    q_status = Q(status='published')
    posts=Post.objects.filter(
        q_category,
        q_tag,
        q_status
    ).order_by('-created')
    paginator = Paginator(posts, 6)
    page_num = request.GET.get('page', 1)
    try:
        page_object = paginator.page(page_num)
    except PageNotAnInteger:
        # if page is not an integer, deliver the first page
        page_object = paginator.page(1)
    except EmptyPage:
        # if the page is out of range, deliver the last page
        page_object = paginator.page(paginator.num_pages)

    categories = Category.objects.all()
    return render(request, 'blog/blog_landing.html', {'title': 'Home', 'page_object': page_object, 'categories': categories})

def PostDetail(request,post_slug):
    from django.shortcuts import render, get_object_or_404
    from .models import Post, Category
    post = get_object_or_404(Post, slug=post_slug)
    categories = Category.get_used_categories()
    return render(request, 'blog/single_post.html', {'post': post, 'categories': categories})