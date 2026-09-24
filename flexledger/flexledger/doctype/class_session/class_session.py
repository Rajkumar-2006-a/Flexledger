import frappe
from frappe.model.document import Document
from frappe.utils import getdate, today


class ClassSession(Document):
    def validate(self):
        if self.status=="Draft" and getdate(self.session_date) < getdate(today()):
            frappe.throw("session_date cannot be in the past for a Draft record")
        credits=frappe.get_value("SESSION TYPE",self.session_type,"credits_required")
        for i in self.attendees:
            doc=frappe.get_doc("Package Purchase",i.package_purchase)
            if i.member!=doc.member:
                frappe.throw(f"Package {i.package_purchase} has invalid member")
            if doc.status!="Active":
                frappe.throw(f"The package {i.package_purchase }is not active")
            if getdate(doc.expirey_date) < getdate(self.session_date):
                frappe.throw("The Package is expired")
            i.credits_charged=credits
            if doc.credits_remaining<credits:
                frappe.throw(f"Memebr {i.member} has insufficient credits . Remaining credits{doc.credits_remaining}")
    def before_submit(self):
        if self.status!="Completed":
            frappe.throw("Need status as Completed ")
        for i in self.attendees:
            if i.attendance_status == "Booked":
                frappe.throw("Every member attendance should be marked")
    def on_submit(self):
        studio=frappe.get_single("STUDIO SETTINGS")
        for i in self.attendees:
            flag=i.attendance_status == "Attended" or (studio.no_show_forfeits_credit and i.attendance_status == "No-show")
            if not flag:
                continue
            doc=frappe.get_doc("Package Purchase",i.package_purchase)
            new_used=doc.credits_used+i.credits_charged
            new_rem=doc.total_credits-new_used
            frappe.db.set_value("Package Purchase",i.package_purchase,{
                'credits_used':new_used,
                'credits_remaining':new_rem,
                'status':("Fully Used" if new_rem<=0 else doc.status )
            },update_modified=True)
            
            if doc.credits_remaining<studio.low_balance_alert_threshold:
                frappe.enqueue(
                    "flexledger.flexledger.api.send_low_balance_email",
                    member=doc.member,
                    remaining=new_rem,
                    now=False
                )
        frappe.enqueue(
        "flexledger.webhook.send_webhook",
        session_name=self.name,
        queue="short"
        )
    def on_cancel(self):
        self.db_set("status", "Cancelled")
        for i in self.attendees:
            should_restore = i.attendance_status == "Attended" or (
                i.attendance_status == "No-Show"
                and frappe.get_single(
                    "Studio Settings"
                ).no_show_forfeits_credit
            )
            if not should_restore:
                continue
            doc = frappe.get_doc(
                "Package Purchase",
                i.package_purchase
            )
            new_used = doc.credits_used - i.credits_charged
            new_remaining = doc.total_credits - new_used  
            frappe.db.set_value(
                "Package Purchase",
                doc.name,
                {"credits_used": new_used,"credits_remaining": new_remaining,
                    "status": (
                        "Active"
                        if doc.status == "Fully Used"
                        else doc.status
                    ),
                },
                update_modified=True
            )

    def on_trash(self):
        if self.status not in ("Cancelled", "Draft"):
            frappe.throw(
                f"Cannot delete a Class Session with status "
                f"'{self.status}'. Cancel it first."
            )