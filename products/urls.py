from django.urls import path
from .views import (
    CategoryListView, CategoryDetailView, CategoryCreateView,
    BrandListView, BrandDetailView,
    ProductListView, ProductDetailView,
    ProductCreateView, ProductUpdateView, ProductDeleteView,
    ProductImageAddView, ProductImageDeleteView,
)

urlpatterns = [
    path('categories/', CategoryListView.as_view(), name='category-list'),
    path('categories/create/', CategoryCreateView.as_view(), name='category-create'),
    path('categories/<slug:slug>/', CategoryDetailView.as_view(), name='category-detail'),

    path('brands/', BrandListView.as_view(), name='brand-list'),
    path('brands/<slug:slug>/', BrandDetailView.as_view(), name='brand-detail'),

    path('', ProductListView.as_view(), name='product-list'),
    path('create/', ProductCreateView.as_view(), name='product-create'),
    path('<slug:slug>/', ProductDetailView.as_view(), name='product-detail'),
    path('<int:pk>/update/', ProductUpdateView.as_view(), name='product-update'),
    path('<int:pk>/delete/', ProductDeleteView.as_view(), name='product-delete'),

    path('<int:pk>/images/add/', ProductImageAddView.as_view(), name='product-image-add'),
    path('<int:pk>/images/<int:image_id>/delete/', ProductImageDeleteView.as_view(), name='product-image-delete'),
]
