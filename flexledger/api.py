import frappe
from frappe.query_builder import DocType
from frappe.utils import add_to_date, today, days_diff

@frappe.whitelist()
def get_low_balance_members(threshold):
    pp=frappe.qb.DocType("Package Purchase")
    query=(
          frappe.qb.from_(pp).select(pp.name,pp.member,pp.credits_remaining,pp.expirey_date)
           .where(pp.credits_remaining <= threshold )
           .where(pp.status =="Active").orderby(pp.credits_remaining )
           )
    result=query.run(as_dict=True)
    print(result)
    return result
    
@frappe.whitelist()
def transfer_package(package_name,new_member):
    try:
        doc=frappe.db.get_value("Package Purchase",package_name,["credits_used","status"],as_dict=True)
        if not doc:
            frappe.throw(f"Package {package_name} does not exists.")
        if doc.credits_used and doc.credits_used>0:
            frappe.throw(f"Cannot transfer {package_name} -credits already used")
        if not frappe.db.exists("MEMBER",new_member):
            frappe.throw(f"Member {new_member} does not exixts.")
        frappe.db.sql("""
                      UPDATE `tabPackage Purchase` SET member=%s,modified=%s
                      WHERE name=%s
                      """,(new_member,frappe.utils.now(),package_name))
        frappe.db.commit()
        return {"success":True,"package":package_name,"new_member":new_member}
    except Exception as e:
        frappe.db.rollback()
        frappe.log_error(title="Package tranfer Failed",message=f"Failed to transfer {package_name} to {new_member}",)
        raise
    
@frappe.whitelist()
def share_class_session(session_name, user_email):
    frappe.share.add(
        doctype="Class Session",
        name=session_name,
        user=user_email,
        read=1
    )  
    
    
def send_low_balance_email(member, remaining):
    member_doc = frappe.get_doc("MEMBER", member)

    frappe.sendmail(
        recipients=member_doc.email,
        subject="Low Balance Alert",
        message=f"""
            <p>Hi {member_doc.member_name},</p>
            <p>Your account balance is running low.</p>
            <p>
                <b>Remaining Balance:</b> {remaining}
            </p>
            <p>Please recharge your account to continue using the service.</p>
            <p>Thank you,<br>
            FlexLedger Team</p>
        """
    )



@frappe.whitelist()
def get_memebers():
    doc=frappe.db.get_all("MEMBER",fields=["*"])
    return doc

def after_install():
    details=[
        {'session_type_name':'1:1 Personal Training','credits_required':2},
        {'session_type_name':'Group HIIT','credits_required':1},
        {'session_type_name':'Yoga Flow','credits_required':1}
        ]
    for i in details:
        frappe.get_doc({'doctype': 'SESSION TYPE','session_type_name':i["session_type_name"],'credits_required':i["credits_required"]}).insert()
    frappe.get_doc({'doctype': 'STUDIO SETTINGS','manager_email':'rajkumar445912@gmail.com'}).insert()
    frappe.msgprint("Sucessfuly executed after install")
    

def check_expiring_packages():
    last = frappe.db.exists("Audit Log", {"action": "check_expiring_packages","date": today()})
    if last:
        return 
    docs = frappe.get_all("Package Purchase",filters={"status": "Active"},fields=["name", "member", "expiry_date"])
    for i in docs:
        days = date_diff(i.expiry_date, today())
        if 0 <= days<= 7:
            frappe.logger("flexledger").info(
                f"Package {i.name} for member {i.member} expires in {days} day(s)"
            )
    frappe.get_doc({"doctype": "Audit Log","doctype_name": "Package Purchase","document_name": "scheduler",
        "action": "check_expiring_packages","user": "Administrator","date": today()}).insert()
    
@frappe.whitelist()
def get_member_balance():
    member_id = frappe.form_dict.get("member_id")
    if not frappe.db.exists("MEMBER", member_id):
        frappe.local.response["http_status_code"] = 404
        return {"error": "Not found"}
    doc = frappe.db.get_value(
        "Package Purchase",
        {"member": member_id, "status": "Active"},
        ["credits_remaining", "expirey_date"],
        as_dict=True
    )
    if not doc:
        frappe.local.response["http_status_code"] = 404
        return {"error": "Not found"}
    return {
        "member": member_id,
        "credits_remaining": doc.credits_remaining,
        "expiry_date": doc.expiry_date
    }

def before_print(doc, method=None, print_settings=None):
    doc.print_summary = f"{doc.member} - {doc.total_credits} credits"