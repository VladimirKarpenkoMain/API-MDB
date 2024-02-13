from django.urls import include, path
from rest_framework.routers import DefaultRouter

import api.views

app_name = 'api'

router = DefaultRouter()
router.register('users', api.views.UserViewSet, basename='user')
router.register('categories', api.views.CategoryViewSet, basename='category')
router.register('genres', api.views.GenreViewSet, basename='genre')
router.register('titles', api.views.TitleViewSet, basename='title')
router.register(r'titles/(?P<title_id>\d+)/reviews', api.views.ReviewViewSet, basename='review')
router.register(r'titles/(?P<title_id>\d+)/reviews/(?P<review_id>\d+)/comments/', api.views.CommentViewSet, basename='comment')

urlpatterns = [
    path("auth/signup/", api.views.UserCreateViewSet.as_view({'post': 'create'}), name='signup'),
    path("auth/token/", api.views.UserReceiveTokenViewSet.as_view({'post': 'create'}), name='token'),
    path("", include(router.urls)),
]
