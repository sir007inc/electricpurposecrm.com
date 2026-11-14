from django import forms
from .models import Contact, Interaction, Note, Task


class ContactForm(forms.ModelForm):
    appointment_date = forms.DateTimeField(
        required=False,
        widget=forms.DateTimeInput(
            attrs={'class': 'form-control', 'type': 'datetime-local'},
            format='%Y-%m-%dT%H:%M'
        ),
        input_formats=['%Y-%m-%dT%H:%M', '%Y-%m-%d %H:%M:%S', '%Y-%m-%d %H:%M', '%Y-%m-%d'],
        label='Appointment Date & Time',
        help_text='Select the scheduled service date and time'
    )

    class Meta:
        model = Contact
        fields = [
            'first_name', 'last_name', 'phone', 'title', 
            'appointment_date', 'status', 'tags', 'background_info'
        ]
        labels = {
            'title': 'Service / Role',
            'background_info': 'Service & Access Notes',
        }
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'First name (e.g. John)'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Last name (e.g. Smith)'}),
            'phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '+1 (555) 000-0000'}),
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. EV Charger Install, 200A Panel'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'tags': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. EV Charger, Panel Upgrade, Urgent'}),
            'background_info': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Gate codes, panel location, job details...'}),
        }


class QuickInteractionForm(forms.ModelForm):
    class Meta:
        model = Interaction
        fields = ['interaction_type', 'title', 'details', 'outcome', 'occurred_at']
        labels = {
            'interaction_type': 'Touchpoint / Service Type',
            'title': 'Subject / Service Needed',
            'details': 'Notes & Conversation Details',
        }
        widgets = {
            'interaction_type': forms.Select(attrs={'class': 'form-select form-select-sm'}),
            'title': forms.TextInput(attrs={'class': 'form-control form-control-sm', 'placeholder': 'e.g. Site visit for EV charger installation'}),
            'details': forms.Textarea(attrs={'class': 'form-control form-control-sm', 'rows': 3, 'placeholder': 'Discussion details, quote estimates, parts needed, next steps...'}),
            'outcome': forms.Select(attrs={'class': 'form-select form-select-sm'}),
            'occurred_at': forms.DateTimeInput(attrs={'class': 'form-control form-control-sm', 'type': 'datetime-local'}),
        }


class QuickNoteForm(forms.ModelForm):
    class Meta:
        model = Note
        fields = ['title', 'content', 'is_pinned']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control form-control-sm', 'placeholder': 'Note title (e.g. Main Breaker Size)'}),
            'content': forms.Textarea(attrs={'class': 'form-control form-control-sm', 'rows': 3, 'placeholder': 'Write electrical note or property observation here...'}),
            'is_pinned': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class QuickTaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = ['title', 'due_date', 'priority']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control form-control-sm', 'placeholder': 'Follow-up / service task (e.g. Order 50A GFCI breaker)...'}),
            'due_date': forms.DateInput(attrs={'class': 'form-control form-control-sm', 'type': 'date'}),
            'priority': forms.Select(attrs={'class': 'form-select form-select-sm'}),
        }
