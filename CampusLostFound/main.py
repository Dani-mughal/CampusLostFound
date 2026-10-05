# =============================================================================
# main.py — Console UI / Entry Point
# =============================================================================
# This file handles ALL user interaction (menus, prompts, input validation).
# It calls LostFoundSystem for every business operation.
#
# SOFTWARE EVOLUTION — PREVENTIVE EVOLUTION:
#   By keeping UI code here and business logic in services.py, we follow
#   the Separation of Concerns principle. If we later add a web or mobile
#   UI, we only write a new "main" layer — services.py stays untouched.
# =============================================================================

from services import LostFoundSystem
from models import Student, Admin


# =============================================================================
# UTILITY / DISPLAY HELPERS
# =============================================================================

def print_header(title: str):
    """Print a formatted section header."""
    print(f"\n{'='*55}")
    print(f"   {title}")
    print(f"{'='*55}")


def print_divider():
    print("-" * 55)


def pause():
    """Wait for the user to press Enter before continuing."""
    input("\n  Press Enter to continue...")


def get_input(prompt: str) -> str:
    """Read non-empty input from the user. Loops until valid."""
    while True:
        value = input(f"  {prompt}: ").strip()
        if value:
            return value
        print("  [!] This field cannot be empty. Please try again.")


def get_int(prompt: str) -> int:
    """Read a valid integer from the user. Loops until valid."""
    while True:
        try:
            return int(input(f"  {prompt}: ").strip())
        except ValueError:
            print("  [!] Please enter a valid number.")


# =============================================================================
# AUTHENTICATION SCREENS
# =============================================================================

def screen_login(system: LostFoundSystem):
    """Login screen — returns the logged-in User object or None."""
    print_header("LOGIN")
    email    = get_input("Email")
    password = get_input("Password")
    user = system.login(email, password)
    if user:
        print(f"\n  Welcome back, {user.name}!")
    else:
        print("\n  [!] Invalid email or password.")
    return user


def screen_register(system: LostFoundSystem):
    """Student registration screen."""
    print_header("STUDENT REGISTRATION")
    try:
        name       = get_input("Full Name")
        email      = get_input("Email")
        password   = get_input("Password")
        student_id = get_input("Student ID")
        department = get_input("Department")
        student = system.register_student(name, email, password,
                                          student_id, department)
        print(f"\n  Account created successfully! Your user ID is #{student.id}")
        print(f"  You can now log in with: {email}")
    except ValueError as e:
        print(f"\n  [!] Registration failed: {e}")
    pause()


# =============================================================================
# STUDENT MENU SCREENS
# =============================================================================

def student_report_lost(system: LostFoundSystem, user):
    """Screen: Report a lost item."""
    print_header("REPORT LOST ITEM")
    name        = get_input("Item Name")
    category    = get_input("Category (e.g. Electronics, Bag, Keys, ID Card)")
    location    = get_input("Location Lost")
    date        = get_input("Date (e.g. 2024-10-01)")
    description = get_input("Description")
    item = system.report_lost_item(user.id, name, category, location,
                                   date, description)
    print(f"\n  Lost item reported! Item ID: #{item.item_id}")
    print(f"  Status: {item.status} (waiting for admin approval)")
    pause()


def student_report_found(system: LostFoundSystem, user):
    """Screen: Report a found item."""
    print_header("REPORT FOUND ITEM")
    name        = get_input("Item Name")
    category    = get_input("Category (e.g. Electronics, Bag, Keys, ID Card)")
    location    = get_input("Location Found")
    date        = get_input("Date (e.g. 2024-10-01)")
    description = get_input("Description")
    item = system.report_found_item(user.id, name, category, location,
                                    date, description)
    print(f"\n  Found item reported! Item ID: #{item.item_id}")
    print(f"  Status: {item.status} (waiting for admin approval)")
    pause()


def student_search(system: LostFoundSystem):
    """Screen: Search approved items."""
    print_header("SEARCH ITEMS")
    print("  Leave a field blank to skip that filter.\n")
    keyword  = input("  Keyword (name/description): ").strip()
    category = input("  Category                  : ").strip()
    location = input("  Location                  : ").strip()

    results = system.search_items(keyword, category, location)
    print(f"\n  Found {len(results)} result(s):\n")
    if results:
        print_divider()
        for item in results:
            print(f"  {item.summary()}")
        print_divider()
    else:
        print("  No matching items found.")
    pause()


