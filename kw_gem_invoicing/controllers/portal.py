from odoo import http
from odoo.addons.portal.controllers.portal import CustomerPortal
from odoo.exceptions import AccessError, MissingError
from odoo.http import request


class PortalAccount(CustomerPortal):

    @http.route(
        ['/preview/<inv_type>/<int:invoice_id>'],
        type='http', auth="public", website=True
    )
    def portal_inv1_detail(self, inv_type, invoice_id, access_token=None,
                           report_type=None, download=False, **kw):
        try:
            invoice_sudo = self._document_check_access(
                'account.move', invoice_id, access_token
            )
        except (AccessError, MissingError):
            return request.redirect('/my')
        reports = {
            'inv1': 'action_kw_gem_invoicing_report_inv1',
            'inv2p1': 'action_kw_gem_invoicing_report_inv2_p1',
            'inv2p2': 'action_kw_gem_invoicing_report_inv2_p2'
        }
        return self._show_report(
            model=invoice_sudo,
            report_type=report_type,
            report_ref=f'kw_gem_invoicing.{reports.get(inv_type)}',
            download=download
        )
