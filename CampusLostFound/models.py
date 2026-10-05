# =============================================================================
# models.py — Data Classes (Entities)
# =============================================================================
# This file contains all the classes that represent the data/entities in the
# Campus Lost & Found Management System.
#
# SOFTWARE EVOLUTION — PREVENTIVE EVOLUTION:
#   Keeping data classes separate from business logic is a form of
#   preventive maintenance / modularisation. If we later swap in a
#   database, we only need to change this file.
# =============================================================================


# ── Unique ID generator ──────────────────────────────────────────────────────

class IDCounter:
    """Simple counter that generates unique integer IDs for every entity."""
    _counters = {}

    @classmethod
    def next(cls, entity: str) -> int:
        cls._counters[entity] = cls._counters.get(entity, 0) + 1
        return cls._counters[entity]


# ── User hierarchy ───────────────────────────────────────────────────────────

class User:
    """
    Base class for all users in the system.

    ENCAPSULATION: password is stored but never printed directly.
    INHERITANCE  : Student and Admin both extend this class.
    """

    def __init__(self, name: str, email: str, password: str):
        self.id       = IDCounter.next("user")
        self.name     = name
        self.email    = email
        self._password = password          # _ prefix signals "private"

    def check_password(self, password: str) -> bool:
        """Verify a login attempt — password comparison stays encapsulated."""
        return self._password == password

    def __str__(self):
        return f"[User #{self.id}] {self.name} <{self.email}>"


class Student(User):
    """
    A university student who can report items and submit claims.

    INHERITANCE: Inherits id, name, email, password from User.
    """

    def __init__(self, name: str, email: str, password: str,
                 student_id: str, department: str):
        super().__init__(name, email, password)
        self.student_id  = student_id
        self.department  = department

    def __str__(self):
        return (f"[Student #{self.id}] {self.name} | "
                f"Dept: {self.department} | SID: {self.student_id}")


class Admin(User):
    """
    An administrator who can approve/reject reports and claims.

    INHERITANCE: Inherits everything from User; no extra fields needed.
    """

    def __init__(self, name: str, email: str, password: str):
        super().__init__(name, email, password)

    def __str__(self):
        return f"[Admin #{self.id}] {self.name} <{self.email}>"


# ── Item hierarchy ───────────────────────────────────────────────────────────

class Item:
    """
    Base class for a reported item (lost or found).

    STATUS LIFECYCLE:
        Pending  ->  Approved  ->  Claimed  ->  Returned
                 \\>  Rejected
    """

    VALID_STATUSES = ("Pending", "Approved", "Rejected", "Claimed", "Returned")

    def __init__(self, name: str, category: str, description: str,
                 location: str, date: str, reporter_id: int):
        self.item_id     = IDCounter.next("item")
        self.name        = name
        self.category    = category
        self.description = description
        self.location    = location
        self.date        = date
        self.reporter_id = reporter_id
        self.status      = "Pending"       # Default status (Reactive Evolution)

    def update_status(self, new_status: str):
        """Change item status after validation."""
        if new_status not in self.VALID_STATUSES:
            raise ValueError(f"Invalid status: {new_status}")
        self.status = new_status

    def matches(self, other: "Item") -> bool:
        """
        Check if two items possibly represent the same real-world object.
        Uses simple keyword overlap on name, category, and location.

        BUSINESS RULE #9: Match detection for lost/found pairs.
        """
        same_category = self.category.lower() == other.category.lower()
        name_overlap  = (self.name.lower() in other.name.lower() or
                         other.name.lower() in self.name.lower())
        loc_overlap   = (self.location.lower() in other.location.lower() or
                         other.location.lower() in self.location.lower())
        return same_category and name_overlap and loc_overlap

    def summary(self) -> str:
        """Return a short one-line description for list displays."""
        return (f"ID:{self.item_id:>3}  [{self.status:<8}]  "
                f"{self.name:<20}  {self.category:<15}  "
                f"Location: {self.location}")

    def details(self) -> str:
        """Return full item details."""
        return (
            f"\n{'--'*25}\n"
            f"  Item ID     : {self.item_id}\n"
            f"  Type        : {type(self).__name__}\n"
            f"  Status      : {self.status}\n"
            f"  Name        : {self.name}\n"
            f"  Category    : {self.category}\n"
            f"  Location    : {self.location}\n"
            f"  Date        : {self.date}\n"
            f"  Description : {self.description}\n"
            f"  Reporter ID : {self.reporter_id}\n"
            f"{'--'*25}"
        )

    def __str__(self):
        return self.summary()


class LostItem(Item):
    """
    An item that a student has reported as lost.

    INHERITANCE: Extends Item - adds semantic meaning to the record.
    """

    def __init__(self, name: str, category: str, description: str,
                 location: str, date: str, reporter_id: int):
        super().__init__(name, category, description, location, date, reporter_id)

    def details(self) -> str:
        return "  ** LOST ITEM **" + super().details()


class FoundItem(Item):
    """
    An item that a student has reported as found.

    INHERITANCE: Extends Item - adds semantic meaning to the record.
    """

    def __init__(self, name: str, category: str, description: str,
                 location: str, date: str, reporter_id: int):
        super().__init__(name, category, description, location, date, reporter_id)

    def details(self) -> str:
        return "  ** FOUND ITEM **" + super().details()


# ── Claim ────────────────────────────────────────────────────────────────────

class Claim:
    """
    A claim submitted by a student asserting ownership of an item.

    STATUS: Pending -> Approved / Rejected
    """

    def __init__(self, item_id: int, student_id: int, reason: str):
        self.claim_id   = IDCounter.next("claim")
        self.item_id    = item_id
        self.student_id = student_id
        self.reason     = reason
        self.status     = "Pending"

    def __str__(self):
        return (f"[Claim #{self.claim_id}]  Item:{self.item_id}  "
                f"Student:{self.student_id}  Status:{self.status}\n"
                f"  Reason: {self.reason}")


# ── Notification ─────────────────────────────────────────────────────────────

class Notification:
    """
    A message sent to a user by the system (e.g., claim approved, match found).
    """

    def __init__(self, user_id: int, message: str):
        self.notification_id = IDCounter.next("notification")
        self.user_id         = user_id
        self.message         = message
        self.is_read         = False

    def mark_read(self):
        self.is_read = True

    def __str__(self):
        tag = "   " if self.is_read else "[!]"
        return f"{tag} [Notif #{self.notification_id}] {self.message}"
