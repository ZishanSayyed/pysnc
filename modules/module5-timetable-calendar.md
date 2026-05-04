# 📘 Module 4 — Timetable, Scheduling & Calendar (Documentation)

---

## 🎯 Objective

Build a **combined timetable, scheduling, and school calendar system** for the multi-tenant School ERP:

* Define school-wide time slots (periods)
* Create weekly timetable entries per class
* Assign teacher + subject to each slot
* Conflict detection (teacher double-booked)
* Per-teacher and per-class timetable views
* Substitution system for one-day teacher overrides
* School calendar with holidays, exams, events, announcements
* Class-level vs school-wide event scoping
* Combined full calendar view (timetable + events in one response)

---

# 🧱 What We Built

## ✅ 1. Four-Model Architecture

### `TimeSlot`
School's daily period structure — reusable across all classes.

| Field | Description |
|---|---|
| `school` | Tenant FK |
| `name` | e.g. "Period 1", "Lunch Break" |
| `start_time` | e.g. `08:00` |
| `end_time` | e.g. `08:45` |
| `slot_number` | Ordering index (1, 2, 3 …) |
| `is_break` | True for lunch / recess |

---

### `TimetableEntry`
One entry = one class + one day + one time slot.

| Field | Description |
|---|---|
| `school` | Tenant FK |
| `class_obj` | Which class |
| `subject` | FK to Subject |
| `teacher` | FK to Teacher |
| `time_slot` | FK to TimeSlot |
| `day_of_week` | `monday` … `saturday` |
| `room` | Optional room / lab label |
| `academic_year` | e.g. `2025-26` |
| `effective_from` | Date this entry starts |
| `effective_to` | Null = ongoing |
| `is_active` | Soft-delete flag |

**Unique constraint:** `(school, class_obj, time_slot, day_of_week, academic_year)`

---

### `TimetableSubstitution`
One-day override for an absent teacher.

| Field | Description |
|---|---|
| `timetable_entry` | FK to original entry |
| `date` | Specific date |
| `substitute_teacher` | FK to Teacher |
| `reason` | Optional note |
| `created_by` | Who created it |

---

### `CalendarEvent`
School calendar — holidays, exams, events, announcements.

| Field | Description |
|---|---|
| `school` | Tenant FK |
| `title` | Event title |
| `description` | Optional detail |
| `event_type` | `holiday` / `exam` / `event` / `announcement` |
| `scope` | `school` (school-wide) or `class` (class-specific) |
| `class_obj` | Required when scope = `class` |
| `start_date` | Start date |
| `end_date` | End date |
| `start_time` | Optional time |
| `end_time` | Optional time |
| `academic_year` | e.g. `2025-26` |
| `is_active` | Soft-delete flag |

---
---
# 🗂️ Files to Create

```
timetable_module/
├── CONFIG_SNIPPETS.py
├── module4-timetable-calendar.md
└── apps/
    └── timetable/
        ├── __init__.py
        ├── apps.py
        ├── models.py
        ├── serializers.py
        ├── views.py
        ├── urls.py
        ├── admin.py
        └── migrations/
            ├── __init__.py
            └── 0001_initial.py

```
---
## ✅ 2. Multi-Tenant Safety

All queries scoped to `request.school`.

## ✅ 3. Conflict Detection

* **Teacher conflict** — teacher already in another class at same slot/day
* **Class conflict** — enforced by DB unique constraint

## ✅ 4. Role-Based Access

| Role | Access |
|---|---|
| Management | Full CRUD on all |
| Teacher | Read-only (own timetable + events) |

---

# ⚙️ Setup

## 1. Add to INSTALLED_APPS (`config/settings.py`)
```python
"apps.timetable",
```

## 2. Add URL (`config/urls.py`)
```python
path("api/timetable/", include("apps.timetable.urls")),
```

## 3. Migrate
```bash
python manage.py makemigrations timetable
python manage.py migrate timetable
```

---

# 📡 TIME SLOT APIs

## ➕ 1. Create Time Slot

```http
POST /api/timetable/slots/
```

```bash
curl -X POST http://127.0.0.1:8000/api/timetable/slots/ \
  -H "Authorization: Bearer MGMT_TOKEN" \
  -H "Content-Type: application/json" \
  -H "X-School-Slug: greenwood" \
  -d '{"name": "Period 1", "start_time": "08:00", "end_time": "08:45", "slot_number": 1, "is_break": false}'
```

Response:
```json
{"id": 1, "name": "Period 1", "start_time": "08:00", "end_time": "08:45", "slot_number": 1, "is_break": false}
```

---

## 📋 2. List Time Slots

```http
GET /api/timetable/slots/
```

```bash
curl -X GET http://127.0.0.1:8000/api/timetable/slots/ \
  -H "Authorization: Bearer MGMT_TOKEN" \
  -H "X-School-Slug: greenwood"
```

