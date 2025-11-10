# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from datetime import datetime
from odoo.exceptions import UserError, ValidationError
from odoo.tools.safe_eval import safe_eval, test_python_expr


class AssetManagement(models.Model):
	_name = 'asset.management'
	_description = 'Asset Master'
	_rec_name = 'name'
	_inherit = ['mail.thread']

	name = fields.Char(string='Asset Name', required=True, tracking=True)
	asset_description = fields.Text(string="Asset Description", tracking=True)
	asset_category_id = fields.Many2one('asset.category', string='Asset Category',
										required=True, change_default=True, tracking=True)
	tag = fields.Char(string="SAP Code", tracking=True)
	plant_id = fields.Many2one("asset.plant", string="Plant Code", tracking=True, required=True)
	plant_name = fields.Char(string='Plant Name', tracking=True)
	work_center_id = fields.Many2one("asset.work.center", string="LPN", tracking=True, required=True)
	functional_location_id = fields.Many2one("asset.functional.location", string="Current Location", tracking=True)
	actual_location = fields.Char(string="Actual Location", tracking=True)
	asset_code = fields.Char(string="Asset ID", copy=False, readonly=True, index=True, default=lambda self: _('New'),
							 tracking=True)
	barcode = fields.Char(string="RFID Code", tracking=True)
	asset_allocation_id = fields.Many2one('res.users', string="Asset Allocation", tracking=True)
	geo_location = fields.Char(string="Geo-Location", tracking=True)
	inventory_count = fields.Integer(string="Inventory Count", tracking=True, default=1)
	physical_count = fields.Integer(string="Loading Count", tracking=True, store=True, default=0)
	asset_code_new = fields.Char(string="Asset Code", tracking=True)
	physical_verification_date = fields.Date(string="Loading Date", tracking=True)
	sr_no = fields.Char(string="S No.")

	assignment_no = fields.Char(string="PM Equipment ID", tracking=True)
	description_1 = fields.Text(string="Description (Engg./PM)", tracking=True)
	description_2 = fields.Text(string="Description (QA)", tracking=True)
	po_no = fields.Char(string="PO No.(Inventory Note)", tracking=True)
	inventory_no = fields.Char(string="Barcode", tracking=True)
	cost_center_descript = fields.Char(string="Cost Center Descript", tracking=True)
	cap_date = fields.Date(string="CAP Date", tracking=True)
	vendor_id = fields.Many2one("res.partner", string="Party Details", tracking=True)
	gross_block = fields.Float(string="Gross Block", tracking=True)
	profit_center = fields.Char(string="Profit Center", tracking=True)
	profit_center_descript = fields.Char(string="Profit Center Descript", tracking=True)
	asset_category_name = fields.Char(string='Asset Category Name', tracking=True,
									  compute="_compute_asset_category_id", store=True)
	functional_location_name = fields.Char(string='Functional Location Name',
										   compute="_compute_functional_location_id", store=True, tracking=True)
	work_center_name = fields.Char(string='Work Center Name',
								   compute="_compute_work_center_id", store=True, tracking=True)
	asset_order_created = fields.Boolean(string="Order Created")
	rfid_code = fields.Char(string="RFID Code", tracking=True)
	is_local_finance_user = fields.Boolean(
		compute='_compute_is_local_finance_user',
		store=False
	)

	def _compute_is_local_finance_user(self):
		group = self.env.ref('custom_asset_management.group_local_finance', raise_if_not_found=False)
		for rec in self:
			rec.is_local_finance_user = group in self.env.user.groups_id if group else False

	def action_update_rfid_code(self):
		for res in self.search([]):
			if res.barcode:
				res.rfid_code = res.barcode

	@api.onchange('inventory_count')
	def onchange_inventory_count(self):
		self.inventory_count = 1
		if self.inventory_count <= 0:
			raise UserError(_(
				"The inventory count should be greater than ZERO"
			))

	@api.onchange('barcode')
	def onchange_barcode(self):
		if self.barcode:
			self.inventory_count = 1
			self.rfid_code = self.barcode

	@api.onchange('plant_id')
	def onchange_plant_id(self):
		if self.plant_id:
			self.plant_name = self.plant_id.plant_name

	# auto generate asset_code
	@api.model
	def create(self, vals):
		if vals.get('asset_code', _('New')) == _('New'):
			vals['asset_code'] = self.env['ir.sequence'].next_by_code('asset.management.sequence') or _('New')
		result = super(AssetManagement, self).create(vals)
		for res in self.search([('id', '!=', result.id)]):
			if res.barcode == result.barcode:
				raise ValidationError(_(
					"RFID code is duplicate"
				))
		return result

	def write(self, vals):
		if vals.get("barcode"):
			for res in self.search([('id', '!=', self.id)]):
				if res.barcode == vals.get("barcode"):
					raise ValidationError(_(
						"RFID code is duplicate"
					))
		return super(AssetManagement, self).write(vals)

	@api.depends('asset_category_id')
	def _compute_asset_category_id(self):
		for i in self:
			if i.asset_category_id:
				i.asset_category_name = i.asset_category_id.name

	@api.depends('functional_location_id')
	def _compute_functional_location_id(self):
		for i in self:
			if i.functional_location_id:
				i.functional_location_name = i.functional_location_id.name

	@api.depends('work_center_id')
	def _compute_work_center_id(self):
		for i in self:
			if i.work_center_id:
				i.work_center_name = i.work_center_id.name


