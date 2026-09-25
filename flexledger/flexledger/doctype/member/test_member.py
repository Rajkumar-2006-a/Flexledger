import frappe
import frappe.defaults

from frappe.tests.utils import FrappeTestCase


def create_events():
	if frappe.flags.test_events_created:
		return

	frappe.set_user("Administrator")

	trainers_doc= frappe.get_doc({
		"doctype": "TRAINER",
		"trainer_name":"Testing Trainer",
		"employee_id": "EMP-003"
		}).insert()
	member_doc = frappe.get_doc({
		"doctype": "MEMBER",
		"member_name":"Testing Member",
		"phone": "1256488945"
		}).insert()
	session_doc = frappe.get_doc({
		"doctype": "SESSION TYPE",
		"session_type_name":"Session Testing 1",
		"duration_minutes": "40"
		}).insert(ignore_if_duplicate=True)

	class_session_doc = frappe.get_doc({
		"doctype": "Class Session",
		"session_type":session_doc.name,
		"trainer": trainers_doc.name,
        "session_date":frappe.utils.getdate(), 
		"start_time":frappe.utils.nowtime()
		}).insert(ignore_if_duplicate=True)
 
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

    def test_class_session(self):
        doc = frappe.get_doc("Class Session",frappe.db.get_value("Class Session", {"session_type": "Session Testing 1"}),)
        print(doc.trainer)
        self.assertEqual(doc.session_type, "Session Testing 1")