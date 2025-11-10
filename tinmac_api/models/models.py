# -*- coding: utf-8 -*-

from cryptography.fernet import Fernet
import hashlib
from hashlib import sha256
from datetime import datetime, timedelta
from odoo import api, fields, models, tools, SUPERUSER_ID, _, Command
from odoo.exceptions import UserError, ValidationError


class res_users(models.Model):
    _inherit = 'res.users'
    
    def encrypt_string(self, hash_string):
        sha_signature = \
            hashlib.sha256(hash_string.encode()).hexdigest()
        return sha_signature
# hash_string = 'admin'
# sha_signature = encrypt_string(hash_string)
# print(sha_signature)
    def decrypt_password(self, password):
        key = "nsHhkPbOUf1CfDfvqKzyxcri6eIi3FOKxQFu_lpY4xw="
        # Instance the Fernet class with the key
        fernet = Fernet(key)
        password = fernet.decrypt(encMessage).decode()
        return [password]

    def validate_session_tinmac_messsage(self, session):
        now = datetime.now()
        session_obj = self.env['session.tinmac']
        print(session_obj)
        is_valid_session = session_obj.search([('user_id', '=', self.id), ('expired_time', '>=', now), ('session', '=', session)], limit = 1)
        print(is_valid_session,'is_valid_session')
        if not is_valid_session:
            return ["Invalid Session/Expired Session"]
        else:
            return ['Okay']
        
    def validate_session_tinmac(self, session):
        now = datetime.now()
        session_obj = self.env['session.tinmac']
        is_valid_session = session_obj.search([('user_id', '=', self.id), ('expired_time', '>=', now), ('session', '=', session)], limit = 1)
        if not is_valid_session:
            raise ValidationError("Invalid Session/Expired Session")
    
    def create_session_and_send_group(self, login, password):
        now = datetime.now()
        session = self.encrypt_string(str(login) + str(now))
        session_obj = self.env['session.tinmac']
        is_valid_session = session_obj.search([('user_id', '=', self.id), ('expired_time', '>=', now)], limit = 1)
        if is_valid_session and is_valid_session.session:
            is_valid_session.session = session
            is_valid_session.login_time = now
        else:
            session_obj.create({
                'session' : session,
                'user_id' : self.id,
                'login_time' : now,
                })
        group = ""
        if self.has_group('custom_asset_management.administrator_see_all_orders'):
            group = "Administrator : All Orders"
        elif self.has_group('custom_asset_management.technician_wise_orders'):
            group = "Orders : Technicians"
        elif self.has_group('custom_asset_management.group_local_finance'):
            group = "Local Finance"
        elif self.has_group('custom_asset_management.group_technician'):
            group = "Technicians"
        return {'session' : session, 'group' : group}
        

class session_tinmac(models.Model):
    _name = "session.tinmac"
    
    session = fields.Char(string="Session")
    user_id = fields.Many2one("res.users", string="Users")
    login_time = fields.Datetime(string="Time")
    expired_time = fields.Datetime(string="E Time", compute='calculate_expired_time', store=True)
    
    @api.depends('login_time')
    def calculate_expired_time(self):
        self.expired_time = self.login_time + timedelta(minutes=30)
        
    
