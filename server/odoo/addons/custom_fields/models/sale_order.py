# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    x_studio_number_in_pack = fields.Float(related='product_uom.factor_inv', string='Num in Pack', store=True)
    x_studio_actual_unit_weight = fields.Float(related='product_id.actual_unit_weight', store=True)
    x_studio_total_actual_weight = fields.Float(string='Actual T.W', store=True)
    x_studio_total_pieces = fields.Float(compute='onchange_qty_on_total_unit', store=True)
    x_studio_input_ton_price = fields.Float(string='Internal Ton Price', store=True)
    x_studio_1 = fields.Float(compute='onchange_x_price_unit')
    x_studio_2 = fields.Float(compute='onchange_x_studio_input_ton_price')
    x_studio_3 = fields.Float(compute='onchange_x_studio_input_ton_weight')

    # x_studio_many2one_field_Y2R95
    # x_studio_actual_unit_weight
    # x_studio_total_actual_weight
    # x_studio_total_external_weight
    # x_studio_external_ton_price
    # x_studio_external_unit_price

    @api.depends('price_unit', 'x_studio_number_in_pack')
    def onchange_x_price_unit(self):
        for record in self:
            if record.x_studio_actual_unit_weight > 0 and record.x_studio_number_in_pack > 0:
                record.x_studio_input_ton_price = (record.price_unit) / (
                            record.x_studio_actual_unit_weight * record.x_studio_number_in_pack)
                record.x_studio_1 = 0
            else:
                record.x_studio_input_ton_price = 0
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
            if val.x_studio_total_actual_weight > 0 and val.x_studio_number_in_pack and val.x_studio_actual_unit_weight:
                val.product_uom_qty = (val.x_studio_total_actual_weight)/(val.x_studio_actual_unit_weight * val.x_studio_number_in_pack)
                val.x_studio_3 = 0
            else:
                val.x_studio_3 = 0

    @api.depends('product_uom_qty', 'x_studio_number_in_pack')
    def onchange_qty_on_total_unit(self):
        for val in self:
            if val.product_uom_qty > 0 and val.x_studio_number_in_pack > 0 and val.x_studio_actual_unit_weight > 0:
                val.x_studio_total_actual_weight = val.product_uom_qty * val.x_studio_number_in_pack * val.x_studio_actual_unit_weight
                val.x_studio_input_ton_price = (val.price_unit) / (val.x_studio_actual_unit_weight * val.x_studio_number_in_pack)
                val.x_studio_total_actual_weight = val.x_studio_number_in_pack * val.product_uom_qty * val.x_studio_actual_unit_weight
            else:
                val.x_studio_total_actual_weight = val.x_studio_input_ton_price = val.x_studio_total_actual_weight = 0

            val.x_studio_total_pieces = val.product_uom_qty * val.x_studio_number_in_pack


