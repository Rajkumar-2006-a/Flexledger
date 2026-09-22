B2c-Dangerous Patters
Bug-1:
self.save() is inside validate .Save process call the validate ,then inside validate calling save will create a recursive calls ,wich creates error or duplicates
Bug-2:
A validate can be called multiple times until the doc is get submitted.So every draft save can double  or triple charge the package.
Corrected version:
def validate(self):
     self.total_charged=sum(r.credits_charged for r in self.attendees)
def on_submit(self):
    pkg = frappe.get_doc("Package Purchase", self.package_purchase)
    pkg.credits_used += self.total_charged
    pkg.save()
B2d-Concurrency
Every document has a modified timestamp when a user open a record ,the timestamp comes with it.
On save frappe checks the loaded modified value against the timestamp in the database.
If someone else saved in between that .Frappe throws error.