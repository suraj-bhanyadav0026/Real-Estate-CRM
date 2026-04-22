from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator, MaxValueValidator

class CustomUser(AbstractUser):
    ROLE_CHOICES = [
        ('admin', _('Admin')),
        ('manager', _('Manager')),
        ('agent', _('Agent')),
    ]
    
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='agent')
    phone = models.CharField(max_length=20, blank=True)
    profile_photo = models.URLField(blank=True)
    specialization = models.JSONField(default=list)  # list of strings
    is_active_agent = models.BooleanField(default=True)
    
    class Meta:
        db_table = 'users'
    
    def __str__(self):
        return self.get_full_name() or self.email

LEAD_STATUS_CHOICES = [
    ('new', 'New'),
    ('contacted', 'Contacted'),
    ('qualified', 'Qualified'),
    ('site_visit_scheduled', 'Site Visit Scheduled'),
    ('negotiation', 'Negotiation'),
    ('closed_won', 'Closed Won'),
    ('closed_lost', 'Closed Lost'),
]

class Lead(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
    phone = models.CharField(max_length=20)
    email = models.EmailField(blank=True, null=True)
    budget_min = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    budget_max = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    location_pref = models.JSONField(default=dict)
    property_type_pref = models.JSONField(default=list)  # ['residential_apartment', ...]
    source = models.CharField(max_length=100, default='website')
    notes = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=LEAD_STATUS_CHOICES, default='new')
    score = models.IntegerField(default=0, validators=[MinValueValidator(0), MaxValueValidator(100)])
    assigned_to = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_leads')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'leads'
        indexes = [
            models.Index(fields=['status']),
            models.Index(fields=['assigned_to']),
            models.Index(fields=['score']),
            models.Index(fields=['phone']),
        ]
        constraints = [
            models.UniqueConstraint(fields=['phone', 'email'], name='unique_lead_contact')
        ]

    def __str__(self):
        return f"{self.name} ({self.phone})"

from django.db.models.signals import pre_save
from django.dispatch import receiver
from django.db.models import Max
from decimal import Decimal
from django.db.models.signals import pre_save
from django.dispatch import receiver

@receiver(pre_save, sender=Lead)
def auto_score_lead(sender, instance, **kwargs):
    \"\"\"Simple AI lead score: budget + source + quick assign.\"\"
    score = 50  # base
    if instance.budget_min and instance.budget_min > Decimal('5000000'):
        score += 30
    if instance.source in ['referral', 'whatsapp']:
        score += 20
    # Add engagement later
    instance.score = min(100, score)

@receiver(pre_save, sender=Lead)
def auto_assign_round_robin(sender, instance, **kwargs):
    \"\"\"Round-robin for managers.\"\"
    if not instance.assigned_to and instance.status == 'new':
        managers = CustomUser.objects.filter(role='manager', is_active_agent=True)
        if managers.exists():
            last_assigned = Lead.objects.filter(status='new').aggregate(Max('id'))['id__max']
            next_manager = managers.order_by('id')[last_assigned % managers.count()] if last_assigned else managers.first()
            instance.assigned_to = next_manager

