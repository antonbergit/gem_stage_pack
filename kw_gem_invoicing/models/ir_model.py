
from odoo import models


class SaleOrderDiagnosisValue(models.Model):
    _inherit = 'sale.order'

    def _cron_update_diagnosis(self):
        for item in self.env['sale.order'].sudo().search(
            [('kw_clinical_diagnosis', '!=', False)]
        ):
            item._compute_kw_report_clinical_diagnosis()

    def _cron_compute_invoice(self):
        for payment in self.env['kw.sale.order.payment'].search([]):
            payment._compute_payer_invoices()

    def _cron_compute_fields(self):
        for order_id in self.env['sale.order'].search([]):
            order_id._compute_received_material()
            order_id._compute_all_service_name()
            order_id._compute_qty_examinations()
            order_id._compute_end_month()
            order_id._compute_kw_sample_names()
            order_id._compute_kw_report_cassette_qty()
            order_id._compute_payer_name()
            order_id._compute_report_payments()
            order_id._compute_report_invoices()

        for line in self.env['sale.order.line'].search([]):
            line._compute_rep_invoices()
            line._compute_agreement_id()
            line._compute_company_type()

        for payroll in self.env['kw.gem.payroll'].search([]):
            payroll._compute_rep_payer_name()
            payroll._compute_rep_invoices()

        for payment in self.env['kw.sale.order.payment'].search([]):
            payment._compute_payer_type()
            payment._compute_payer_invoices()
            payment._compute_report_payment_sum()
            payment._compute_report_payments()
