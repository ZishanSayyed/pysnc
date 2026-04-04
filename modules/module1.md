# 📘 Module 1 — Multi-School Tenant + Authentication (Documentation)

## 🎯 Objective

Build the **foundation of a multi-tenant SaaS School ERP system**:

* Multi-school support (tenant-based)
* Custom user model with roles
* JWT authentication
* Role-based access control
* School & user management APIs

---

# 🧱 What We Built

## ✅ 1. Multi-Tenant Architecture

* Each **School** is a tenant
* Identified via:

  * Subdomain OR
  * `X-School-Slug` header
* Middleware attaches:

```python
request.school
```

---

## ✅ 2. Custom User Model

Extended Django user:

* `role` → management / teacher / student / parent
* `school` → links user to tenant
* `is_platform_admin` → global admin

---

## ✅ 3. JWT Authentication

* Login returns **access token**
* Token used in:

```http
Authorization: Bearer <token>
```

---

## ✅ 4. Role-Based Access

* Management → manage users
* Platform Admin → manage schools
* Users restricted to their school data

---

# 🔐 AUTH APIs

## 🔑 1. Login

### Endpoint

```http
POST /api/auth/login/
```

### cURL

```bash
curl -X POST http://127.0.0.1:8000/api/auth/login/ \
-H "Content-Type: application/json" \
-d "{\"username\":\"admin\",\"password\":\"yourpassword\"}"
```

### Response

```json
{
  "access": "JWT_TOKEN",
  "role": "management",
  "school": "demo"
}
```

---

## 👤 2. Get Current User

### Endpoint

```http
GET /api/auth/me/
```

### cURL

```bash
curl -X GET http://127.0.0.1:8000/api/auth/me/ \
-H "Authorization: Bearer YOUR_TOKEN"
```

### Response

```json
{
  "id": 1,
  "username": "admin",
  "role": "management",
  "school": "demo"
}
```

---

# 👥 USER MANAGEMENT APIs

## 📋 3. List Users (Management Only)

```bash
curl -X GET http://127.0.0.1:8000/api/auth/users/ \
-H "Authorization: Bearer YOUR_TOKEN"
```

👉 Returns all users in current school

---

## ➕ 4. Create User

```bash
curl -X POST http://127.0.0.1:8000/api/auth/users/create/ \
-H "Authorization: Bearer YOUR_TOKEN" \
-H "Content-Type: application/json" \
-d "{\"username\":\"teacher1\",\"password\":\"1234\",\"role\":\"teacher\"}"
```

👉 Automatically assigns:

* `school = request.school`

---

## ✏️ 5. Update User

```bash
curl -X PUT http://127.0.0.1:8000/api/auth/users/2/ \
-H "Authorization: Bearer YOUR_TOKEN" \
-H "Content-Type: application/json" \
-d "{\"role\":\"management\"}"
```

---

# 🏫 SCHOOL APIs

## 📋 6. List Schools (Platform Admin)

```bash
curl -X GET http://127.0.0.1:8000/api/schools/ \
-H "Authorization: Bearer YOUR_TOKEN"
```

---

## ➕ 7. Create School

```bash
curl -X POST http://127.0.0.1:8000/api/schools/ \
-H "Authorization: Bearer YOUR_TOKEN" \
-H "Content-Type: application/json" \
-d "{\"name\":\"Test School\",\"slug\":\"testschool\"}"
```

---

## 🔍 8. Get School Detail

```bash
curl -X GET http://127.0.0.1:8000/api/schools/YOUR_UUID/ \
-H "Authorization: Bearer YOUR_TOKEN"
```

---

## ✏️ 9. Update School

```bash
curl -X PUT http://127.0.0.1:8000/api/schools/YOUR_UUID/ \
-H "Authorization: Bearer YOUR_TOKEN" \
-H "Content-Type: application/json" \
-d "{\"name\":\"Updated School\"}"
```

---

# 🔁 Complete API Flow

1. Login → get token
2. Use token in headers
3. Create school (platform admin)
4. Assign users to school
5. Create/manage users
6. All data scoped per school

---

# 🔐 Security & Data Isolation

* Users can only access:

```python
SchoolUser.objects.filter(school=request.school)
```

* Prevents cross-school data leaks

---

# 🎯 Outcome of Module 1

✅ Multi-tenant SaaS foundation
✅ Secure authentication (JWT)
✅ Role-based system
✅ School isolation
✅ User & school management APIs

---

# 🚀 Ready for Next

👉 Module 2: **Students Management**

* Student model
* Class mapping
* Bulk CSV upload
* Search & filters

---
