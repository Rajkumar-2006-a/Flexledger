frappe.ui.form.on("Attendee Entry", {
    member(frm, cdt, cdn) {
        let row = locals[cdt][cdn];
        console.log(row.member);
        frappe.db.get_value("Package Purchase", {member: row.member, status: "Active"}, ["name", "credits_remaining"])
            .then((r) => {console.log(r);
                if (!r.message.name) {
                    frappe.msgprint("No active package for this member");
                    return;
                }
                frappe.model.set_value(cdt, cdn, "package_purchase", r.message.name);
                frappe.model.set_value(cdt, cdn, "balance_display", r.message.credits_remaining);
            })
    }
})
frappe.ui.form.on("Class Session", {
    setup(frm) {
        frm.set_query("trainer", () => {
            return {filters: {
                    "status": "Active",
                    "specialization": frm.doc.session_type}
            }
        })
    },
    refresh(frm) {
    if (frm.doc.status === "Active") {
            frm.dashboard.add_indicator("Active", "green");
        }
        else if (frm.doc.status === "Pending") {
            frm.dashboard.add_indicator("Pending", "orange");
        }
        else if (frm.doc.status === "Expired") {
            frm.dashboard.add_indicator("Expired", "red");
        }
        else if (frm.doc.status === "Completed") {
            frm.dashboard.add_indicator("Completed", "blue");
        }
        if (frm.doc.status == "Scheduled" && frm.doc.session_date <= frappe.datetime.get_today()) {
            frm.add_custom_button("Finalize Session", () => {
                frm.set_value("status", "Completed");
                frm.save();
            })
        }
        if (frm.doc.status !== "Cancelled" && frm.doc.docstatus === 1) {
frm.add_custom_button("Cancel Session", function () {
        let d = new frappe.ui.Dialog({
            title: "Cancel Class Session",
            fields: [{
                fieldname: "reason",
                label: "Cancellation Reason",
                fieldtype: "Small Text",
                reqd: 1
            }],
            primary_action_label: "Confirm Cancellation",
            primary_action(values) {
                frappe.db
                    .set_value(frm.doctype, frm.docname, "cancellation_reason", values.reason)
                    .then(() => {
                        frappe.call({
                            method: "frappe.client.cancel",
                            args: { doctype: frm.doctype, name: frm.docname },
                            freeze: true,
                            callback: () => {
                                d.hide();
                                frm.reload_doc();
                            }
                        });
                    });
            }
            });
           d.show();
            });
            frm.add_custom_button("Swap Trainer", function() {
                frappe.prompt(
                    {
                        fieldname: "new_trainer",
                        label: "New Trainer",
                        fieldtype: "Link",
                        options: "TRAINER",
                        reqd: 1
                    },
                    function(values) {
                        frappe.confirm(
                        `Swap trainer to ${values.new_trainer}?`,
                        function() {
                        frappe.call({
                        method: "frappe.client.set_value",
                        args: {
                            doctype: "Class Session",
                            name: frm.doc.name,
                            fieldname: "trainer",
                            value: values.new_trainer
                            },
                            callback: function() {
                            frm.set_value("trainer", values.new_trainer);
                            frm.trigger("trainer");
                            frappe.msgprint("Trainer swapped successfully.");
                                    }
                                });
                            }
                        );
                    },
                    "Swap Trainer",
                    "Submit"
                );
            });
        }
    },

    trainer(frm) {
        console.log("trainer changed to", frm.doc.trainer);
    }
});