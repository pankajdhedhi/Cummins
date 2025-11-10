# -*- coding: utf-8 -*-

{
    'name': 'Restrict Concurrent User Login',
    'version': '16.0.1.0.0',
    'category': 'Extra Tools',
    'summary': """Ensures restricted concurrent sessions, enforces user force
    logout, and automates session expiry for enhanced security.""",
    'description': """This module ensures security by restricting concurrent
    user sessions and provides the option for forced logout. It includes
    automatic session expiry after a set duration, managing user logins
    efficiently.""",
    'author': 'TiMAD IT Solution',
    'company': 'TiMAD IT Solution',
    'maintainer': 'TiMAD IT Solution',
    'website': 'https://www.timadit.com',
    'data': [
        'data/ir_cron_data.xml',
        'views/res_users_views.xml',
        'views/login_clear_session_template.xml',
    ],
    'images': ['static/description/banner.jpg'],
    'license': 'LGPL-3',
    'installable': True,
    'auto_install': False,
    'application': False,
}
