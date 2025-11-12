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
        # group = ""
        # if self.has_group('lpn_management.administrator_see_all_orders'):
        #     group = "Administrator : All Orders"
        # elif self.has_group('lpn_management.technician_wise_orders'):
        #     group = "Orders : Technicians"
        # elif self.has_group('lpn_management.group_local_finance'):
        #     group = "Local Finance"
        # elif self.has_group('lpn_management.group_technician'):
        #     group = "Technicians"
        # return {'session' : session, 'group' : group}
        # return {'session_token' : session, 'plant_id': self.plant_id.id if self.plant_id else False}
        return {'session_token' : session}
        

class session_tinmac(models.Model):
    _name = "session.tinmac"
    
    session = fields.Char(string="Session")
    user_id = fields.Many2one("res.users", string="Users")
    login_time = fields.Datetime(string="Time")
    expired_time = fields.Datetime(string="E Time", compute='calculate_expired_time', store=True)
    
    @api.depends('login_time')
    def calculate_expired_time(self):
        self.expired_time = self.login_time + timedelta(minutes=30)
        
