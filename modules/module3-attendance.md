# 📘 Module 3 — Attendance System (Documentation)

---

## 🎯 Objective

Build a **full attendance tracking system** for the multi-tenant School ERP:

* Daily attendance marking (class-wise)
* Subject-wise attendance sessions
* Per-student attendance summary with %
* Class-level daily summary
* Finalize/lock sessions to prevent edits
* Bulk-status endpoint for frontend form pre-filling

---

# 🧱 What We Built

## ✅ 1. Two-Model Architecture

### `AttendanceSession`
One session = one class + one subject + one date.  
A teacher opens a session, marks all students, then finalizes it.

| Field | Description |
|---|---|
| `school` | Tenant FK |
| `class_obj` | Which class |
| `subject` | Optional — null for daily, set for subject-wise |
| `teacher` | Who marked it |
| `date` | Date of session |
| `session_type` | `daily` or `subject` |
| `is_finalized` | Lock flag — no edits after this |

**Unique constraint:** `(school, class_obj, subject, date)` — prevents duplicate sessions.

---

### `AttendanceRecord`
One record per student per session.

| Field | Description |
|---|---|
| `session` | FK to session |
| `student` | FK to student |
| `status` | `present` / `absent` / `late` / `excused` |
| `remarks` | Optional note |

---

## ✅ 2. Multi-Tenant Safety

All queries scoped to `request.school`:

```python
AttendanceSession.objects.filter(school=request.school)
```

---

## ✅ 3. Role-Based Access

| Role | Access |
|---|---|
| Management | Full CRUD + finalize |
| Teacher | Create sessions, mark attendance, view |
| Student / Parent | Coming in later module |

---

# 🗂️ Files Created

```
apps/
└── attendance/
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

# ⚙️ Setup Steps

## Step 1 — Add to INSTALLED_APPS

In `config/settings.py`:

```python
INSTALLED_APPS = [
    ...
    "apps.attendance",
]
```

---

## Step 2 — Wire URL

In `config/urls.py`:

```python
path("api/attendance/", include("apps.attendance.urls")),
```

---

## Step 3 — Run Migration

```bash
# Let Django generate it fresh
python manage.py makemigrations attendance
python manage.py migrate attendance
```

---

# 📡 ATTENDANCE APIs

## 📋 1. List Attendance Sessions

### Endpoint
```http
GET /api/attendance/
```

### Query Params
| Param | Description |
|---|---|
| `date` | Filter by exact date (YYYY-MM-DD) |
| `class_id` | Filter by class |
| `subject_id` | Filter by subject |
| `from_date` | Date range start |
| `to_date` | Date range end |

### cURL
```bash
curl -X GET "http://127.0.0.1:8000/api/attendance/?class_id=1&date=2025-06-10" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "X-School-Slug: greenwood"
```

### Response
```json
[
  {
    "id": 1,
    "class_obj": 1,
    "class_name": "Grade 10 A (2025-26)",
    "subject": 1,
    "subject_name": "Mathematics",
    "teacher": 1,
    "teacher_name": "Bob Brown",
    "date": "2025-06-10",
    "session_type": "subject",
    "is_finalized": false,
    "total_students": 30,
    "present_count": 27,
    "absent_count": 3,
    "created_at": "2025-06-10T08:30:00Z"
  }
]
```

---

## ➕ 2. Create Attendance Session (Mark Attendance)

Creates the session AND all student records in a single request.

### Endpoint
```http
POST /api/attendance/
```

### cURL — Daily Attendance
```bash
curl -X POST http://127.0.0.1:8000/api/attendance/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -H "X-School-Slug: greenwood" \
  -d '{
    "class_obj": 1,
    "subject": null,
    "teacher": 1,
    "date": "2025-06-10",
    "session_type": "daily",
    "records": [
      { "student": 1, "status": "present", "remarks": "" },
      { "student": 2, "status": "absent",  "remarks": "Sick leave" },
      { "student": 3, "status": "late",    "remarks": "Arrived 10 mins late" },
      { "student": 4, "status": "excused", "remarks": "Sports event" }
    ]
  }'
