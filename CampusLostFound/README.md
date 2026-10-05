# Campus Lost & Found Management System

**Software Evolution Techniques — Assignment Project**  
**Language:** Python 3 | **Type:** Console Application | **Storage:** In-memory (lists)

---

## How to Run

```bash
# Navigate to the project folder
cd CampusLostFound

# Run the application
python main.py
```

> **Python 3** required. No external packages needed — the standard library is enough.

---

## Project Structure

```
CampusLostFound/
│
├── main.py       — Console UI: all menus, screens, and user input
├── models.py     — Data classes: User, Student, Admin, Item, LostItem,
│                              FoundItem, Claim, Notification
├── services.py   — Business logic: LostFoundSystem class
└── README.md     — This file
```

---

## Default Accounts

| Role    | Email                    | Password  |
|---------|--------------------------|-----------|
| Admin   | admin@university.com     | admin123  |
| Student | alice@university.com     | alice123  | *(demo data only)*
| Student | bob@university.com       | bob123    | *(demo data only)*

---

## Demo Scenario (HP Laptop)

1. Run `python main.py`
2. Enter **y** when prompted to load demo data
3. The system creates two students (Alice & Bob) and two approved HP Laptop reports
4. Log in as **Alice** → Submit Claim on Item #1 or #2
5. Log in as **Admin** → Approve the claim → Item status becomes *Claimed*
6. Admin → Mark Item as Returned → Status becomes *Returned*
7. Log in as Alice/Bob → Check Notifications

---

## Class Responsibilities

| Class            | File        | Responsibility                                         |
|------------------|-------------|--------------------------------------------------------|
| `IDCounter`      | models.py   | Generate unique integer IDs for all entities           |
| `User`           | models.py   | Base: id, name, email, password, login check           |
| `Student`        | models.py   | Extends User; adds student_id, department              |
| `Admin`          | models.py   | Extends User; marks a user as administrator            |
| `Item`           | models.py   | Base: item_id, name, category, location, status, match |
| `LostItem`       | models.py   | Extends Item; represents a reported lost item          |
| `FoundItem`      | models.py   | Extends Item; represents a reported found item         |
| `Claim`          | models.py   | Ownership claim by a student on an item                |
| `Notification`   | models.py   | System message to a user (read/unread)                 |
| `LostFoundSystem`| services.py | All business logic: manage users/items/claims/notifs   |
| `main.py`        | main.py     | Console UI, menus, input, calls service methods        |

---

## Business Rules (implemented)

| # | Rule                                                                |
|---|---------------------------------------------------------------------|
| 1 | New reports start as **Pending**                                    |
| 2 | Students cannot see Rejected reports                                |
| 3 | Only **Approved** items appear in search results                    |
| 4 | Claims start as **Pending**                                         |
| 5 | Admin can approve or reject claims                                  |
| 6 | Approved claim → item status becomes **Claimed**                    |
| 7 | Admin can mark a Claimed item as **Returned**                       |
| 8 | Returned item → status becomes **Returned**                         |
| 9 | System detects possible matches (same name/category/location)       |
| 10| Notifications sent on approval, rejection, match, and return        |

---

## Software Evolution Explanation

### 1. Adaptive Evolution

**Definition:** Adapting the software to work in a new environment without changing its behaviour.

**Current state:** Console application.

**Future adaptation:** Add a REST API layer so the same business logic serves a mobile or web app.

```
Console / Web / Mobile App
          |
      REST API Layer         ← would be added (e.g. Flask/FastAPI routes)
          |
   LostFoundSystem           ← services.py — stays UNCHANGED
          |
    In-memory lists          ← later replaced by a real database
```

Because `LostFoundSystem` in `services.py` contains **all** business logic with no UI code, adding an API layer only requires writing new route functions that call the same service methods. No existing code breaks.

---

### 2. Reactive Evolution

**Definition:** Reacting to a problem that emerged after deployment.

**Problem:** Students posted fake or prank lost/found reports, causing confusion.

**Change made:**

| Before (broken) | After (fixed)                        |
|-----------------|--------------------------------------|
| Report → Visible immediately | Report → **Pending** → Admin reviews → Approved/Rejected |

