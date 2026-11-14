import csv
from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse, JsonResponse
from django.contrib import messages
from django.db.models import Q
from django.core.paginator import Paginator
from django.utils import timezone
from .models import Contact, Interaction, Note, Task
from .forms import ContactForm, QuickInteractionForm, QuickNoteForm, QuickTaskForm


def dashboard(request):
    total_contacts = Contact.objects.count()
    leads_count = Contact.objects.filter(status='lead').count()
    installations_count = Contact.objects.filter(status='installation').count()
    pending_tasks_count = Task.objects.filter(is_completed=False).count()
    scheduled_appointments_count = Contact.objects.filter(appointment_date__isnull=False).count()

    now = timezone.now()
    upcoming_appointments = Contact.objects.filter(appointment_date__gte=now).order_by('appointment_date')[:6]
    pending_tasks = Task.objects.filter(is_completed=False).select_related('contact').order_by('due_date')[:6]
    recent_interactions = Interaction.objects.select_related('contact').order_by('-occurred_at')[:8]
    recent_contacts = Contact.objects.order_by('-created_at')[:5]

    context = {
        'total_contacts': total_contacts,
        'leads_count': leads_count,
        'installations_count': installations_count,
        'pending_tasks_count': pending_tasks_count,
        'scheduled_appointments_count': scheduled_appointments_count,
        'upcoming_appointments': upcoming_appointments,
        'pending_tasks': pending_tasks,
        'recent_interactions': recent_interactions,
        'recent_contacts': recent_contacts,
    }
    return render(request, 'crm/dashboard.html', context)


def contact_list(request):
    query = request.GET.get('q', '').strip()
    status_filter = request.GET.get('status', '').strip()
    schedule_filter = request.GET.get('schedule', '').strip()

    contacts = Contact.objects.all()

    if query:
        contacts = contacts.filter(
            Q(first_name__icontains=query) |
            Q(last_name__icontains=query) |
            Q(phone__icontains=query) |
            Q(title__icontains=query) |
            Q(tags__icontains=query) |
            Q(background_info__icontains=query)
        ).distinct()

    if status_filter:
        contacts = contacts.filter(status=status_filter)

    if schedule_filter == 'scheduled':
        contacts = contacts.filter(appointment_date__isnull=False).order_by('appointment_date')
    elif schedule_filter == 'upcoming':
        contacts = contacts.filter(appointment_date__gte=timezone.now()).order_by('appointment_date')
    elif schedule_filter == 'unscheduled':
        contacts = contacts.filter(appointment_date__isnull=True).order_by('-created_at')

    paginator = Paginator(contacts, 15)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'contacts': page_obj,
        'query': query,
        'status_filter': status_filter,
        'schedule_filter': schedule_filter,
        'status_choices': Contact.STATUS_CHOICES,
        'total_results': paginator.count,
    }
    return render(request, 'crm/contact_list.html', context)


def calendar_view(request):
    total_appointments = Contact.objects.count()
    scheduled_appointments = Contact.objects.filter(appointment_date__isnull=False).count()
    pending_followups = Task.objects.filter(is_completed=False).count()
    completed_followups = Task.objects.filter(is_completed=True).count()

    context = {
        'total_appointments': total_appointments,
        'scheduled_appointments': scheduled_appointments,
        'pending_followups': pending_followups,
        'completed_followups': completed_followups,
    }
    return render(request, 'crm/calendar.html', context)


def calendar_events_api(request):
    events = []

    # 1. Appointments (Contacts with appointment_date)
    contacts = Contact.objects.filter(appointment_date__isnull=False)
    for contact in contacts:
        color_map = {
            'installation': '#198754',  # Green
            'lead': '#e0a800',          # Darker amber
            'prospect': '#0d6efd',      # Blue
            'partner': '#0dcaf0',       # Cyan
            'inactive': '#6c757d',      # Gray
        }
        color = color_map.get(contact.status, '#0d6efd')

        events.append({
            'id': f'appointment-{contact.pk}',
            'title': f"⚡ {contact.full_name} - {contact.title or contact.get_status_display()}",
            'start': contact.appointment_date.isoformat(),
            'url': f"/contacts/{contact.pk}/",
            'backgroundColor': color,
            'borderColor': color,
            'textColor': '#ffffff',
            'extendedProps': {
                'type': 'appointment',
                'client_name': contact.full_name,
                'phone': contact.phone or 'No phone',
                'service': contact.title or 'General Electrical Service',
                'status': contact.get_status_display(),
                'status_badge': contact.status_badge_class,
                'datetime_str': contact.appointment_date.strftime('%b %d, %Y at %I:%M %p'),
                'detail_url': f"/contacts/{contact.pk}/",
            }
        })

    # 2. Follow-ups (Tasks with due_date)
    tasks = Task.objects.filter(due_date__isnull=False).select_related('contact')
    for task in tasks:
        if task.is_completed:
            color = '#6c757d'
        elif task.priority == 'high':
            color = '#dc3545'  # Red
        elif task.priority == 'medium':
            color = '#fd7e14'  # Orange
        else:
            color = '#6f42c1'  # Purple

        client_name = task.contact.full_name if task.contact else "General Follow-up"
        detail_url = f"/contacts/{task.contact.pk}/" if task.contact else "/contacts/"

        events.append({
            'id': f'task-{task.pk}',
            'title': f"📋 Follow-up: {task.title}" + (f" ({client_name})" if task.contact else ""),
            'start': task.due_date.isoformat(),
            'allDay': True,
            'url': detail_url,
            'backgroundColor': color,
            'borderColor': color,
            'textColor': '#ffffff',
            'extendedProps': {
                'type': 'followup',
                'title': task.title,
                'client_name': client_name,
                'priority': task.get_priority_display(),
                'is_completed': task.is_completed,
                'due_date_str': task.due_date.strftime('%b %d, %Y'),
                'detail_url': detail_url,
            }
        })

    return JsonResponse(events, safe=False)


