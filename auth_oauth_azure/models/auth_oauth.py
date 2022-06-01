from odoo import fields, models


class AuthOAuthProvider(models.Model):
    _inherit = 'auth.oauth.provider'
    is_azure = fields.Boolean(string='Azure')
