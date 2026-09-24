frappe.ui.form.on("MEMBER", {
    refresh(frm) {
        let is_manager = frappe.user.has_role("FIT Studio Manager");
        frm.set_df_property("phone", "hidden", is_manager ? 0 : 1);
    }
});