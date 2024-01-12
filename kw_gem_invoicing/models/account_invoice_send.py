import logging

from odoo import models, api, fields

_logger = logging.getLogger(__name__)


class AccountInvoiceSend(models.TransientModel):
    _inherit = 'account.invoice.send'
    _description = 'Extention default_get() logic'

    kw_additional_recipients = fields.Many2many(
        comodel_name='financial.email',
    )

    @api.model
    def default_get(self, vals):
        defaults = super(AccountInvoiceSend, self).default_get(vals)
        default_template = self.env['mail.template'].sudo().search([
            ('model', '=', 'account.move'),
            ('template_fs', '=',
             'kw_gem_invoicing/data/mail_template_data.xml')
        ], limit=1)
        defaults['template_id'] = default_template.id \
            if default_template else False
        return defaults

    @api.onchange('partner_ids')
    def update_financial_emails(self):
        email_ids = []
        for partner in self.partner_ids:
            email_ids.extend(partner.kw_financial_email_ids.ids)
        self.kw_additional_recipients = [(6, None, email_ids)]

    def kw_send_and_print_action(self):
        self.ensure_one()
        recipients = [mail.name for mail in self.kw_additional_recipients]
        active_record = self.env[self.model].browse(self.res_id)
        template = self.env['mail.template'].sudo().search([
            ('model', '=', 'account.move'),
            ('template_fs', '=',
             'kw_gem_invoicing/data/mail_template_data.xml')
        ], limit=1)
        vals = {'email_to': ','.join(recipients)}
        template.send_mail(
            res_id=active_record.id,
            force_send=True,
            email_values=vals
        )
        return super().send_and_print_action()
