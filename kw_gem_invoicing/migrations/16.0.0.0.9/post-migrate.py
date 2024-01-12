import logging

from odoo import api, SUPERUSER_ID

_logger = logging.getLogger(__name__)


def migrate(cr, installed_version):
    env = api.Environment(cr, SUPERUSER_ID, {})
    _logger.info('start migrate')

    for order_id in env['sale.order'].search([]):
        order_id._compute_received_material()
        order_id._compute_all_service_name()
        order_id._compute_qty_examinations()
        order_id._compute_end_month()
        order_id._compute_kw_sample_names()
        order_id._compute_kw_report_cassette_qty()
        order_id._compute_payer_name()
        order_id._compute_report_payments()
        order_id._compute_report_invoices()

    for line in env['sale.order.line'].search([]):
        line._compute_rep_invoices()
        line._compute_agreement_id()
        line._compute_company_type()

    for payroll in env['kw.gem.payroll'].search([]):
        payroll._compute_rep_payer_name()
        payroll._compute_rep_invoices()

    for payment in env['kw.sale.order.payment'].search([]):
        payment._compute_payer_type()
        payment._compute_payer_invoices()
        payment._compute_payer_invoices()
        payment._compute_report_payment_sum()
        payment._compute_report_payments()

    _logger.info('end migrate')
