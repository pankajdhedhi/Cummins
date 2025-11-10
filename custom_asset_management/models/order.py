# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
import datetime
from odoo.exceptions import UserError, ValidationError
DEFAULT_DATE_FORMAT = '%d/%m/%Y'


class Order(models.Model):
    _name = 'order.order'
    _description = 'Order'
    _rec_name = 'name'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    state = fields.Selection([
        ('order_created', 'Order Created'),
        ('assign', 'Assigned'),
        ('inprogress', 'Inprogress'),
        ('validate', 'Completed'),
        ('apporve', 'Approved'),
        ('close', 'Closed'),
        ('reject', 'Rejected')],
        string="Status", default="order_created", tracking=True)
    name = fields.Char(string="Order ID", required=True, copy=False, readonly=True, index=True,
                       default=lambda self: _('New'), tracking=True)
    order_description = fields.Text(string="Order Description")
    asset_ids = fields.One2many("asset.order.line", "asset_id")
    order_datetime = fields.Datetime(string="Order Date/Time", tracking=True)
    create_uid = fields.Many2one("res.users", string="Created By", tracking=True, default=lambda self: self.env.user)
    technician_id = fields.Many2one("res.users", string="Assigned To", tracking=True)
    assigned_datetime = fields.Datetime(string="Assigned Date/Time", tracking=True)
    approval_id = fields.Many2one("res.users", string="Approved By", tracking=True,
                                  domain=lambda self: [('groups_id', 'in', self.env.ref(
                                      'custom_asset_management.group_central_finance').id)])
    reason = fields.Text(string="Reject Reason", readonly=True, tracking=True)
    is_hide_reject = fields.Boolean(default=False, readonly=True)
    work_center_ids = fields.Many2many("asset.work.center", string="CTP LPN")
    plant_id = fields.Many2one("asset.plant", string="Plant")
    reject = fields.Boolean(string='Reject', default=False, store=True,
                            compute="_compute_reject_asset_ids")
    company_id = fields.Many2one('res.company', 'Company', default=lambda self: self.env.company)
    technician_datetime = fields.Datetime(string="Completed Date/Time", tracking=True)
    approval_datetime = fields.Datetime(string="Approved Date/Time", tracking=True)
    closed_user_id = fields.Many2one("res.users", string="Closed By", tracking=True)
    closed_datetime = fields.Datetime(string="Closed Date/Time", tracking=True)

    @api.onchange('asset_ids', 'asset_ids.asset_code_id')
    def _check_exist_assets_in_line(self):
        for asset in self:
            exist_asset_list = []
            for line in asset.asset_ids:
                if line.asset_code_id.id in exist_asset_list:
                    raise ValidationError(_('Asset should be one per line.'))
                exist_asset_list.append(line.asset_code_id.id)

    # Dashboard Filter Data
    def get_dashboard_filter_data(self, tech_user, plants, state, work_centers, period):
        is_local_finance = self.env.user.has_group('custom_asset_management.group_local_finance')
        is_central_finance = self.env.user.has_group('custom_asset_management.group_central_finance')
        filtered_data = {}
        domain = []
        js_domain = []
        assets_domain = []
        assets_js_domain = []
        #if tech_user:
        if is_central_finance:
            domain = []
            # js_domain += [['technician_id', '=', tech_user]]
        else:
            domain += [('technician_id', '=', self.env.user.id)]
            assets_domain += [('asset_allocation_id', '=', self.env.user.id)]

        sel_plant = ''
        sel_plant_str = ''
        if plants:
            if plants != 'Select Plant':
                domain += [('plant_id', '=', int(plants))]
                assets_domain += [('plant_id', '=', int(plants))]
                js_domain += [['plant_id', '=', int(plants)]]
                assets_js_domain += [['plant_id', '=', int(plants)]]
                plant_id = self.env['asset.plant'].search([('id', '=', int(plants))])
                sel_plant = plant_id.id
                sel_plant_str = plant_id.name
            else:
                sel_plant = 'Select Plant'
                sel_plant_str = 'Select Plant'
        
        if state:
            domain += [('state', '=', state)]
            js_domain += [['state', '=', state]]
        if work_centers:
            domain += [('work_center_ids', '=', int(work_centers))]
            js_domain += [['work_center_ids', '=', int(work_centers)]]
        sel_day = ''
        sel_day_str = ''
        
        if period:
            today = datetime.datetime.today()
            if period == '7_day':
                ago_date = today - datetime.timedelta(days=7)
                domain += [('order_datetime', '>=', ago_date)]
                js_domain += [['order_datetime', '>=', ago_date.strftime('%Y-%m-%d')]]
                assets_domain += [('create_date', '>=', ago_date)]
                assets_js_domain += [['create_date', '>=', ago_date.strftime('%Y-%m-%d')]]
                sel_day = '7_day'
                sel_day_str = 'Last 7 Days'
            elif period == '30_day':
                ago_date = today - datetime.timedelta(days=30)
                domain += [('order_datetime', '>=', ago_date)]
                js_domain += [['order_datetime', '>=', ago_date.strftime('%Y-%m-%d')]]
                assets_domain += [('create_date', '>=', ago_date)]
                assets_js_domain += [['create_date', '>=', ago_date.strftime('%Y-%m-%d')]]
                sel_day = '30_day'
                sel_day_str = 'Last 30 Days'
            elif period == '90_day':
                ago_date = today - datetime.timedelta(days=90)
                domain += [('order_datetime', '>=', ago_date)]
                js_domain += [['order_datetime', '>=', ago_date.strftime('%Y-%m-%d')]]
                assets_domain += [('create_date', '>=', ago_date)]
                assets_js_domain += [['create_date', '>=', ago_date.strftime('%Y-%m-%d')]]
                sel_day = '90_day'
                sel_day_str = 'Last 90 Days'
            elif period == '180_day':
                ago_date = today - datetime.timedelta(days=180)
                domain += [('order_datetime', '>=', ago_date)]
                js_domain += [['order_datetime', '>=', ago_date.strftime('%Y-%m-%d')]]
                assets_domain += [('create_date', '>=', ago_date)]
                assets_js_domain += [['create_date', '>=', ago_date.strftime('%Y-%m-%d')]]
                sel_day = '180_day'
                sel_day_str = 'Last 180 Days'
            elif period == '365_day':
                ago_date = today - datetime.timedelta(days=365)
                domain += [('order_datetime', '>=', ago_date)]
                js_domain += [['order_datetime', '>=', ago_date.strftime('%Y-%m-%d')]]
                assets_domain += [('create_date', '>=', ago_date)]
                assets_js_domain += [['create_date', '>=', ago_date.strftime('%Y-%m-%d')]]
                sel_day = '365_day'
                sel_day_str = 'Last 365 Days'
            elif period == '3_year':
                ago_date = today - datetime.timedelta(days=1095)
                domain += [('order_datetime', '>=', ago_date)]
                js_domain += [['order_datetime', '>=', ago_date.strftime('%Y-%m-%d')]]
                assets_domain += [('create_date', '>=', ago_date)]
                assets_js_domain += [['create_date', '>=', ago_date.strftime('%Y-%m-%d')]]
                sel_day = '3_year'
                sel_day_str = 'Last 3 Years'
            else:
                domain += [('order_datetime', '<=', today)]
                js_domain += [['order_datetime', '<=', today.strftime('%Y-%m-%d')]]
                assets_domain += [('create_date', '<=', today)]
                assets_js_domain += [['create_date', '<=', today.strftime('%Y-%m-%d')]]
                # domain += []
                # js_domain += []
                sel_day = 'Select Period'
                sel_day_str = 'Select Period'

        is_not_local_finance = not self.env.user.has_group('custom_asset_management.group_local_finance')
        users = {}
        user = self.env.user
        if not is_not_local_finance:
            user_ids = user
            users[user.id] = user.name
            domain += [('plant_id', 'in', user.plant_id.ids)]
            assets_domain += [('plant_id', 'in', user.plant_id.ids)]
        else:
            user_ids = self.env['res.users'].sudo().search([('share', '=', False)])
            for user_id in user_ids:
                users[user_id.id] = user_id.name

        order_ids = self.env['order.order'].sudo().search(domain)
        data = {}
        order = []
        order_count = []

        order_user_created = {}
        order_user_assign = {}
        order_user_inprogress = {}
        order_user_validate = {}
        order_user_apporve = {}
        order_user_close = {}
        order_user_reject = {}
        for user_id in user_ids:
            in_progress_count = order_created_count = apporve_count = 0
            close_count = validate_count = reject_count = assign_count = 0
            for order_id in order_ids.filtered(lambda o: o.state == 'order_created'):
                #if order_id.technician_id == user_id:
                    order_created_count += 1
            order_user_created[user_id.name] = order_created_count
            for order_id in order_ids.filtered(lambda o: o.state == 'assign'):
                #if order_id.technician_id == user_id:
                    assign_count += 1
            order_user_assign[user_id.name] = assign_count
            for order_id in order_ids.filtered(lambda o: o.state == 'inprogress'):
                #if order_id.technician_id == user_id:
                    in_progress_count += 1
            order_user_inprogress[user_id.name] = in_progress_count
            for order_id in order_ids.filtered(lambda o: o.state == 'validate'):
                #if order_id.technician_id == user_id:
                    validate_count += 1
            order_user_validate[user_id.name] = validate_count
            for order_id in order_ids.filtered(lambda o: o.state == 'apporve'):
                #if order_id.technician_id == user_id:
                    apporve_count += 1
            order_user_apporve[user_id.name] = apporve_count
            for order_id in order_ids.filtered(lambda o: o.state == 'close'):
                #if order_id.technician_id == user_id:
                    close_count += 1
            order_user_close[user_id.name] = close_count
            for order_id in order_ids.filtered(lambda o: o.state == 'reject'):
                #if order_id.technician_id == user_id:
                    reject_count += 1
            order_user_reject[user_id.name] = reject_count

        plants = {}
        plant_ids = self.env['asset.plant'].sudo().search([])
        plants['Select Plant'] = 'Select Plant'
        asset_total = self.env['asset.management'].sudo().search_count(assets_domain)
        verified_asset = self.env['asset.management'].sudo().search_count(assets_domain + [('physical_count', '>', 0)])
        pending_asset = self.env['asset.management'].sudo().search_count(assets_domain + [('physical_count', '<=', 0)])
        for plant_id in plant_ids:
            plants[plant_id.id] = plant_id.name
        work_centers = {}
        work_center_ids = self.env['asset.work.center'].sudo().search([])
        for work_center_id in work_center_ids:
            work_centers[work_center_id.id] = work_center_id.name

        for order_id in order_ids:
            if order_id.state == 'order_created':
                o_state = 'Order Created'
            elif order_id.state == 'assign':
                o_state = 'Assigned'
            elif order_id.state == 'inprogress':
                o_state = 'Inprogress'
            elif order_id.state == 'validate':
                o_state = 'Completed'
            elif order_id.state == 'apporve':
                o_state = 'Approved'
            elif order_id.state == 'close':
                o_state = 'Closed'
            elif order_id.state == 'reject':
                o_state = 'Rejected'
            else:
                o_state = ''
            work_center = ''
            if order_id.work_center_ids:
                for work_center_id in order_id.work_center_ids:
                    work_center += work_center_id.name + ' '
            order_data = {}
            order_count.append(order_id.id)
            order_data['id'] = order_id.id
            order_data['name'] = order_id.name
            order_data['work_center'] = work_center
            order_data['reason'] = order_id.reason
            order_data['plant_id'] = order_id.plant_id.name if order_id.plant_id.name else ""
            order_data['technician_id'] = order_id.technician_id.name if order_id.technician_id.name else ""
            order_data['order_datetime'] = order_id.order_datetime
            order_data['state'] = o_state
            order.append(order_data)
        filtered_data['order_ids'] = order
        filtered_data['order_total'] = len(order_ids)
        filtered_data['order_created'] = len(order_ids.filtered(lambda x: x.state == 'order_created'))
        filtered_data['order_assigned'] = len(order_ids.filtered(lambda x: x.state == 'assign'))
        filtered_data['order_inprocess'] = len(order_ids.filtered(lambda x: x.state == 'inprogress'))
        filtered_data['order_validate'] = len(order_ids.filtered(lambda x: x.state == 'validate'))
        filtered_data['order_apporve'] = len(order_ids.filtered(lambda x: x.state == 'apporve'))
        filtered_data['order_closed'] = len(order_ids.filtered(lambda x: x.state == 'close'))
        filtered_data['order_reject'] = len(order_ids.filtered(lambda x: x.state == 'reject'))
        filtered_data['users'] = users
        filtered_data['plants'] = plants
        filtered_data['work_centers'] = work_centers
        filtered_data['order_user_created'] = order_user_created
        filtered_data['order_user_assign'] = order_user_assign
        filtered_data['order_user_validate'] = order_user_validate
        filtered_data['order_user_inprogress'] = order_user_inprogress
        filtered_data['order_user_apporve'] = order_user_apporve
        filtered_data['order_user_close'] = order_user_close
        filtered_data['order_user_reject'] = order_user_reject
        filtered_data['is_not_local_finance'] = is_not_local_finance
        filtered_data['sel_day'] = sel_day
        filtered_data['sel_day_str'] = sel_day_str
        filtered_data['sel_plant'] = sel_plant
        filtered_data['sel_plant_str'] = sel_plant_str
        filtered_data['domain'] = domain
        filtered_data['asset_total'] = asset_total
        filtered_data['verified_asset'] = verified_asset
        filtered_data['pending_asset'] = asset_total - verified_asset
        filtered_data['js_domain'] = str(js_domain)[1:-1] if len(js_domain) >= 1 else str(js_domain)
        filtered_data['assets_js_domain'] = str(assets_js_domain)[1:-1] if len(assets_js_domain) >= 1 else str(assets_js_domain)
        return filtered_data

    # auto generate name
    @api.model
    def create(self, vals):
        if vals.get('name', _('New')) == _('New'):
            sequence = self.env['ir.sequence'].next_by_code('order.order.sequence') or _('New')
            year = str(datetime.date.today().year)[-2:]
            plant_id = self.env['asset.plant'].search([('id', '=', vals.get('plant_id'))])
            vals['name'] = 'PIO/'+plant_id.plant_code_name+'/'+str(year)+'/'+sequence
            vals['order_datetime'] = fields.datetime.now()
        if not vals.get('asset_ids'):
            raise UserError(_('Add at least one line in assets list.'))
        result = super(Order, self).create(vals)
        for order_line in result.asset_ids:
            order_line.asset_code_id.asset_order_created = True
        return result

    # def unlink(self):
    #     for record in self:
    #         print ("=====///////=====",record)
    #         if record.state != 'draft':
    #             raise UserError(_('You can not delete an order in progress.\nPlease reset to draft or cancel it first.'))
    #         else:
    #             super(Order, self).unlink()

    @api.depends('asset_ids', 'asset_ids.rejected')
    def _compute_reject_asset_ids(self):
        for rec in self:
            rec.reject = False
            if rec.asset_ids:
                reject = rec.asset_ids.filtered(lambda x: x.rejected == True)
                if reject:
                    rec.reject = True
                else:
                    rec.reject = False

    # Assign Technician
    def action_assign_technician(self):
        self.write({
            "state": "assign",
        })

    # Start order
    def action_start(self):
        self.write({
            "state": "inprogress",
        })
        return True

    def api_action_validate(self):
        self.write({
            "state": "validate",
            'technician_datetime': fields.datetime.now()
        })
        return True

    # Validate order
    def action_validate(self):
        if self.asset_ids:
            physical_count_zero = self.asset_ids.filtered(lambda x: x.physical_count == 0)
            if physical_count_zero:
                return {
                    'name': _('Confirmation'),
                    'type': 'ir.actions.act_window',
                    'view_mode': 'form',
                    'res_model': 'asset.order.message.wizard',
                    'target': 'new',
                    'context': {
                        'default_order_id': self.id,
                        'default_state': 'validate',
                        'default_message': _(
                            "There are assets with Physical Inventory Count “Zero”. Do you want to complete the order.",
                            )
                    }
                }
            else:
                return {
                    'name': _('Successful'),
                    'type': 'ir.actions.act_window',
                    'view_mode': 'form',
                    'res_model': 'asset.order.message.wizard',
                    'target': 'new',
                    'context': {
                        'default_order_id': self.id,
                        'default_state': 'apporve',
                        'default_message': _("Order %s has been completed successfully.", self.name)
                    }
                }

    def action_order_reject(self):
        reject_id = self.asset_ids.filtered(lambda o: o.rejected)
        if not reject_id:
            raise UserError(_(
                "Please select the record to reject the order"
            ))
        else:
            return {
                'name': _('Reject'),
                'type': 'ir.actions.act_window',
                'view_mode': 'form',
                'res_model': 'order.reject',
                'target': 'new',
                'context': {
                    'default_order_id': self.id,
                    'default_state': 'reject',
                    #'default_message': _("Order %s has been rejected successfully.", self.name)
                }
            }

