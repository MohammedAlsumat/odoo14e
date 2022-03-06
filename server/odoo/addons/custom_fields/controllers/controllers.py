# -*- coding: utf-8 -*-
# from odoo import http


# class CustomFields(http.Controller):
#     @http.route('/custom_fields/custom_fields/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/custom_fields/custom_fields/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('custom_fields.listing', {
#             'root': '/custom_fields/custom_fields',
#             'objects': http.request.env['custom_fields.custom_fields'].search([]),
#         })

#     @http.route('/custom_fields/custom_fields/objects/<model("custom_fields.custom_fields"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('custom_fields.object', {
#             'object': obj
#         })
