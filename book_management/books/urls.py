from django.urls import path
from .views import BookList, BookDetail, UserLoginView, TokenRefreshView, AveragePriceByYearView, UserCreateView

urlpatterns = [
    path('books/', BookList.as_view(), name='book-list'),
    path('books/<str:pk>/', BookDetail.as_view(), name='book-detail'),
    path('login/', UserLoginView.as_view(), name='user-login'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token-refresh'),
    path('books/average-price/<int:year>/', AveragePriceByYearView.as_view(), name='average-price-by-year'),
    path('users/', UserCreateView.as_view(), name='create-user'),
]