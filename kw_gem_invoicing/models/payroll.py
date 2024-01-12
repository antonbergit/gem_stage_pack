import logging

from odoo import models, fields, api

_logger = logging.getLogger(__name__)


class Payroll(models.Model):
    _inherit = 'kw.gem.payroll'
    _description = 'Payroll'

    name = fields.Char()
    kw_report_payer_name = fields.Char(
        compute='_compute_rep_payer_name',
        compute_sudo=True, store=True)
    kw_report_agreement_name = fields.Char(
        compute='_compute_rep_payer_name',
        compute_sudo=True, store=True)
    kw_report_payer_types = fields.Char(
        compute='_compute_rep_payer_name',
        compute_sudo=True, store=True)
    kw_report_invoiced_amount_for_other = fields.Float(
        compute='_compute_rep_invoices', compute_sudo=True, store=True)
    kw_report_not_invoiced_amount_for_other = fields.Float(
        compute='_compute_rep_invoices', compute_sudo=True, store=True)
    kw_sale_order_line_uom_qty = fields.Float(
        compute='_compute_kw_sale_order_line_uom_qty',
        compute_sudo=True,
        store=True
    )

    @api.depends('sale_order_id.kw_agreement_id', 'sale_order_id.partner_id',
                 'sale_order_id.is_split_by_payers', 'service_id',
                 'sale_order_line_id.order_partner_id')
    def _compute_rep_payer_name(self):
        for res in self:
            if not res.sale_order_id.order_line:
                continue
            if res.sale_order_id.is_split_by_payers:
                payer_ids = res.sale_order_id.order_line.filtered(
                    lambda line: line.product_id == res.service_id).\
                    mapped('order_partner_id')
                res.kw_report_payer_name = ', '.join(payer_ids.mapped('name'))
                res.kw_report_agreement_name = ', '.join([
                    x.payer_agreement_id.name
                    for x in res.sale_order_id.kw_order_payment_ids.filtered(
                        lambda p: p.partner_id in payer_ids)])
                payer_types = self.env['res.partner'].search([
                    ('id', 'in', payer_ids.ids)]).mapped('company_type')
            else:
                res.kw_report_payer_name = \
                    res.sale_order_line_id.order_partner_id.name
                res.kw_report_agreement_name = \
                    res.sale_order_line_id.kw_report_payer_agreement_id.name
                payer_types = res.sale_order_line_id \
                    .mapped('kw_report_company_type')
            payer_types_list = []
            company_types = {'person': 'Individual', 'company': 'Company'}
            for payer_type in payer_types:
                payer_types_list.append(company_types.get(payer_type, ''))
            res.kw_report_payer_types = ',\n'.join(payer_types_list)

    @api.depends('sale_order_id.invoice_ids')
    def _compute_rep_invoices(self):
        for payroll in self:
            total_payers = sum(payroll.sale_order_id.order_line.filtered(
                lambda line: line.product_id == payroll.service_id
                and line.order_partner_id.id !=
                payroll.sale_order_id.kw_patient_id.id).mapped('price_total'))
            payer_move_ids = payroll.sale_order_id.invoice_ids.filtered(
                lambda x: x.partner_id != payroll.sale_order_id.kw_patient_id
                and x.state != 'cancel')
            invoice_line_ids = payer_move_ids.mapped(
                'invoice_line_ids').filtered(
                lambda x: payroll.sale_order_id in x.sale_line_ids
                .mapped('order_id')
                and x.product_id == payroll.service_id)
            payroll.kw_report_invoiced_amount_for_other = sum(
                invoice_line_ids.mapped('price_total'))
            payroll.kw_report_not_invoiced_amount_for_other = \
                total_payers - sum(invoice_line_ids.mapped('price_total'))

    @api.depends('sale_order_line_id.product_uom_qty')
    def _compute_kw_sale_order_line_uom_qty(self):
        for payroll in self:
            payroll.kw_sale_order_line_uom_qty = \
                payroll.sale_order_line_id.product_uom_qty
