import logging
import time

from datetime import timedelta

from odoo import models, fields, api
from odoo.exceptions import AccessError

_logger = logging.getLogger(__name__)


class Order(models.Model):
    _inherit = 'sale.order'

    @api.depends('state', 'order_line.invoice_status', 'invoice_ids.state')
    def _get_invoice_status(self):
        res = super(Order, self)._get_invoice_status()
        unconfirmed_orders = self.filtered(
            lambda so: so.state not in ['sale', 'done'])
        unconfirmed_orders.invoice_status = 'no'
        confirmed_orders = self - unconfirmed_orders
        for order in confirmed_orders:
            posted_am = order.invoice_ids.filtered(
                lambda x: x.state == 'posted')
            total_sum = sum(posted_am.mapped('amount_total_signed'))
            if posted_am \
                    and order.invoice_status not in ['invoiced', 'upselling']:
                order.invoice_status = 'partially_invoiced'
            elif total_sum == order.amount_total:
                order.invoice_status = 'invoiced'
        return res

    invoice_status = fields.Selection(
        selection_add=[("partially_invoiced", "Partially invoiced")])
    kw_payments_qty = fields.Integer(
        compute='_compute_kw_payments_qty',
        string='Payments qty',
        compute_sudo=True, )
    kw_order_invoices_ids = fields.Many2many(
        comodel_name='account.payment',
        compute='_compute_kw_payments_qty',
        compute_sudo=True)
    kw_microscopy_text = fields.Text(
        string='Microscopy Template',
        compute_sudo=True, store=True,
        compute="_compute_microscopy_text")
    kw_report_month_end_date = fields.Date(
        compute='_compute_end_month', compute_sudo=True, store=True)
    kw_report_sample_names = fields.Char(
        compute='_compute_kw_sample_names', compute_sudo=True, store=True, )
    kw_report_qty_examinations = fields.Integer(
        compute='_compute_qty_examinations',  compute_sudo=True, store=True, )
    kw_report_examination_names = fields.Char(
        compute='_compute_qty_examinations', compute_sudo=True, store=True)
    kw_report_all_service_name = fields.Char(
        compute='_compute_all_service_name', compute_sudo=True, store=True)
    kw_report_received_material = fields.Char(
        compute='_compute_received_material', compute_sudo=True, store=True)
    kw_report_payer_name = fields.Char(
        compute='_compute_payer_name',  compute_sudo=True, store=True)
    kw_report_agreement_name = fields.Char(
        compute='_compute_payer_name',  compute_sudo=True, store=True)
    kw_report_payer_types = fields.Char(
        compute='_compute_payer_name', compute_sudo=True, store=True)
    kw_report_payments_sum = fields.Float(
        compute='_compute_report_payments', compute_sudo=True, store=True, )
    kw_report_payments_sum_str = fields.Char(
        compute='_compute_report_payments', compute_sudo=True, store=True, )
    kw_report_payments_amount_due = fields.Float(
        compute='_compute_report_payments', compute_sudo=True, store=True, )
    kw_report_invoiced_amount_for_other = fields.Float(
        compute='_compute_report_invoices', compute_sudo=True, store=True, )
    kw_report_not_invoiced_amount_for_other = fields.Float(
        compute='_compute_report_invoices', compute_sudo=True, store=True, )
    kw_report_sample_qty = fields.Integer(
        compute='_compute_kw_sample_names', compute_sudo=True, store=True, )
    kw_report_cassette_qty = fields.Integer(
        compute='_compute_kw_report_cassette_qty', compute_sudo=True,
        store=True, )
    kw_report_slide_qty = fields.Integer(
        compute='_compute_kw_report_cassette_qty', compute_sudo=True,
        store=True, )
    kw_report_clinical_diagnosis = fields.Char(
        compute='_compute_kw_report_clinical_diagnosis',
        compute_sudo=True,
        store=True,
    )

    @api.depends('kw_clinical_diagnosis')
    def _compute_kw_report_clinical_diagnosis(self):
        for obj in self:
            if not obj.kw_clinical_diagnosis:
                continue

            if self.env.user.lang in obj.kw_clinical_diagnosis:
                obj.kw_report_clinical_diagnosis = \
                    obj.kw_clinical_diagnosis.get(self.env.user.lang)
            else:
                if isinstance(obj.kw_report_clinical_diagnosis, dict):
                    obj.kw_report_clinical_diagnosis = \
                        list(obj.kw_clinical_diagnosis.values())[0]
                elif isinstance(obj.kw_report_clinical_diagnosis, str):
                    obj.kw_report_clinical_diagnosis = \
                        obj.kw_clinical_diagnosis

    @api.depends('kw_conclusion_microscopy_ids')
    def _compute_microscopy_text(self):
        for obj in self:
            obj.kw_microscopy_text = ', '.join(
                obj.kw_conclusion_microscopy_ids.mapped(
                    'microscopy_id').mapped('name'))

    @api.depends('kw_container_ids')
    def _compute_received_material(self):
        for result in self:
            if result.kw_container_ids:
                names = []
                for x in result.kw_container_ids:
                    names += x.container_name_ids.mapped('name')
                result.kw_report_received_material = ', '.join(names)
            else:
                result.kw_report_received_material = ''

    @api.depends('order_line.product_id')
    def _compute_all_service_name(self):
        for result in self:
            if result.order_line:
                names = {line.product_id.name for line in result.order_line
                         if line.product_id and line.kw_product_qty != 0}
                result.kw_report_all_service_name = ', '.join(list(names))
            else:
                result.kw_report_all_service_name = ''

    @api.depends('kw_sample_ids')
    @api.constrains('kw_sample_ids')
    def _compute_qty_examinations(self):
        for result in self:
            types = []
            for x in result.kw_sample_ids:
                types += [el.name for el in x.examination_type_ids]
            result.kw_report_qty_examinations = len(types)
            result.kw_report_examination_names = ', '.join(types)

    @api.depends('kw_conclusion_completion_date')
    # @api.constrains('kw_conclusion_completion_date')
    def _compute_end_month(self):
        for record in self:
            if record.kw_conclusion_completion_date:
                next_month = record.kw_conclusion_completion_date.replace(
                    day=28) + timedelta(days=4)
                end_month = next_month - timedelta(days=next_month.day)
                record.kw_report_month_end_date = end_month
            else:
                record.kw_report_month_end_date = ''

    @api.depends('kw_sample_ids')
    # @api.constrains('kw_sample_ids')
    def _compute_kw_sample_names(self):
        for result in self:
            result.kw_report_sample_names = \
                ', '.join([', '.join(x.sample_name_ids.mapped('name'))
                           for x in result.kw_sample_ids])
            result.kw_report_sample_qty = len(result.kw_sample_ids) or 0

    @api.depends('kw_cassette_qty', 'kw_slide_ids')
    def _compute_kw_report_cassette_qty(self):
        for result in self:
            result.kw_report_cassette_qty = result.kw_cassette_qty
            # result.kw_report_cassette_qty = (
            #     self.env['kw.gem.cassette'].search_count([
            #         ('sale_order_id', '=', result.id)]))
            result.kw_report_slide_qty = (
                self.env['kw.gem.slide'].search_count([
                    ('sale_order_id', '=', result.id)]))

    @api.depends('is_multiple_payers', 'partner_id', 'order_line')
    def _compute_payer_name(self):
        for result in self:
            if result.is_multiple_payers:
                payer_ids = set(result.order_line.filtered(
                    lambda la: not la.display_type)
                    .mapped('order_partner_id.id'))
                result.kw_report_payer_name = ', '.join(
                    [x.partner_id.name
                     for x in result.kw_order_payment_ids])
                result.kw_report_agreement_name = ', '.join(
                    [x.payer_agreement_id.name
                     for x in result.kw_order_payment_ids])
            else:
                payer_ids = [result.partner_id.id]
                result.kw_report_payer_name = result.partner_id.name
                result.kw_report_agreement_name = result.kw_agreement_id.name
            payer_types = self.env['res.partner'].search([
                ('id', 'in', list(payer_ids))]).mapped('company_type')
            payer_dict = []
            for str_ in payer_types:
                if str_ == 'person':
                    payer_dict.append('Individual')
                elif str_ == 'company':
                    payer_dict.append('Company')
            result.kw_report_payer_types = ',\n'.join(payer_dict)

    @api.depends('invoice_ids.kw_payments_ids')
    def _compute_report_payments(self):
        for obj in self:
            obj.kw_report_payments_sum_str = ''
            inv = obj.invoice_ids.filtered(
                lambda line: line.state == 'posted' and
                line.partner_id == obj.kw_patient_id)
            payments = self.env['account.payment'].search([
                ('state', '=', 'posted'),
                ('id', 'in', inv.mapped('kw_payments_ids').ids)])
            if payments:
                obj.kw_report_payments_sum = sum(payments.mapped('amount'))
                obj.kw_report_payments_amount_due = (
                    sum(obj.order_line.filtered(lambda
                        line: line.order_partner_id.id == obj.kw_patient_id.id)
                        .mapped('price_total')) - obj.kw_report_payments_sum)
                continue
            obj.kw_report_payments_sum = 0
            obj.kw_report_payments_amount_due = sum(obj.order_line.filtered(
                lambda line: line.order_partner_id.id == obj.kw_patient_id.id
            ).mapped('price_total')) - obj.kw_report_payments_sum

    @api.depends('invoice_ids')
    def _compute_report_invoices(self):
        for obj in self:
            total_payers = sum(obj.order_line.filtered(
                lambda line: line.order_partner_id.id != obj.kw_patient_id.id)
                .mapped('price_total'))
            payer_move_ids = obj.invoice_ids.filtered(
                lambda x: x.partner_id.id != obj.kw_patient_id.id
                and x.state == 'posted')
            invoice_line_ids = payer_move_ids.mapped(
                'invoice_line_ids').filtered(
                lambda x: obj in x.sale_line_ids.mapped('order_id'))
            obj.kw_report_invoiced_amount_for_other = sum(
                invoice_line_ids.mapped('price_total')) or False
            obj.kw_report_not_invoiced_amount_for_other = \
                total_payers - sum(invoice_line_ids.mapped('price_total'))

    def _prepare_invoice(self):
        obj = super()._prepare_invoice()
        obj['partner_id'] = self._context.get('kw_payer_id')
        obj['kw_date_from'] = self._context.get('kw_date_from')
        obj['kw_date_to'] = self._context.get('kw_date_to')
        obj['kw_invoice_type'] = self._context.get('kw_invoice_type')
        return obj

    def _get_invoiceable_lines(self, final=False):
        kw_payer_id = self._context.get('kw_payer_id')
        lines = super()._get_invoiceable_lines(final)
        if not kw_payer_id:
            return lines.filtered(
                lambda x: x.kw_product_qty == x.qty_to_invoice
            )
        return lines.filtered(
            lambda x: x.order_partner_id.id == kw_payer_id and
            x.kw_product_qty == x.qty_to_invoice
        )

    def _compute_kw_payments_qty(self):
        for obj in self:
            payment_ids = obj.invoice_ids.mapped('kw_payments_ids')
            obj.write({
                'kw_order_invoices_ids': [(6, 0, payment_ids.ids)],
                'kw_payments_qty': len(payment_ids.ids), })

    def action_payment(self):
        view_id = \
            self.env.ref('kw_gem_invoicing.kw_gem_sale_order_payment_tree').id
        return {
            'type': 'ir.actions.act_window',
            'name': 'Payments',
            'view_mode': 'tree',
            'res_model': 'account.payment',
            'target': 'new',
            'views': [[view_id, 'tree']],
            'domain': [('id', 'in', self.kw_order_invoices_ids.ids)],
            'context': {'create': False,
                        'default_id': self.kw_order_invoices_ids.ids}
        }

    def _create_consolidated_inv(self, final=False):
        if not self.env['account.move'].check_access_rights('create', False):
            try:
                self.check_access_rights('write')
                self.check_access_rule('write')
            except AccessError:
                return self.env['account.move']
        invoice_vals_list = []
        invoice_item_sequence = 0
        invoice_line_vals = []

        time_mark = time.time()
        invoice_vals = self[0]._prepare_invoice()
        for order in self:
            order = order.with_company(order.company_id)

            invoiceable_lines = order._get_invoiceable_lines(final)
            if not any(not line.display_type for line in invoiceable_lines):
                continue
            invoice_line_vals.append((0, 0, {
                'display_type': 'line_section',
                'name': order.name,
                'sequence': invoice_item_sequence, }))
            invoice_item_sequence += 1
            down_payment_section_added = False
            for line in invoiceable_lines:
                if not down_payment_section_added and line.is_downpayment:
                    invoice_line_vals.append(
                        (0, 0, order._prepare_down_payment_section_line(
                            sequence=invoice_item_sequence,
                        )),
                    )
                    down_payment_section_added = True
                    invoice_item_sequence += 1
                invoice_line_vals.append(
                    (0, 0, line._prepare_invoice_line(
                        sequence=invoice_item_sequence,
                    )),
                )
                invoice_item_sequence += 1

            invoice_vals['invoice_line_ids'] = invoice_line_vals
        invoice_vals_list.append(invoice_vals)
        _logger.info("DEBUG#8147#: %5.2f - SO fetch invoiceable_lines",
                     (time.time() - time_mark))

        time_mark = time.time()
        moves = self.env['account.move'].sudo().with_context(
            default_move_type='out_invoice').create(invoice_vals_list)
        delta_time = time.time() - time_mark
        _logger.info("DEBUG#8147#: %5.2f s for %d l (r %7.5f spl)- AM=>AML", (
            delta_time,
            len(invoice_vals_list[0]['invoice_line_ids']),
            delta_time / len(invoice_vals_list[0]['invoice_line_ids'])
        ))

        if final:
            moves.sudo().filtered(lambda m: m.amount_total < 0). \
                action_switch_invoice_into_refund_credit_note()
        for move in moves:
            move.message_post_with_view(
                'mail.message_origin_link',
                values={'self': move, 'origin': move.line_ids.mapped(
                    'sale_line_ids.order_id')},
                subtype_id=self.env.ref('mail.mt_note').id, )

        return moves


class OrderLine(models.Model):
    _inherit = 'sale.order.line'

    def _prepare_invoice_line(self, **optional_values):
        invoice_line = super()._prepare_invoice_line(**optional_values)
        invoice_line.update({
            'discount': self.kw_discount,
            # 'quantity': self.subtotal_before_discount / self.price_unit,
            'kw_quantity': self.product_uom_qty,
            'kw_discount_amount': self.kw_discount_amount,
            'kw_subtotal_before_discount': self.subtotal_before_discount,
            'price_total': self.price_total,
        })
        return invoice_line

    # total_count_display_type = fields.Integer(
    #     compute='_compute_total_count_display_type', store=True)
    #
    # @api.depends('display_type')
    # def _compute_total_count_display_type(self):
    #     for res in self.env['sale.order.line'].search([]):
    #         res.total_count_display_type = \
    #             len(res.order_id.order_line.filtered(
    #                 lambda line:
    #                 line.display_type in ['line_section', 'line_note']))