class SaleReport(models.Model):
    _inherit = "sale.report"

    x_studio_number_in_pack = fields.Float(string='Num in Pack', readonly=True)
    x_studio_actual_unit_weight = fields.Float(string='Actual U.W', readonly=True)
    x_studio_total_actual_weight = fields.Float(string='Actual T.W', readonly=True)
    x_studio_total_pieces = fields.Float(string='Num of pieces', readonly=True)
    x_studio_input_ton_price = fields.Float(string='Internal Ton Price', readonly=True)

    def _query(self, with_clause='', fields={}, groupby='', from_clause=''):
        with_ = ("WITH %s" % with_clause) if with_clause else ""

        select_ = """
            coalesce(min(l.id), -s.id) as id,
            l.product_id as product_id,
            l.product_uom as product_uom,
            CASE WHEN l.product_id IS NOT NULL THEN sum(l.product_uom_qty) ELSE 0 END as product_uom_qty,
            CASE WHEN l.product_id IS NOT NULL THEN sum(l.qty_delivered) ELSE 0 END as qty_delivered,
            CASE WHEN l.product_id IS NOT NULL THEN sum(l.qty_invoiced) ELSE 0 END as qty_invoiced,
            CASE WHEN l.product_id IS NOT NULL THEN sum(l.qty_to_invoice) ELSE 0 END as qty_to_invoice,
            CASE WHEN l.product_id IS NOT NULL THEN sum(l.price_total / CASE COALESCE(s.currency_rate, 0) WHEN 0 THEN 1.0 ELSE s.currency_rate END) ELSE 0 END as price_total,
            CASE WHEN l.product_id IS NOT NULL THEN sum(l.price_subtotal / CASE COALESCE(s.currency_rate, 0) WHEN 0 THEN 1.0 ELSE s.currency_rate END) ELSE 0 END as price_subtotal,
            CASE WHEN l.product_id IS NOT NULL THEN sum(l.untaxed_amount_to_invoice / CASE COALESCE(s.currency_rate, 0) WHEN 0 THEN 1.0 ELSE s.currency_rate END) ELSE 0 END as untaxed_amount_to_invoice,
            CASE WHEN l.product_id IS NOT NULL THEN sum(l.untaxed_amount_invoiced / CASE COALESCE(s.currency_rate, 0) WHEN 0 THEN 1.0 ELSE s.currency_rate END) ELSE 0 END as untaxed_amount_invoiced,
            count(*) as nbr,
            l.x_studio_number_in_pack as x_studio_number_in_pack,
            l.x_studio_actual_unit_weight as x_studio_actual_unit_weight,
            l.x_studio_total_actual_weight as x_studio_total_actual_weight,
            l.x_studio_total_pieces as x_studio_total_pieces,
            l.x_studio_input_ton_price as x_studio_input_ton_price,
            s.name as name,
            s.date_order as date,
            s.state as state,
            s.partner_id as partner_id,
            s.user_id as user_id,
            s.company_id as company_id,
            s.campaign_id as campaign_id,
            s.medium_id as medium_id,
            s.source_id as source_id,
            extract(epoch from avg(date_trunc('day',s.date_order)-date_trunc('day',s.create_date)))/(24*60*60)::decimal(16,2) as delay,
            t.categ_id as categ_id,
            s.pricelist_id as pricelist_id,
            s.analytic_account_id as analytic_account_id,
            s.team_id as team_id,
            p.product_tmpl_id,
            partner.country_id as country_id,
            partner.industry_id as industry_id,
            partner.commercial_partner_id as commercial_partner_id,
            CASE WHEN l.product_id IS NOT NULL THEN sum(p.weight * l.product_uom_qty) ELSE 0 END as weight,
            CASE WHEN l.product_id IS NOT NULL THEN sum(p.volume * l.product_uom_qty) ELSE 0 END as volume,
            l.discount as discount,
            CASE WHEN l.product_id IS NOT NULL THEN sum((l.price_unit * l.product_uom_qty * l.discount / 100.0 / CASE COALESCE(s.currency_rate, 0) WHEN 0 THEN 1.0 ELSE s.currency_rate END))ELSE 0 END as discount_amount,
            s.id as order_id
        """

        for field in fields.values():
            select_ += field

        from_ = """
                sale_order_line l
                      inner join sale_order s on (s.id=l.order_id)
                      join res_partner partner on s.partner_id = partner.id
                        inner join product_product p on (l.product_id=p.id)
                            inner join product_template t on (p.product_tmpl_id=t.id)
                    inner join uom_uom u on (u.id=l.product_uom)
                    inner join uom_uom u2 on (u2.id=l.product_uom)
                    inner join product_pricelist pp on (s.pricelist_id = pp.id)
                %s
        """ % from_clause

        groupby_ = """
            l.id,
            l.product_id,
            l.order_id,
            l.product_uom,
            t.categ_id,
            s.name,
            s.date_order,
            s.partner_id,
            s.user_id,
            s.state,
            s.company_id,
            s.campaign_id,
            s.medium_id,
            s.source_id,
            s.pricelist_id,
            s.analytic_account_id,
            s.team_id,
            p.product_tmpl_id,
            partner.country_id,
            partner.industry_id,
            partner.commercial_partner_id,
            l.discount,
            s.id %s
        """ % (groupby)

        return '%s (SELECT %s FROM %s GROUP BY %s)' % (with_, select_, from_, groupby_)