# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import json

import requests

from odoo import api, fields, models
from odoo.exceptions import AccessDenied, UserError
from odoo.addons.auth_signup.models.res_users import SignupError

from odoo.addons import base

# Override default behavior by checking if it's azure provider or not
# The following is returned from https://graph.microsoft.com/oidc/userinfo
# {
# "sub": "static random string",
# "name": "firstname lastname",
# "family_name": "lastname",
# "given_name": "firsname",
# "picture": "https://graph.microsoft.com/v1.0/me/photo/$value",
# "email": "email"
# }
# no user_id attr is available. Therefore email attr is used instead.


class ResUsers(models.Model):
    _inherit = 'res.users'

    @api.model
    def _generate_signup_values(self, provider, validation, params):
        oauth_uid = validation['email']
        email = validation.get('email', 'provider_%s_user_%s' % (provider, oauth_uid))
        name = validation.get('name', email)
        return {
            'name': name,
            'login': email,
            'email': email,
            'oauth_provider_id': provider,
            'oauth_uid': oauth_uid,
            'oauth_access_token': params['access_token'],
            'active': True,
        }

    @api.model
    def _auth_oauth_signin(self, provider, validation, params):
        """ retrieve and sign in the user corresponding to provider and validated access token
            :param provider: oauth provider id (int)
            :param validation: result of validation of access token (dict)
            :param params: oauth parameters (dict)
            :return: user login (str)
            :raise: AccessDenied if signin failed
            This method can be overridden to add alternative signin methods.
        """
        oauth_uid = validation['email']
        try:
            oauth_user = self.search([("oauth_uid", "=", oauth_uid), ('oauth_provider_id', '=', provider)])
            if not oauth_user:
                raise AccessDenied()
            assert len(oauth_user) == 1
            oauth_user.write({'oauth_access_token': params['access_token']})
            return oauth_user.login
        except AccessDenied as access_denied_exception:
            if self.env.context.get('no_user_creation'):
                return None
            state = json.loads(params['state'])
            token = state.get('t')
            values = self._generate_signup_values(provider, validation, params)
            try:
                _, login, _ = self.signup(values, token)
                return login
            except (SignupError, UserError):
                raise access_denied_exception
    # End Fix

    def _auth_oauth_rpc(self, endpoint, access_token, provider):
        oauth_provider = self.env['auth.oauth.provider'].browse(provider)
        if oauth_provider.is_azure:
            return requests.get(endpoint, headers={'Authorization': 'Bearer ' + access_token}, timeout=10).json()
        else:
            self._auth_oauth_rpc(endpoint, access_token)

    @api.model
    def _auth_oauth_validate(self, provider, access_token):
        """ return the validation data corresponding to the access token """
        oauth_provider = self.env['auth.oauth.provider'].browse(provider)
        validation = self._auth_oauth_rpc(oauth_provider.validation_endpoint, access_token, provider)
        if validation.get("error"):
            raise Exception(validation['error'])
        if oauth_provider.data_endpoint:
            data = self._auth_oauth_rpc(oauth_provider.data_endpoint, access_token, provider)
            validation.update(data)
        return validation
