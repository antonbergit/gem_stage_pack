import logging

from odoo import models

_logger = logging.getLogger(__name__)


class ResPartner(models.Model):
    _inherit = 'res.partner'

    def set_email_if_empty(self):
        """Set partner email if not set (copy latest financial email)
        """
        for partner in self:
            conditions = (
                len(partner.kw_financial_email_ids.ids) > 0,
                not partner.email
            )
            if all(conditions):
                partner.email = partner.kw_financial_email_ids[-1].name