class AssetAPI(models.Model):
    _inherit = 'order.order'

    def get_order_details(self, session):
        self.env.user.validate_session_tinmac(session)
        order_date_str = self.order_datetime.strftime('%Y-%m-%d %H:%M:%S') if self.order_datetime else ''
        technician_date_str = self.technician_datetime.strftime('%Y-%m-%d %H:%M:%S') if self.technician_datetime else ''
        order_lines = []
        for order_line in self.asset_ids:
            order_lines.append({
                'id': order_line.id,
                'asset_name': order_line.asset_code_id.name,
                'physical_verification_date': order_line.asset_code_id.physical_verification_date,
                'asset_code_new': order_line.asset_code_id.asset_code_new,
                'asset_category_id':order_line.asset_code_id.asset_category_id and order_line.asset_code_id.asset_category_id.id or '',
                'asset_category_name': order_line.asset_code_id.asset_category_id and order_line.asset_code_id.asset_category_id.sudo().name or '',
                'work_center_id': order_line.asset_code_id.work_center_id and order_line.asset_code_id.work_center_id.id or '',
                'work_center_name': order_line.asset_code_id.work_center_id and order_line.asset_code_id.work_center_id.sudo().name or '',
                'asset_id': order_line.asset_id and order_line.asset_id.id or '',
                'asset_code_id': order_line.asset_code_id and order_line.asset_code_id.id or '',
                'tag': order_line.tag and order_line.tag or '',
                'barcode': order_line.asset_code_id.barcode and order_line.asset_code_id.barcode or '',
                'actual_location': order_line.asset_code_id.actual_location and order_line.asset_code_id.actual_location or '',
                'inventory_count': order_line.inventory_count and order_line.inventory_count or '',
                'physical_count': order_line.physical_count and order_line.physical_count or '',
                'plant_id': order_line.plant_id and order_line.plant_id.id or '',
                'plant_name': order_line.plant_id and order_line.plant_id.sudo().name or '',
                'functional_location_id': order_line.functional_location_id and order_line.functional_location_id.id or '',
                'functional_location_name': order_line.functional_location_id and order_line.functional_location_id.sudo().name or '',
                'approved': order_line.approved and order_line.approved or '',
                'rejected': order_line.rejected and order_line.rejected or '',
                'remark': order_line.remark and order_line.remark or '',
                'geo_location': order_line.asset_code_id.geo_location and order_line.asset_code_id.geo_location or '',
                'po_no': order_line.asset_code_id.po_no and order_line.asset_code_id.po_no or '',
                'cost_center_descript': order_line.asset_code_id.cost_center_descript and order_line.asset_code_id.cost_center_descript or '',
                'gross_block': order_line.asset_code_id.gross_block and order_line.asset_code_id.gross_block or '',
                'vendor_id': order_line.asset_code_id.vendor_id and order_line.asset_code_id.vendor_id.id or '',
                'vendor_id_name': order_line.asset_code_id.vendor_id and order_line.asset_code_id.vendor_id.sudo().name or '',
                'profit_center': order_line.asset_code_id.profit_center and order_line.asset_code_id.profit_center or '',
                'profit_center_descript': order_line.asset_code_id.profit_center_descript and order_line.asset_code_id.profit_center_descript or '',
                'assignment_no': order_line.asset_code_id.assignment_no and order_line.asset_code_id.assignment_no or '',
                'cap_date': order_line.asset_code_id.cap_date and order_line.asset_code_id.cap_date or '',
                'description_1': order_line.asset_code_id.description_1 and order_line.asset_code_id.description_1 or '',
                'description_2': order_line.asset_code_id.description_2 and order_line.asset_code_id.description_2 or '',
                # 'functional_location_name': order_line.asset_code_id.functional_location_name and order_line.asset_code_id.functional_location_name or '',
                # 'asset_category_name': order_line.asset_code_id.asset_category_name and order_line.asset_code_id.asset_category_name or '',
                'inventory_no': order_line.asset_code_id.inventory_no and order_line.asset_code_id.inventory_no or '',
                'asset_allocation_id': order_line.asset_code_id.asset_allocation_id and order_line.asset_code_id.asset_allocation_id.id or '',
                'asset_allocation_name': order_line.asset_code_id.asset_allocation_id and order_line.asset_code_id.asset_allocation_id.sudo().name or '',
                'asset_code':order_line.asset_code_id.asset_code and order_line.asset_code_id.asset_code or '',
                'asset_description':order_line.asset_code_id.asset_description and order_line.asset_code_id.asset_description or '',
                'sr_no': order_line.asset_code_id.sr_no and order_line.asset_code_id.sr_no or '',
                "physical_counts": order_line.physical_count and order_line.physical_count or '',
                "phy_verification_date": order_line.physical_verification_date and order_line.physical_verification_date or ''
                })
        rec = {
            'order_name': self.name,
            'order_no': self.id,
            'order_date': order_date_str,
            'technician_id': self.technician_id and self.technician_id.id or '',
            'technician_name': self.technician_id and self.technician_id.sudo().name or '',
            'technician_datetime': technician_date_str,
            'state': self.state,
            'reason': self.reason and self.reason or '',
            'order_line': order_lines,
            "order_description": self.order_description and self.order_description or '',
            "created_by": self.create_uid and self.create_uid.sudo().name or '',
            "assigned_to": self.technician_id and self.technician_id.sudo().name or '',
            "approve_by": self.approval_id and self.approval_id.sudo().name or '',
            "cost_centers": self.work_center_ids and self.work_center_ids.ids or '',
            "plant_id": self.plant_id and self.plant_id.id or '',
            "plant_name": self.plant_id and self.plant_id.sudo().name or '',
            "reject": self.is_hide_reject and self.is_hide_reject
        }
        return rec