**Where in the code:**

- Every `LostItem` and `FoundItem` is created with `status = "Pending"` (see `Item.__init__` in `models.py`).
- `search_items()` in `services.py` filters out anything that is not `"Approved"`.
- Admin must explicitly call `approve_item()` or `reject_item()`.
- Notifications are sent to the reporter for both outcomes.

---

### 3. Preventive Evolution

**Definition:** Making changes now to prevent problems later (refactoring, modularisation).

**Applied through:**

| Technique               | Where                                      |
|-------------------------|--------------------------------------------|
| **Separation of concerns** | UI in `main.py`, logic in `services.py`, data in `models.py` |
| **Encapsulation**        | `_password` is private; accessed only via `check_password()` |
| **Reusable helpers**     | `_find_item()`, `_find_claim()`, `_notify()`, `_require_admin()` in `LostFoundSystem` |
| **Single-responsibility methods** | Each method does exactly one thing |
| **No God-function**      | `main()` only routes to screens; screens only call service methods |
| **Inheritance**          | `Student`/`Admin` extend `User`; `LostItem`/`FoundItem` extend `Item` |

---

## OOP Concepts Used

### Inheritance

```
User
├── Student    (adds student_id, department)
└── Admin      (marks user as admin)

Item
├── LostItem   (semantic: this item was lost)
└── FoundItem  (semantic: this item was found)
```

### Encapsulation

- `User._password` — stored with underscore convention; only exposed via `check_password()`
- `LostFoundSystem._find_item()`, `_notify()`, etc. — internal helpers prefixed with `_`
- All data lists (`users`, `items`, `claims`, `notifications`) owned by one class

### Polymorphism

- `item.details()` — overridden in `LostItem` and `FoundItem` to prepend type label
- `isinstance(user, Admin)` — used for routing to correct menu

---

## UML Diagrams You Can Draw

### 1. Class Diagram
Show all 9 classes with attributes, methods, and relationships:
- `User` → `Student` (inheritance)
- `User` → `Admin` (inheritance)
- `Item` → `LostItem` (inheritance)
- `Item` → `FoundItem` (inheritance)
- `LostFoundSystem` → uses all other classes (dependency/composition)

### 2. Use Case Diagram
Actors: **Student**, **Admin**
Use cases:
- Student: Register, Login, Report Lost, Report Found, Search, View Details, Submit Claim, View Claims, View Notifications
- Admin: Login, View Reports, Approve/Reject Report, View Claims, Approve/Reject Claim, Mark Returned, View Notifications

### 3. Sequence Diagram (Claim Approval Flow)
```
Student → system.submit_claim()
system  → creates Claim (Pending)
system  → notifies Admin

Admin   → system.approve_claim()
system  → sets Claim.status = "Approved"
system  → sets Item.status  = "Claimed"
system  → notifies Student
```

### 4. Activity Diagram (Report Submission Flow)
```
Student submits report
      ↓
Status = Pending
      ↓
Admin reviews
   ↙       ↘
Approved   Rejected
   ↓           ↓
Visible    Hidden from students
```

### 5. State Diagram (Item Status)
```
Pending → Approved → Claimed → Returned
        ↘
        Rejected
```

---

## Quick Viva Answers

**Q: Why is `LostFoundSystem` a separate class?**  
A: To separate business logic from UI and data. This is Preventive Evolution — it makes the system easier to maintain and extend.

**Q: What is Reactive Evolution in your project?**  
A: We added admin approval after fake reports became a problem. Items now start as Pending instead of being visible immediately.

**Q: How would you add a mobile app?**  
A: Add an API layer (e.g., Flask routes) that calls `LostFoundSystem` methods. No changes to `services.py` or `models.py` needed. This is Adaptive Evolution.

**Q: What is encapsulation here?**  
A: The `_password` field in `User` is never accessed directly. Only `check_password()` can compare passwords. This hides internal implementation.

**Q: Where is inheritance used?**  
A: `Student` and `Admin` both inherit from `User`. `LostItem` and `FoundItem` both inherit from `Item`, gaining all base attributes and methods automatically.
