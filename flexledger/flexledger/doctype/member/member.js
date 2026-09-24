frappe.ui.form.on("Member", {
    refresh(frm) {
        let is_manager = frappe.user.has_role("FIT Studio Manager");

        frm.toggle_display("phone", is_manager);
    }
});