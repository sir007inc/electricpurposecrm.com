from django.contrib import admin
from .models import Contact, Interaction, Note, Task


class NoteInline(admin.TabularInline):
    model = Note
    extra = 1
    fields = ('title', 'content', 'is_pinned')


class InteractionInline(admin.TabularInline):
    model = Interaction
    extra = 1
    fields = ('interaction_type', 'title', 'outcome', 'occurred_at')


class TaskInline(admin.TabularInline):
    model = Task
    extra = 0
    fields = ('title', 'due_date', 'priority', 'is_completed')


@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'title', 'appointment_date', 'phone', 'status', 'created_at')
    list_filter = ('status', 'appointment_date', 'created_at')
    search_fields = ('first_name', 'last_name', 'phone', 'title', 'tags', 'background_info')
    inlines = [InteractionInline, NoteInline, TaskInline]
    fieldsets = (
        ("Client Information", {
            "fields": (("first_name", "last_name"), "title", "phone")
        }),
        ("Schedule & Status", {
            "fields": ("appointment_date", "status", "tags", "background_info")
        }),
    )


@admin.register(Interaction)
class InteractionAdmin(admin.ModelAdmin):
    list_display = ('title', 'contact', 'interaction_type', 'outcome', 'occurred_at')
    list_filter = ('interaction_type', 'outcome', 'occurred_at')
    search_fields = ('title', 'details', 'contact__first_name', 'contact__last_name')
    date_hierarchy = 'occurred_at'


@admin.register(Note)
class NoteAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'contact', 'is_pinned', 'created_at')
    list_filter = ('is_pinned', 'created_at')
    search_fields = ('title', 'content', 'contact__first_name', 'contact__last_name')


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ('title', 'contact', 'priority', 'due_date', 'is_completed')
    list_filter = ('is_completed', 'priority', 'due_date')
    search_fields = ('title', 'contact__first_name', 'contact__last_name')
