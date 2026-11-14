from django.db import models
from django.utils import timezone


class Contact(models.Model):
    STATUS_CHOICES = [
        ('lead', 'Lead'),
        ('prospect', 'Prospect'),
        ('installation', 'Installation'),
        ('partner', 'Contractor / Partner'),
        ('inactive', 'Inactive'),
    ]

    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    title = models.CharField(max_length=120, blank=True, verbose_name="Role / Service", help_text="e.g. EV Charger Install, 200A Panel Upgrade, Inspection, Rewiring")
    phone = models.CharField(max_length=50, blank=True)
    appointment_date = models.DateTimeField(null=True, blank=True, verbose_name="Appointment Date & Time", help_text="Scheduled date and time for service appointment")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='lead')
    tags = models.CharField(max_length=255, blank=True, help_text="Comma-separated tags (e.g. Urgent, EV Charger, 200A, Generator)")
    background_info = models.TextField(blank=True, verbose_name="Service & Access Notes", help_text="Gate codes, panel location, job notes, preferred service time...")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-updated_at']
        verbose_name = "Appointment"
        verbose_name_plural = "Appointments"

    def __str__(self):
        return self.full_name

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}".strip()

    @property
    def initials(self):
        first = self.first_name[0].upper() if self.first_name else ''
        last = self.last_name[0].upper() if self.last_name else ''
        return f"{first}{last}" or '?'

    @property
    def tag_list(self):
        if not self.tags:
            return []
        return [tag.strip() for tag in self.tags.split(',') if tag.strip()]

    @property
    def is_upcoming(self):
        if not self.appointment_date:
            return False
        return self.appointment_date >= timezone.now()

    @property
    def status_badge_class(self):
        badge_map = {
            'lead': 'bg-warning text-dark',
            'prospect': 'bg-primary text-white',
            'installation': 'bg-success text-white',
            'partner': 'bg-info text-dark',
            'inactive': 'bg-secondary text-white',
        }
        return badge_map.get(self.status, 'bg-light text-dark')


class Interaction(models.Model):
    TYPE_CHOICES = [
        ('call', 'Phone Call'),
        ('email', 'Email Sent/Received'),
        ('meeting', 'Site Visit / Estimate'),
        ('message', 'SMS / Text Message'),
        ('demo', 'Service Inspection / Walkthrough'),
        ('note', 'Service Note'),
    ]

    OUTCOME_CHOICES = [
        ('successful', 'Job Approved / Positive'),
        ('neutral', 'Quote Sent / Information Shared'),
        ('follow_up_needed', 'Follow-up Needed'),
        ('unreachable', 'Unreachable / Left Voicemail'),
    ]

    contact = models.ForeignKey(Contact, on_delete=models.CASCADE, related_name='interactions')
    interaction_type = models.CharField(max_length=20, choices=TYPE_CHOICES, default='call')
    title = models.CharField(max_length=200)
    details = models.TextField()
    outcome = models.CharField(max_length=25, choices=OUTCOME_CHOICES, default='neutral')
    occurred_at = models.DateTimeField(default=timezone.now)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-occurred_at']

    def __str__(self):
        return f"{self.get_interaction_type_display()} with {self.contact.full_name}: {self.title}"

    @property
    def type_icon_class(self):
        icon_map = {
            'call': 'bi-telephone-fill text-success',
            'email': 'bi-envelope-fill text-primary',
            'meeting': 'bi-tools text-warning',
            'message': 'bi-chat-dots-fill text-info',
            'demo': 'bi-lightning-charge-fill text-danger',
            'note': 'bi-file-earmark-text-fill text-secondary',
        }
        return icon_map.get(self.interaction_type, 'bi-clock-history')


class Note(models.Model):
    contact = models.ForeignKey(Contact, on_delete=models.CASCADE, null=True, blank=True, related_name='notes')
    title = models.CharField(max_length=150, blank=True)
    content = models.TextField()
    is_pinned = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-is_pinned', '-created_at']

    def __str__(self):
        return self.title or f"Note on {self.contact}"


class Task(models.Model):
    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High / Urgent'),
    ]

    contact = models.ForeignKey(Contact, on_delete=models.CASCADE, null=True, blank=True, related_name='tasks')
    title = models.CharField(max_length=200)
    due_date = models.DateField(null=True, blank=True)
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='medium')
    is_completed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['is_completed', 'due_date', '-created_at']

    def __str__(self):
        return self.title
