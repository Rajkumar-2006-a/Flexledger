
frappe.ui.form.on("Package Purchase", {
	total_credits(frm)
    {
        frm.set_value("credits_used",0)

    },
    refresh(frm)
    {
        if (frm.doc.expirey_date < frappe.datetime.get_today())
        {
            frm.set_value("status","Expired")
        }
    }
});
