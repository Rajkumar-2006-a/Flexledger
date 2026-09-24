
import frappe


def rename_member(old_name, new_name):
    frappe.rename_doc("MEMBER", old_name, new_name, merge=False)
def get_studio_name():
    return frappe.db.get_single_value('STUDIO SETTINGS','studio_name') 
   
