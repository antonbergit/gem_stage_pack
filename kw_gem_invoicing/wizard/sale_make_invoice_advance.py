import logging

from odoo import models, fields, api, exceptions, _

_logger = logging.getLogger(__name__)


class SaleAdvancePaymentInv(models.TransientModel):
    _inherit = 'sale.advance.payment.inv'

    kw_payer_ids = fields.Many2many(
        comodel_name='res.partner', )

    kw_payer_is_required = fields.Boolean()

    kw_payer_id = fields.Many2one(
        comodel_name='res.partner', domain="[('id', 'in', kw_payer_ids)]",
        string='Сhoose Payer', )

    kw_invoice_type = fields.Selection([
        ('consolidated', 'Consolidated invoice'),
        ('single', 'Single invoice'), ], default='single', )
    kw_date_from = fields.Datetime()
    kw_date_to = fields.Datetime()
    kw_order_ids = fields.Many2many(
        comodel_name='sale.order',
        relation='gem_kw_order_rel', )

    @api.model
    def default_get(self, field_list):
        result = super().default_get(field_list)
        if self._context.get('kw_invoice_type'):
            result['kw_invoice_type'] = self._context.get(
                'kw_invoice_type')
        if not (self._context.get('active_model') == 'sale.order' and
                self._context.get('active_id', False)):
            return result
        payer_ids = []
        for obj in self._context.get('active_ids'):
            sale_order_id = self.env['sale.order'].search([('id', '=', obj)])

            # Create Consolidated Invoice
            if len(self._context.get('active_ids')) > 1:
                payer_ids += sale_order_id.order_line.filtered(
                    lambda x: x.invoice_status == 'to invoice' and
                    x.order_partner_id.company_type == 'company').mapped(
                        'order_partner_id.id')
            # Create Invoice
            else:
                payer_ids += sale_order_id.order_line.filtered(
                    lambda x: x.invoice_status == 'to invoice').mapped(
                    'order_partner_id.id')
        result['kw_order_ids'] = [(6, 0, self._context.get('active_ids'))]
        result['kw_payer_ids'] = [(6, 0, payer_ids)]
        result['kw_payer_is_required'] = payer_ids

        if len(result['kw_payer_ids']) == 1 and payer_ids:
            result['kw_payer_id'] = payer_ids[0]

        return result

    def create_invoices(self):
        kw_payer_id = self.kw_payer_id.id
        return super(SaleAdvancePaymentInv, self.with_context(
            kw_order_ids=self.kw_order_ids,
            kw_date_to=self.kw_date_to,
            kw_date_from=self.kw_date_from, kw_payer_id=kw_payer_id,
            kw_invoice_type='single')).create_invoices()

    def create_consolidated_inv(self):
        if not self.kw_payer_ids:
            raise exceptions.UserError(
                _("There is nothing to invoice!"))

        sale_orders = self.env['sale.order'].browse(
            self._context.get('active_ids', []))
        for sale_order_id in sale_orders:
            kw_date_order = sale_order_id.date_order

            self.kw_date_from = min(kw_date_order, self.kw_date_from) \
                if self.kw_date_from else kw_date_order
            self.kw_date_to = max(kw_date_order, self.kw_date_to) \
                if self.kw_date_to else kw_date_order

        move_id = sale_orders.with_context(
            kw_order_ids=self.kw_order_ids,
            kw_date_to=self.kw_date_to,
            kw_date_from=self.kw_date_from,
            kw_payer_id=self.kw_payer_id.id,
            kw_invoice_type='consolidated')._create_consolidated_inv(
            final=self.deduct_down_payments)

        if len(move_id) == 1:
            res = {
                'type': 'ir.actions.act_window',
                'res_model': 'account.move',
                'view_mode': 'form',
                'res_id': move_id.id,
                'views': [(False, 'form')], }
        else:
            res = sale_orders.action_view_invoice()

        if self._context.get('open_invoices', False):
            return res
        return {'type': 'ir.actions.act_window_close'}