def student_view_item(system: LostFoundSystem):
    """Screen: View full details of a single item."""
    print_header("VIEW ITEM DETAILS")
    item_id = get_int("Enter Item ID")
    item    = system.get_item_details(item_id)
    if item and item.status == "Approved":
        print(item.details())
    elif item:
        print(f"\n  [!] Item #{item_id} is not available for viewing "
              f"(Status: {item.status}).")
    else:
        print(f"\n  [!] Item #{item_id} not found.")
    pause()


def student_submit_claim(system: LostFoundSystem, user):
    """Screen: Submit a claim on an approved item."""
    print_header("SUBMIT CLAIM")
    item_id = get_int("Enter Item ID to Claim")
    reason  = get_input("Reason / Proof of Ownership")
    try:
        claim = system.submit_claim(user.id, item_id, reason)
        print(f"\n  Claim submitted! Claim ID: #{claim.claim_id}")
        print(f"  Status: {claim.status} (waiting for admin review)")
    except (ValueError, PermissionError) as e:
        print(f"\n  [!] Could not submit claim: {e}")
    pause()


def student_view_claims(system: LostFoundSystem, user):
    """Screen: View all claims made by this student."""
    print_header("MY CLAIMS")
    claims = system.get_claims_for_student(user.id)
    if claims:
        for c in claims:
            print(f"\n  {c}")
    else:
        print("  You have not submitted any claims yet.")
    pause()


def student_view_notifications(system: LostFoundSystem, user):
    """Screen: View notifications for this student."""
    print_header("NOTIFICATIONS")
    notifications = system.get_notifications(user.id)
    if notifications:
        for n in notifications:
            print(f"  {n}")
        system.mark_notifications_read(user.id)
        print("\n  All notifications marked as read.")
    else:
        print("  No notifications yet.")
    pause()


def student_menu(system: LostFoundSystem, user: Student):
    """Main menu loop for a logged-in student."""
    while True:
        print_header(f"STUDENT MENU  —  {user.name}")
        print("  1. Report Lost Item")
        print("  2. Report Found Item")
        print("  3. Search Items")
        print("  4. View Item Details")
        print("  5. Submit Claim")
        print("  6. View My Claims")
        print("  7. View Notifications")
        print("  8. Logout")

        choice = input("\n  Enter choice (1-8): ").strip()

        if   choice == "1": student_report_lost(system, user)
        elif choice == "2": student_report_found(system, user)
        elif choice == "3": student_search(system)
        elif choice == "4": student_view_item(system)
        elif choice == "5": student_submit_claim(system, user)
        elif choice == "6": student_view_claims(system, user)
        elif choice == "7": student_view_notifications(system, user)
        elif choice == "8":
            print(f"\n  Goodbye, {user.name}!")
            break
        else:
            print("\n  [!] Invalid choice. Please enter a number from 1 to 8.")


# =============================================================================
# ADMIN MENU SCREENS
# =============================================================================

def admin_view_reports(system: LostFoundSystem):
    """Screen: View all item reports."""
    print_header("ALL REPORTS")
    items = system.get_all_items()
    if items:
        print_divider()
        for item in items:
            label = "LOST " if item.__class__.__name__ == "LostItem" else "FOUND"
            print(f"  [{label}] {item.summary()}")
        print_divider()
    else:
        print("  No reports yet.")
    pause()


def admin_approve_report(system: LostFoundSystem, admin):
    """Screen: Approve a pending report."""
    print_header("APPROVE REPORT")
    item_id = get_int("Enter Item ID to Approve")
    try:
        system.approve_item(admin.id, item_id)
        print(f"\n  Item #{item_id} has been APPROVED.")
    except (ValueError, PermissionError) as e:
        print(f"\n  [!] Error: {e}")
    pause()


def admin_reject_report(system: LostFoundSystem, admin):
    """Screen: Reject a pending report."""
    print_header("REJECT REPORT")
    item_id = get_int("Enter Item ID to Reject")
    try:
        system.reject_item(admin.id, item_id)
        print(f"\n  Item #{item_id} has been REJECTED.")
    except (ValueError, PermissionError) as e:
        print(f"\n  [!] Error: {e}")
    pause()


def admin_view_claims(system: LostFoundSystem):
    """Screen: View all claims."""
    print_header("ALL CLAIMS")
    claims = system.get_all_claims()
    if claims:
        for c in claims:
            print(f"\n  {c}")
    else:
        print("  No claims yet.")
    pause()


