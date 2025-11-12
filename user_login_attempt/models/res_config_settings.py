
from odoo import fields, models, api


class res_config_settings(models.TransientModel):
    _inherit = 'res.config.settings'

    login_failed_block_duration = fields.Integer(string="Account Block Duration", default=60, config_parameter="base.login_cooldown_duration")
    login_failed_attempt = fields.Integer(string="Failed Attempt", default=10, config_parameter="base.login_cooldown_after")
