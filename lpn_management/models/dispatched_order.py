from odoo import models, fields, api, _
import datetime
from odoo.exceptions import UserError, ValidationError


class DispatchedOrder(models.Model):
    _name = "dispatched.order"
    _description = "Dispatched Order"
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string="Order ID", required=True, copy=False, readonly=True, index=True,
                       default=lambda self: _('New'), tracking=True)
    dispatch_date = fields.Datetime(string="Dispatch Date/Time", default=fields.Datetime.now)
    dispatch_desc = fields.Text(string="Dispatch Description")
    from_plant_id = fields.Many2one("plant.location", string="Plant From")
    to_plant_id = fields.Many2one("plant.location", string="Plant To")
    create_uid = fields.Many2one("res.users", string="Created By", tracking=True, default=lambda self: self.env.user)
    checked_datetime = fields.Datetime(string="Checked Date/Time", tracking=True)
    checked_uid = fields.Many2one("res.users", string="Checked By", tracking=True)
    state = fields.Selection([
        ('order_created', 'Order Created'),
        ('dispatched', 'Dispatched')],
        string="Status", default="order_created", tracking=True)
    lpn_line_ids = fields.One2many("dispatched.order.lpn", "order_id", string="Master LPN List")

    # auto generate name
    @api.model
    def create(self, vals):
        if vals.get('name', _('New')) == _('New'):
            sequence = self.env['ir.sequence'].next_by_code('dispatched.order.sequence') or _('New')
            year = str(datetime.date.today().year)[-2:]
            #plant_id = self.env['plant.location'].search([('id', '=', vals.get('from_plant_id'))])
            vals['name'] = 'DO/' + str(year) + '/' + sequence
            vals['dispatch_date'] = fields.datetime.now()
        if not vals.get('lpn_line_ids'):
            raise UserError(_('Add at least one line in Master LPN list.'))
        result = super(DispatchedOrder, self).create(vals)
        for order_line in result.lpn_line_ids:
            order_line.lpn_id.dispatch_order_created = True
        return result


class DispatchedOrderLpn(models.Model):
    _name = "dispatched.order.lpn"
    _description = "Dispatched Order LPN"

    order_id = fields.Many2one("dispatched.order", string="Dispatch Order", ondelete="cascade")
    lpn_id = fields.Many2one("lpn.master", string="Master LPN", required=True)
    name = fields.Char(string="LPN Number", copy=False, index=True)
    rfid_code = fields.Char(string="RFID Code")
    product_category_id = fields.Many2one("lpn.product.category", string="LPN Product Category")
    plant_location_id = fields.Many2one("plant.location", string="Plant Location")
    generation_date = fields.Date(string="Date of Generation")
    dispatched = fields.Boolean(string="Dispatched")
    remark = fields.Text(string="Remark")

    @api.onchange('dispatched')
    def _onchange_dispatched(self):
        if self.order_id:
            all_dispatched = all(line.dispatched for line in self.order_id.lpn_line_ids)
            if all_dispatched:
                self.order_id.state = 'dispatched'
            else:
                self.order_id.state = 'draft'
