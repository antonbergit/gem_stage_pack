# pylint: disable=too-many-branches, consider-using-ternary
# pylint: disable=too-many-nested-blocks, too-many-locals
import base64
import logging

from odoo import fields, models, tools, api
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class MailTemplate(models.Model):
    _inherit = 'mail.template'
    _description = 'extend field report_template'

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
        return defaults

    def write(self, vals):
        # set the default attachments
        if self.template_fs == 'kw_gem_invoicing/data/mail_template_data.xml':
            reports = self.env['ir.actions.report'].sudo().search([
                ('model', '=', 'account.move'),
                ('report_name', 'ilike', 'kw_gem_invoicing')
            ]).ids
            vals['kw_report_template_ids'] = [(6, None, reports)]
        return super(MailTemplate, self).write(vals)

    def generate_email(self, res_ids, vals):
        """This function was overwritten from original to resolve the
            problem with multiple files attached.

            the iteration through all attacments was added and
             'report_template' was replaced with 'kw_report_template_ids'

            source: addons/mail/models/mail_template.py
        """
        self.ensure_one()
        multi_mode = True
        if isinstance(res_ids, int):
            res_ids = [res_ids]
            multi_mode = False

        results = dict()
        for _, (template, template_res_ids)\
                in self._classify_per_lang(res_ids).items():
            for field in vals:
                generated_field_values = template._render_field(
                    field, template_res_ids,
                    post_process=(field == 'body_html')
                )
                for res_id, field_value in generated_field_values.items():
                    results.setdefault(res_id, dict())[field] = field_value
            # compute recipients
            if any(field in vals for field
                   in ['email_to', 'partner_to', 'email_cc']):
                results = template.generate_recipients(
                    results, template_res_ids)
            # update values for all res_ids
            for res_id in template_res_ids:
                values = results[res_id]
                if values.get('body_html'):
                    values['body'] = tools.html_sanitize(values['body_html'])
                # if asked in vals to return, parse generated date into
                # tz agnostic UTC as expected by ORM
                scheduled_date = values.pop('scheduled_date', None)
                if 'scheduled_date' in vals and scheduled_date:
                    parsed_datetime = self.env[
                        'mail.mail']._parse_scheduled_datetime(
                        scheduled_date)
                    values['scheduled_date'] = parsed_datetime.replace(
                        tzinfo=None) if parsed_datetime else False

                # technical settings
                values.update(
                    mail_server_id=template.mail_server_id.id or False,
                    auto_delete=template.auto_delete,
                    model=template.model,
                    res_id=res_id or False,
                    attachment_ids=[
                        attach.id for attach in template.attachment_ids],
                )

            # Add report in attachments: generate once for all template_res_ids
            if template.kw_report_template_ids:
                for res_id in template_res_ids:
                    move_name = self.env['account.move'].sudo().search([
                        ('id', '=', res_id)
                    ]).name
                    attachments = []
                    templates = template.kw_report_template_ids\
                        if template.kw_report_template_ids \
                        else [template.report_template]
                    for obj in templates:
                        report = obj
                        report_service = report.print_report_name \
                            .split('%')[0][1:] + move_name

                        if report.report_type in ['qweb-html', 'qweb-pdf']:
                            result, report_format = self.env[
                                'ir.actions.report'
                            ]._render_qweb_pdf(report, [res_id])
                        else:
                            res = self.env[
                                'ir.actions.report'
                            ]._render(report, [res_id])
                            if not res:
                                raise UserError(_(
                                    'Unsupported report type %s found.',
                                    report.report_type
                                ))
                            result, report_format = res

                        # TODO in trunk, change return format to binary
                        # to match message_post expected format
                        result = base64.b64encode(result)
                        report_name = report_service
                        ext = "." + report_format
                        if not report_name.endswith(ext):
                            report_name += ext
                        attachments.append((report_name, result))
                        results[res_id]['attachments'] = attachments
        return multi_mode and results or results[res_ids[0]]
