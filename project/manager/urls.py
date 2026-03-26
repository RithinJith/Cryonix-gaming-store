from django.urls import path
from manager import views


urlpatterns = [
    path('adminhome',views.adminhome,name='adminhome'),
    path('category',views.category,name='category'),
    path('view',views.view,name='view'), 
    path('delete/<int:id>',views.delete,name='delete'),
    path('editdata/<int:id>',views.editdata,name='editdata'),
    path('add_product',views.add_product,name='add_product'),
    path('view_prodct',views.view_prodct,name='view_prodct'),
    path('delete_prodct/<int:id>',views.delete_prodct,name='delete_prodct'),
    path('edit_prodct/<int:id>',views.edit_prodct,name='edit_prodct'),
    path('userorder_for_admin',views.userorder_for_admin,name='userorder_for_admin'),
    path('orderdetails_for_manager/<int:id>/', views.orderdetails_for_manager, name='orderdetails_for_manager')    ,
    path('cancel_order/<int:id>',views.cancel_order,name='cancel_order'),
    path('Completeorder/<int:id>',views.Completeorder,name='Completeorder')
]