def contact_detail(request, pk):
    contact = get_object_or_404(Contact, pk=pk)
    interactions = contact.interactions.all().order_by('-occurred_at')
    notes = contact.notes.all().order_by('-is_pinned', '-created_at')
    tasks = contact.tasks.all().order_by('is_completed', 'due_date')

    interaction_form = QuickInteractionForm(initial={'occurred_at': timezone.now().strftime('%Y-%m-%dT%H:%M')})
    note_form = QuickNoteForm()
    task_form = QuickTaskForm()

    context = {
        'contact': contact,
        'interactions': interactions,
        'notes': notes,
        'tasks': tasks,
        'interaction_form': interaction_form,
        'note_form': note_form,
        'task_form': task_form,
    }
    return render(request, 'crm/contact_detail.html', context)


def contact_create(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            contact = form.save()
            messages.success(request, f"Appointment for '{contact.full_name}' scheduled successfully!")
            return redirect('crm:contact_detail', pk=contact.pk)
    else:
        form = ContactForm()

    return render(request, 'crm/contact_form.html', {'form': form, 'title': 'Schedule New Appointment'})


def contact_update(request, pk):
    contact = get_object_or_404(Contact, pk=pk)
    if request.method == 'POST':
        form = ContactForm(request.POST, instance=contact)
        if form.is_valid():
            contact = form.save()
            messages.success(request, f"Appointment for '{contact.full_name}' updated successfully!")
            return redirect('crm:contact_detail', pk=contact.pk)
    else:
        form = ContactForm(instance=contact)

    return render(request, 'crm/contact_form.html', {'form': form, 'contact': contact, 'title': f'Edit Appointment - {contact.full_name}'})


def contact_delete(request, pk):
    contact = get_object_or_404(Contact, pk=pk)
    if request.method == 'POST':
        name = contact.full_name
        contact.delete()
        messages.success(request, f"Appointment for '{name}' deleted.")
        return redirect('crm:contact_list')
    return render(request, 'crm/confirm_delete.html', {'object': contact, 'type': 'Appointment'})


def interaction_create(request, contact_pk):
    contact = get_object_or_404(Contact, pk=contact_pk)
    if request.method == 'POST':
        form = QuickInteractionForm(request.POST)
        if form.is_valid():
            interaction = form.save(commit=False)
            interaction.contact = contact
            interaction.save()
            messages.success(request, f"Logged {interaction.get_interaction_type_display()} successfully.")
        else:
            messages.error(request, "Error saving interaction. Please check input.")
    return redirect('crm:contact_detail', pk=contact.pk)


def interaction_delete(request, pk):
    interaction = get_object_or_404(Interaction, pk=pk)
    contact_pk = interaction.contact.pk
    if request.method == 'POST':
        interaction.delete()
        messages.success(request, "Interaction entry removed.")
    return redirect('crm:contact_detail', pk=contact_pk)


def note_create(request, contact_pk):
    contact = get_object_or_404(Contact, pk=contact_pk)
    if request.method == 'POST':
        form = QuickNoteForm(request.POST)
        if form.is_valid():
            note = form.save(commit=False)
            note.contact = contact
            note.save()
            messages.success(request, "Note added.")
        else:
            messages.error(request, "Could not add note.")
    return redirect('crm:contact_detail', pk=contact.pk)


def note_delete(request, pk):
    note = get_object_or_404(Note, pk=pk)
    contact_pk = note.contact.pk
    if request.method == 'POST':
        note.delete()
        messages.success(request, "Note deleted.")
    return redirect('crm:contact_detail', pk=contact_pk)


def task_create(request, contact_pk):
    contact = get_object_or_404(Contact, pk=contact_pk)
    if request.method == 'POST':
        form = QuickTaskForm(request.POST)
        if form.is_valid():
            task = form.save(commit=False)
            task.contact = contact
            task.save()
            messages.success(request, "Task created.")
    return redirect('crm:contact_detail', pk=contact.pk)


def task_toggle(request, pk):
    task = get_object_or_404(Task, pk=pk)
    if request.method == 'POST':
        task.is_completed = not task.is_completed
        task.save()
        status_text = "completed" if task.is_completed else "re-opened"
        messages.success(request, f"Task marked as {status_text}.")
    if task.contact:
        return redirect('crm:contact_detail', pk=task.contact.pk)
    return redirect('crm:dashboard')


def export_contacts_csv(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="appointments_export.csv"'
    writer = csv.writer(response)
    writer.writerow(['First Name', 'Last Name', 'Service / Role', 'Phone', 'Appointment Date & Time', 'Status', 'Tags', 'Created At'])

    for c in Contact.objects.all():
        writer.writerow([
            c.first_name,
            c.last_name,
            c.title,
            c.phone,
            c.appointment_date.strftime('%Y-%m-%d %H:%M') if c.appointment_date else 'Unscheduled',
            c.get_status_display(),
            c.tags,
            c.created_at.strftime('%Y-%m-%d %H:%M')
        ])
    return response
