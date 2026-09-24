import frappe
import requests

def send_webhook(session_name):
    settings = frappe.get_single("Studio Settings")
    if not settings.webhook_url:
        return
    doc = frappe.get_doc("Class Session", session_name)
    payload = {
        "event": "session_completed",
        "session": doc.name,
        "attendees": len(doc.attendees)
    }
    try:
        r = requests.post(settings.webhook_url, json=payload, timeout=5)
        r.raise_for_status()
        frappe.logger("flexledger").info(f"Webhook sent successfully for {session_name}")
    except Exception as e:
        frappe.log_error(f"Webhook failed: {e}", "Webhook Error")