---

## ✏️ 3. Update / ❌ 4. Delete Time Slot

```http
PUT  /api/timetable/slots/{id}/
DELETE /api/timetable/slots/{id}/
```

> ⚠️ Delete fails if any TimetableEntry references this slot.

---

# 📡 TIMETABLE ENTRY APIs

## 🔍 5. Check Conflict (Dry Run)

```http
POST /api/timetable/entries/check-conflict/
```

```bash
curl -X POST http://127.0.0.1:8000/api/timetable/entries/check-conflict/ \
  -H "Authorization: Bearer MGMT_TOKEN" \
  -H "Content-Type: application/json" \
  -H "X-School-Slug: greenwood" \
  -d '{"class_obj": 1, "teacher": 1, "time_slot": 2, "day_of_week": "monday", "academic_year": "2025-26"}'
```

Response (no conflict):
```json
{"conflict": false, "message": "Slot is available."}
```

Response (conflict):
```json
{
  "conflict": true,
  "conflict_type": "teacher",
  "message": "Bob Brown is already teaching Mathematics in Grade 9 B at this slot."
}
```

---

## ➕ 6. Create Timetable Entry

```http
POST /api/timetable/entries/
```

```bash
curl -X POST http://127.0.0.1:8000/api/timetable/entries/ \
  -H "Authorization: Bearer MGMT_TOKEN" \
  -H "Content-Type: application/json" \
  -H "X-School-Slug: greenwood" \
  -d '{
    "class_obj": 1,
    "subject": 1,
    "teacher": 1,
    "time_slot": 1,
    "day_of_week": "monday",
    "room": "Room 101",
    "academic_year": "2025-26",
    "effective_from": "2025-06-01"
  }'
```

Response:
```json
{
  "id": 1,
  "class_obj": 1,
  "class_name": "Grade 10 A (2025-26)",
  "subject": 1,
  "subject_name": "Mathematics",
  "teacher": 1,
  "teacher_name": "Bob Brown",
  "time_slot": 1,
  "slot_name": "Period 1",
  "start_time": "08:00",
  "end_time": "08:45",
  "day_of_week": "monday",
  "room": "Room 101",
  "academic_year": "2025-26",
  "effective_from": "2025-06-01",
  "effective_to": null,
  "is_active": true
}
```

---

## 📋 7. List Entries

```http
GET /api/timetable/entries/
```

Query params: `class_id`, `teacher_id`, `day_of_week`, `academic_year`, `subject_id`

```bash
curl -X GET "http://127.0.0.1:8000/api/timetable/entries/?class_id=1&academic_year=2025-26" \
  -H "Authorization: Bearer MGMT_TOKEN" \
  -H "X-School-Slug: greenwood"
```

---

## ✏️ 8. Update Entry

```http
PUT /api/timetable/entries/{id}/
```

> Conflict check re-runs on update.

---

## ❌ 9. Deactivate Entry

```http
DELETE /api/timetable/entries/{id}/
```

Soft-deletes (`is_active = false`).

---

# 📡 TIMETABLE VIEW APIs

## 🗓️ 10. Class Weekly Timetable

```http
GET /api/timetable/class/{class_id}/?academic_year=2025-26
```

```bash
curl -X GET "http://127.0.0.1:8000/api/timetable/class/1/?academic_year=2025-26" \
  -H "Authorization: Bearer MGMT_TOKEN" \
  -H "X-School-Slug: greenwood"
```

Response:
```json
{
  "class_name": "Grade 10 A (2025-26)",
  "academic_year": "2025-26",
  "timetable": {
    "monday": [
      {"slot_number": 1, "slot_name": "Period 1", "start_time": "08:00", "end_time": "08:45", "subject": "Mathematics", "teacher": "Bob Brown", "room": "Room 101"},
      {"slot_number": 2, "slot_name": "Period 2", "start_time": "08:45", "end_time": "09:30", "subject": "English",     "teacher": "Alice Green", "room": "Room 102"}
    ],
    "tuesday": [ "..." ],
    "wednesday": [ "..." ]
  }
}
```

---

## 👩‍🏫 11. Teacher Weekly Timetable

```http
GET /api/timetable/teacher/{teacher_id}/?academic_year=2025-26
```

```bash
curl -X GET "http://127.0.0.1:8000/api/timetable/teacher/1/?academic_year=2025-26" \
  -H "Authorization: Bearer MGMT_TOKEN" \
  -H "X-School-Slug: greenwood"
```

Response:
```json
{
  "teacher_name": "Bob Brown",
  "academic_year": "2025-26",
  "timetable": {
    "monday": [
      {"slot_number": 1, "slot_name": "Period 1", "start_time": "08:00", "end_time": "08:45", "class_name": "Grade 10 A (2025-26)", "subject": "Mathematics", "room": "Room 101"}
    ]
  }
}
```

