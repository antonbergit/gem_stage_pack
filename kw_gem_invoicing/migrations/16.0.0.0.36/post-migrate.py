import logging

from odoo import api, SUPERUSER_ID

_logger = logging.getLogger(__name__)


def migrate(cr, installed_version):
    env = api.Environment(cr, SUPERUSER_ID, {})
    _logger.info('start migrate')

    for payroll in env['kw.gem.payroll'].search([]):
        payroll._compute_rep_payer_name()
        payroll._compute_rep_invoices()
        payroll._compute_kw_sale_order_line_uom_qty()

    _logger.info('end migrate')
