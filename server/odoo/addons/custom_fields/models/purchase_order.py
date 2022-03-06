# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    x_studio_internal_purchase = fields.Boolean(string='Internal Purchase')
    x_studio_external_purchase = fields.Boolean(string='External Purchase')


class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    x_studio_number_in_pack = fields.Float(related='product_uom.factor_inv', string='Num in Pack')
    x_studio_actual_unit_weight = fields.Float(related='product_id.actual_unit_weight')
    x_studio_total_actual_weight = fields.Float(string='Actual T.W')
    x_studio_total_pieces = fields.Float(compute='onchange_qty_on_total_unit', store=True)
    x_studio_input_ton_price = fields.Float(string='Internal Ton Price', store=True)

    x_studio_1 = fields.Float(compute='onchange_x_price_unit')
    x_studio_2 = fields.Float(compute='onchange_x_studio_input_ton_price')
    x_studio_3 = fields.Float(compute='onchange_x_studio_input_ton_weight')
    x_studio_4 = fields.Float(compute='total_external_weight')
    x_studio_5 = fields.Float(compute='onchange_total_external_weight')
    x_studio_6 = fields.Float(compute='get_external_unit_price')
    x_studio_7 = fields.Float(compute='update_external_unit_price')

    x_studio_many2one_field_Y2R95 = fields.Many2one('external.weights', string='External Weight')
    x_studio_total_external_weight = fields.Float(string='Total External Weight ')
    x_studio_external_ton_price = fields.Float(string='External Ton Price')
    x_studio_external_unit_price = fields.Float(string='External Unit Price')
    product_external_weight = fields.Float(related='x_studio_many2one_field_Y2R95.x_studio_external_unit_weight')
    # x_studio_related_field_QhwV7 to product_external_weight

    @api.depends('x_studio_number_in_pack', 'x_studio_external_ton_price', 'product_external_weight')
    def update_external_unit_price(self):
        for val in self:
            if val.x_studio_number_in_pack > 0 and val.x_studio_external_ton_price > 0 and val.product_external_weight > 0 and val.x_studio_many2one_field_Y2R95:
                val.price_unit = val.x_studio_external_unit_price = val.x_studio_number_in_pack * val.x_studio_external_ton_price * val.product_external_weight
            else:
                val.x_studio_external_unit_price = 0
            val.x_studio_7 = 0

    @api.depends('x_studio_number_in_pack', 'x_studio_external_ton_price', 'product_external_weight')
    def get_external_unit_price(self):
        for record in self:
            # if record.product_external_weight > 0 and record.x_studio_number_in_pack > 0 and record.x_studio_external_ton_price:
            #     record.price_unit = record.product_external_weight * record.x_studio_number_in_pack * record.x_studio_external_ton_price
            #
            # else:
            #     record.price_unit = 0
            record.x_studio_6 = 0

    @api.depends('x_studio_number_in_pack', 'product_external_weight', 'x_studio_total_external_weight')
    def onchange_total_external_weight(self):
        for record in self:
            if record.x_studio_total_external_weight > 0 and record.product_external_weight > 0 and record.x_studio_number_in_pack > 0 and record.x_studio_many2one_field_Y2R95:
                record.product_qty = (record.x_studio_total_external_weight) / (
                            record.product_external_weight * record.x_studio_number_in_pack)
                record.x_studio_5 = 0
            else:
                record.x_studio_5 = 0

    @api.depends('product_qty', 'x_studio_number_in_pack', 'product_external_weight')
    def total_external_weight(self):
        for record in self:
            if record.x_studio_number_in_pack > 0 and record.product_qty > 0 and record.product_external_weight > 0 and record.x_studio_many2one_field_Y2R95:
                record.x_studio_total_external_weight = record.x_studio_number_in_pack * record.product_qty * record.product_external_weight
                record.x_studio_external_ton_price = (record.price_unit) / (record.product_external_weight * record.x_studio_number_in_pack)
            else:
                record.x_studio_total_external_weight = 0
            record.x_studio_4 = 0

    @api.onchange('x_studio_many2one_field_Y2R95')
    def onchange_x_studio_many2one_field(self):
        for val in self:
            if val.x_studio_many2one_field_Y2R95:
                if val.x_studio_many2one_field_Y2R95.x_studio_many2one_field_RgPYK:
                    val.product_id = val.x_studio_many2one_field_Y2R95.x_studio_many2one_field_RgPYK.id

    @api.depends('price_unit', 'x_studio_number_in_pack')
    def onchange_x_price_unit(self):
        for record in self:
            if record.x_studio_actual_unit_weight > 0 and record.x_studio_number_in_pack > 0:
                record.x_studio_input_ton_price = (record.price_unit) / (
                        record.x_studio_actual_unit_weight * record.x_studio_number_in_pack)

            if record.product_external_weight > 0 and record.x_studio_number_in_pack > 0:
                record.x_studio_external_ton_price = (record.price_unit) / (
                        record.product_external_weight * record.x_studio_number_in_pack)

            record.x_studio_1 = 0

    @api.depends('x_studio_input_ton_price', 'x_studio_number_in_pack')
    def onchange_x_studio_input_ton_price(self):
        for record in self:
            if record.x_studio_actual_unit_weight > 0:
                record.price_unit = record.x_studio_input_ton_price * record.x_studio_actual_unit_weight * record.x_studio_number_in_pack
                record.x_studio_2 = 0
            else:
                record.price_unit = 0
                record.x_studio_2 = 0

    @api.depends('x_studio_total_actual_weight', 'x_studio_number_in_pack')
    def onchange_x_studio_input_ton_weight(self):
        for val in self:
            if val.x_studio_total_actual_weight > 0 and val.x_studio_total_actual_weight and val.x_studio_actual_unit_weight * val.x_studio_number_in_pack:
                val.product_qty = (val.x_studio_total_actual_weight) / (
                            val.x_studio_actual_unit_weight * val.x_studio_number_in_pack)
                val.x_studio_3 = 0
            else:
                val.x_studio_3 = 0

    @api.depends('product_qty', 'x_studio_number_in_pack')
    def onchange_qty_on_total_unit(self):
        for val in self:
            if val.product_qty > 0 and val.x_studio_number_in_pack > 0 and val.x_studio_actual_unit_weight > 0:
                val.x_studio_total_actual_weight = val.product_qty * val.x_studio_number_in_pack * val.x_studio_actual_unit_weight
                val.x_studio_total_pieces = val.product_qty * val.x_studio_number_in_pack
                val.x_studio_input_ton_price = (val.price_unit) / (
                            val.x_studio_actual_unit_weight * val.x_studio_number_in_pack)
                val.x_studio_total_actual_weight = val.x_studio_number_in_pack * val.product_qty * val.x_studio_actual_unit_weight
            else:
                val.x_studio_total_pieces = val.x_studio_total_actual_weight = val.x_studio_input_ton_price = val.x_studio_total_actual_weight = 0


