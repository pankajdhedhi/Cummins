# -*- coding: utf-8 -*-
import base64
import pytz
from datetime import datetime
from dateutil.relativedelta import relativedelta
from odoo import http, fields, SUPERUSER_ID, _
from odoo.http import request
from odoo.exceptions import UserError, AccessError
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT


class Asset(http.Controller):

    

    @http.route([
        '''/asset/order/<model("order.order"):po_rec>/info'''
    ], type='json', auth='user', cors='*')
    def asset_order_detail(self, po_rec, **kw):
        try:
            rec = po_rec.get_order_details()
            return {'success': True,
                    'comments': 'Successful!',
                    'orders': rec}
        except Exception as e:
            return {'success': False,
                    'message': str(e)}

    @http.route('/order/order_master_list', type='json',  cors='*')
    def order_master(self, **kw):
        """
        This controller will return list of order_master_list data.
        :param kw: Pass extra params
        :return: Dict of equipment data.
        """
        order_master_list = request.env['order.order'].search_read([], ['id', 'name', 'order_datetime', 'state', 'reason'])
        return {
            'success': True,
            'comments': 'Successful!',
            'order_master_list': order_master_list,
        }

    @http.route('/asset/asset_master_list', type='json',  cors='*')
    def asset_master(self, **kw):
        """
        This controller will return list of asset_master_list data.
        :param kw: Pass extra params
        :return: Dict of equipment data.
        """
        asset_master_list = request.env['asset.management'].search_read([], ['id', 'name'])
        return {
            'success': True,
            'comments': 'Successful!',
            'asset_master_list': asset_master_list,
        }

    @http.route([
        '''/asset/order/<model("asset.order.line"):line_rec>/<string:state>'''
    ], type='json',  cors='*')
    def asset_line_start_end(self, line_rec, state, **kw):
        print(line_rec, state)
        try:
            if state == 'assign':
                line_rec.asset_id.action_start()
                return {'success': True,
                        'comments': 'Successful!',
                        'order_line': {'id': line_rec.id,
                                       }
                        }
            if state == 'inprogress':
                line_rec.asset_id.action_validate()
                return {'success': True,
                        'comments': 'Successful!',
                        'order_line': {'id': line_rec.id,
                                       }
                        }
        except Exception as e:
            return {'success': False,
                    'message': str(e)}

    @http.route('''/asset/order/line/<model('asset.order.line'):line_id>/save''', type='json',
                cors='*')
    def asset_order_line_save(self, line_id, **kw):

        if line_id:
            try:
                line_id.write(kw)
                return {'success': True,
                        'line_id': line_id.id,
                        'message': "Order Line is updated."}
            except Exception as e:
                return {'success': False,
                        'message': str(e)}
        return {'success': False,
                'message': 'Order Line Id is missing.'}

    @http.route('''/asset/<model('asset.management'):asset_id>/update''', type='json',
                cors='*')
    def asset_update(self, asset_id, **kw):

        if asset_id:
            try:
                asset_id.write(kw)
                return {'success': True,
                        'line_id': asset_id.id,
                        'message': "Asset Line is updated."}
            except Exception as e:
                return {'success': False,
                        'message': str(e)}
        return {'success': False,
                'message': 'Asset Line Id is missing.'}

