
from odoo import models, fields, api, _


class AssetOrderMessageWizard(models.TransientModel):
    _name = 'asset.order.message.wizard'
    _description = 'Order Message Wizard'

    message = fields.Text(required=True, readonly=True)
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

    def action_ok(self):
        order_id = self.env['order.order'].browse(self.order_id.id)
        if order_id.state == 'validate':
            approved_ids = order_id.asset_ids.filtered(lambda o: o.approved)
            approved_ids.write({'state': 'apporve'})
            for line in approved_ids:
                if line.approved:
                    line.asset_code_id.write({
                        'physical_verification_date': line.physical_verification_date
                    })
            order_id.write({
                'state': 'apporve',
                'approval_datetime': fields.datetime.now()
            })
            email_template = self.env.ref('custom_asset_management.to_send_mail_approved_order').id
            template = self.env['mail.template'].browse(email_template)
            email_to = order_id.technician_id.email
            email_values = {
                'email_from': (', '.join(str(a.email) for a in self.env.user)),
                'email_to': email_to,
            }
            mail_id = template.sudo().send_mail(order_id.id, email_values=email_values, force_send=True)

        elif order_id.state == 'apporve':
            order_id.write({
                'state': 'close',
                'closed_user_id': self.env.user.id,
                'closed_datetime': fields.datetime.now()
            })

        elif order_id.state == 'inprogress':
            order_id.write({
                'state': 'validate',
                'technician_datetime': fields.datetime.now()
            })
            for line in order_id.asset_ids:
                if line.rejected:
                    line.rejected = False

                if line.approved:
                    line.asset_code_id.write({
                        'physical_verification_date': line.physical_verification_date
                    })
            email_template = self.env.ref('custom_asset_management.to_send_mail_approve_order').id
            template = self.env['mail.template'].browse(email_template)
            email_to = order_id.approval_id.email
            email_values = {
                'email_from': (', '.join(str(a.email) for a in self.env.user)),
                'email_to': email_to,
            }
            mail_id = template.sudo().send_mail(self.order_id.id, email_values=email_values, force_send=True)

    def action_reject(self):
        print ("Rejected")