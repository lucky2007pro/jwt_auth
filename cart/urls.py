from django.urls import path
from .views import (
    CartView, CartItemAddView, CartItemUpdateView,
    CartItemRemoveView, CartClearView,
)

urlpatterns = [
    path('', CartView.as_view(), name='cart'),
    path('add/', CartItemAddView.as_view(), name='cart-add'),
    path('update/<int:item_id>/', CartItemUpdateView.as_view(), name='cart-update'),
    path('remove/<int:item_id>/', CartItemRemoveView.as_view(), name='cart-remove'),
    path('clear/', CartClearView.as_view(), name='cart-clear'),
]
