from django.urls import path
from . import views

urlpatterns = [
    path('', views.accueil, name='accueil'),
    path('evaluation_user/guidage/', views.guidage_page, name='guidage_page'),
    path('evaluation_user/evaluation/', views.evaluation_page, name='evaluation_page'),
    path('evaluation_user/discussion/', views.evaluation_discussion, name='evaluation_discussion'),
    path('evalution_search_construit/', views.evalution_search_construit, name='evalution_search_construit'),
    path('modal_search/', views.modal_search_view, name='modal_search_view'),
    path('submit-evaluation/', views.submit_evaluation_data, name='submit_evaluation'),
    path('submit-evaluation-with-pdf/', views.submit_evaluation_with_pdf, name='submit_evaluation_with_pdf'),
    path('modify-profile/', views.modify_profile, name='modify_profile'),
    path('admin/', views.admin_page, name='admin_page'),
    path('admin/utilisateurs/', views.utilisateurs_view, name='utilisateurs'),
    path('add_user/', views.add_user_view, name='add_user'),
    path('delete_user/<int:user_id>/', views.delete_user, name='delete_user'),
    path('login/', views.login_view, name='login_view'),
    path('logout/', views.logout_view, name='logout_view'),
    path('search-users/', views.search_users, name='search_users'),
]