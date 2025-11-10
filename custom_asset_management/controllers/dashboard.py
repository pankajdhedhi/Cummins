from docutils.nodes import pending
from odoo import http
from odoo.http import request


class AssetManagementDashboard(http.Controller):

    @http.route('/asset/fetch/dashboard', type="json", auth='user')
    def fetch_asset_dashboard(self):
        is_not_local_finance = not request.env.user.has_group('custom_asset_management.group_local_finance')
        is_not_central_finance = request.env.user.has_group('custom_asset_management.group_central_finance')
        print(is_not_local_finance, "IS LOCAL")
        user = request.env.user
        work_centers = {}
        work_center_ids = request.env['asset.work.center'].sudo().search([])
        for work_center_id in work_center_ids:
            work_centers[work_center_id.id] = work_center_id.name

        plants = {}
        plant_ids = []
        users = {}
        if is_not_central_finance:
            order_ids = request.env['order.order'].sudo().search([])
            domain_created = [('plant_id', 'in', user.plant_id.ids)]
            order_total = request.env['order.order'].sudo().search_count([])
            asset_total = request.env['asset.management'].sudo().search_count([])
            verified_asset = request.env['asset.management'].sudo().search_count([('physical_count','>',0)])
            pending_asset = request.env['asset.management'].sudo().search_count([('physical_count', '<=', 0)])
            order_created_ids = request.env['order.order'].sudo().search(domain_created)
            order_created = request.env['order.order'].sudo().search_count(
                [('state', '=', 'order_created')])
            order_assigned = request.env['order.order'].sudo().search_count(
                [('state', '=', 'assign')])
            order_inprocess = request.env['order.order'].sudo().search_count(
                [('state', '=', 'inprogress')])
            order_validate = request.env['order.order'].sudo().search_count(
                [('state', '=', 'validate')])
            order_apporve = request.env['order.order'].sudo().search_count(
                [('state', '=', 'apporve')])
            order_closed = request.env['order.order'].sudo().search_count(
                [('state', '=', 'close')])
            order_reject = request.env['order.order'].sudo().search_count(
                [('state', '=', 'reject')])

            plant_ids = request.env['asset.plant'].sudo().search([])
            for plant_id in plant_ids:
                plants[plant_id.id] = plant_id.name
            user_ids = request.env['res.users'].sudo().search([('share', '=', False)])
            for user_id in user_ids:
                users[user_id.id] = user_id.name
            plant_ids = plant_ids.ids
            domain =[]
        else:
            domain = [('plant_id', 'in', user.plant_id.ids), ('technician_id','=', user.id)]
            domain_created = [('plant_id', 'in', user.plant_id.ids), ('create_uid','=', user.id)]
            asset_total = request.env['asset.management'].sudo().search_count([])
            verified_asset = request.env['asset.management'].sudo().search_count([('physical_count', '>', 0)])
            pending_asset = request.env['asset.management'].sudo().search_count([('physical_count', '<=', 0)])
            order_ids = request.env['order.order'].sudo().search(domain)
            order_created_ids = request.env['order.order'].sudo().search(domain_created)
            order_created = request.env['order.order'].sudo().search_count(
                [('state', '=', 'order_created')] + domain_created)
            order_assigned = request.env['order.order'].sudo().search_count(
                [('state', '=', 'assign')] + domain)
            order_inprocess = request.env['order.order'].sudo().search_count(
                [('state', '=', 'inprogress')] + domain)
            order_validate = request.env['order.order'].sudo().search_count(
                [('state', '=', 'validate')] + domain)
            order_apporve = request.env['order.order'].sudo().search_count(
                [('state', '=', 'apporve')] + domain)
            order_closed = request.env['order.order'].sudo().search_count(
                [('state', '=', 'close')] + domain)
            order_reject = request.env['order.order'].sudo().search_count(
                [('state', '=', 'reject')] + domain)
            order_total = order_created+order_assigned+order_inprocess+order_apporve+order_validate+order_closed+order_reject
            # plant_ids = user.plant_id.ids
            # user_ids = user
            # users[user.id] = user.name

            plant_ids = request.env['asset.plant'].sudo().search([])
            for plant_id in plant_ids:
                plants[plant_id.id] = plant_id.name
            user_ids = request.env['res.users'].sudo().search([('share', '=', False)])
            for user_id in user_ids:
                users[user_id.id] = user_id.name
            plant_ids = plant_ids.ids
            domain = []

        dashboard_data = {}
        order_user_created = {}
        order_user_assign = {}
        order_user_inprogress = {}
        order_user_validate = {}
        order_user_apporve = {}
        order_user_close = {}
        order_user_reject = {}
        #order_user_complete = {}
        for user_id in user_ids:
            in_progress_count = order_created_count = apporve_count = 0
            close_count = validate_count = reject_count = assign_count = 0
            for order_id in order_created_ids.filtered(lambda o: o.state == 'order_created'):
                if order_id.technician_id == user_id:
                    order_created_count += 1
            order_user_created[user_id.name] = order_created_count
            for order_id in order_ids.filtered(lambda o: o.state == 'assign'):
                if order_id.technician_id == user_id:
                    assign_count += 1
            order_user_assign[user_id.name] = assign_count
            for order_id in order_ids.filtered(lambda o: o.state == 'inprogress'):
                if order_id.technician_id == user_id:
                    in_progress_count += 1
            order_user_inprogress[user_id.name] = in_progress_count
            for order_id in order_ids.filtered(lambda o: o.state == 'validate'):
                if order_id.technician_id == user_id:
                    validate_count += 1
            order_user_validate[user_id.name] = validate_count
            for order_id in order_ids.filtered(lambda o: o.state == 'apporve'):
                if order_id.technician_id == user_id:
                    apporve_count += 1
            order_user_apporve[user_id.name] = apporve_count
            for order_id in order_ids.filtered(lambda o: o.state == 'close'):
                if order_id.technician_id == user_id:
                    close_count += 1
            order_user_close[user_id.name] = close_count
            for order_id in order_ids.filtered(lambda o: o.state == 'reject'):
                if order_id.technician_id == user_id:
                    reject_count += 1
            order_user_reject[user_id.name] = reject_count

        contract = []
        order_count = []
        for order_id in order_ids:
            if order_id.state == 'order_created':
                state = 'Order Created'
            elif order_id.state == 'assign':
                state = 'Assigned'
            elif order_id.state == 'inprogress':
                state = 'Inprogress'
            elif order_id.state == 'validate':
                state = 'Completed'
            elif order_id.state == 'apporve':
                state = 'Approved'
            elif order_id.state == 'close':
                state = 'Closed'
            elif order_id.state == 'reject':
                state = 'Rejected'
            else:
                state = ''
            work_center = ''
            if order_id.work_center_ids:
                for work_center_id in order_id.work_center_ids:
                    work_center += work_center_id.name + ' '
            order_data = {}
            order_count.append(order_id.id)
            order_data['name'] = order_id.name or ''
            order_data['id'] = order_id.id or ''
            order_data['work_center'] = work_center
            order_data['reason'] = order_id.reason or ''
            order_data['plant_id'] = order_id.plant_id.name if order_id.plant_id.name else ""
            order_data['technician_id'] = order_id.technician_id.name if order_id.technician_id.name else ""
            order_data['order_datetime'] = order_id.order_datetime or ''
            order_data['state'] = state
            contract.append(order_data)
        dashboard_data['order_ids'] = contract
        dashboard_data['users'] = users

        dashboard_data['order_user_created'] = order_user_created
        dashboard_data['order_user_assign'] = order_user_assign
        dashboard_data['order_user_validate'] = order_user_validate
        dashboard_data['order_user_inprogress'] = order_user_inprogress
        dashboard_data['order_user_apporve'] = order_user_apporve
        dashboard_data['order_user_close'] = order_user_close
        dashboard_data['order_user_reject'] = order_user_reject

        dashboard_data['plants'] = plants
        dashboard_data['plant_ids'] = plant_ids
        dashboard_data['work_centers'] = work_centers
        dashboard_data['order_total'] = order_total
        dashboard_data['order_created'] = order_created
        dashboard_data['order_assigned'] = order_assigned
        dashboard_data['order_inprocess'] = order_inprocess
        dashboard_data['order_validate'] = order_validate
        dashboard_data['order_apporve'] = order_apporve
        dashboard_data['order_closed'] = order_closed
        dashboard_data['order_reject'] = order_reject
        dashboard_data['is_not_local_finance'] = is_not_local_finance
        dashboard_data['asset_total'] = asset_total
        dashboard_data['verified_asset'] = verified_asset
        dashboard_data['pending_asset'] = asset_total - verified_asset
        dashboard_data['domain'] = domain
        dashboard_data['sel_day_str'] = ''
        dashboard_data['sel_plant_str'] = ''
        dashboard_data['dash_init'] = True
        return dashboard_data
