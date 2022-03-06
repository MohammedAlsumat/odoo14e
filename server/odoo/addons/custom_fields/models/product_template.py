# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models


class Product(models.Model):
    _inherit = 'product.template'

    x_studio_product_interval = fields.Float(string='Product Interval')


class ProductAttributeValue(models.Model):
    _inherit = 'product.attribute.value'

    x_studio_custom_value_actual = fields.Float(string='Custom Value (Actual)')


class ProductAttribute(models.Model):
    _inherit = 'product.attribute'

    x_studio_size = fields.Boolean(string='Size')


class ProductTemplateAttributeValue(models.Model):
    _inherit = 'product.template.attribute.value'

    custom_value_actual = fields.Float(related='product_attribute_value_id.x_studio_custom_value_actual')


class ProductProduct(models.Model):
    _inherit = "product.product"

    x_studio_external_weights = fields.One2many('external.weights', 'x_studio_many2one_field_RgPYK', string='External Weights')
    x_studio_product_interval_1 = fields.Float(related='product_tmpl_id.x_studio_product_interval')
    total_weight = fields.Float(compute='_get_total_size')
    actual_unit_weight = fields.Float(compute='_get_total_size')

    def _get_total_size(self):
        for val in self:
            total_size = 1
            for attr in val.product_template_attribute_value_ids:
                if attr.custom_value_actual:
                    total_size *= attr.custom_value_actual
            if total_size == 1:
                val.total_weight = 0
                val.actual_unit_weight = 0
            elif val.x_studio_product_interval_1:
                val.total_weight = total_size
                val.actual_unit_weight = total_size/val.x_studio_product_interval_1
            else:
                val.actual_unit_weight = 0
                val.total_weight = 0


class ExternalWeight(models.Model):
    _name = 'external.weights'

    _rec_name = 'x_name'
    x_name = fields.Char(string='Name', required='true')
    x_studio_length = fields.Float(string='Length' , required='true')
    x_studio_width = fields.Float(string='Width')
    x_studio_thickness = fields.Float(string='Thickness', required='true')
    x_studio_wth = fields.Float(string='w*t*h', compute='_get_studio_wth')
    x_studio_many2one_field_RgPYK = fields.Many2one('product.product', string='Product', required='true')
    x_studio_product_interval_external_weight = fields.Float(string='Product Interval External Weight',
                                                             related='x_studio_many2one_field_RgPYK.x_studio_product_interval')
    x_studio_external_unit_weight = fields.Float(string='External Unit Weight', compute='_get_studio_wth', store=True)

    @api.depends('x_studio_length', 'x_studio_width', 'x_studio_thickness','x_studio_wth','x_studio_product_interval_external_weight')
    def _get_studio_wth(self):
        for record in self:
            if record.x_studio_width > 0 or record.x_studio_thickness > 0 or record.x_studio_length > 0:
                record.x_studio_wth = record.x_studio_width * record.x_studio_thickness * record.x_studio_length

            else:
                record.x_studio_wth = 0

            if record.x_studio_wth > 0 and record.x_studio_product_interval_external_weight:
                record.x_studio_external_unit_weight = record.x_studio_wth / record.x_studio_product_interval_external_weight

            else:
                record.x_studio_external_unit_weight = 0