```

### cURL — Subject-wise Attendance
```bash
curl -X POST http://127.0.0.1:8000/api/attendance/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -H "X-School-Slug: greenwood" \
  -d '{
    "class_obj": 1,
    "subject": 1,
    "teacher": 1,
    "date": "2025-06-10",
    "session_type": "subject",
    "records": [
      { "student": 1, "status": "present" },
      { "student": 2, "status": "absent" }
    ]
  }'
```

### Response
```json
{
  "id": 2,
  "class_obj": 1,
  "class_name": "Grade 10 A (2025-26)",
  "subject": 1,
  "subject_name": "Mathematics",
  "teacher": 1,
  "teacher_name": "Bob Brown",
  "date": "2025-06-10",
  "session_type": "subject",
  "is_finalized": false,
  "total_students": 4,
  "present_count": 2,
  "absent_count": 1,
  "created_at": "2025-06-10T08:30:00Z"
}
```

---

## 🔍 3. Session Detail (with all records)

### Endpoint
```http
GET /api/attendance/{id}/
```

### cURL
```bash
curl -X GET http://127.0.0.1:8000/api/attendance/1/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "X-School-Slug: greenwood"
```

### Response
```json
{
  "id": 1,
  "class_name": "Grade 10 A (2025-26)",
  "subject_name": "Mathematics",
  "date": "2025-06-10",
  "is_finalized": false,
  "total_students": 4,
  "present_count": 3,
  "absent_count": 1,
  "records": [
    {
      "id": 1,
      "student": 1,
      "student_id": "STU-001",
      "student_name": "John Doe",
      "status": "present",
      "remarks": "",
      "marked_at": "2025-06-10T08:31:00Z"
    },
    {
      "id": 2,
      "student": 2,
      "student_id": "STU-002",
      "student_name": "Jane Smith",
      "status": "absent",
      "remarks": "Sick leave",
      "marked_at": "2025-06-10T08:31:00Z"
    }
  ]
}
```

---

## ✏️ 4. Update a Single Student's Record

Change status for one student without re-submitting the whole session.

### Endpoint
```http
PATCH /api/attendance/{session_id}/records/{record_id}/
```

### cURL
```bash
curl -X PATCH http://127.0.0.1:8000/api/attendance/1/records/2/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -H "X-School-Slug: greenwood" \
  -d '{
    "status": "present",
    "remarks": "Came in later, marked present"
  }'
