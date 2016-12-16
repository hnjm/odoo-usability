# -*- coding: utf-8 -*-
# © 2015-2016 Akretion (http://www.akretion.com)
# @author Alexis de Lattre <alexis.delattre@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields, api


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    state = fields.Selection(track_visibility='onchange')
    picking_type_id = fields.Many2one(track_visibility='onchange')
    dest_address_id = fields.Many2one(track_visibility='onchange')
    currency_id = fields.Many2one(track_visibility='onchange')
    payment_term_id = fields.Many2one(track_visibility='onchange')
    fiscal_position_id = fields.Many2one(track_visibility='onchange')
    incoterm_id = fields.Many2one(track_visibility='onchange')
    partner_ref = fields.Char(track_visibility='onchange')
    # for report
    delivery_partner_id = fields.Many2one(
        'res.partner', compute='_compute_delivery_partner_id', readonly=True)

    @api.multi
    @api.depends('dest_address_id', 'picking_type_id')
    def _compute_delivery_partner_id(self):
        for o in self:
            delivery_partner_id = False
            if o.dest_address_id:
                delivery_partner_id = o.dest_address_id
            elif (
                    o.picking_type_id.warehouse_id and
                    o.picking_type_id.warehouse_id.partner_id):
                delivery_partner_id = o.picking_type_id.warehouse_id.partner_id
            o.delivery_partner_id = delivery_partner_id


class ResPartner(models.Model):
    _inherit = 'res.partner'

    # Fix an access right issue when accessing partner form without being
    # a member of the purchase/User group
    @api.multi
    def _purchase_invoice_count(self):
        poo = self.env['purchase.order']
        aio = self.env['account.invoice']
        for partner in self:
            try:
                partner.purchase_order_count = poo.search_count(
                    [('partner_id', 'child_of', partner.id)])
            except:
                pass
            try:
                partner.supplier_invoice_count = aio.search_count([
                    ('partner_id', 'child_of', partner.id),
                    ('type', '=', 'in_invoice')])
            except:
                pass