# Please select the record to reject the order
    # %(action_reject_reason_wizard)d
    # Approve order
    def action_order_approve(self):
        count = 0
        approved_count = 0
        for rec in self.asset_ids:
            count += 1
            if rec.approved:
                rec.asset_code_id.write({'physical_count': rec.physical_count})
                approved_count += 1
            else:
                raise UserError(_(
                    "Order can be approved only when all line items are in the Approved state"
                ))
        if count == approved_count:
            if len(self.asset_ids) > 0:
                return {
                    'name': _('Successful'),
                    'type': 'ir.actions.act_window',
                    'view_mode': 'form',
                    'res_model': 'asset.order.message.wizard',
                    'target': 'new',
                    'context': {
                        'default_order_id': self.id,
                        'default_state': 'apporve',
                        'default_message': _("Order %s has been approved successfully.", self.name)
                    }
                }
        return None

    def action_order_close(self):
        return {
            'name': _('Successful'),
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'asset.order.message.wizard',
            'target': 'new',
            'context': {
                'default_order_id': self.id,
                'default_state': 'close',
                'default_message': _("Order %s has been closed successfully.", self.name)
            }
        }

    # Re-Start order
    def action_order_restart(self):
        self.write({
            "state": "inprogress",
        })


class OrderLine(models.Model):
    _name = 'asset.order.line'
    _description = 'Order Line'

    asset_id = fields.Many2one("order.order")
    asset_code_id = fields.Many2one("asset.management", string="Asset Description", required=True)
    tag = fields.Char(string="SAP Code", store=True)
    inventory_no = fields.Char(string="Barcode")
    asset_code_new = fields.Char(string="Asset Code", store=True)
    plant_id = fields.Many2one("asset.plant", string="Plant", store=True)
    work_center_id = fields.Many2one("asset.work.center", string="CTP LPN", store=True)
    functional_location_id = fields.Many2one("asset.functional.location", string="Current Location", store=True)
    inventory_count = fields.Integer(string="Inventory Count", store=True)
    physical_count = fields.Integer(string="Loading Count", store=True)
    physical_verification_date = fields.Date(string="Loading Date", store=True)
    rfid_tag = fields.Char(string="RFID Tag")
    approved = fields.Boolean(string="Approved", default=False, store=True)
    rejected = fields.Boolean(string="Rejected", default=False, store=True)
    remark = fields.Char(string="Remarks")
    state = fields.Selection([
        ('order_created', 'Order Created'),
        ('assign', 'Assigned'),
        ('inprogress', 'Inprogress'),
        ('validate', 'Completed'),
        ('apporve', 'Approved'),
        ('close', 'Closed'),
        ('reject', 'Rejected')],
        string="Status")

    @api.onchange('asset_code_id')
    def onchange_asset_code_id(self):
        self.inventory_no = self.asset_code_id.inventory_no
        self.asset_code_new = self.asset_code_id.asset_code_new
        self.tag = self.asset_code_id.tag
        self.work_center_id = self.asset_code_id.work_center_id
        self.functional_location_id = self.asset_code_id.functional_location_id
        self.inventory_count = self.asset_code_id.inventory_count

    def unlink(self):
        for record in self:
            record.asset_code_id.asset_order_created = False
            super(OrderLine, self).unlink()

    def write(self, vals):
        for order_line in self:
            order_line.asset_code_id.asset_order_created = True
        return super(OrderLine, self).write(vals)

    @api.model
    def create(self, vals):
        result = super(OrderLine, self).create(vals)
        result.asset_code_id.asset_order_created = True
        return result

    @api.onchange('rfid_tag')
    def onchange_rfid_tag(self):
        if self.rfid_tag:
            if self.physical_count and self.physical_verification_date:
                return {
                    'value': {'rfid_tag': False},
                    'warning': {
                        'title': _("Already Scanned"),
                        'message': _("Asset is already scanned"),
                        'type': 'notification',
                    }
                }

            elif self.rfid_tag == self.asset_code_id.barcode:
                self.physical_verification_date = fields.Date.context_today(self)
                self.physical_count = 1
                return {
                    'value': {'rfid_tag': False},
                    'warning': {
                        'title': _("Success"),
                        'message': _("RFID code scanned successfully."),
                        'type': 'notification',
                    }
                }

            else:
                return {
                    'value': {'rfid_tag': False},
                    'warning': {
                        'title': _("Invalid RFID"),
                        'message': _("Invalid RFID Tag"),
                        'type': 'notification',
                    }
                }

        return None

    # get physical_verification_date when edit physical count
    @api.onchange('physical_count')
    def get_physical_verification_date(self):
        if self.physical_count:
            self.physical_verification_date = datetime.datetime.today()

    @api.depends('asset_id.state')
    def set_access_for_fields(self):
        if self.env['res.users'].has_group(
                'custom_asset_management.group_central_finance_manager'):
            self.able_to_modify_fields = True
        # if self.asset_id.state == 'assign' and self.env['res.users'].has_group('custom_asset_management.group_local_finance'):
        #     self.able_to_modify_fields = True
        # elif self.asset_id.state == 'inprogress' and not self.env['res.users'].has_group('custom_asset_management.group_local_finance'):
        #     self.able_to_modify_fields = True
        # elif self.asset_id.state == 'close':
        #     self.able_to_modify_fields = True
        else:
            self.able_to_modify_fields = False

    able_to_modify_fields = fields.Boolean(compute=set_access_for_fields, string='Is user able to modify fields?')