---

# 📡 SUBSTITUTION APIs

## ➕ 12. Create Substitution

```http
POST /api/timetable/substitutions/
```

```bash
curl -X POST http://127.0.0.1:8000/api/timetable/substitutions/ \
  -H "Authorization: Bearer MGMT_TOKEN" \
  -H "Content-Type: application/json" \
  -H "X-School-Slug: greenwood" \
  -d '{"timetable_entry": 1, "date": "2025-06-10", "substitute_teacher": 2, "reason": "Bob is on leave"}'
```

Response:
```json
{
  "id": 1,
  "timetable_entry": 1,
  "date": "2025-06-10",
  "substitute_teacher": 2,
  "substitute_teacher_name": "Alice Green",
  "reason": "Bob is on leave",
  "created_by": 1,
  "created_by_name": "greenwood.admin",
  "created_at": "2025-06-10T08:00:00Z"
}
```

---

## 📋 13. List Substitutions

```http
GET /api/timetable/substitutions/
```

Query params: `date`, `class_id`, `teacher_id`

```bash
curl -X GET "http://127.0.0.1:8000/api/timetable/substitutions/?date=2025-06-10" \
  -H "Authorization: Bearer MGMT_TOKEN" \
  -H "X-School-Slug: greenwood"
```

---

## ❌ 14. Delete Substitution

```http
DELETE /api/timetable/substitutions/{id}/
```

---

# 📡 CALENDAR EVENT APIs

## ➕ 15. Create Calendar Event

```http
POST /api/timetable/events/
```

### School-wide Holiday
```bash
curl -X POST http://127.0.0.1:8000/api/timetable/events/ \
  -H "Authorization: Bearer MGMT_TOKEN" \
  -H "Content-Type: application/json" \
  -H "X-School-Slug: greenwood" \
  -d '{
    "title": "Diwali Holiday",
    "description": "School closed for Diwali",
    "event_type": "holiday",
    "scope": "school",
    "start_date": "2025-10-20",
    "end_date": "2025-10-22",
    "academic_year": "2025-26"
  }'
```

### Exam (School-wide)
```bash
curl -X POST http://127.0.0.1:8000/api/timetable/events/ \
  -H "Authorization: Bearer MGMT_TOKEN" \
  -H "Content-Type: application/json" \
  -H "X-School-Slug: greenwood" \
  -d '{
    "title": "Mid-Term Exams",
    "event_type": "exam",
    "scope": "school",
    "start_date": "2025-09-01",
    "end_date": "2025-09-10",
    "academic_year": "2025-26"
  }'
```

### Class-level Announcement
```bash
curl -X POST http://127.0.0.1:8000/api/timetable/events/ \
  -H "Authorization: Bearer MGMT_TOKEN" \
  -H "Content-Type: application/json" \
  -H "X-School-Slug: greenwood" \
  -d '{
    "title": "Grade 10 A — Parent-Teacher Meeting",
    "event_type": "announcement",
    "scope": "class",
    "class_obj": 1,
    "start_date": "2025-07-15",
    "end_date": "2025-07-15",
    "start_time": "10:00",
    "end_time": "13:00",
    "academic_year": "2025-26"
  }'
```

Response:
```json
{
  "id": 1,
  "title": "Diwali Holiday",
  "description": "School closed for Diwali",
  "event_type": "holiday",
  "scope": "school",
  "class_obj": null,
  "class_name": null,
  "start_date": "2025-10-20",
  "end_date": "2025-10-22",
  "start_time": null,
  "end_time": null,
  "academic_year": "2025-26",
  "is_active": true,
  "created_by": 1,
  "created_by_name": "greenwood.admin",
  "created_at": "2025-06-01T10:00:00Z"
}
```

---

## 📋 16. List Calendar Events

```http
GET /api/timetable/events/
```

Query params: `event_type`, `scope`, `class_id`, `academic_year`, `from_date`, `to_date`

```bash
# All holidays
curl -X GET "http://127.0.0.1:8000/api/timetable/events/?event_type=holiday&academic_year=2025-26" \
  -H "Authorization: Bearer MGMT_TOKEN" \
  -H "X-School-Slug: greenwood"

# Events for a specific class
curl -X GET "http://127.0.0.1:8000/api/timetable/events/?scope=class&class_id=1" \
  -H "Authorization: Bearer MGMT_TOKEN" \
  -H "X-School-Slug: greenwood"

# Events in date range
curl -X GET "http://127.0.0.1:8000/api/timetable/events/?from_date=2025-09-01&to_date=2025-09-30" \
  -H "Authorization: Bearer MGMT_TOKEN" \
  -H "X-School-Slug: greenwood"
```

---

## ✏️ 17. Update / ❌ 18. Delete Event

