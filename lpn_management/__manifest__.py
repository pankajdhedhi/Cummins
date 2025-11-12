{
    "name": "LPN Management",
    "version": "16.0.1",
    "category": "Inventory",
    "summary": "Manage LPN Numbers with RFID, Category, Plant Location, and Child LPNs",
    "author": "Pankaj Dhedhi",
    "depends": ["base", "mail"],
    "data": [
        "security/ir.model.access.csv",
        "data/data.xml",
        #"data/email_template.xml",
        "views/lpn_master_views.xml",
        #"views/dispatched_order_views.xml",
        #"views/lpn_config_views.xml",
        "views/cycle_count_lpn_views.xml"
    ],
    "installable": True,
    "application": True,
}