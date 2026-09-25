import frappe
import frappe.defaults

from frappe.tests.utils import FrappeTestCase


def create_events():
    if frappe.flags.test_events_created:
        return

    frappe.set_user("Administrator")

    trainers_doc= frappe.get_doc({"doctype": "TRAINER","trainer_name":"Testing Trainer","employee_id": "EMP-003"
        }).insert()
    member_doc = frappe.get_doc({"doctype": "MEMBER","member_name":"Testing Member","phone": "1256488945"
        }).insert()
    session_doc = frappe.get_doc({"doctype": "SESSION TYPE","session_type_name":"Session Testing 1",
        "duration_minutes": "40"
        }).insert(ignore_if_duplicate=True)

    class_session_doc = frappe.get_doc({"doctype": "Class Session","session_type":session_doc.name,"trainer": trainers_doc.name,
        "session_date":frappe.utils.getdate(), 
        "start_time":frappe.utils.nowtime()
        }).insert(ignore_if_duplicate=True)
    package_doc = frappe.get_doc({"doctype": "Package Purchase","total_credits":60,"amount_paid": 600,"member": member_doc.name,
        "expirey_date":frappe.utils.getdate(), }).insert(ignore_if_duplicate=True)
    frappe.flags.test_events_created = True

class TestEvent(FrappeTestCase):
    def setUp(self):
        create_events()

    def tearDown(self):
        frappe.set_user("Administrator")

    def test_trainer(self):
        doc = frappe.get_doc("TRAINER",frappe.db.get_value("TRAINER", {"trainer_name": "Testing Trainer"}),)
        print(doc.trainer_name)
        self.assertEqual(doc.trainer_name, "Testing Trainer")

    def test_session(self):
        doc = frappe.get_doc("SESSION TYPE",frappe.db.get_value("SESSION TYPE", {"session_type_name": "Session Testing 1"}),)
        print(doc.session_type_name)
        self.assertEqual(doc.session_type_name, "Session Testing 1")

    def test_member(self):
        doc = frappe.get_doc("MEMBER",frappe.db.get_value("MEMBER", {"member_name": "Testing Member"}),)
        print(doc.member_name)
        self.assertEqual(doc.member_name, "Testing Member")
    
    def test_package_purchase(self):
        doc = frappe.get_doc("Package Purchase",frappe.db.get_value("Package Purchase", {"amount_paid": 600}),)
        print(f"Total Credits {doc.total_credits}")
        print(f"Credits reamining {doc.credits_remaining}")
        self.assertEqual(doc.total_credits, 60)
    
    def test_class_session(self):
        doc = frappe.get_doc("Class Session",frappe.db.get_value("Class Session", {"session_type": "Session Testing 1"}))
        self.assertEqual(doc.docstatus, 0)
        if not doc.attendees:
            member_id = frappe.db.get_value("MEMBER", {"member_name": "Testing Member"})
            pkg_id = frappe.db.get_value("Package Purchase", {"member": member_id})
            credits_req = frappe.db.get_value("SESSION TYPE", {"session_type_name":"Session Testing 1"},"credits_required")
            doc.append("attendees", {"member": member_id,"package_purchase": pkg_id,"attendance_status": "Attended","credits_charged":credits_req,"attendance_status":"Attended"})
            
        self.assertEqual(doc.session_type, "Session Testing 1")
        doc.status = "Completed"
        doc.save()
        doc.submit()
        member_id = frappe.db.get_value("MEMBER", {"member_name": "Testing Member"})
        pkg_id = frappe.db.get_value("Package Purchase", {"member": member_id},"credits_remaining")
        self.assertEqual(doc.docstatus, 1)
        self.assertEqual(pkg_id,59)

