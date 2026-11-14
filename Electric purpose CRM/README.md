# Electric Purpose Appointment CRM - Electrical Service & Appointment Management System

A streamlined electrical service appointment and client CRM built with **Python 3.12** and **Django 6.1**.

---

## Features

- **Dashboard**: High-level KPIs (Appointments, Active Leads, Installation, Pending Tasks), recent interactions stream, upcoming follow-ups, and recently scheduled appointments.
- **Appointments Directory**: Search across names, phone numbers, electrical services, and tags; filter by status (Lead, Prospect, Installation, Contractor / Partner, Inactive); paginated table; CSV export.
- **360° Appointment Profile**:
  - Detailed client snapshot (phone, service needed, service & access notes, tags).
  - Interactive **Touchpoint Timeline**: Chronological history of site visits, calls, SMS, inspection walkthroughs, and notes with outcome tracking.
  - Inline **Quick Log**: Log touchpoints or add notes directly from the appointment page.
  - **Pinned Notes**: Highlight critical client context or panel details at the top of the profile.
  - **Follow-up Checklist**: Track service tasks and parts orders with priorities, due dates, and one-click completion.
- **Built-in Django Admin**: Pre-configured admin portal with filters, search, inline interaction/note logging, and structured fieldsets.

---

## Quick Start

### 1. Run the Development Server
Open PowerShell in this directory (`C:\Users\mfes\OneDrive\Desktop\Electric purpose CRM`):

```powershell
.\.venv\Scripts\python.exe manage.py runserver
```

Open your browser to:
- **Web App**: [http://127.0.0.1:8000/](http://127.0.0.1:8000/)
- **Django Admin**: [http://127.0.0.1:8000/admin/](http://127.0.0.1:8000/admin/)

### 2. Login Credentials
- **Username**: `admin`
- **Password**: `admin123`