class AssetPlant(models.Model):
	_name = 'asset.plant'
	_description = 'Asset Plant'

	name = fields.Char(string="Plant Code with Name")
	plant_code_name = fields.Char(string="Plant Code", required=True)
	plant_name = fields.Char(string="Plant Name", required=True)
	plant_address = fields.Char(string="Plant Address")

	# auto generate asset_code
	@api.model
	def create(self, vals):
		if vals.get('plant_code_name') and vals.get('plant_name'):
			vals['name'] = f"[{vals.get('plant_code_name')}] {vals.get('plant_name')}"
		result = super(AssetPlant, self).create(vals)
		return result

	def write(self, vals):
		for record in self:
			plant_code_name = vals.get('plant_code_name') or record.plant_code_name
			plant_name = vals.get('plant_name') or record.plant_name
			if 'plant_code_name' in vals or 'plant_name' in vals:
				vals['name'] = f"[{plant_code_name}] {plant_name}"
		result = super(AssetPlant, self).write(vals)
		return result


class AssetWorkCenter(models.Model):
	_name = 'asset.work.center'
	_description = 'Asset Work Center'

	name = fields.Char(string="Work Center Name")
	work_center_code = fields.Char(string="Work Center Code")
	work_center_detail = fields.Char(string="Work Center Details")


class AssetFunctionalLocation(models.Model):
	_name = 'asset.functional.location'
	_description = 'Asset Functional Location'

	name = fields.Char(string="Func. Location Name")
	fl_code = fields.Char(string="Func. Location Code")
	fl_detail = fields.Char(string="Func. Location Details")


class AssetCategory(models.Model):
	_name = 'asset.category'
	_description = 'Asset Category'

	name = fields.Char(string="Asset Category")
	category_details = fields.Char(string="Category Details")


class CreateOrder(models.TransientModel):
	_name = 'asset.order.create'
	_description = 'Create Order'

	# Create Order from asset
	def action_button_create_order(self):
		assets_all = self.env[self._context.get('active_model')].browse(self._context.get('active_ids'))
		plants = list(set(data.plant_id.id for data in assets_all))
		asset_order_created = list(set(data.asset_order_created for data in assets_all))
		true_assets = assets_all.filtered(lambda r: r.asset_order_created == True).sorted(key=lambda r: r.name)
		if true_assets:
			raise UserError(_(
				"You cannot create another order for the same asset which an order has been created"
			))
		no_rfid_assets = assets_all.filtered(lambda r: not r.barcode).sorted(key=lambda r: r.name)
		if no_rfid_assets:
			asset_names = ", ".join(no_rfid_assets.mapped('name'))
			raise UserError(_(
				"RFID code is required to create a order for asset %r.", asset_names
			))
		work_centers = list(set(data.work_center_id.id for data in assets_all))
		if len(plants) > 1:
			raise UserError(_(
				"You cannot create a order with more then one plant"
			))
		else:
			order_line = []
			for record in self._context.get('active_ids'):
				assets = self.env[self._context.get('active_model')].browse(record)
				for asset in assets:
					if not asset.work_center_id:
						raise UserError(_(
							"Cost center is required for asset %r.", asset.name
						))
					else:
						order_line.append((0, 0, {
							'asset_code_id': asset.id,
							'tag': asset.tag,
							'inventory_no': asset.inventory_no,
							'asset_code_new': asset.asset_code_new,
							'plant_id': asset.plant_id.id,
							'work_center_id': asset.work_center_id.id,
							'functional_location_id': asset.functional_location_id.id,
							'inventory_count': asset.inventory_count,
							'physical_count': asset.physical_count,
						}))
					asset.asset_order_created = True

			values = {
				'state': 'order_created',
				'order_datetime': datetime.now(),
				'asset_ids': order_line,
				'work_center_ids': [(6, 0, work_centers)],
				'plant_id': plants[0]
			}
			created_order_id = self.env["order.order"].create(values)
			return {
				'type': 'ir.actions.act_window',
				'res_model': 'order.order',
				'view_type': 'form',
				'view_mode': 'form',
				'res_id': created_order_id.id,
				'target': 'current',
			}
