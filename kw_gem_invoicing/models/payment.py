import logging

from odoo import models, fields, api

_logger = logging.getLogger(__name__)


class SaleOrderPayment(models.Model):
    _inherit = 'kw.sale.order.payment'

    kw_report_payer_type = fields.Selection(
        selection=[('person', 'Individual'), ('company', 'Company')],
        related='partner_id.company_type', store=True)
    kw_report_payer_invoiced_amount_for_other = fields.Float(
        compute='_compute_payer_invoices',
        compute_sudo=True,
        store=True
    )
    kw_report_payer_not_invoiced_amount_for_other = fields.Float(
        compute='_compute_payer_invoices',
        compute_sudo=True,
        store=True
    )
    kw_report_payments_sum = fields.Float(
        compute='_compute_report_payment_sum', store=True)
    kw_report_payments_amount_due = fields.Float(
        compute='_compute_report_payments', store=True)

    @api.depends('partner_id')
    def _compute_payer_type(self):
        for obj in self:
            obj.kw_report_payer_type = obj.partner_id.company_type

    @api.depends('sale_order_id.invoice_ids')
    def _compute_payer_invoices(self):
        for obj in self:
            payer_move_ids = obj.sale_order_id.invoice_ids.filtered(
                lambda x: x.partner_id.id == obj.partner_id.id and
                x.state in ('draft', 'posted'))
            invoice_line_ids = payer_move_ids.mapped(
                'invoice_line_ids').filtered(
                lambda x: obj.sale_order_id in x.sale_line_ids.
                mapped('order_id'))
            obj.kw_report_payer_invoiced_amount_for_other = sum(
                invoice_line_ids.mapped('price_total'))
            total_payers = sum(obj.sale_order_id.order_line.filtered(
                lambda line: line.order_partner_id == obj.partner_id)
                .mapped('price_total'))
            obj.kw_report_payer_not_invoiced_amount_for_other = \
                total_payers - obj.kw_report_payer_invoiced_amount_for_other

    @api.depends('sale_order_id.invoice_ids.kw_payments_ids')
    def _compute_report_payment_sum(self):
        for obj in self:
            if obj.partner_id.id != obj.sale_order_id.kw_patient_id.id:
                obj.kw_report_payments_sum = 0
                continue
            inv = obj.sale_order_id.invoice_ids.filtered(
                lambda line: line.state == 'posted'
                and line.partner_id == obj.partner_id)
            payments = self.env['account.payment'].search([
                ('state', '=', 'posted'),
                ('id', 'in', inv.mapped('kw_payments_ids').ids)
            ])
            if payments:
                obj.kw_report_payments_sum = sum(
                    payments.mapped('amount'))
                continue
            obj.kw_report_payments_sum = 0

    @api.depends('sale_order_id.invoice_ids.kw_payments_ids')
    def _compute_report_payments(self):
        for obj in self:
            if obj.partner_id != obj.sale_order_id.kw_patient_id:
                obj.kw_report_payments_sum = 0
                obj.kw_report_payments_amount_due = 0
                continue
            price_total = obj.sale_order_id.order_line.filtered(
                lambda line: obj.sale_order_id.kw_patient_id.id ==
                line.order_partner_id.id).mapped('price_total')
            obj.kw_report_payments_amount_due = (
                sum(price_total) - obj.kw_report_payments_sum)