class Technician(models.TransientModel):
    _name = 'order.technician'
    _description = 'Assign Technician'

    technician_id = fields.Many2one("res.users", string="Assign To", required=True,
                                    domain=lambda self: [('groups_id', 'in', self.env.ref(
                                        'custom_asset_management.group_local_finance').id)])
    approval_id = fields.Many2one("res.users", string="Approved By", required=True,
                                  domain=lambda self: [('groups_id', 'in', self.env.ref(
                                      'custom_asset_management.group_central_finance').id)])
    plant_id = fields.Many2one("asset.plant", string="Plant")

    # Assign Technician
    def assign_technician(self):
        order_obj = self.env['order.order']
        active_id = self.env.context['active_id']
        if active_id:
            order = order_obj.search([('id', '=', active_id)])
            if order:
                order.write({
                    "technician_id": self.technician_id.id,
                    "approval_id": self.approval_id.id,
                    "state": "assign",
                    "assigned_datetime": fields.datetime.now()
                })
                email_template = self.env.ref('custom_asset_management.to_send_mail_assign_order').id
                template = self.env['mail.template'].browse(email_template)
                email_to = self.technician_id.email
                email_values = {
                    'email_from': (', '.join(str(a.email) for a in self.env.user)),
                    'email_to': email_to,
                }
                mail_id = template.sudo().send_mail(order.id, email_values=email_values, force_send=True)

    # default gets the values on wizard
    @api.model
    def default_get(self, fields):
        rec = super(Technician, self).default_get(fields)
        order = self.env['order.order']
        if self.env.context.get('active_id'):
            order_id = order.browse(self.env.context['active_ids'])
            if order_id.plant_id:
                rec.update({
                    'plant_id': order_id.plant_id.id,
                })
                return rec
        return None

    # get plant wise technician
    @api.onchange('plant_id')
    def get_technician(self):
        for rec in self:
            if rec.plant_id:
                return {'domain': {'technician_id': [('plant_id', '=', rec.plant_id.ids)]}}
        return None