def admin_approve_claim(system: LostFoundSystem, admin):
    """Screen: Approve a pending claim."""
    print_header("APPROVE CLAIM")
    claim_id = get_int("Enter Claim ID to Approve")
    try:
        system.approve_claim(admin.id, claim_id)
        print(f"\n  Claim #{claim_id} APPROVED. Item status updated to 'Claimed'.")
    except (ValueError, PermissionError) as e:
        print(f"\n  [!] Error: {e}")
    pause()


def admin_reject_claim(system: LostFoundSystem, admin):
    """Screen: Reject a pending claim."""
    print_header("REJECT CLAIM")
    claim_id = get_int("Enter Claim ID to Reject")
    try:
        system.reject_claim(admin.id, claim_id)
        print(f"\n  Claim #{claim_id} REJECTED.")
    except (ValueError, PermissionError) as e:
        print(f"\n  [!] Error: {e}")
    pause()


def admin_mark_returned(system: LostFoundSystem, admin):
    """Screen: Mark a claimed item as returned."""
    print_header("MARK ITEM AS RETURNED")
    item_id = get_int("Enter Item ID to Mark as Returned")
    try:
        system.mark_returned(admin.id, item_id)
        print(f"\n  Item #{item_id} marked as RETURNED.")
    except (ValueError, PermissionError) as e:
        print(f"\n  [!] Error: {e}")
    pause()


def admin_view_notifications(system: LostFoundSystem, admin):
    """Screen: View admin notifications."""
    print_header("ADMIN NOTIFICATIONS")
    notifications = system.get_notifications(admin.id)
    if notifications:
        for n in notifications:
            print(f"  {n}")
        system.mark_notifications_read(admin.id)
        print("\n  All notifications marked as read.")
    else:
        print("  No notifications.")
    pause()


def admin_menu(system: LostFoundSystem, admin: Admin):
    """Main menu loop for a logged-in administrator."""
    while True:
        print_header(f"ADMIN MENU  —  {admin.name}")
        print("  1. View All Reports")
        print("  2. Approve Report")
        print("  3. Reject Report")
        print("  4. View Claims")
        print("  5. Approve Claim")
        print("  6. Reject Claim")
        print("  7. Mark Item as Returned")
        print("  8. View Notifications")
        print("  9. Logout")

        choice = input("\n  Enter choice (1-9): ").strip()

        if   choice == "1": admin_view_reports(system)
        elif choice == "2": admin_approve_report(system, admin)
        elif choice == "3": admin_reject_report(system, admin)
        elif choice == "4": admin_view_claims(system)
        elif choice == "5": admin_approve_claim(system, admin)
        elif choice == "6": admin_reject_claim(system, admin)
        elif choice == "7": admin_mark_returned(system, admin)
        elif choice == "8": admin_view_notifications(system, admin)
        elif choice == "9":
            print(f"\n  Goodbye, {admin.name}!")
            break
        else:
            print("\n  [!] Invalid choice. Please enter a number from 1 to 9.")


# =============================================================================
# MAIN APPLICATION LOOP
# =============================================================================

def main():
    """
    Application entry point.

    Initialises the system, optionally loads demo data, and presents
    the top-level menu (Login / Register / Exit).
    """
    system = LostFoundSystem()

    print_header("CAMPUS LOST & FOUND MANAGEMENT SYSTEM")
    print("  University of [Your University Name]")
    print("  Software Evolution Techniques — Assignment Project")
    print_divider()

    # Offer to load demo data so the assignment scenario runs immediately
    load_demo = input("\n  Load demo data (Alice/Bob/HP Laptop scenario)? (y/n): ").strip().lower()
    if load_demo == "y":
        system.seed_demo_data()

    # ── Top-level navigation loop ──────────────────────────────────────────
    while True:
        print_header("MAIN MENU")
        print("  1. Login")
        print("  2. Register (New Student)")
        print("  3. Exit")

        choice = input("\n  Enter choice (1-3): ").strip()

        if choice == "1":
            user = screen_login(system)
            if user:
                if isinstance(user, Admin):
                    admin_menu(system, user)
                elif isinstance(user, Student):
                    student_menu(system, user)

        elif choice == "2":
            screen_register(system)

        elif choice == "3":
            print("\n  Thank you for using the Campus Lost & Found System. Goodbye!\n")
            break

        else:
            print("\n  [!] Invalid choice. Please enter 1, 2, or 3.")


# Standard Python entry-point guard
if __name__ == "__main__":
    main()
