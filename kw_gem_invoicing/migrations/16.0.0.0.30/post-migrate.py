import logging

from odoo import api, SUPERUSER_ID

_logger = logging.getLogger(__name__)


def migrate(cr, installed_version):
    env = api.Environment(cr, SUPERUSER_ID, {})
    _logger.info('start migrate')

    for payroll in env['kw.gem.payroll'].search([]):
        _logger.info(f'---{payroll.kw_report_payer_types}')
        payroll._compute_rep_payer_name()
        _logger.info(f'changed_to: {payroll.kw_report_payer_types}')

    _logger.info('end migrate')
