import frappe
from frappe.query_builder import DocType


def get_low_balance_memebers(threshold):
    pp=frappe.qb.Doctype("Package Purchase")
    query=(
          frappe.qb.from_(pp).select(pp.name,pp.memeber,pp.credits_remaining,pp.expiry_date)
           .where(pp.credits_remaining <= threshold )
           .where(pp.status =="Active").orderby(pp.credits_remaining )
           )
    result=query.run(as_dict=True)
    print(result)

def transfer_package(package_name,new_memeber):
    try:
        doc=frappe.db.get_value("Packgae Purchase",package_name,["credits_used","status"],as_dict=True)
        if not doc:
            frappe.throw(f"Package {package_name} does not exists.")
        if doc.credits_used and doc.credits_used>0:
            frappe.throw(f"Cannot transfer {package_name} -credits already used")
        if not frappe.db.exists("MEMBER",new_member):
            frappe.throw(f"Memeber {new_memeber} does not exixts.")
        frappe.db.sql("""
                      UPDATE `tabPackage Purchase` SET memeber=%s,modified=%s
                      WHERE name=%s
                      """,(new_memeber,frappe.utils.now(),package_name))
        frappe.db.commit()
        return {"success":True,"package":package_name,"new_memeber":new_memeber}
    except Exception as e:
        frappe.db.rollback()
        frappe.log_error(title="Package tranfer Failed",message=f"Failed to transfer {package_name} to {new_memeber}",)
        raise
        
        