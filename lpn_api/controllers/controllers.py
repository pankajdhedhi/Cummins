# -*- coding: utf-8 -*-
# import datetime
from datetime import datetime

from odoo import http
from odoo.http import request
import xmlrpc.client
import json
import logging
_logger = logging.getLogger(__name__)
url = "http://185.209.229.33:8069"
db = 'Cummins_Test'
# url = "http://localhost:8069"
# db = 'asset16gcp'
common = xmlrpc.client.ServerProxy('{}/xmlrpc/2/common'.format(url), allow_none=True)
models = xmlrpc.client.ServerProxy('{}/xmlrpc/2/object'.format(url), allow_none=True)
from cryptography.fernet import Fernet


# uid = common.authenticate(db, username, password, {})
# models.execute_kw(db, uid, password, 'res.partner', 'search', [[['is_company', '=', True]]])

def _auth_and_validate(username, password, session):
    uid = common.authenticate(db, username, password, {})
    if not uid:
        return None, {'success': False, 'message': 'Access Denied/user not found.'}
    # Validate session if provided
    if session is not None:
        msg = models.execute_kw(db, uid, password, 'res.users', 'validate_session_tinmac_messsage', [[uid], session])
        if msg and msg[0] != 'Okay':
            return None, {'success': False, 'message': str(msg[0])}
    return uid, None

def _get_existing_fields(uid, password, model, attributes=('string',)):
    # Returns a set of field names for the model so we can dynamically build domains safely
    fields = models.execute_kw(db, uid, password, model, 'fields_get', [], {'attributes': list(attributes)})
    return set(fields.keys())

def _build_or_domain(fields_present, candidates):
    """
    Build a domain like ['|','|', (field1,'op',val), (field2,'op',val), ...]
    Includes only fields that exist on the model.
    candidates: list of tuples (field, operator, value)
    """
    active_terms = [(f, op, val) for (f, op, val) in candidates if f in fields_present]
    if not active_terms:
        return []  # caller should handle and fallback (e.g., search by name)
    if len(active_terms) == 1:
        return [active_terms[0]]
    # chain ORs
    domain = []
    for i, term in enumerate(active_terms):
        if i == 0:
            continue
        domain.append('|')
    domain.extend(active_terms)
    return domain

