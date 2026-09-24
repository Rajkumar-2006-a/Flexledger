import frappe
from frappe.model.document import Document
from frappe.model.naming import make_autoname


class PackagePurchase(Document):
    def validate(self):
        doc=self.get_doc_before_save()
        self.credits_remaining = self.total_credits - self.credits_used

    def autoname(self):
        member_code = self.member.split("-")[-1]

        self.name = make_autoname(
            f"MEM{member_code}-PKG-.###"
        )
