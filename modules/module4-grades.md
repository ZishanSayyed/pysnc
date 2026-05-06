# 📘 Module 4 — Grades & Results (Documentation)

---

## 🎯 Objective

Build a complete **Grades & Results system** for the multi-tenant School ERP:

* Exam management (unit test, mid-term, final)
* Per-subject marks configuration
* Bulk marks entry by teacher/management
* Auto grade calculation (A+, A, B, C, D, F)
* Student result card with rank
* Class leaderboard
* Publish/unpublish results

---

# 🧱 What We Built

## ✅ 1. Three-Model Architecture

### `Exam`
One exam event for a class — e.g. "Mid-Term 2025 — Grade 10 A"

| Field | Description |
|---|---|
| `school` | Tenant FK |
| `name` | Exam name |
| `exam_type` | `unit_test` / `mid_term` / `final` / `assignment` / `practical` |
| `class_obj` | Which class |
| `total_marks` | Default total for the exam |
| `passing_marks` | Default passing threshold |
| `exam_date` | Date of exam |
| `academic_year` | e.g. `2025-26` |
| `is_published` | Results visible to students/parents |

---

### `ExamSubject`
Each subject inside an exam with its own marks split.

| Field | Description |
|---|---|
| `exam` | FK to Exam |
| `subject` | FK to Subject |
| `max_marks` | Max marks for this subject |
| `passing_marks` | Passing threshold for this subject |

**Unique constraint:** `(exam, subject)` — one entry per subject per exam.

---

### `StudentResult`
Marks scored by a student in one subject of one exam.

| Field | Description |
|---|---|
| `exam_subject` | FK to ExamSubject |
| `student` | FK to Student |
| `marks_obtained` | Decimal marks |
| `is_absent` | Absent flag |
| `remarks` | Optional note |

**Auto-computed properties:** `grade`, `is_pass`

---

## ✅ 2. Grade Scale

| % Range | Grade |
|---|---|
| 90–100 | A+ |
| 75–89 | A |
| 60–74 | B |
| 45–59 | C |
| 35–44 | D |
| Below 35 | F |
| Absent | AB |

---

## ✅ 3. Role-Based Access

| Role | Access |
|---|---|
| Management | Full CRUD, publish, bulk entry |
| Teacher | Enter marks, view results |
| Student / Parent | View published results (coming later) |

---

# 🗂️ Files Created

```
apps/
└── grades/
    ├── __init__.py
    ├── apps.py
    ├── models.py
    ├── serializers.py
    ├── views.py
    ├── urls.py
    └── admin.py
```

---

# ⚙️ Setup Steps

## Step 1 — Add to INSTALLED_APPS

```python
# config/settings.py
INSTALLED_APPS = [
    ...
    "apps.grades",
]
```

## Step 2 — Wire URL

```python
# config/urls.py
path("api/grades/", include("apps.grades.urls")),
```

## Step 3 — Migrate

```bash
python manage.py makemigrations grades
python manage.py migrate grades
```

---

# 📡 GRADES APIs

---

## 📋 1. List Exams

```http
GET /api/grades/exams/
```

### Query Params
| Param | Description |
|---|---|
| `class_id` | Filter by class |
| `exam_type` | Filter by type |

### cURL
```bash
curl -X GET "http://127.0.0.1:8000/api/grades/exams/?class_id=1" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "X-School-Slug: greenwood"
```

### Response
```json
[
  {
    "id": 1,
    "name": "Mid-Term 2025",
    "exam_type": "mid_term",
    "class_obj": 1,
    "class_name": "Grade 10 A (2025-26)",
    "total_marks": 500,
    "passing_marks": 175,
    "exam_date": "2025-09-15",
    "academic_year": "2025-26",
    "is_published": false,
    "total_students": 30,
    "exam_subjects": [
      { "id": 1, "subject": 1, "subject_name": "Mathematics", "max_marks": 100, "passing_marks": 35 },
      { "id": 2, "subject": 2, "subject_name": "English",     "max_marks": 100, "passing_marks": 35 }
    ],
    "created_at": "2025-06-01T10:00:00Z"
  }
]
```

---

## ➕ 2. Create Exam (with subjects in one shot)

```http
POST /api/grades/exams/
```

### cURL
```bash
curl -X POST http://127.0.0.1:8000/api/grades/exams/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -H "X-School-Slug: greenwood" \
  -d '{
    "name": "Mid-Term 2025",
    "exam_type": "mid_term",
    "class_obj": 1,
    "total_marks": 500,
    "passing_marks": 175,
    "exam_date": "2025-09-15",
    "academic_year": "2025-26",
    "subject_ids": [1, 2, 3]
  }'
```

> Passing `subject_ids` auto-creates `ExamSubject` rows using the exam's default `total_marks` / `passing_marks`.

---

## ➕ 3. Add More Subjects to Exam

```http
POST /api/grades/exams/{id}/add-subjects/
```

### cURL
```bash
curl -X POST http://127.0.0.1:8000/api/grades/exams/1/add-subjects/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -H "X-School-Slug: greenwood" \
  -d '{
    "subject_ids": [4, 5],
    "max_marks": 100,
    "passing_marks": 35
  }'
```

### Response
```json
{ "added_subject_ids": [4, 5], "total_subjects": 5 }
```

---

## 📝 4. Bulk Enter Marks (for one subject)

Enter marks for all students in a class for one exam subject.  
Use `update_or_create` — safe to re-submit with corrections.

