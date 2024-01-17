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
        default_template = self.env.ref(
            'kw_gem_invoicing.account_move_mail_template'
        )
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
        template = self.env.ref(
            'kw_gem_invoicing.account_move_mail_template'
        )
        template.attachment_ids = [(6, None, self.attachment_ids.ids)]
        vals = {'email_to': ','.join(recipients)}
        # we won't use 'force_send=True' here for acces this object
        mail_id = template.send_mail(
            res_id=active_record.id,
            force_send=False,
            email_values=vals,
        )
        mail_mail = self.env['mail.mail'].browse(mail_id)
        # manually create a mail.message record
        self.env['mail.message'].create({
            'record_name': active_record.name,
            'res_id': active_record.id,
            'subject': mail_mail.subject,
            'body': mail_mail.body,
            'attachment_ids': [(6, 0, mail_mail.attachment_ids.ids)],
            'email_from': False,
            'model': self.model,
        })
        # now we send & clean email
        mail_mail.send()
        if self.is_print:
            # print document if necessary
            return self._print_document()
        return {'type': 'ir.actions.act_window_close'}
