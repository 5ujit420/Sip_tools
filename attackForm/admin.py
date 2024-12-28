from django.contrib import admin
from .models import Attack


class AttackAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'is_active', 'interface', 'username', 'server_ip', 'packets', 'sip_username_range', 'sip_server_ip_range')
    search_fields = ('id', 'name', 'interface', 'username', 'server_ip', 'sip_username_range', 'sip_server_ip_range')
    list_filter = ('is_active',)

admin.site.register(Attack)