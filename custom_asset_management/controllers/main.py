from odoo import http
from odoo.http import request
from werkzeug.utils import redirect
import re
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
import logging

_logger = logging.getLogger(__name__)

class ForceResetPassword(http.Controller):

    @http.route('/web', type='http', auth='user')
    def web_client(self, **kwargs):
        user = request.env.user
        if user.force_reset_password and request.httprequest.path != '/web/reset_password/force':
            return redirect('/web/reset_password/force')
        context = request.env['ir.http'].webclient_rendering_context()
        response = request.render('web.webclient_bootstrap', qcontext=context)
        return response

    @http.route('/web/reset_password/force', type='http', auth='user', website=True)
    def reset_password_page(self, **kwargs):
        return request.render('custom_asset_management.reset_password_template')

    @http.route('/web/reset_password/submit', type='http', auth='user', csrf=False)
    def submit_new_password(self, **kwargs):
        new_password = kwargs.get('new_password')  # Get the new_password from kwargs
        if not new_password:
            return request.redirect('/web/reset_password/force')

        # Basic password policy check
        password_valid, error_msg = self._validate_password_policy(new_password)
        if not password_valid:
            return self.reset_password_page(error=error_msg)

        # Change password using Odoo's method to ensure proper password hashing
        user = request.env.user

        # Use the `write()` method to change the password, Odoo will handle the hashing
        user.sudo().write({
            'password': new_password,
            'force_reset_password': False,
        })

        # Manually commit the changes to the database
        request.env.cr.commit()

        # Log out the user to force the session to reset
        request.session.logout()  # Use session.logout() to properly log out the user

        # Manually clear the session and cookies
        response = request.make_response('')
        response.delete_cookie('session_id')  # Clear the session cookie

        # Redirect the user to the login page
        response.headers['Content-Type'] = 'text/html; charset=utf-8'
        response.set_data("""
                    <html>
                        <head>
                            <meta http-equiv="refresh" content="2" />
                            <script type="text/javascript">
                                // Redirect to the login page after 2 seconds
                                setTimeout(function() {
                                    window.location.href = '/web/login';  // Redirect to login page
                                }, 2000); // 1 seconds delay
                            </script>
                        </head>
                        <body>
                            <h2>Password has been updated successfully.</h2>
                            <p>Redirecting you to the login page...</p>
                        </body>
                    </html>
                """)
        return response

    def _validate_password_policy(self, password):
        """
        Enforce password policy:
        - At least 8 characters
        - At least one uppercase letter
        - At least one lowercase letter
        - At least one digit
        - At least one special character
        """
        if len(password) < 8:
            raise UserError(_(
                "Password must be at least 8 characters long."
            ))
        if not re.search(r'[A-Z]', password):
            raise UserError(_(
                "Password must contain at least one uppercase letter."
            ))
        if not re.search(r'[a-z]', password):
            raise UserError(_(
                "Password must contain at least one lowercase letter."
            ))
        if not re.search(r'[0-9]', password):
            raise UserError(_("Password must contain at least one number."))

        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            raise UserError(_("Password must contain at least one special character."))

        return True, None