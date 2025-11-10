from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError


class LpnProductCategory(models.Model):
    _name = 'lpn.product.category'
    _description = 'Product Category'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string="Product Category")
    category_details = fields.Char(string="Product Category Details")


class PlantLocation(models.Model):
    _name = 'plant.location'
    _description = 'Plant Location'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string="Plant Code with Name")
    plant_code = fields.Char(string="Plant Code", required=True)
    plant_name = fields.Char(string="Plant Name", required=True)
    plant_address = fields.Char(string="Plant Address")

    # auto generate plant code
    @api.model
    def create(self, vals):
        if vals.get('plant_code') and vals.get('plant_name'):
            vals['name'] = f"[{vals.get('plant_code')}] {vals.get('plant_name')}"
        result = super(PlantLocation, self).create(vals)
        return result

    def write(self, vals):
        for record in self:
            plant_code = vals.get('plant_code') or record.plant_code
            plant_name = vals.get('plant_name') or record.plant_name
            if 'plant_code' in vals or 'plant_name' in vals:
                vals['name'] = f"[{plant_code}] {plant_name}"
        result = super(PlantLocation, self).write(vals)
        return result