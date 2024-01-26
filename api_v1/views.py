
from django.http import HttpRequest
def Extract_Data_From_JSON(request:HttpRequest, key:str, value_type, request_section:str='body', default=None):
    """
    Extracts data from a JSON request.
    :param request: HttpRequest object
    :param key: Key to extract from JSON
    :param value_type: Type of value to extract
    :param request_section: Section of request to extract from (body or query)
    :param default: Default value to return if key is not found or value is not of type value_type
    """
    from json import loads as json_loads
    try:
        if request_section == 'query':
            value = request.GET[key]
            return value_type(value)
        if value_type == 'file':
            return request.FILES[key].read()
        value = json_loads(request.body.decode('utf-8'))[key]
        return value_type(value)
    except:
        return default
        
def API_Version_Not_Supported(request:HttpRequest,api_version:str):
    from django.http import JsonResponse
    return JsonResponse(data={'message': 'API version not supported'}, status=400)
    
def Query_Post(request:HttpRequest):
    from blog.models import Post
    from django.db.models import Q
    from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
    from django.http import JsonResponse

    # Extract data from request
    page = Extract_Data_From_JSON(request=request, key='page', request_section='body', value_type=int, default=1)
    page_size = Extract_Data_From_JSON(request=request, key='page_size', request_section='body', value_type=int, default=12)
    category_slug = Extract_Data_From_JSON(request=request, key='category_slug', request_section='body', value_type=str, default='')
    tag_slug = Extract_Data_From_JSON(request=request, key='tag_slug', request_section='body', value_type=str, default='')
    search = Extract_Data_From_JSON(request=request, key='search', request_section='body', value_type=str, default='')

    # Query
    q_category_slug = Q(category__slug=category_slug) if category_slug else Q()
    q_tag_slug = Q(tags__slug=tag_slug) if tag_slug else Q()
    q_search = Q(title__icontains=search)|Q(content__icontains=search)|Q(summary__icontains=search) if search else Q()
    q_status = Q(status='published')

    posts = Post.objects.filter(q_category_slug&q_tag_slug&q_search&q_status).order_by('-created')

    paginator = Paginator(posts, page_size)
    try:
        posts = paginator.page(page)
    except PageNotAnInteger:
        posts = paginator.page(1)
        page=1
    except EmptyPage:
        posts = []

    posts = [post.preview_response for post in posts]
    return JsonResponse(data={
        'posts': posts,
        'page': page,
        'page_size': page_size,
        'num_pages': paginator.num_pages,
        'num_posts': paginator.count,
        'category_slug': category_slug,
        'tag_slug': tag_slug,
        'search': search,
    }, status=200)

def Query_Post_Detail(request:HttpRequest, post_slug:int):
    from blog.models import Post
    from django.http import JsonResponse
    from django.shortcuts import get_object_or_404

    post = get_object_or_404(Post, slug=post_slug)
    return JsonResponse(data={'post':post.full_data_response}, status=200)

def Query_Category(request:HttpRequest):
    from blog.models import Category
    from django.http import JsonResponse

    categories = [category.response for category in Category.get_used_categories()]
    return JsonResponse(data={
        'categories': categories,
    }, status=200)


