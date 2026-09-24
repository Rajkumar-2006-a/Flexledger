import frappe

def session_query(user):
    if not user:
        user = frappe.session.user
    roles = frappe.get_roles(user)
    if "FIT Trainer" in roles and "FIT Studio Manager" not in roles:
        return "(`tabPackage Purchase`.trainer = {user} )".format(user=frappe.db.escape(user))
