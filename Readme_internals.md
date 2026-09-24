## B2c-Dangerous Patters
Bug-1:
self.save() is inside validate .Save process call the validate ,then inside validate calling save will create a recursive calls ,wich creates error or duplicates

Bug-2:
A validate can be called multiple times until the doc is get submitted.So every draft save can double  or triple charge the package.
The validate will run on insert,save,submit
Corrected version:
def validate(self):
     self.total_charged=sum(r.credits_charged for r in self.attendees)
def on_submit(self):
    pkg = frappe.get_doc("Package Purchase", self.package_purchase)
    pkg.credits_used += self.total_charged
    pkg.save()


## B2d-Concurrency
Every document has a modified timestamp when a user open a record ,the timestamp comes with it.
On save frappe checks the loaded modified value against the timestamp in the database.
If someone else saved in between that .Frappe throws error.

## C3 — Attendee Entry & Package Purchase
It will automatically chnages.This happens because Frappe maintains Link-field references when a document is renamed. The linked Package Purchase records store the Member document's name, so when that name changes, Frappe updates the references to the new name.

## D2 — Row-Level Filtering & Data 
frappe.get_all is dangerous in a whitelisted method because a user with low permission can access the whitelisted method and use get_all.
The frappe.get_all ignore all permission and fetches the data,so it will create data breaches.

## E1-- the recursion pitfall
 Error Name:maximum recursion depth exceeded
slef.save() will trigger the on_update so calling self.save() inside it will cause a recursive calls.
## E2 --merge=Truue
Setting merge = True in Frappe combines duplicate incoming records into the existing 
document rather than rejecting them or throwing a duplicate key error.
## E3 — One Performance Judgment Call
frappe.db.get_value("Studio Settings", None, "default_cancellation_window_hours")
Because instead of loading the entire doc in the memory ,we can fecth the exact value using the frappe.db.get_value.
Calling frappe.get_doc repeatedly inside a loop compounds object instantiation and memory thrashing per iteration.

## I1
`f-string` version
threshold = frappe.form_dict.get("threshold")
query = f"""
    SELECT name, member, credits_remaining, expiry_date, status
    FROM `tabPackage Purchase`
    WHERE status = "Active" AND credits_remaining <= {threshold}
"""
frappe.db.sql(query)

Parameterized version
SELECT name, member, credits_remaining, expiry_date, status
FROM `tabPackage Purchase`
WHERE status = "Active" AND credits_remaining <= %(threshold)s

Safer Version

F-string puts the user’s input directly inside the SQL query, so the input can be treated as SQL code.
Parameterized queries send the input separately, so the database treats it only as a value, not as a command.
This prevents malicious input from changing or adding SQL commands to the query.
Therefore, always use parameterized queries to protect the database from SQL injection.

##k2 -N+1
sessions = frappe.get_all("Class Session", fields=["name", "trainer"])
trainers = frappe.get_all(
    "Trainer",
    filters={"name": ["in", [s.trainer for s in sessions]]},
    fields=["name", "phone"]
)
trainer_map = {t.name: t.phone for t in trainers}

for s in sessions:
    print(s.trainer, trainer_map.get(s.trainer))

## L1--CRUD with curl
 curl -X GET "http://127.0.0.1:8005/api/resource/MEMBER/MEM-2026-0001"   -H "Authorization: token 4304189c1986e0d:8463211bc802145"
{"data":{"name":"MEM-2026-0001","owner":"Administrator","creation":"2026-09-22 16:11:28.806409",
"modified":"2026-09-22 16:13:12.840256","modified_by":"Administrator","docstatus":0,
"idx":3,"member_name":"RAJ Kumar","phone":"6380532229","email":"rajkumar445912@gmail.com",
"join_date":"2026-09-22","status":"Active","user":"rajkumar445912@gmail.com","doctype":"MEMBER"}}

## N1
JavaScript executes entirely in the browser, which is fully under the end user's control. 
Hiding the phone field with frm.toggle_display() only changes what gets rendered on screen 
it has no effect on what the server sends over the wire. I proved this by hiding phone for 
non-Manager roles in the client script, then calling frappe.client.get_value("Member", "MEM-2026-0001", "phone")
 directly from the browser console while logged in as a non-Manager user — the phone number was 
returned anyway, because the server-side permission layer never restricted that field.
