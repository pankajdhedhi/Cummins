# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
from odoo.http import request


class Users(models.Model):
	_inherit = 'res.users'

	plant_id = fields.Many2many("asset.plant", string="Plant")
	force_reset_password = fields.Boolean(string="Force Password Reset", default=False)

	@api.model_create_multi
	def create(self, vals_list):
		users = super(Users, self).create(vals_list)
		users.force_reset_password = True
		if not users.has_group('base.group_user'):
			raise UserError(_('You must need to create Internal User only'))
		if not users.has_group('base.group_system'):
			if users.has_group('custom_asset_management.group_central_finance') and users.has_group('custom_asset_management.group_central_finance_manager'):
				raise UserError(_('You must need to assign only one Assets Role'))
			elif users.has_group('custom_asset_management.group_central_finance') and users.has_group('custom_asset_management.group_local_finance'):
				raise UserError(_('You must need to assign only one Assets Role'))
			elif users.has_group('custom_asset_management.group_central_finance') and users.has_group('custom_asset_management.group_central_finance_it_manager'):
				raise UserError(_('You must need to assign only one Assets Role'))
			elif users.has_group('custom_asset_management.group_central_finance_manager') and users.has_group('custom_asset_management.group_local_finance'):
				raise UserError(_('You must need to assign only one Assets Role'))
			elif users.has_group('custom_asset_management.group_central_finance_manager') and users.has_group('custom_asset_management.group_central_finance_it_manager'):
				raise UserError(_('You must need to assign only one Assets Role'))
			elif users.has_group('custom_asset_management.group_local_finance') and users.has_group('custom_asset_management.group_central_finance_it_manager'):
				raise UserError(_('You must need to assign only one Assets Role'))
		if not users.has_group('custom_asset_management.group_central_finance') and not users.has_group(
					'custom_asset_management.group_central_finance_manager') and not users.has_group(
					'custom_asset_management.group_local_finance') and not users.has_group(
					'custom_asset_management.group_central_finance_it_manager'):
			raise UserError(_('You must need to assign one Assets Role'))

		return users

	def write(self, values):
		res = super(Users, self).write(values)
		for rec in self:
			if not rec.has_group('base.group_user'):
				raise UserError(_('You must need to create Internal User only'))
			if not rec.has_group('base.group_system'):
				if rec.has_group('custom_asset_management.group_central_finance') and rec.has_group('custom_asset_management.group_central_finance_manager'):
					raise UserError(_('You must need to assign only one Assets Role'))
				elif rec.has_group('custom_asset_management.group_central_finance') and rec.has_group('custom_asset_management.group_local_finance'):
					raise UserError(_('You must need to assign only one Assets Role'))
				elif rec.has_group('custom_asset_management.group_central_finance') and rec.has_group('custom_asset_management.group_central_finance_it_manager'):
					raise UserError(_('You must need to assign only one Assets Role'))
				elif rec.has_group('custom_asset_management.group_central_finance_manager') and rec.has_group('custom_asset_management.group_local_finance'):
					raise UserError(_('You must need to assign only one Assets Role'))
				elif rec.has_group('custom_asset_management.group_central_finance_manager') and rec.has_group('custom_asset_management.group_central_finance_it_manager'):
					raise UserError(_('You must need to assign only one Assets Role'))
				elif rec.has_group('custom_asset_management.group_local_finance') and rec.has_group('custom_asset_management.group_central_finance_it_manager'):
					raise UserError(_('You must need to assign only one Assets Role'))
			if not rec.has_group('custom_asset_management.group_central_finance') and not rec.has_group(
					'custom_asset_management.group_central_finance_manager') and not rec.has_group(
					'custom_asset_management.group_local_finance') and not rec.has_group(
					'custom_asset_management.group_central_finance_it_manager'):
				raise UserError(_('You must need to assign one Assets Role'))
			if rec.login == 'admin' and 'password' in values:
				# Block all except self (admin) from changing their own password
				if self.env.uid != rec.id:
					raise UserError(_("You are not allowed to change the admin password."))
			if rec.id == 2 and self.env.uid != 2:
				raise UserError(_("You are not allowed to modify the Admin user."))
		return res

	def copy(self, default=None):
		if self.id == 2:
			raise UserError(_("You are not allowed to duplicate the admin user."))
		return super(Users, self).copy(default)
