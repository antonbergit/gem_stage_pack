import logging

from odoo import api, SUPERUSER_ID

_logger = logging.getLogger(__name__)


def migrate(cr, installed_version):
    env = api.Environment(cr, SUPERUSER_ID, {})
    _logger.info('start migrate')

    for order_payment in env['kw.gem.payroll'].sudo().search([]):
        order_payment._compute_rep_payer_name()

    _logger.info('end migrate')