```

### Response
```json
{
  "id": 2,
  "student": 2,
  "student_id": "STU-002",
  "student_name": "Jane Smith",
  "status": "present",
  "remarks": "Came in later, marked present",
  "marked_at": "2025-06-10T08:31:00Z"
}
```

> ⚠️ Returns `403` if session is already finalized.

---

## 🔒 5. Finalize Session

Lock a session — no edits allowed after this.

### Endpoint
```http
POST /api/attendance/{id}/finalize/
```

### cURL
```bash
curl -X POST http://127.0.0.1:8000/api/attendance/1/finalize/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "X-School-Slug: greenwood"
```

### Response
```json
{
  "detail": "Session finalized.",
  "id": 1
}
```

---

## 📊 6. Class-wise Summary

Aggregated summary per session — useful for dashboards.

### Endpoint
```http
GET /api/attendance/class-summary/
```

### Query Params
| Param | Description |
|---|---|
| `class_id` | Filter by class |
| `from_date` | Start date |
| `to_date` | End date |

### cURL
```bash
curl -X GET "http://127.0.0.1:8000/api/attendance/class-summary/?class_id=1&from_date=2025-06-01&to_date=2025-06-30" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "X-School-Slug: greenwood"
```

### Response
```json
[
  {
    "date": "2025-06-10",
    "class_name": "Grade 10 A (2025-26)",
    "subject_name": "Mathematics",
    "total_students": 30,
    "present": 27,
    "absent": 2,
    "late": 1,
    "attendance_pct": 93.33
  },
  {
    "date": "2025-06-10",
    "class_name": "Grade 10 A (2025-26)",
    "subject_name": null,
    "total_students": 30,
    "present": 28,
    "absent": 2,
    "late": 0,
    "attendance_pct": 93.33
  }
]
```

---

## 👨‍🎓 7. Student Attendance Summary

Attendance % for a specific student, optionally filtered by subject/date range.

### Endpoint
```http
GET /api/attendance/student/{student_id}/
```

### Query Params
| Param | Description |
|---|---|
| `subject_id` | Filter by subject |
| `from_date` | Start date |
| `to_date` | End date |

### cURL — Overall
```bash
curl -X GET http://127.0.0.1:8000/api/attendance/student/1/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "X-School-Slug: greenwood"
```

### cURL — For a Subject
```bash
curl -X GET "http://127.0.0.1:8000/api/attendance/student/1/?subject_id=1&from_date=2025-06-01" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "X-School-Slug: greenwood"
```

### Response
```json
{
  "student_id": "STU-001",
  "student_name": "John Doe",
  "total_sessions": 20,
  "present": 17,
  "absent": 2,
  "late": 1,
  "excused": 0,
  "attendance_pct": 90.0
}
```

> 💡 `attendance_pct` counts both `present` and `late` as attended.

---

## 📋 8. Bulk Status (Pre-fill Form)

Get all students in a class for a given date, with their current status if already marked.  
Useful for frontend: pre-load the attendance form.

### Endpoint
```http
GET /api/attendance/bulk-status/
```

### Required Params
| Param | Required | Description |
|---|---|---|
| `class_id` | ✅ | Class to load |
| `date` | ✅ | Date |
| `subject_id` | ❌ | Optional subject filter |

### cURL
```bash
curl -X GET "http://127.0.0.1:8000/api/attendance/bulk-status/?class_id=1&date=2025-06-10&subject_id=1" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "X-School-Slug: greenwood"
```

### Response
```json
{
  "date": "2025-06-10",
  "class_name": "Grade 10 A (2025-26)",
  "session_exists": true,
  "session_id": 1,
  "is_finalized": false,
  "students": [
    { "student_id": 1, "student_code": "STU-001", "student_name": "John Doe",   "status": "present" },
    { "student_id": 2, "student_code": "STU-002", "student_name": "Jane Smith",  "status": "absent"  },
    { "student_id": 3, "student_code": "STU-003", "student_name": "Raj Patel",   "status": null      }
  ]
}
```

> `status: null` means not yet marked for this student.

---

# 🔁 Complete Attendance Flow

```
1. GET /api/attendance/bulk-status/?class_id=1&date=2025-06-10
   → Load all students in class (pre-fill form)

2. POST /api/attendance/
   → Submit session + all student statuses in one shot

3. PATCH /api/attendance/1/records/2/
   → Correct a single student if needed

4. POST /api/attendance/1/finalize/
   → Lock the session

5. GET /api/attendance/student/1/
   → View student's running attendance %

6. GET /api/attendance/class-summary/?class_id=1
   → Dashboard view for management
```

---

# ⚠️ Common Errors

| Error | Cause | Fix |
|---|---|---|
| `Attendance session already exists` | Duplicate session for same class/subject/date | Only one session per combo per day |
| `Session is finalized. Cannot edit.` | Trying to edit after finalize | Create a new session or check date |
| `class_id and date are required` | Missing params on bulk-status | Always pass both |
| `403 Forbidden` | Wrong role | Use management or teacher token |

---

# 🎯 Outcome of Module 3

✅ Daily + subject-wise attendance sessions
✅ Multi-tenant scoped (school isolation)
✅ Finalize/lock protection
✅ Per-student attendance % with filters
✅ Class-level summary for dashboards
✅ Bulk-status endpoint for frontend form pre-fill
✅ Role-based access (management + teacher)

---

# 🚀 Next Module

👉 **Module 4 — Grades & Results**

* Exam model
* Per-subject marks entry
* Grade calculation
* Student result card
* Class rank / leaderboard