class LPNManagementAPI(http.Controller):
   
    @http.route('/lpn/create_session', type='json', auth='public')
    def lpn_create_session(self, **kw):
        data = json.loads(request.httprequest.data)
        username = data.get('username')
        password = data.get('password')
        # password = str.encode(password)
        # password = self.decrypt_password(password)
        # password = password and password[0]
        uid = common.authenticate(db, username, password, {})
        print(uid)
        if uid:
            try:
                res = models.execute_kw(db, uid, password, 'res.users', 'create_session_and_send_group',
                                        [[uid], username, password])
                return {'success': True,
                        'comments': 'Successful!',
                        'data': res}
            except Exception as e:
                return {'success': False,
                        'message': str(e)}
        else:
            return {'success': False,
                    'message': 'Access Denied/user not found.'}
    
    @http.route('/lpn/api/master-lpn-list', type='json', auth='public', methods=['POST'])
    def get_master_lpn_list(self, **kwargs):
        """
        Get list of Master LPNs with pagination and search
        
        POST /lpn/api/master-lpn-list
        {
            "username": "admin",
            "password": "admin123",
            "user_id": 1,
            "session_token": "token_here",
            "limit": 20,
            "offset": 0,
            "search": "LPN001"
        }
        """
        try:
            data = json.loads(request.httprequest.data)
            username = data.get('username')
            password = data.get('password')
            session_token = data.get('session_token')
            limit = data.get('limit', 20)
            offset = data.get('offset', 0)
            search_query = data.get('search', '')

            # Authenticate
            try:
                uid = common.authenticate(db, username, password, {})
                if not uid:
                    return {'success': False, 'message': 'Invalid credentials'}
            except:
                return {'success': False, 'message': 'Authentication failed'}

            # Validate session
            message = models.execute_kw(
                db, uid, password, 'res.users', 'validate_session_tinmac_messsage',
                [[uid], session_token]
            )
            if message and message[0] != 'Okay':
                return {'success': False, 'message': str(message[0])}
            print("Authenticated UID:", uid)
            # Build search domain
            domain = []
            if search_query:
                domain = ['|', '|', '|',
                          ('name', 'ilike', search_query),
                          ('rfid_code', 'ilike', search_query),
                          ('subinventory_code', 'ilike', search_query)]
            print("Search Domain:", domain)
            logging.info(f"Search Domain: {domain}")

            # Get total count
            total_count = models.execute_kw(
                db, uid, password, 'lpn.master', 'search_count',
                [domain]
            )
            logging.info(f"Total Master LPN count: {total_count}")
            # Get paginated results
            master_lpn_ids = models.execute_kw(
                db, uid, password, 'lpn.master', 'search',
                [domain], {'offset': offset, 'limit': limit, 'order': 'name desc'}
            )
            logging.info(f"Master LPN IDs: {master_lpn_ids}")

            # Read data with all fields
            master_lpns = models.execute_kw(
                db, uid, password, 'lpn.master', 'read',
                [master_lpn_ids, ['name', 'rfid_code', 'subinventory_code', 'generation_date', 'physical_audit', 'max_qty']]
            )
            logging.info(f"Master LPN Data: {master_lpns}")
            # Get child LPN counts
            lpn_list = []
            for lpn in master_lpns:
                child_count = models.execute_kw(
                    db, uid, password, 'lpn.child', 'search_count',
                    [[('parent_id', '=', lpn['id'])]]
                )
                logging.info(f"Master LPN ID {lpn['id']} has {child_count} child LPNs.")
                lpn_list.append({
                    'id': lpn['id'],
                    'name': lpn['name'],
                    'rfid_code': lpn['rfid_code'],
                    'subinventory_code': lpn['subinventory_code'],
                    'generation_date': lpn.get('generation_date'),
                    'physical_audit': lpn.get('physical_audit', False),
                    'max_qty': lpn.get('max_qty', 0),
                    'child_count': child_count,
                })


            return {
                'success': True,
                'comments': 'Successful!',
                'master_lpn_list': lpn_list,
                'pagination': {
                    'total_count': total_count,
                    'limit': limit,
                    'offset': offset,
                    'has_more': (offset + limit) < total_count,
                    'page': (offset // limit) + 1,
                    'total_pages': (total_count + limit - 1) // limit
                }
            }
        except Exception as e:
            _logger.error(f"Get master LPN list error: {str(e)}")
            return {
                'success': False,
                'message': f'Error: {str(e)}'
            }

    @http.route('/lpn/api/master-lpn-detail', type='json', auth='public', methods=['POST'])
    def get_master_lpn_detail(self, **kwargs):
        """
        Get detailed view of Master LPN with all Child LPNs
        
        POST /lpn/api/master-lpn-detail
        {
            "username": "admin",
            "password": "admin123",
            "user_id": 1,
            "session_token": "token_here",
            "master_id": 1
        }
        """
        try:
            data = json.loads(request.httprequest.data)
            username = data.get('username')
            password = data.get('password')
           
            session_token = data.get('session_token')
            master_id = data.get('master_id')

            # Authenticate
            try:
                uid = common.authenticate(db, username, password, {})
                if not uid:
                    return {'success': False, 'message': 'Invalid credentials'}
            except:
                return {'success': False, 'message': 'Authentication failed'}

            # Validate session
            message = models.execute_kw(
                db, uid, password, 'res.users', 'validate_session_tinmac_messsage',
                [[uid], session_token]
            )
            if message and message[0] != 'Okay':
                return {'success': False, 'message': str(message[0])}

            # Get master LPN
            master_lpn_data = models.execute_kw(
                db, uid, password, 'lpn.master', 'read',
                [master_id, ['name', 'rfid_code', 'subinventory_code', 'generation_date', 'physical_audit', 'max_qty', 'child_lpn_ids']]
            )

            if not master_lpn_data:
                return {
                    'success': False,
                    'message': 'Master LPN not found'
                }

            master_lpn = master_lpn_data[0]
            print(master_lpn)

            # Get child LPNs
            child_lpn_list = []
            if master_lpn.get('child_lpn_ids'):
                child_lpns_data = models.execute_kw(
                    db, uid, password, 'lpn.child', 'read',
                    [master_lpn['child_lpn_ids'], ['name', 'tsn', 'turbo_qty', 'turbo_item', 'turbo_type', 'subinventory_code']]
                )
                print(child_lpns_data)

                for child_lpn in child_lpns_data:
                    child_lpn_list.append({
                        'id': child_lpn['id'],
                        'name': child_lpn['name'],
                        'tsn': child_lpn.get('tsn'),
                        'turbo_qty': child_lpn.get('turbo_qty', 0),
                        'turbo_item': child_lpn.get('turbo_item'),
                        'turbo_type': child_lpn.get('turbo_type'),
                        'subinventory_code': child_lpn.get('subinventory_code'),
                    })

            return {
                'success': True,
                'message': 'Master LPN detail fetched',
                'data': {
                    'id': master_lpn['id'],
                    'name': master_lpn['name'],
                    'rfid_code': master_lpn['rfid_code'],
                    'subinventory_code': master_lpn['subinventory_code'],
                    'generation_date': master_lpn.get('generation_date'),
                    'physical_audit': master_lpn.get('physical_audit', False),
                    'max_qty': master_lpn.get('max_qty', 0),
                    'child_count': len(child_lpn_list),
                    'child_lpns': child_lpn_list
                }
            }
        except Exception as e:
            _logger.error(f"Get master LPN detail error: {str(e)}")
            return {
                'success': False,
                'message': f'Error: {str(e)}'
            }

    # ==================== CHILD LPN ====================

    @http.route('/lpn/api/child-lpn-list', type='json', auth='public', methods=['POST'])
    def get_child_lpn_list(self, **kwargs):
        """
        Get list of Child LPNs with pagination and search
        
        POST /lpn/api/child-lpn-list
        {
            "username": "admin",
            "password": "admin123",
            "user_id": 1,
            "session_token": "token_here",
            "limit": 20,
            "offset": 0,
            "search": "TSN001",
            "parent_id": 1
        }
        """
        try:
            data = json.loads(request.httprequest.data)
            username = data.get('username')
            password = data.get('password')

            session_token = data.get('session_token')
            limit = data.get('limit', 20)
            offset = data.get('offset', 0)
            search_query = data.get('search', '')
            parent_id = data.get('parent_id')

            # Authenticate
            try:
                uid = common.authenticate(db, username, password, {})
                if not uid:
                    return {'success': False, 'message': 'Invalid credentials'}
            except:
                return {'success': False, 'message': 'Authentication failed'}

            # Validate session
            message = models.execute_kw(
                db, uid, password, 'res.users', 'validate_session_tinmac_messsage',
                [[uid], session_token]
            )
            if message and message[0] != 'Okay':
                return {'success': False, 'message': str(message[0])}

            # Build search domain
            domain = []
            if parent_id:
                domain.append(('parent_id', '=', parent_id))

            if search_query:
                domain.append(['|', '|',
                    ('name', 'ilike', search_query),
                    ('tsn', 'ilike', search_query),
                    ('turbo_item', 'ilike', search_query)
                ])

            # Get total count
            total_count = models.execute_kw(
                db, uid, password, 'lpn.child', 'search_count',
                [domain]
            )

            # Get paginated results
            child_lpn_ids = models.execute_kw(
                db, uid, password, 'lpn.child', 'search',
                [domain], {'offset': offset, 'limit': limit, 'order': 'tsn'}
            )

            # Read data
            child_lpns = models.execute_kw(
                db, uid, password, 'lpn.child', 'read',
                [child_lpn_ids, ['name', 'parent_id', 'tsn', 'turbo_qty', 'turbo_item', 'turbo_type', 'subinventory_code']]
            )

            lpn_list = []
            for lpn in child_lpns:
                lpn_list.append({
                    'id': lpn['id'],
                    'name': lpn['name'],
                    'parent_id': lpn['parent_id'][0] if lpn.get('parent_id') else None,
                    'parent_name': lpn['parent_id'][1] if lpn.get('parent_id') else '',
                    'tsn': lpn.get('tsn'),
                    'turbo_qty': lpn.get('turbo_qty', 0),
                    'turbo_item': lpn.get('turbo_item'),
                    'turbo_type': lpn.get('turbo_type'),
                    'subinventory_code': lpn.get('subinventory_code'),
                })

            return {
                'success': True,
                'comments': 'Successful!',
                'child_lpn_list': lpn_list,
                'pagination': {
                    'total_count': total_count,
                    'limit': limit,
                    'offset': offset,
                    'has_more': (offset + limit) < total_count,
                    'page': (offset // limit) + 1,
                    'total_pages': (total_count + limit - 1) // limit
                }
            }
        except Exception as e:
            _logger.error(f"Get child LPN list error: {str(e)}")
            return {
                'success': False,
                'message': f'Error: {str(e)}'
            }

    # ==================== PHYSICAL AUDIT ====================

    @http.route('/lpn/api/audit/scan-master', type='json', auth='public', methods=['POST'])
    def audit_scan_master_lpn(self, **kwargs):
        try:
            data = json.loads(request.httprequest.data)  # ✅ Correct way to get parsed JSON
            username = data.get('username')
            password = data.get('password')
            session_token = data.get('session_token')
            rfid_code = data.get('rfid_code')

            if isinstance(rfid_code, dict):  # ✅ Handle malformed input
                rfid_code = rfid_code.get('rfid_code')

            if not rfid_code:
                return {'success': False, 'message': 'RFID code is required'}

            # Authenticate
            uid = common.authenticate(db, username, password, {})
            if not uid:
                return {'success': False, 'message': 'Invalid credentials'}

            # Validate session
            message = models.execute_kw(
                db, uid, password, 'res.users', 'validate_session_tinmac_messsage',
                [[uid], session_token]
            )
            if message and message[0] != 'Okay':
                return {'success': False, 'message': str(message[0])}

            # Search Master LPN by RFID
            _logger.info(f"🔍 Searching Master LPN with RFID: {rfid_code}")
            master_lpn_ids = models.execute_kw(
                db, uid, password, 'lpn.master', 'search',
                [[('rfid_code', '=', rfid_code)]],  # ✅ Correctly structured domain
                {'limit': 1}
            )
            logging.info(f"Master LPN IDs found: {master_lpn_ids}")

            if not master_lpn_ids:
                return {'success': False, 'message': 'Master LPN not found'}

            master_lpn_data = models.execute_kw(
            db, uid, password, 'lpn.master', 'read',
            [master_lpn_ids],
            {'fields': ['name', 'rfid_code', 'child_lpn_ids', 'physical_audit']}  # ✅ Always use dict for 'read'
        )
            logging.info(f"Master LPN Data: {master_lpn_data}")
            master_lpn = master_lpn_data[0]

            # Fetch child LPNs
            tsn_list = []

            if master_lpn.get('child_lpn_ids'):
                child_lpns_data = models.execute_kw(
                    db, uid, password, 'lpn.child', 'read',
                    [master_lpn['child_lpn_ids']],
                    {'fields': ['id', 'tsn', 'turbo_item', 'turbo_type']}  # ✅ FIXED
                )
                logging.info(f"Child LPNs Data: {child_lpns_data}")
                tsn_list = [{
                    'id': c['id'],
                    'tsn': c.get('tsn'),
                    'turbo_item': c.get('turbo_item'),
                    'turbo_type': c.get('turbo_type'),
                    'is_scanned': False
                } for c in child_lpns_data]

            logging.info(f"TSN List: {tsn_list}")

            # Create audit log
            # audit_log_id = models.execute_kw(
            #     db, uid, password, 'lpn.audit.log', 'create', [{
            #         'master_lpn_id': master_lpn['id'],
            #         'total_tsn': len(tsn_list),
            #         'scanned_tsn': 0,
            #         'audit_status': 'in_progress',
            #     }]
            # )
            # logging.info(f"Audit Log ID: {audit_log_id}")

            return {
                'success': True,
                'comments': 'Master LPN found',
                'data': {
                    # 'audit_id': audit_log_id,
                    'master_id': master_lpn['id'],
                    'master_name': master_lpn['name'],
                    'rfid_code': master_lpn['rfid_code'],
                    'tsn_list': tsn_list,
                    'total_tsn': len(tsn_list),
                    'physical_audit': master_lpn['physical_audit']
                }
            }

        except Exception as e:
            _logger.error(f"Audit scan master error: {str(e)}")
            return {'success': False, 'message': f'Error: {str(e)}'}

    @http.route('/lpn/api/audit/scan-tsn', type='json', auth='public', methods=['POST'])
    def audit_scan_tsn(self, **kwargs):
        """
        Scan TSN barcode on turbo
        """
        try:
            data = json.loads(request.httprequest.data)
            username = data.get('username')
            password = data.get('password')
            session_token = data.get('session_token')
            master_id = data.get('master_id')
            tsn_barcode = data.get('tsn_barcode')

            # Authenticate User
            try:
                uid = common.authenticate(db, username, password, {})
                if not uid:
                    return {'success': False, 'message': 'Invalid credentials'}
            except:
                return {'success': False, 'message': 'Authentication failed'}

            # Validate Session Token
            message = models.execute_kw(
                db, uid, password,
                'res.users', 'validate_session_tinmac_messsage',
                [[uid], session_token]
            )

            if message and message[0] != 'Okay':
                return {'success': False, 'message': str(message[0])}

            if not master_id or not tsn_barcode:
                return {'success': False, 'message': 'Master ID and TSN barcode are required'}

            # Fetch Master LPN
            master_lpn_data = models.execute_kw(
                db, uid, password, 'lpn.master', 'read',
                [[master_id]],  # must be list of IDs
                {'fields': ['name', 'rfid_code', 'child_lpn_ids']}
            )

            if not master_lpn_data:
                return {'success': False, 'message': 'Master LPN not found'}

            master_lpn = master_lpn_data[0]

            # Fetch Child LPNs
            tsn_list = []
            scanned_count = 0
            found_tsn = None

            if master_lpn.get('child_lpn_ids'):
                child_lpns_data = models.execute_kw(
                    db, uid, password, 'lpn.child', 'read',
                    [master_lpn['child_lpn_ids']],
                    {'fields': ['id', 'tsn', 'turbo_item', 'turbo_type']}
                )

                for child_lpn in child_lpns_data:
                    is_this_scanned = (child_lpn.get('tsn') == tsn_barcode)
                    if is_this_scanned:
                        found_tsn = child_lpn

                    tsn_list.append({
                        'id': child_lpn['id'],
                        'tsn': child_lpn.get('tsn'),
                        'turbo_item': child_lpn.get('turbo_item'),
                        'turbo_type': child_lpn.get('turbo_type'),
                        'is_scanned': is_this_scanned
                    })

                    if is_this_scanned:
                        scanned_count += 1

            if not found_tsn:
                return {'success': False, 'message': 'TSN not found in this Master LPN'}

            all_scanned = (scanned_count == len(tsn_list))

            return {
                'success': True,
                'comments': 'TSN scanned successfully',
                'data': {
                    'master_id': master_lpn['id'],
                    'scanned_tsn': found_tsn.get('tsn'),
                    'tsn_list': tsn_list,
                    'scanned_count': scanned_count,
                    'total_count': len(tsn_list),
                    'all_scanned': all_scanned
                }
            }

        except Exception as e:
            _logger.error(f"Audit scan TSN error: {str(e)}")
            return {'success': False, 'message': f'Error: {str(e)}'}

    @http.route('/lpn/api/audit/complete', type='json', auth='public', methods=['POST'])
    def audit_complete(self, **kwargs):
        try:
            data = json.loads(request.httprequest.data)
            username = data.get('username')
            password = data.get('password')
            session_token = data.get('session_token')
            master_id = data.get('master_id')

            # Authenticate
            try:
                uid = common.authenticate(db, username, password, {})
                if not uid:
                    return {'success': False, 'message': 'Invalid credentials'}
            except:
                return {'success': False, 'message': 'Authentication failed'}

            # Validate session
            message = models.execute_kw(
                db, uid, password, 'res.users', 'validate_session_tinmac_messsage',
                [[uid], session_token]
            )
            if message and message[0] != 'Okay':
                return {'success': False, 'message': str(message[0])}

            if not master_id:
                return {'success': False, 'message': 'Master ID required'}

            # ✅ Correct read() usage
            master_lpn_data = models.execute_kw(
                db, uid, password, 'lpn.master', 'read',
                [[master_id]],
                {'fields': ['name', 'child_lpn_ids']}
            )

            if not master_lpn_data:
                return {'success': False, 'message': 'Master LPN not found'}

            master_lpn = master_lpn_data[0]

            # ✅ Correct write() usage
            models.execute_kw(
                db, uid, password, 'lpn.master', 'write',
                [[master_id], {'physical_audit': True}]
            )

            return {
                'success': True,
                'comments': 'Physical Audit is successful',
                'data': {
                    'master_id': master_lpn['id'],
                    'master_name': master_lpn['name'],
                    'audit_status': 'Completed',
                    'audit_date': datetime.now().isoformat()
                }
            }

        except Exception as e:
            _logger.error(f"Audit complete error: {str(e)}")
            return {'success': False, 'message': f'Error: {str(e)}'}

    # ==================== CYCLE COUNT ====================

    @http.route('/lpn/api/cycle-count/start', type='json', auth='public', methods=['POST'])
    def cycle_count_start(self, **kwargs):
        """
        Start a new cycle count session
        
        POST /lpn/api/cycle-count/start
        {
            "username": "admin",
            "password": "admin123",
            "user_id": 1,
            "session_token": "token_here",
            "plant_location_id": 1,
            "count_date": "2024-01-15"
        }
        """
        try:
            data = json.loads(request.httprequest.data)
            username = data.get('username')
            password = data.get('password')
            user_id = data.get('user_id')
            session_token = data.get('session_token')
            plant_location_id = data.get('plant_location_id')
            count_date = data.get('count_date', datetime.now().date().isoformat())

            # Authenticate
            try:
                uid = common.authenticate(db, username, password, {})
                if not uid:
                    return {'success': False, 'message': 'Invalid credentials'}
            except:
                return {'success': False, 'message': 'Authentication failed'}

            # Validate session
            message = models.execute_kw(
                db, uid, password, 'res.users', 'validate_session_tinmac_messsage',
                [[uid], session_token]
            )
            if message and message[0] != 'Okay':
                return {'success': False, 'message': str(message[0])}

            # Create cycle count record
            cycle_count_name = f"CC-{datetime.now().strftime('%Y%m%d%H%M%S')}"
            cycle_count_id = models.execute_kw(
                db, uid, password, 'lpn.cycle.count', 'create', [{
                    'name': cycle_count_name,
                    'plant_location_id': plant_location_id,
                    'generation_date': count_date,
                }]
            )

            return {
                'success': True,
                'comments': 'Cycle count session started',
                'data': {
                    'session_id': cycle_count_id,
                    'session_name': cycle_count_name,
                    'start_time': datetime.now().isoformat(),
                    'plant_location_id': plant_location_id
                }
            }
        except Exception as e:
            _logger.error(f"Cycle count start error: {str(e)}")
            return {
                'success': False,
                'message': f'Error: {str(e)}'
            }

    @http.route('/lpn/api/cycle-count/scan', type='json', auth='public', methods=['POST'])
    def cycle_count_scan(self, **kwargs):
        try:
            data = json.loads(request.httprequest.data)
            username = data.get('username')
            password = data.get('password')
            session_token = data.get('session_token')
            rfid_code = data.get('rfid_code')

            if isinstance(rfid_code, dict):
                rfid_code = rfid_code.get('rfid_code')

            if not rfid_code:
                return {'success': False, 'message': 'RFID code is required'}

            uid = common.authenticate(db, username, password, {})
            if not uid:
                return {'success': False, 'message': 'Invalid credentials'}

            message = models.execute_kw(
                db, uid, password,
                'res.users', 'validate_session_tinmac_messsage',
                [[uid], session_token]
            )
            if message and message[0] != 'Okay':
                return {'success': False, 'message': str(message[0])}
            print("Authenticated UID:", uid)
            logging.info(f"Authenticated UID: {uid}")
            logging.info(f"RFID Code to scan: {rfid_code}")
            # print(f"🔍 Searching Master LPN with RFID: {rfid_code}")

            # ✅ Correct search
            
            master_lpn_ids = models.execute_kw(
                db, uid, password, 'lpn.master', 'search',
                [[('rfid_code', '=', rfid_code)]],  # ✅ Correctly structured domain
                {'limit': 1}
            )
            logging.info(f"Master LPN IDs found: {master_lpn_ids}")

            if not master_lpn_ids:
                return {'success': False, 'message': 'Master LPN not found'}

            # master_lpn_data = models.execute_kw(
            #     db, uid, password,
            #     'lpn.master', 'read',
            #     master_lpn_ids,
            #     ['name', 'rfid_code', 'child_lpn_ids']
            # )
            master_lpn_data = models.execute_kw(
            db, uid, password, 'lpn.master', 'read',
            [master_lpn_ids],
            {'fields': ['id','name', 'rfid_code', 'child_lpn_ids', 'physical_audit']}  # ✅ Always use dict for 'read'
        )
            logging.info(f"Master LPN Data: {master_lpn_data}")
            master_lpn = master_lpn_data[0]

            return {
                'success': True,
                'comments': 'Master LPN scanned successfully',
                'data': {
                    'master_id': master_lpn['id'],
                    'master_name': master_lpn['name'],
                    'rfid_code': master_lpn['rfid_code'],
                    'child_count': len(master_lpn.get('child_lpn_ids', [])),
                    'scan_time': datetime.now().isoformat()
                }
            }

        except Exception as e:
            _logger.error("Cycle count scan error: %s", str(e))
            return {'success': False, 'message': f'Error: {str(e)}'}

    @http.route('/lpn/api/cycle-count/submit', type='json', auth='public', methods=['POST'])
    def cycle_count_submit(self, **kwargs):
        try:
            data = json.loads(request.httprequest.data)
            username = data.get('username')
            password = data.get('password')
            session_token = data.get('session_token')
            scanned_master_lpns = data.get('scanned_master_lpns', [])

            # Authenticate user
            uid = common.authenticate(db, username, password, {})
            if not uid:
                return {'success': False, 'message': 'Invalid credentials'}

            # Validate session
            message = models.execute_kw(
                db, uid, password,
                'res.users', 'validate_session_tinmac_messsage',
                [[uid], session_token]
            )
            if message and message[0] != 'Okay':
                return {'success': False, 'message': str(message[0])}

            # ✅ Create records directly from scanned list
            for item in scanned_master_lpns:
                models.execute_kw(
                    db, uid, password,
                    'lpn.cycle.count', 'create',
                    [{
                        'name': item.get('master_name'),
                        'rfid_code': item.get('rfid_code'),
                    }]
                )

            return {
                'success': True,
                'comments': 'Cycle count saved successfully',
                'data': {
                    'total_saved': len(scanned_master_lpns),
                    'submission_time': datetime.now().isoformat()
                }
            }

        except Exception as e:
            _logger.error("Cycle count submit error: %s", str(e))
            return {'success': False, 'message': f'Error: {str(e)}'}


    # ==================== SEARCH & STATS ====================

    @http.route('/lpn/api/search', type='json', auth='public', methods=['POST'])
    def search_lpn(self, **kwargs):
        """
        Search Master LPNs by name or RFID
        
        POST /lpn/api/search
        {
            "username": "admin",
            "password": "admin123",
            "user_id": 1,
            "session_token": "token_here",
            "query": "LPN001",
            "type": "master"
        }
        """
        try:
            data = json.loads(request.httprequest.data)
            username = data.get('username')
            password = data.get('password')
            user_id = data.get('user_id')
            session_token = data.get('session_token')
            search_query = data.get('query', '')
            search_type = data.get('type', 'master')

            # Authenticate
            try:
                uid = common.authenticate(db, username, password, {})
                if not uid:
                    return {'success': False, 'message': 'Invalid credentials'}
            except:
                return {'success': False, 'message': 'Authentication failed'}

            # Validate session
            message = models.execute_kw(
                db, uid, password, 'res.users', 'validate_session_tinmac_messsage',
                [[uid], session_token]
            )
            if message and message[0] != 'Okay':
                return {'success': False, 'message': str(message[0])}

            if not search_query or len(search_query) < 2:
                return {
                    'success': False,
                    'message': 'Search query must be at least 2 characters'
                }

            if search_type == 'master':
                domain = ['|', '|',
                    ('name', 'ilike', search_query),
                    ('rfid_code', 'ilike', search_query),
                    ('subinventory_code', 'ilike', search_query)
                ]
                lpn_ids = models.execute_kw(
                    db, uid, password, 'lpn.master', 'search',
                    [domain], {'limit': 20}
                )
                lpns_data = models.execute_kw(
                    db, uid, password, 'lpn.master', 'read',
                    [lpn_ids], ['id', 'name', 'rfid_code']
                )

                data_list = []
                for lpn in lpns_data:
                    data_list.append({
                        'id': lpn['id'],
                        'name': lpn['name'],
                        'rfid_code': lpn['rfid_code'],
                        'type': 'master'
                    })
            else:
                domain = ['|', '|',
                    ('name', 'ilike', search_query),
                    ('tsn', 'ilike', search_query),
                    ('turbo_item', 'ilike', search_query)
                ]
                lpn_ids = models.execute_kw(
                    db, uid, password, 'lpn.child', 'search',
                    [domain], {'limit': 20}
                )
                lpns_data = models.execute_kw(
                    db, uid, password, 'lpn.child', 'read',
                    [lpn_ids], ['id', 'name', 'tsn', 'parent_id']
                )

                data_list = []
                for lpn in lpns_data:
                    data_list.append({
                        'id': lpn['id'],
                        'name': lpn['name'],
                        'tsn': lpn.get('tsn'),
                        'parent_id': lpn['parent_id'][0] if lpn.get('parent_id') else None,
                        'type': 'child'
                    })

            return {
                'success': True,
                'comments': f'Found {len(data_list)} results',
                'data': data_list
            }
        except Exception as e:
            _logger.error(f"Search error: {str(e)}")
            return {
                'success': False,
                'message': f'Error: {str(e)}'
            }

    @http.route('/lpn/api/stats', type='json', auth='public', methods=['POST'])
    def get_lpn_stats(self, **kwargs):
        """
        Get LPN statistics
        
        POST /lpn/api/stats
        {
            "username": "admin",
            "password": "admin123",
            "user_id": 1,
            "session_token": "token_here"
        }
        """
        try:
            data = json.loads(request.httprequest.data)
            username = data.get('username')
            password = data.get('password')
            user_id = data.get('user_id')
            session_token = data.get('session_token')

            # Authenticate
            try:
                uid = common.authenticate(db, username, password, {})
                if not uid:
                    return {'success': False, 'message': 'Invalid credentials'}
            except:
                return {'success': False, 'message': 'Authentication failed'}

            # Validate session
            message = models.execute_kw(
                db, uid, password, 'res.users', 'validate_session_tinmac_messsage',
                [[uid], session_token]
            )
            if message and message[0] != 'Okay':
                return {'success': False, 'message': str(message[0])}

            total_master_lpn = models.execute_kw(
                db, uid, password, 'lpn.master', 'search_count', [[]]
            )
            total_child_lpn = models.execute_kw(
                db, uid, password, 'lpn.child', 'search_count', [[]]
            )
            audited_lpn = models.execute_kw(
                db, uid, password, 'lpn.master', 'search_count',
                [[('physical_audit', '=', True)]]
            )

            return {
                'success': True,
                'comments': 'Statistics fetched',
                'data': {
                    'total_master_lpn': total_master_lpn,
                    'total_child_lpn': total_child_lpn,
                    'audited_lpn': audited_lpn,
                    'pending_audit': total_master_lpn - audited_lpn
                }
            }
        except Exception as e:
            _logger.error(f"Stats error: {str(e)}")
            return {
                'success': False,
                'message': f'Error: {str(e)}'
            }


    