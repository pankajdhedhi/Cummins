{
    'name': "User Login Attempts",
    'category': 'Productivity',
    'version': '16.0.1.0',
    'author': 'Pankaj',
    'description': """
        User Failed Login Attempt
    """,
    'summary': """users failed login attempt login failed attempt wrong password multiple time account security secure user account for login failure block account for failed login attempt login alert lock out prevent suspicious login attempts""",
    'depends': ['base_setup'],
    'data': [
        'views/res_config_settings_view.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': False,
}

