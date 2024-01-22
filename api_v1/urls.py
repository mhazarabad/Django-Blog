from django.urls import path
from . import views
from django.views.decorators.csrf import csrf_exempt

urlpatterns = [
    path(route='v1.0/posts/', view=csrf_exempt(views.Query_Post)),
    path(route='v1.0/posts/<int:post_id>/', view=csrf_exempt(views.Query_Post_Detail)),
    path(route='v1.0/categories/', view=csrf_exempt(views.Query_Category)),
    path(route='v<str:api_version>/posts/', view=csrf_exempt(views.API_Version_Not_Supported)),
]