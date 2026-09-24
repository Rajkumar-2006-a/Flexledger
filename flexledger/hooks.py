app_name = "flexledger"
app_title = "Flexledger"
app_publisher = "raj"
app_description = "A custom app that tracks session credits down to the last punch on the card"
app_email = "rajkumar445912@gmail.com"
app_license = "mit"

permission_query_conditions = {
    "Class Session": "flexledger.permission.session_query",
}
after_install = "flexledger.api.after_install"
doc_events = {
    "*": {
        "on_update": "flexledger.audit.log_change",
        "on_submit": "flexledger.audit.log_change",
        "on_cancel": "flexledger.audit.log_change",
    }
}
fixtures = [
    {
        "dt": "Role",
        "filters": [
            ["name", "in", ["FIT Front Desk", "FIT Trainer", "FIT Studio Manager"]]
        ]
    }
]
scheduler_events = {
    "daily": [
        "flexledger.api.check_expiring_packages"
    ]
}