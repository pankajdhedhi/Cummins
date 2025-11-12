from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError


class LpnCycleCount(models.Model):
    _name = "lpn.cycle.count"
    _description = "LPN Cycle Count"
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string="LPN Name", required=True, copy=False, index=True)
    rfid_code = fields.Char(string="RFID Code")
    # product_category_id = fields.Many2one("lpn.product.category", string="LPN Product Category")
    # plant_location_id = fields.Many2one("plant.location", string="Plant Location")
    generation_date = fields.Date(string="Date of Generation", default=fields.Date.context_today)