```http
PUT    /api/timetable/events/{id}/
DELETE /api/timetable/events/{id}/
```

Delete soft-deletes (`is_active = false`).

---

# 📡 COMBINED CALENDAR VIEW

## 🗓️ 19. Full Calendar (Timetable + Events)

Returns weekly timetable grid + all relevant calendar events in one response. This is the primary endpoint for the frontend calendar UI.

```http
GET /api/timetable/calendar/
```

Query params:

| Param | Required | Description |
|---|---|---|
| `class_id` | ❌ | Scope to a class (timetable + class events + school events) |
| `academic_year` | ❌ | Filter by year |
| `from_date` | ❌ | Filter events from this date |
| `to_date` | ❌ | Filter events to this date |

```bash
# Full calendar for Grade 10 A — June 2025
curl -X GET "http://127.0.0.1:8000/api/timetable/calendar/?class_id=1&academic_year=2025-26&from_date=2025-06-01&to_date=2025-06-30" \
  -H "Authorization: Bearer MGMT_TOKEN" \
  -H "X-School-Slug: greenwood"
```

Response:
```json
{
  "class_id": "1",
  "academic_year": "2025-26",
  "timetable": {
    "monday": [
      {"slot_number": 1, "slot_name": "Period 1", "start_time": "08:00", "end_time": "08:45", "subject": "Mathematics", "teacher": "Bob Brown", "room": "Room 101", "class_name": "Grade 10 A (2025-26)"},
      {"slot_number": 2, "slot_name": "Period 2", "start_time": "08:45", "end_time": "09:30", "subject": "English", "teacher": "Alice Green", "room": "Room 102", "class_name": "Grade 10 A (2025-26)"}
    ],
    "tuesday": [ "..." ],
    "wednesday": [ "..." ]
  },
  "events": [
    {
      "id": 1,
      "title": "Diwali Holiday",
      "event_type": "holiday",
      "scope": "school",
      "class_obj": null,
      "class_name": null,
      "start_date": "2025-10-20",
      "end_date": "2025-10-22",
      "start_time": null,
      "end_time": null,
      "academic_year": "2025-26"
    },
    {
      "id": 3,
      "title": "Grade 10 A — Parent-Teacher Meeting",
      "event_type": "announcement",
      "scope": "class",
      "class_obj": 1,
      "class_name": "Grade 10 A (2025-26)",
      "start_date": "2025-07-15",
      "end_date": "2025-07-15",
      "start_time": "10:00",
      "end_time": "13:00",
      "academic_year": "2025-26"
    }
  ]
}
```

> When `class_id` is provided, events include both school-wide and class-specific events. Without `class_id`, only school-wide events are returned alongside all timetable entries.

---

# 🔁 Complete Flow

```
1. POST /api/timetable/slots/  (× N)
   → Define all periods for the school day

2. POST /api/timetable/entries/check-conflict/
   → Dry-run conflict check before each entry

3. POST /api/timetable/entries/  (× N)
   → Fill the weekly grid per class

4. POST /api/timetable/events/
   → Add holidays, exams, events, announcements (school or class scoped)

5. GET /api/timetable/calendar/?class_id=1&academic_year=2025-26
   → Frontend calendar: weekly timetable + all events in one call

6. GET /api/timetable/class/1/
   → Weekly timetable grid for a class

7. GET /api/timetable/teacher/1/
   → Teacher's weekly schedule

8. POST /api/timetable/substitutions/
   → Handle one-day teacher absence

9. GET /api/timetable/substitutions/?date=2025-06-10
   → Today's substitutions for notice board
```

---

# ⚠️ Common Errors

| Error | Cause | Fix |
|---|---|---|
| `Teacher already has a class at this slot` | Teacher double-booked | Change slot or teacher |
| `UNIQUE constraint failed` | Duplicate entry for same class/slot/day | One subject per slot per day per class |
| `class_obj is required when scope is 'class'` | Missing class for class-level event | Pass `class_obj` when scope = class |
| `end_date cannot be before start_date` | Date order wrong | Check dates |
| `403 Forbidden` | Wrong role | Use management token |

---

# 🎯 Outcome of Module 4

✅ Reusable time slot definitions per school
✅ Weekly timetable grid per class
✅ Teacher conflict detection on create/update
✅ Class timetable view (grouped by day)
✅ Teacher timetable view (grouped by day)
✅ Substitution system for daily overrides
✅ School calendar — holidays, exams, events, announcements
✅ Class-level vs school-wide event scoping
✅ Combined full calendar view (timetable + events merged)
✅ Multi-tenant scoped (school isolation)
✅ Role-based access (management full, teacher read-only)

---

# 🚀 Next Module

👉 **Module 5 — Fees Tracking**

* Fee structure per class
* Student fee assignment
* Payment recording
* Outstanding dues report
