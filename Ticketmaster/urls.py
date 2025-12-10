from django.urls import *
from Ticketmaster import views

urlpatterns = [
    path("search/", views.search, name="search"),
    path("accounts/", views.createaccount, name="createaccount"),
    path("login/", views.login_view, name="login_view"),
    path('like/', views.likeEvent, name="likeEvent"),
    path('event/<event_id>/',views.event_view, name="event_view"),
    path('event/<event_id>/comment/',views.comment_view, name="comment_view"),
    path('event/<event_id>/comment/edit/',views.comment_edit, name="comment_edit"),
    path('event/<event_id>/comment/delete/',views.comment_delete, name="comment_delete"),
    path('user/<user_id>', views.user_view, name="user_view"),
    path('user/<user_id>/does-not-exist',views.user_dne, name="user_dne"),
    path('event/<event_id>/does-not-exist',views.event_dne, name="event_dne"),
    path('logout/', views.logout_view, name="logout_view"),
    path('ldcheck/', views.get_lightdark_cookie, name='ld_get'),
    path('ld/', views.set_lightdark_cookie, name='ld_set'),
]