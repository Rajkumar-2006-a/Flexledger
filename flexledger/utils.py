
import frappe


def rename_member(old_name, new_name):
    frappe.rename_doc("MEMBER", old_name, new_name, merge=False)