from django.db import models

class Attack(models.Model):
    id = models.CharField(primary_key=True, max_length=100)  # Unique identifier, e.g., "invite_flood"
    name = models.CharField(max_length=100)  # e.g., Invite Flood, SIP Enumeration
    description = models.TextField()  # Details about the attack
    is_active = models.BooleanField(default=True)  # If the attack can be executed

    sip_username_range = models.CharField(max_length=255, blank=True, null=True)
    sip_server_ip_range = models.CharField(max_length=255, blank=True, null=True)

    interface = models.CharField(max_length=100, blank=True, null=True)
    username = models.CharField(max_length=100, blank=True, null=True)
    server_ip = models.GenericIPAddressField(max_length=100, blank=True, null=True)
    packets = models.PositiveBigIntegerField(max_length=100, blank=True, null=True)
    
    def __str__(self):
        return self.name
