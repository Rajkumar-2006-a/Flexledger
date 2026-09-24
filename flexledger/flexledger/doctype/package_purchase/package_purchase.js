
frappe.ui.form.on("Package Purchase", {
    refresh(frm)
    {
        if (frm.doc.expirey_date < frappe.datetime.get_today())
        {
            frm.set_value("status","Expired")
        }
    }
});
