# -*- coding: utf-8 -*-

{
    'name': "Background image in Login page",
    'version': '16.0.1.0',
    'summary': """Module helps to set background image in Login page.| Background image | image|Login | Login page|website|""",
    'description': """Module helps to set background image in Login page.""",
    'license': 'OPL-1',
    'website': "",
    'author': 'TiMAD IT Solution',
    'category': 'Tools',
    'depends': ['base', 'portal'],
    'data': [
        'views/res_company.xml',
    ],
    # 'assets': {
    #     'web.assets_frontend': [
    #         'tm_login_bg_img/static/src/css/bg_image.scss',
    #     ],
    # },
    'sequence': 1,
    "application": True,
    "installable": True
}
