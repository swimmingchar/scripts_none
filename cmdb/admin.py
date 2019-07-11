from django.contrib import admin
from cmdb.models import Host

# Register your models here.

class HostAdmin(admin.ModelAdmin):
    list_display=(
        'hostname',
        'ip',
        'os',
        'cpu_p'
    )

admin.site.register(Host,HostAdmin)