class PurchaseReport(models.Model):
    _inherit = "purchase.report"

    x_studio_many2one_field_Y2R95 = fields.Many2one('external.weights', string='External Weight', readonly=True)
    x_studio_total_actual_weight = fields.Float(string='Actual T.W', readonly=True)
    x_studio_total_pieces = fields.Float(string='Num of Pieces', readonly=True)
    x_studio_input_ton_price = fields.Float(string='Internal Ton Price', readonly=True)
    x_studio_total_external_weight = fields.Float(string='Total External Weight', readonly=True)
    x_studio_external_ton_price = fields.Float(string='External Ton Price', readonly=True)

    def _select(self):
        select_str = """
            WITH currency_rate as (%s)
                SELECT
                    l.x_studio_total_actual_weight as x_studio_total_actual_weight,
                    l.x_studio_total_pieces as x_studio_total_pieces,
                    l.x_studio_input_ton_price as x_studio_input_ton_price,
                    l.x_studio_total_external_weight as x_studio_total_external_weight,
                    l.x_studio_external_ton_price as x_studio_external_ton_price,
                    po.id as order_id,
                    min(l.id) as id,
                    po.date_order as date_order,
                    po.state,
                    po.date_approve,
                    po.dest_address_id,
                    po.partner_id as partner_id,
                    po.user_id as user_id,
                    po.company_id as company_id,
                    po.fiscal_position_id as fiscal_position_id,
                    l.product_id,
                    p.product_tmpl_id,
                    t.categ_id as category_id,
                    po.currency_id,
                    l.product_uom as product_uom,
                    extract(epoch from age(po.date_approve,po.date_order))/(24*60*60)::decimal(16,2) as delay,
                    extract(epoch from age(l.date_planned,po.date_order))/(24*60*60)::decimal(16,2) as delay_pass,
                    count(*) as nbr_lines,
                    sum(l.price_total / COALESCE(po.currency_rate, 1.0))::decimal(16,2) as price_total,
                    (sum(l.product_qty * l.price_unit / COALESCE(po.currency_rate, 1.0))/NULLIF(sum(l.product_qty),0.0))::decimal(16,2) as price_average,
                    partner.country_id as country_id,
                    partner.commercial_partner_id as commercial_partner_id,
                    analytic_account.id as account_analytic_id,
                    sum(p.weight * l.product_qty) as weight,
                    sum(p.volume * l.product_qty) as volume,
                    sum(l.price_subtotal / COALESCE(po.currency_rate, 1.0))::decimal(16,2) as untaxed_total,
                    sum(l.product_qty ) as qty_ordered,
                    sum(l.qty_received) as qty_received,
                    sum(l.qty_invoiced) as qty_billed,
                    case when t.purchase_method = 'purchase' 
                         then sum(l.product_qty) - sum(l.qty_invoiced)
                         else sum(l.qty_received) - sum(l.qty_invoiced)
                    end as qty_to_be_billed
        """ % self.env['res.currency']._select_companies_rates() + ", spt.warehouse_id as picking_type_id, po.effective_date as effective_date"
        return select_str

    def _from(self):
        from_str = """
            purchase_order_line l
                join purchase_order po on (l.order_id=po.id)
                join res_partner partner on po.partner_id = partner.id
                    left join product_product p on (l.product_id=p.id)
                        left join product_template t on (p.product_tmpl_id=t.id)
                left join uom_uom line_uom on (line_uom.id=l.product_uom)
                left join uom_uom product_uom on (product_uom.id=t.uom_id)
                left join account_analytic_account analytic_account on (l.account_analytic_id = analytic_account.id)
                left join currency_rate cr on (cr.currency_id = po.currency_id and
                    cr.company_id = po.company_id and
                    cr.date_start <= coalesce(po.date_order, now()) and
                    (cr.date_end is null or cr.date_end > coalesce(po.date_order, now())))
        """ + " left join stock_picking_type spt on (spt.id=po.picking_type_id)"
        return from_str

    def _group_by(self):
        group_by_str = """
            GROUP BY
                l.id,
                po.company_id,
                po.user_id,
                po.partner_id,
                line_uom.factor,
                po.currency_id,
                l.price_unit,
                po.date_approve,
                l.date_planned,
                l.product_uom,
                po.dest_address_id,
                po.fiscal_position_id,
                l.product_id,
                p.product_tmpl_id,
                t.categ_id,
                po.date_order,
                po.state,
                line_uom.uom_type,
                line_uom.category_id,
                t.uom_id,
                t.purchase_method,
                line_uom.id,
                product_uom.factor,
                partner.country_id,
                partner.commercial_partner_id,
                analytic_account.id,
                po.id
        """ + ", spt.warehouse_id, effective_date"
        return group_by_str