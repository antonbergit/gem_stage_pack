
from odoo import models, fields, api


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    kw_report_invoiced_amount_for_other = fields.Float(
        compute='_compute_rep_invoices', compute_sudo=True, store=True)
    kw_report_not_invoiced_amount_for_other = fields.Float(
        compute='_compute_rep_invoices', compute_sudo=True, store=True)
    kw_report_payer_agreement_id = fields.Many2one(
        comodel_name='agreement', compute_sudo=True,
        compute='_compute_agreement_id', store=True)
    kw_report_company_type = fields.Selection(
        selection=[('person', 'Individual'), ('company', 'Company')],
        compute='_compute_company_type', compute_sudo=True, store=True)

    @api.depends('order_id.is_multiple_payers',
                 'order_id.kw_order_payment_ids', 'order_partner_id')
    def _compute_agreement_id(self):
        for res in self:
            if res.order_id.is_multiple_payers \
                    and res.order_id.kw_order_payment_ids:
                agreement = res.order_id.kw_order_payment_ids.filtered(
                    lambda lag:
                    lag.partner_id == res.order_partner_id).mapped(
                    'payer_agreement_id')
            else:
                agreement = res.order_id.kw_agreement_id
            res.kw_report_payer_agreement_id = agreement

    @api.depends('order_partner_id')
    def _compute_company_type(self):
        for obj in self:
            obj.kw_report_company_type = obj.order_partner_id.company_type

    @api.depends('order_id.invoice_ids')
    def _compute_rep_invoices(self):
        for obj in self:
            invoice_ids = obj.order_id.invoice_ids.filtered(
                lambda x: x.partner_id.id == obj.order_partner_id.id
                and x.state == 'posted')
            invoice_line_ids = invoice_ids.mapped(
                'invoice_line_ids').filtered(
                lambda x: obj.order_id in x.sale_line_ids.mapped('order_id')
                and x.product_id == obj.product_id)
            obj.kw_report_invoiced_amount_for_other = sum(
                invoice_line_ids.mapped('price_total'))
            total_payers = sum(obj.order_id.order_line.filtered(
                lambda line: line.order_partner_id == obj.order_partner_id and
                line.product_id == obj.product_id).mapped('price_total'))
            obj.kw_report_not_invoiced_amount_for_other = \
                total_payers - sum(invoice_line_ids.mapped('price_total'))
