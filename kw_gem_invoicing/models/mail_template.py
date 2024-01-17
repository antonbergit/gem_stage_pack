import logging

from odoo import fields, models, api

_logger = logging.getLogger(__name__)


class MailTemplate(models.Model):
    _inherit = 'mail.template'
    _description = 'add multiple report_templates'

    kw_report_template_ids = fields.Many2many(
        comodel_name='ir.actions.report',
        string='Invoice Attachments',
        domain="[('model', '=', 'account.move')]"
    )

    @api.model
    def default_get(self, vals):
        defaults = super(MailTemplate, self).default_get(vals)
        # set the mail server
        mail_server = self.env['ir.mail_server'].sudo().search([
            ('smtp_host', '=', 'server.zhordaniaclinic.ge')
        ], limit=1)
        defaults['mail_server_id'] = mail_server.id if mail_server else None
        # set the default report_templates
        reports = self.env['ir.actions.report'].sudo().search([
            ('model', '=', 'account.move'),
            ('report_name', 'ilike', 'kw_gem_invoicing')
        ]).ids
        defaults['kw_report_template_ids'] = [(6, None, reports)]
        return defaults
