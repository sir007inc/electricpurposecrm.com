from django.urls import path
from . import views

app_name = 'crm'

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    
    # Appointments
    path('contacts/', views.contact_list, name='contact_list'),
    path('contacts/new/', views.contact_create, name='contact_create'),
    path('contacts/<int:pk>/', views.contact_detail, name='contact_detail'),
    path('contacts/<int:pk>/edit/', views.contact_update, name='contact_update'),
    path('contacts/<int:pk>/delete/', views.contact_delete, name='contact_delete'),
    path('contacts/export/csv/', views.export_contacts_csv, name='export_contacts_csv'),

    # Calendar & Schedule
    path('calendar/', views.calendar_view, name='calendar'),
    path('calendar/events/', views.calendar_events_api, name='calendar_events_api'),

    # Appointment quick actions
    path('contacts/<int:contact_pk>/interactions/new/', views.interaction_create, name='interaction_create'),
    path('interactions/<int:pk>/delete/', views.interaction_delete, name='interaction_delete'),
    path('contacts/<int:contact_pk>/notes/new/', views.note_create, name='note_create'),
    path('notes/<int:pk>/delete/', views.note_delete, name='note_delete'),
    path('contacts/<int:contact_pk>/tasks/new/', views.task_create, name='task_create'),
    path('tasks/<int:pk>/toggle/', views.task_toggle, name='task_toggle'),
]
