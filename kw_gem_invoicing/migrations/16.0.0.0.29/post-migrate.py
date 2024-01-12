import logging

from odoo import api, SUPERUSER_ID

_logger = logging.getLogger(__name__)


def migrate(cr, installed_version):
    env = api.Environment(cr, SUPERUSER_ID, {})
    _logger.info('start migrate')

    for order_id in env['sale.order'].search([]):
        order_id._compute_report_invoices()

    for line in env['sale.order.line'].search([]):
        line._compute_rep_invoices()

    _logger.info('end migrate')
