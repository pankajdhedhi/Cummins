# -*- coding: utf-8 -*-
{
    'name': "Asset Management",

    'summary': """
        Asset Management""",

    'description': """
        Asset Management
    """,

    'author': "My Company",
    'website': "http://www.yourcompany.com",

    'category': 'Uncategorized',
    'version': '16.15.1',
    'sequence': 1,

    'depends': ['base', 'mail'],

    # always loaded
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'data/data.xml',
        'data/email_template.xml',
        'views/asset_views.xml',
        'views/plant_master_view.xml',
        'views/work_center_master_view.xml',
        'views/functional_location_master_view.xml',
        'views/technician_wizard_view.xml',
        'views/order_view.xml',
        'views/asset_validation_view.xml',
        'views/asset_category_view.xml',
        'views/report_order.xml',
        'views/res_users.xml',
        'views/templates.xml',
        'wizard/asset_order_massage_wizard_view.xml',
    ],
    'assets': {
            'web.assets_backend': [
                'custom_asset_management/static/src/xml/dashboard.xml',
                'custom_asset_management/static/src/js/dashboard.js',
                'custom_asset_management/static/src/css/dashboard.css',
            ],
        },
}
