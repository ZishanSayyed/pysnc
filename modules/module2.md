# 📘 Module 2 — Student Profiles (Documentation)

---

## 🎯 Objective

Build the **Student Management System** for the multi-tenant School ERP:

* Student profile management
* Link students to SchoolUser
* Class & parent mapping
* Bulk CSV upload
* Search & filtering
* Role-based access control

---

# 🧱 What We Built

## ✅ 1. Student Model

Each student:

* Belongs to a **School (tenant)**
* Linked to a **SchoolUser**
* Has unique `student_id` per school
* Can be assigned:

  * Class
  * Parent

---

## ✅ 2. Multi-Tenant Safety

All queries scoped using:

```python
Student.objects.for_school(request.school)
```

👉 Prevents cross-school data access

---

## ✅ 3. Role-Based Access

| Role       | Access             |
| ---------- | ------------------ |
| Management | Full CRUD          |
| Teacher    | Read-only          |
| Student    | Own data (later)   |
| Parent     | Child data (later) |

---

## 👨‍🎓 STUDENT APIs

---

## 📋 1. List Students

### Endpoint

```http
GET /api/students/
```

### Query Params

| Param    | Description          |
| -------- | -------------------- |
| class_id | Filter by class      |
| search   | Search by first name |

---

### cURL

```bash
curl -X GET http://127.0.0.1:8000/api/students/ \
-H "Authorization: Bearer YOUR_TOKEN"
```

---

### Example Response

```json
[
  {
    "id": 1,
    "student_id": "STU-001",
    "full_name": "John Doe",
    "class_name": "Grade 10 A",
    "gender": "Male",
    "admission_date": "2025-01-10",
    "attendance_pct": 0,
    "is_active": true
  }
]
```

---

## ➕ 2. Create Student

### Endpoint

```http
POST /api/students/
```

---

### cURL

```bash
curl -X POST http://127.0.0.1:8000/api/students/ \
-H "Authorization: Bearer YOUR_TOKEN" \
-H "Content-Type: application/json" \
-d "{
  \"user\": 2,
  \"student_id\": \"STU-002\",
  \"date_of_birth\": \"2010-05-12\",
  \"gender\": \"Male\",
  \"address\": \"Mumbai\",
  \"admission_date\": \"2025-01-01\",
  \"emergency_contact\": \"9876543210\"
}"
```

---

## 🔍 3. Student Detail

```http
GET /api/students/{id}/
```

### cURL

```bash
curl -X GET http://127.0.0.1:8000/api/students/1/ \
-H "Authorization: Bearer YOUR_TOKEN"
```

---

## ✏️ 4. Update Student

```http
PUT /api/students/{id}/
```

### cURL

```bash
curl -X PUT http://127.0.0.1:8000/api/students/1/ \
-H "Authorization: Bearer YOUR_TOKEN" \
-H "Content-Type: application/json" \
-d "{
  \"address\": \"Updated Address\"
}"
```

---

## ❌ 5. Delete Student (Soft Delete)

```http
DELETE /api/students/{id}/
```

### Behavior

* Sets:

```json
"is_active": false
```

---

### cURL

```bash
curl -X DELETE http://127.0.0.1:8000/api/students/1/ \
-H "Authorization: Bearer YOUR_TOKEN"
```

---

## 📊 6. Student Attendance

```http
GET /api/students/{id}/attendance/
```

### cURL

```bash
curl -X GET http://127.0.0.1:8000/api/students/1/attendance/ \
-H "Authorization: Bearer YOUR_TOKEN"
```

### Response

```json
{
  "student": "STU-001",
  "attendance_pct": 0
}
```

---

## 📈 7. Student Grades

```http
GET /api/students/{id}/grades/
```

### cURL

```bash
curl -X GET http://127.0.0.1:8000/api/students/1/grades/ \
-H "Authorization: Bearer YOUR_TOKEN"
```

### Response

```json
{
  "message": "Coming in Module 4"
}
```

---

## 📂 8. Bulk Upload (CSV)

### Endpoint

```http
POST /api/students/bulk-upload/
```

---

### Required Columns

```
first_name,last_name,email,student_id,date_of_birth,gender,admission_date,address
```

---

### Sample CSV

```csv
first_name,last_name,email,student_id,date_of_birth,gender,admission_date,address
John,Doe,john@example.com,STU-101,2010-01-01,Male,2025-01-01,Mumbai
```

---

### cURL

```bash
curl -X POST http://127.0.0.1:8000/api/students/bulk-upload/ \
-H "Authorization: Bearer YOUR_TOKEN" \
-F "file=@students.csv"
```

---

### Response

```json
{
  "created": 10,
  "updated": 2,
  "errors": 1,
  "error_rows": [
    {"row": 3, "error": "Invalid date"}
  ]
}
```
---
# Class Module 

# 1. Create Class 10
```
curl -X POST http://127.0.0.1:8000/api/classes/ \
  -H "Authorization: Bearer MGMT_TOKEN" \
  -H "Content-Type: application/json" \
  -H "X-School-Slug: greenwood" \
  -d '{"name": "Class 10", "section": "A", "academic_year": "2025-26", "capacity": 40}'

```
# 2. Add subjects to Class 10 (repeat for each subject id)
```
curl -X POST http://127.0.0.1:8000/api/classes/1/add-subject/ \
  -H "Authorization: Bearer MGMT_TOKEN" \
  -H "Content-Type: application/json" \
  -H "X-School-Slug: greenwood" \
  -d '{"subject_id": 1}'

```
# 3. Assign student → auto-enrolled in all subjects above
```
curl -X POST http://127.0.0.1:8000/api/classes/1/assign-student/ \
  -H "Authorization: Bearer MGMT_TOKEN" \
  -H "Content-Type: application/json" \
  -H "X-School-Slug: greenwood" \
  -d '{"student_id": 25}'

```
# 4. Check student's enrollments
```
curl -X GET "http://127.0.0.1:8000/api/classes/enrollments/?student_id=25" \
  -H "Authorization: Bearer MGMT_TOKEN" \
  -H "X-School-Slug: greenwood"

```
# 5. Uncheck one subject for this student (is_active=false)

```
curl -X PATCH http://127.0.0.1:8000/api/classes/enrollments/3/ \
  -H "Authorization: Bearer MGMT_TOKEN" \
  -H "Content-Type: application/json" \
  -H "X-School-Slug: greenwood" \
  -d '{"is_active": false}'
```

---
---

# 🔁 Complete Flow

1. Login → get JWT token
2. Create student (linked to SchoolUser)
3. Assign class / parent
4. Fetch students list
5. Filter/search students
6. Upload bulk CSV
7. View attendance & grades

---

# 🔐 Security & Isolation

* All queries use:

```python
Student.objects.for_school(request.school)
```

* Prevents cross-school data leaks

---

# ⚠️ Common Errors

| Error                     | Cause                           |
| ------------------------- | ------------------------------- |
| ImportError (permissions) | Missing `IsManagementOrTeacher` |
| managers not found        | Missing `managers.py`           |
| class not found           | classes app not created         |
| parent not found          | parents app not created         |
| CSV failure               | Wrong columns                   |

---

# 🎯 Outcome of Module 2

✅ Student profile system
✅ Multi-tenant safe
✅ Role-based APIs
✅ CSV bulk upload
✅ Search & filtering
✅ Attendance-ready structure

---

# 🚀 Next Module

👉 Module 3: **Attendance System**

* Daily attendance
* Class-wise marking
* Attendance percentage calculation

---