```http
POST /api/grades/exam-subjects/{exam_subject_id}/bulk-results/
```

### cURL
```bash
curl -X POST http://127.0.0.1:8000/api/grades/exam-subjects/1/bulk-results/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -H "X-School-Slug: greenwood" \
  -d '{
    "results": [
      { "student": 1, "marks_obtained": 88 },
      { "student": 2, "marks_obtained": 72 },
      { "student": 3, "marks_obtained": 45 },
      { "student": 4, "is_absent": true }
    ]
  }'
```

### Response
```json
{
  "created": 3,
  "updated": 1,
  "errors": 0,
  "error_details": []
}
```

---

## 📋 5. View All Marks for a Subject

```http
GET /api/grades/exam-subjects/{id}/results/
```

### cURL
```bash
curl -X GET http://127.0.0.1:8000/api/grades/exam-subjects/1/results/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "X-School-Slug: greenwood"
```

### Response
```json
[
  {
    "id": 1,
    "student": 1,
    "student_code": "STU-001",
    "student_name": "John Doe",
    "subject_name": "Mathematics",
    "max_marks": 100,
    "marks_obtained": "88.00",
    "is_absent": false,
    "grade": "A",
    "is_pass": true,
    "remarks": null
  }
]
```

---

## 🎓 6. Student Result Card

Full result card for one student in one exam — with rank.

```http
GET /api/grades/results/card/?student_id=1&exam_id=1
```

### cURL
```bash
curl -X GET "http://127.0.0.1:8000/api/grades/results/card/?student_id=1&exam_id=1" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "X-School-Slug: greenwood"
```

### Response
```json
{
  "student_id": "STU-001",
  "student_name": "John Doe",
  "exam_name": "Mid-Term 2025",
  "exam_type": "mid_term",
  "exam_date": "2025-09-15",
  "class_name": "Grade 10 A (2025-26)",
  "total_marks": 500,
  "marks_obtained": "412.00",
  "percentage": 82.4,
  "overall_grade": "A",
  "is_pass": true,
  "rank": 3,
  "subjects": [
    {
      "subject_name": "Mathematics",
      "max_marks": 100,
      "marks_obtained": "88.00",
      "is_absent": false,
      "grade": "A",
      "is_pass": true,
      "remarks": null
    },
    {
      "subject_name": "English",
      "max_marks": 100,
      "marks_obtained": "79.00",
      "is_absent": false,
      "grade": "A",
      "is_pass": true,
      "remarks": null
    }
  ]
}
```

---

## 🏆 7. Class Leaderboard

```http
GET /api/grades/exams/{id}/leaderboard/
```

### cURL
```bash
curl -X GET http://127.0.0.1:8000/api/grades/exams/1/leaderboard/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "X-School-Slug: greenwood"
```

### Response
```json
[
  {
    "rank": 1,
    "student_id": "STU-005",
    "student_name": "Priya Singh",
    "marks_obtained": "456.00",
    "total_marks": 500,
    "percentage": 91.2,
    "overall_grade": "A+",
    "is_pass": true
  },
  {
    "rank": 2,
    "student_id": "STU-003",
    "student_name": "Raj Patel",
    "marks_obtained": "430.00",
    "total_marks": 500,
    "percentage": 86.0,
    "overall_grade": "A",
    "is_pass": true
  }
]
```

---

## 📢 8. Publish Results

Make results visible to students and parents.

```http
POST /api/grades/exams/{id}/publish/
```

### cURL
```bash
curl -X POST http://127.0.0.1:8000/api/grades/exams/1/publish/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "X-School-Slug: greenwood"
```

### Response
```json
{ "detail": "Results published.", "id": 1 }
```

---

## ✏️ 9. Update a Single Result

```http
PUT /api/grades/results/{id}/
```

### cURL
```bash
curl -X PUT http://127.0.0.1:8000/api/grades/results/1/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -H "X-School-Slug: greenwood" \
  -d '{
    "marks_obtained": 91,
    "remarks": "Re-checked paper"
  }'
```

---

# 🔁 Complete Grades Flow

```
1. POST /api/grades/exams/
   → Create exam with subject_ids

2. POST /api/grades/exam-subjects/{id}/bulk-results/
   → Enter marks for each subject (repeat per subject)

3. GET /api/grades/results/card/?student_id=&exam_id=
   → View full result card with rank

4. GET /api/grades/exams/{id}/leaderboard/
   → Class rank list

5. POST /api/grades/exams/{id}/publish/
   → Release results to students/parents
```

---

# ⚠️ Common Errors

| Error | Cause | Fix |
|---|---|---|
| `student_id and exam_id are required` | Missing query params on card | Pass both |
| `Student not found` in bulk-results | Wrong student ID or wrong school | Check student belongs to school |
| Duplicate result | Re-submitting same student+subject | Safe — uses `update_or_create` |
| `403 Forbidden` | Teacher trying management action | Use management token |

---

# 🎯 Outcome of Module 4

✅ Exam creation with subject splits
✅ Bulk marks entry (update-safe)
✅ Auto grade + pass/fail calculation
✅ Full student result card with rank
✅ Class leaderboard
✅ Publish/unpublish results
✅ Multi-tenant scoped throughout

---

# 🚀 Next Module

👉 **Module 5 — Timetable / Scheduling**

* Period slots configuration
* Weekly timetable per class
* Teacher schedule view
* Clash detection
