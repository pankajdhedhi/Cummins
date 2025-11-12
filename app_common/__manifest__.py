# -*- coding: utf-8 -*-


{
    'name': "TiMAD Common Util and Tools",
    'version': '16.24.04.18',
    'author': 'timadit.com',
    'category': 'Base',
    'website': 'https://www.timadit.com',
    'live_test_url': 'https://demo.odooapp.cn',
    'license': 'LGPL-3',
    'sequence': 2,
    'price': 0.00,
    'currency': 'EUR',
    'images': ['static/description/banner.png'],
    'summary': '''
    Core for common use for timadit.com apps.
    
    ''',
    'description': '''
    need to setup odoo.conf, add follow:
    server_wide_modules = web,app_common
    1. Quick import data from excel with .py code
    2. Quick m2o default value
    3. Filter for useless field
    4. UTC local timezone convert
    5. Get browser ua, user-agent
    6. Image to local, image url to local, media to local attachment
    7. Log cron job
    8. Boost for less no use mail
    9. Customize .rng file
    10. Misc like get distance between two points
    11. Multi-language Support. Multi-Company Support
    12. Support Odoo 17,16,15,14,13,12, Enterprise and Community and odoo.sh Edition.
    13. Full Open Source.
    ==========
    5. Odoo 16,
    ''',
    'depends': [
        'mail',
        'web',
    ],
    'data': [
        'views/ir_cron_views.xml',
        # 'report/.xml',
    ],
    'qweb': [
        'static/src/xml/*.xml',
    ],
    'demo': [],
    # 'pre_init_hook': 'pre_init_hook',
    # 'post_init_hook': 'post_init_hook',
    # 'uninstall_hook': 'uninstall_hook',
    # 'external_dependencies': {'python': ['pyyaml', 'ua-parser', 'user-agents']},
    'installable': True,
    'application': True,
    'auto_install': True,
}
