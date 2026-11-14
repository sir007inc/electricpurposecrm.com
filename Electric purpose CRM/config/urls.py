from django.contrib import admin
from django.urls import path, include

admin.site.site_header = "Electric Purpose Appointment CRM"
admin.site.site_title = "Electric Purpose Appointment CRM Admin"
admin.site.index_title = "Electric Purpose Appointment CRM Administration"

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('crm.urls')),
]