class Reason(models.TransientModel):
    _name = 'order.reject'
    _description = 'Reject Reason'

    reason = fields.Text(string="Reason", required=True)
    #message = fields.Text(required=True, readonly=True)
    order_id = fields.Many2one('order.order', string="Order ID")
    state = fields.Selection([
        ('order_created', 'Order Created'),
        ('assign', 'Assigned'),
        ('inprogress', 'Inprogress'),
        ('validate', 'Completed'),
        ('apporve', 'Approved'),
        ('close', 'Closed'),
        ('reject', 'Rejected')],
        string="State", default="order_created")

    # Reason
    def action_reject_reson(self):
        order_id = self.env['order.order'].browse(self.order_id.id)
        approved_ids = order_id.asset_ids.filtered(lambda o: o.approved)
        approved_ids.write({'state': 'apporve'})

        if order_id:
            for rec in order_id.asset_ids:
                if rec.rejected:
                    rec.physical_count = ''
                    rec.physical_verification_date = ''
                    rec.write({'rejected': True})
                    order_id.write({
                        "reason": self.reason,
                        "state": "reject",
                        "is_hide_reject": True,
                    })
        email_template = self.env.ref('custom_asset_management.to_send_mail_rejected_order').id
        template = self.env['mail.template'].browse(email_template)
        email_to = order_id.technician_id.email
        email_values = {
            'email_from': (', '.join(str(a.email) for a in self.env.user)),
            'email_to': email_to,
        }
        mail_id = template.sudo().send_mail(order_id.id, email_values=email_values, force_send=True)
        return {
            'name': _('Successful'),
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'asset.order.message.wizard',
            'target': 'new',
            'context': {
                'default_order_id': self.order_id.id,
                'default_state': 'reject',
                'default_message': _("Order %s has been rejected successfully.", self.order_id.name)
            }
        }
