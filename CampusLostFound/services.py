# =============================================================================
# services.py — Business Logic
# =============================================================================
# This file contains the LostFoundSystem class, which holds ALL business logic.
#
# SOFTWARE EVOLUTION — PREVENTIVE EVOLUTION:
#   Keeping business logic in one service class (instead of spreading it
#   across Item, Claim, or main.py) makes the code easy to maintain,
#   refactor, and extend without breaking other parts.
#
# SOFTWARE EVOLUTION — ADAPTIVE EVOLUTION:
#   If we later add a mobile app or web interface, we would keep this file
#   exactly as-is and simply add an API layer on top of it:
#
#     Console / Web / Mobile
#           |
#          API  (would be added here — e.g. Flask routes calling these methods)
#           |
#     LostFoundSystem  (this file — stays unchanged)
#           |
#       In-memory lists  (later replaced by a database)
# =============================================================================

from models import (Admin, Claim, FoundItem, IDCounter,
                    LostItem, Notification, Student, User)


class LostFoundSystem:
    """
    Central service class for the Campus Lost & Found application.

    Responsibilities
    ----------------
    - Manage users (register, login)
    - Manage items (report, approve, reject, return)
    - Manage claims (submit, approve, reject)
    - Manage notifications (create, deliver)
    - Run match detection between lost and found items
    """

    def __init__(self):
        # ── In-memory data stores (lists act as our "database") ──
        self.users         = []   # list[User]
        self.items         = []   # list[Item]
        self.claims        = []   # list[Claim]
        self.notifications = []   # list[Notification]

        # Seed the default admin account
        self._seed_admin()

    # =========================================================================
    # SEED DATA
    # =========================================================================

    def _seed_admin(self):
        """Create the default administrator account on startup."""
        admin = Admin("Administrator", "admin@university.com", "admin123")
        self.users.append(admin)

    def seed_demo_data(self):
        """
        Populate the system with demo students and items so that the
        assignment scenario (HP Laptop match) can be demonstrated
        immediately without manual entry.
        """
        # Register two demo students
        alice = self.register_student(
            "Alice Johnson", "alice@university.com", "alice123",
            "S001", "Computer Science"
        )
        bob = self.register_student(
            "Bob Smith", "bob@university.com", "bob123",
            "S002", "Electrical Engineering"
        )

        # Alice reports a LOST HP Laptop
        lost = self.report_lost_item(
            reporter_id=alice.id,
            name="HP Laptop",
            category="Electronics",
            location="Computer Lab",
            date="2024-10-01",
            description="Black laptop with university sticker on the lid"
        )

        # Bob reports a FOUND HP Laptop
        found = self.report_found_item(
            reporter_id=bob.id,
            name="HP Laptop",
            category="Electronics",
            location="Computer Lab",
            date="2024-10-01",
            description="Black HP laptop found on a desk near the printer"
        )

        # Admin approves both reports (simulating admin action)
        admin = self._get_admin()
        self.approve_item(admin.id, lost.item_id)
        self.approve_item(admin.id, found.item_id)

        print("\n  [Demo data loaded]")
        print("  Students : Alice (alice@university.com / alice123)")
        print("            Bob   (bob@university.com   / bob123)")
        print("  Admin    : admin@university.com / admin123")
        print("  Both students have an approved HP Laptop report.\n")

    # =========================================================================
    # USER MANAGEMENT
    # =========================================================================

    def register_student(self, name: str, email: str, password: str,
                         student_id: str, department: str) -> Student:
        """Register a new student. Raises ValueError if email is taken."""
        if self._find_user_by_email(email):
            raise ValueError(f"Email '{email}' is already registered.")
        student = Student(name, email, password, student_id, department)
        self.users.append(student)
        return student

    def login(self, email: str, password: str) -> User:
        """
        Authenticate a user by email and password.
        Returns the User object on success, None on failure.
        """
        user = self._find_user_by_email(email)
        if user and user.check_password(password):
            return user
        return None

    # =========================================================================
    # ITEM MANAGEMENT
    # =========================================================================

    def report_lost_item(self, reporter_id: int, name: str, category: str,
                         location: str, date: str, description: str) -> LostItem:
        """
        Create a LostItem with status 'Pending'.

        SOFTWARE EVOLUTION — REACTIVE EVOLUTION:
            Originally items were published immediately.
            After fake-report incidents, we changed the flow so that
            every new report starts as 'Pending' and must be approved
            by an admin before students can see it.
        """
        item = LostItem(name, category, description, location, date, reporter_id)
        self.items.append(item)
        self._check_for_matches(item)   # Business Rule #9
        return item

    def report_found_item(self, reporter_id: int, name: str, category: str,
                          location: str, date: str, description: str) -> FoundItem:
        """
        Create a FoundItem with status 'Pending'.

        Same Reactive Evolution rationale as report_lost_item().
        """
        item = FoundItem(name, category, description, location, date, reporter_id)
        self.items.append(item)
        self._check_for_matches(item)   # Business Rule #9
        return item

    def approve_item(self, admin_id: int, item_id: int) -> bool:
        """
        Admin approves a pending report → status becomes 'Approved'.
        Raises PermissionError if caller is not an Admin.
        """
        self._require_admin(admin_id)
        item = self._find_item(item_id)
        if not item:
            raise ValueError(f"Item #{item_id} not found.")
        item.update_status("Approved")
        # Notify the reporter
        self._notify(item.reporter_id,
                     f"Your {type(item).__name__} report for '{item.name}' "
                     f"has been APPROVED.")
        return True

    def reject_item(self, admin_id: int, item_id: int) -> bool:
        """
        Admin rejects a pending report → status becomes 'Rejected'.
        Raises PermissionError if caller is not an Admin.
        """
        self._require_admin(admin_id)
        item = self._find_item(item_id)
        if not item:
            raise ValueError(f"Item #{item_id} not found.")
        item.update_status("Rejected")
        self._notify(item.reporter_id,
                     f"Your {type(item).__name__} report for '{item.name}' "
                     f"has been REJECTED by the administrator.")
        return True

    def mark_returned(self, admin_id: int, item_id: int) -> bool:
        """
        Admin marks a claimed item as 'Returned'.
        Business Rule #7 and #8.
        """
        self._require_admin(admin_id)
        item = self._find_item(item_id)
        if not item:
            raise ValueError(f"Item #{item_id} not found.")
        if item.status != "Claimed":
            raise ValueError("Only items with status 'Claimed' can be marked Returned.")
        item.update_status("Returned")
        self._notify(item.reporter_id,
                     f"Item '{item.name}' has been marked as RETURNED.")
        return True

    def search_items(self, keyword: str = "", category: str = "",
                     location: str = "") -> list:
        """
        Return only APPROVED items that match the search terms.
        Business Rule #2 & #3: rejected/pending items are hidden from students.
        """
        results = []
        for item in self.items:
            if item.status != "Approved":
                continue
            kw_match  = (not keyword  or
                         keyword.lower()  in item.name.lower() or
                         keyword.lower()  in item.description.lower())
            cat_match = (not category or
                         category.lower() in item.category.lower())
            loc_match = (not location or
                         location.lower() in item.location.lower())
            if kw_match and cat_match and loc_match:
                results.append(item)
        return results

    def get_all_items(self) -> list:
        """Return every item (admin view — no status filter)."""
        return self.items

    def get_item_details(self, item_id: int):
        """Return full details of a single item by ID."""
        return self._find_item(item_id)

    # =========================================================================
    # CLAIM MANAGEMENT
    # =========================================================================

    def submit_claim(self, student_id: int, item_id: int, reason: str) -> Claim:
        """
        Student submits a claim on an approved item.
        Business Rule #4: claim starts as 'Pending'.
        """
        item = self._find_item(item_id)
        if not item:
            raise ValueError(f"Item #{item_id} not found.")
        if item.status != "Approved":
            raise ValueError("Claims can only be made on Approved items.")
        # Prevent duplicate claims by the same student on the same item
        for c in self.claims:
            if c.item_id == item_id and c.student_id == student_id:
                raise ValueError("You have already submitted a claim for this item.")
        claim = Claim(item_id, student_id, reason)
        self.claims.append(claim)
        # Notify admin (first admin found)
        admin = self._get_admin()
        if admin:
            self._notify(admin.id,
                         f"New claim #{claim.claim_id} received for "
                         f"Item #{item_id} by Student #{student_id}.")
        return claim

    def approve_claim(self, admin_id: int, claim_id: int) -> bool:
        """
        Admin approves a claim.
        Business Rule #5 & #6: item status becomes 'Claimed'.
        """
        self._require_admin(admin_id)
        claim = self._find_claim(claim_id)
        if not claim:
            raise ValueError(f"Claim #{claim_id} not found.")
        claim.status = "Approved"
        # Update the linked item
        item = self._find_item(claim.item_id)
        if item:
            item.update_status("Claimed")
        # Notify the student (Business Rule #10)
        self._notify(claim.student_id,
                     f"Your claim #{claim.claim_id} for item "
                     f"'{item.name if item else claim.item_id}' "
                     f"has been APPROVED. Please collect the item.")
        return True

    def reject_claim(self, admin_id: int, claim_id: int) -> bool:
        """Admin rejects a claim."""
        self._require_admin(admin_id)
        claim = self._find_claim(claim_id)
        if not claim:
            raise ValueError(f"Claim #{claim_id} not found.")
        claim.status = "Rejected"
        item = self._find_item(claim.item_id)
        self._notify(claim.student_id,
                     f"Your claim #{claim.claim_id} for item "
                     f"'{item.name if item else claim.item_id}' "
                     f"has been REJECTED by the administrator.")
        return True

    def get_claims_for_student(self, student_id: int) -> list:
        """Return all claims submitted by a specific student."""
        return [c for c in self.claims if c.student_id == student_id]

    def get_all_claims(self) -> list:
        """Return all claims (admin view)."""
        return self.claims

    # =========================================================================
    # NOTIFICATION MANAGEMENT
    # =========================================================================

    def get_notifications(self, user_id: int) -> list:
        """Return all notifications for a user."""
        return [n for n in self.notifications if n.user_id == user_id]

    def mark_notifications_read(self, user_id: int):
        """Mark all of a user's notifications as read."""
        for n in self.notifications:
            if n.user_id == user_id:
                n.mark_read()

    # =========================================================================
    # MATCH DETECTION (Business Rule #9)
    # =========================================================================

    def _check_for_matches(self, new_item):
        """
        After a new item is reported, scan existing items for possible matches.
        A match is: one LostItem + one FoundItem with similar name/category/location.

        When a match is found, notify both reporters (Business Rule #10).
        """
        opposite_type = FoundItem if isinstance(new_item, LostItem) else LostItem
        for existing in self.items:
            if existing.item_id == new_item.item_id:
                continue
            if not isinstance(existing, opposite_type):
                continue
            if new_item.matches(existing):
                msg = (f"Possible match found! Your report "
                       f"'{new_item.name}' (ID:{new_item.item_id}) may match "
                       f"another report (ID:{existing.item_id}). "
                       f"Please contact the administrator.")
                self._notify(new_item.reporter_id, msg)
                self._notify(existing.reporter_id,
                             f"Possible match found for your report "
                             f"'{existing.name}' (ID:{existing.item_id}) with "
                             f"a new report (ID:{new_item.item_id}).")

    # =========================================================================
    # PRIVATE HELPER METHODS
    # =========================================================================

    def _find_user_by_email(self, email: str) -> User:
        for u in self.users:
            if u.email.lower() == email.lower():
                return u
        return None

    def _find_item(self, item_id: int):
        for i in self.items:
            if i.item_id == item_id:
                return i
        return None

    def _find_claim(self, claim_id: int):
        for c in self.claims:
            if c.claim_id == claim_id:
                return c
        return None

    def _get_admin(self) -> Admin:
        for u in self.users:
            if isinstance(u, Admin):
                return u
        return None

    def _require_admin(self, user_id: int):
        """Raise PermissionError if user_id does not belong to an Admin."""
        for u in self.users:
            if u.id == user_id and isinstance(u, Admin):
                return
        raise PermissionError("Only an administrator can perform this action.")

    def _notify(self, user_id: int, message: str):
        """Create and store a notification for a user."""
        notif = Notification(user_id, message)
        self.notifications.append(notif)
