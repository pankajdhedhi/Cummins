from odoo import models, fields, api, _
from datetime import datetime
from odoo.exceptions import UserError, ValidationError


class LpnMaster(models.Model):
    _name = "lpn.master"
    _description = "LPN Master"
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string="Master LPN", required=True, copy=False, index=True)
    rfid_code = fields.Char(string="RFID Code")
    subinventory_code = fields.Char(string="Subinventory Code")
    generation_date = fields.Datetime(string="Creation Date", default=lambda self: fields.Datetime.now())
    child_lpn_ids = fields.One2many("lpn.child", "parent_id", string="Child LPNs")
    max_qty = fields.Integer(string="Max Qty")
    physical_audit = fields.Boolean(string="Physical Audit")


class LpnChild(models.Model):
    _name = "lpn.child"
    _description = "Child LPN"

    parent_id = fields.Many2one("lpn.master", string="Parent LPN", ondelete="cascade")
    name = fields.Char(string="Child LPN", required=True)
    subinventory_code = fields.Char(string="Subinventory Code")
    turbo_qty = fields.Integer(string="Turbo Qty")
    tsn = fields.Char(string="TSN")
    turbo_item = fields.Char("Turbo Item")
    turbo_type = fields.Char(string="Turbo Type")


# class LpnCreateOrder(models.TransientModel):
#     _name = 'lpn.order.create'
#     _description = 'Create Order'
#
#     # Create Dispatch Order from LPN
#     def action_button_create_dispatch_order(self):
#         lpn_all = self.env[self._context.get('active_model')].browse(self._context.get('active_ids'))
#         dispatch_order_created = list(set(data.dispatch_order_created for data in lpn_all))
#         true_assets = lpn_all.filtered(lambda r: r.dispatch_order_created == True).sorted(key=lambda r: r.name)
#         if true_assets:
#             raise UserError(_(
#                 "You cannot create another dispatch order for the same LPN which an order has been created"
#             ))
#         no_rfid_lpn = lpn_all.filtered(lambda r: not r.rfid_code).sorted(key=lambda r: r.name)
#         if no_rfid_lpn:
#             lpn_names = ", ".join(no_rfid_lpn.mapped('name'))
#             raise UserError(_(
#                 "RFID code is required to create a order for LPN %r.", lpn_names
#             ))
#         plant_locations = list(set(data.plant_location_id.id for data in lpn_all))
#         if len(plant_locations) > 1:
#             raise UserError(_(
#                 "You cannot create a order with more then one plant locations"
#             ))
#         else:
#             order_line = []
#             for record in self._context.get('active_ids'):
#                 lpns = self.env[self._context.get('active_model')].browse(record)
#                 for lpn in lpns:
#                     order_line.append((0, 0, {
#                         'name': lpn.name,
#                         'rfid_code': lpn.rfid_code,
#                         'product_category_id': lpn.product_category_id.id,
#                         'plant_location_id': lpn.plant_location_id.id,
#                         'generation_date': lpn.generation_date,
#                         'lpn_id': lpn.id,
#                     }))
#                     lpn.dispatch_order_created = True
#
#             values = {
#                 'state': 'order_created',
#                 'dispatch_date': datetime.now(),
#                 'lpn_line_ids': order_line,
#                 'from_plant_id': plant_locations[0]
#             }
#             created_order_id = self.env["dispatched.order"].create(values)
#             return {
#                 'type': 'ir.actions.act_window',
#                 'res_model': 'dispatched.order',
#                 'view_type': 'form',
#                 'view_mode': 'form',
#                 'res_id': created_order_id.id,
#                 'target': 'current',
#             }
