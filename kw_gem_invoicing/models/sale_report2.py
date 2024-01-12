import logging

from odoo import models, fields, _

_logger = logging.getLogger(__name__)


class AccountInvoiceSaleReport2(models.Model):
    _name = 'kw.gem.sale.report2'
    _auto = False
    _description = 'Report on Cases/Payers (1 case - number of payers)'

    payer_id = fields.Many2one(
        comodel_name='res.partner', string="Payers")
    payer_agreement_id = fields.Many2one(
        comodel_name="agreement",
        string="All Payers' Agreement", )
    company_type = fields.Selection(
        selection=[('person', 'Individual'), ('company', 'Company')],
        string='Payer Type', )
    payer_invoiced_amount_for_other = fields.Float(
        string="Invoiced Amount to Other Payers", )
    payer_not_invoiced_amount_for_other = fields.Float(
        string="Not Invoiced Amount to Other Payers", )
    order_id = fields.Many2one(comodel_name='sale.order')
    name = fields.Char(string="Sale Order")
    date = fields.Datetime(string="Order Datе")
    kw_stage = fields.Selection(
        string='Order Status', selection=[
            ('draft', _('New')),
            ('confirm', _('Registered')),
            ('progress', _('Laboratory')),
            ('described', _('Described')),
            ('cassettes', _('Cassettes')),
            ('process', _('Processing')),
            ('slides', _('Slides')),
            ('colored', _('Colored')),
            ('preparation_done', _('Preparation done')),
            ('result', _('Conclusion start')),
            ('conclusion_to_be_confirmed', _('Conclusion to be confirmed')),
            ('conclusion', _('Conclusion done')),
            ('sent', _('Conclusion sent')),
            ('archive', _('Archive')),
            ('canceled', _('Canceled')),
        ], )
    archive_date = fields.Datetime(string='Archiving Date', )
    conclusion_date = fields.Datetime()
    month_end_date = fields.Date()
    patient_id = fields.Many2one(comodel_name='res.partner', string='Patient')
    years_old_on_report = fields.Integer(string="Patient's Age(on report day)")
    years_old_on_conclusion = fields.Integer(
        string="Patient's Age(on conclusion day)", )
    gender = fields.Selection([
        ('male', 'Male'),
        ('female', 'Female'),
        ('other', 'Other / Undefined')],
        string="Patient's Gender", )
    partner_id = fields.Many2one(
        comodel_name='res.partner', string="Main payer", )
    agreement_id = fields.Many2one(
        comodel_name="agreement",
        string='Main Agreement', )
    subtotal_before_discount = fields.Float()
    total_discount_amount = fields.Float(string="Total Discount", )
    total_service = fields.Float(string="Total Payable Amount", )
    total_patient = fields.Float(string='Total Payable Amount for Patient', )
    total_payers = fields.Float(string="Total Payable Amount for Other Payers")
    clinical_diagnosis_id = fields.Char(
        # comodel_name='kw.sale.order.clinical.diagnosis',
        string="Diagnosis from Initial Document", )
    sending_organization = fields.Many2one(comodel_name='res.partner', )
    surgery_name_id = fields.Many2one(
        comodel_name='kw.gem.surgery.name', string="Surgery name", )
    surgery_date = fields.Date()
    received_material = fields.Char(string="Materials from Initial Document", )
    total_containers = fields.Integer(string="Total Incoming Containers", )
    total_cassettes = fields.Integer(string="Total Incoming Cassettes", )
    total_slides = fields.Integer(string="Total Incoming Slides", )
    number_of_services = fields.Integer()
    names_of_services = fields.Char(
        string='All Services Names', comodel_name='product.product', )
    sample_qty = fields.Integer(string='Sample Q-ty', )
    cassette_qty = fields.Integer(string='Cassette Q-ty', )
    slide_qty = fields.Integer(string='Slide Q-ty', )
    sample_names = fields.Char(string='Materials from Object', )
    examtype_numbers = fields.Integer(string='Number of Examinations', )
    examination_names = fields.Char()
    icd = fields.Many2one(string="ICD from Conlcusion",
                          comodel_name='kw.sale.order.clinical.diagnosis', )
    questionnaire = fields.Char()
    microscopy = fields.Char(string='Microscopy Template', )
    user_id = fields.Many2one(comodel_name="res.users", string="Salesperson")
    invoice_status = fields.Selection([
        ('upselling', 'Upselling Opportunity'),
        ('invoiced', 'Fully Invoiced'),
        ('to invoice', 'To Invoice'),
        ('no', 'Nothing to Invoice'),
        ("partially_invoiced", "Partially invoiced")],
        string="Invoice Status for Order", )
    res_lab_assist = fields.Char(string='Responsible Laboratory Assistant', )
    user_create_by = fields.Char(string='Conclusion Created by', )
    user_complete_by = fields.Char(string='Conclusion Completed by', )
    payments_sum = fields.Float(string="Payment Made by Patient", )
    payments_amount_due = fields.Float(string="Patient's Amount Due", )

    service_name = fields.Char(default='', store=True)
    doctor_1 = fields.Char(default='', store=True)
    doctor_2 = fields.Char(default='', store=True)
    service_code = fields.Char(default='', store=True)
    invoice_number = fields.Char()
    invoice_date = fields.Date()

    def _select(self, fields_=None):
        return self._select_sale(fields_)

    def _select_sale(self, fields_=None):
        if not fields_:
            fields_ = {}
        select_ = """SELECT
            payment.id as id,
            payment.partner_id as payer_id,
            CASE WHEN payment.kw_report_payer_type = NULL then NULL else
                payment.kw_report_payer_type END as company_type,
            payment.payer_agreement_id as payer_agreement_id,
            SUM(CASE WHEN l.order_id = payment.sale_order_id and
                l.order_partner_id = payment.partner_id then
                l.subtotal_before_discount else 0 END)
                as subtotal_before_discount,
            SUM(CASE WHEN l.order_id = s.id and l.order_partner_id =
                payment.partner_id then CAST(l.kw_discount_amount
                AS numeric(10, 2)) else 0 END) as total_discount_amount,
            SUM(CASE WHEN l.order_id = s.id and l.order_partner_id =
                payment.partner_id then l.price_total else 0 END)
                as total_service,
            SUM(CASE WHEN l.order_id = s.id and l.order_partner_id =
                payment.partner_id and payment.partner_id = s.kw_patient_id
                then l.price_total else 0 END) as total_patient,
            SUM(CASE WHEN l.order_id = s.id and l.order_partner_id =
                payment.partner_id then l.price_total else 0 END)
                 as total_payers,
            payment.sale_order_id as order_id,
            s.name as name,
            s.kw_stage as kw_stage,
            s.kw_archive_date as archive_date,
            s.date_order as date,
            COUNT(DISTINCT CASE WHEN l.order_partner_id = payment.partner_id
                then l.product_id END) as number_of_services,
            CASE WHEN s.kw_report_qty_examinations = NULL then 0 else
            s.kw_report_qty_examinations END as examtype_numbers,
            CASE WHEN s.kw_report_examination_names = '' or
                s.kw_report_examination_names is NULL then '' else
                s.kw_report_examination_names END as examination_names,
            CASE WHEN s.kw_report_all_service_name = '' or
                s.kw_report_all_service_name is NULL then NULL else
                s.kw_report_all_service_name END as names_of_services,
            CASE WHEN s.kw_report_received_material = '' or
                s.kw_report_received_material is NULL then NULL else
                s.kw_report_received_material END as received_material,
            s.kw_conclusion_completion_date as conclusion_date,
            s.kw_report_month_end_date as month_end_date,
            s.kw_patient_id as patient_id,
            EXTRACT(YEAR FROM age(NOW(), rp.birthday)) as years_old_on_report,
            EXTRACT(YEAR FROM age(s.kw_conclusion_completion_date,
                rp.birthday)) as years_old_on_conclusion,
            rp.gender as gender,
            s.partner_id as partner_id,
            s.kw_agreement_id as agreement_id,
            s.kw_report_clinical_diagnosis as clinical_diagnosis_id,
            s.kw_sending_organization as sending_organization,
            s.kw_surgery_name_id as surgery_name_id,
            s.kw_clinical_diagnose_id as icd,
            s.kw_surgery_date as surgery_date,
            s.kw_total_containers as total_containers,
            s.kw_total_cassettes as total_cassettes,
            s.kw_total_slides as total_slides,
            CASE WHEN s.kw_questionnaire_text = '' then NULL else
                s.kw_questionnaire_text END as questionnaire,
            CASE WHEN s.kw_microscopy_text = '' then NULL else
                s.kw_microscopy_text END as microscopy,
            CASE WHEN s.kw_report_sample_names = '' or s.kw_report_sample_names
                is NULL then NULL else s.kw_report_sample_names END
                as sample_names,
            NULL as service_name,
            NULL as service_code,
            NULL as doctor_1,
            NULL as doctor_2,
            s.user_id as user_id,
            s.invoice_status,
            s.kw_responsible_assistant as res_lab_assist,
            s.kw_conclusion_started_by as user_create_by,
            s.kw_report_sample_qty as sample_qty,
            s.kw_report_cassette_qty as cassette_qty,
            s.kw_report_slide_qty as slide_qty,
            s.kw_conclusion_completed_by as user_complete_by,
            payment.kw_report_payments_sum as payments_sum,
            payment.kw_report_payments_amount_due as payments_amount_due,
            payment.kw_report_payer_invoiced_amount_for_other
                as payer_invoiced_amount_for_other,
            payment.kw_report_payer_not_invoiced_amount_for_other
                as payer_not_invoiced_amount_for_other,
            payment.create_uid as create_uid,
            payment.create_date as create_date,
            payment.write_uid as write_uid,
            payment.write_date as write_date,
            '' as invoice_number,
            '' as invoice_date
            """
        for field in fields_.values():
            select_ += field
        return select_

    def _from_sale(self, from_clause=''):
        from_ = """
            FROM kw_sale_order_payment payment
            LEFT JOIN sale_order s ON
            (s.id = payment.sale_order_id)
            LEFT JOIN res_partner rp ON (s.kw_patient_id = rp.id)
            LEFT JOIN sale_order_line l ON (s.id = l.order_id)
            %s""" % from_clause
        return from_

    def _group_by_sale(self, groupby=''):
        groupby_ = """
            GROUP BY
            payment.id,
            s.id,
            rp.gender,
            s.partner_id,
            s.kw_clinical_diagnose_id,
            rp.birthday
            %s
        """ % (groupby)
        return groupby_

    # payment.partner_id,,
    #

    def _where(self):
        return '''WHERE payment.partner_id IS NOT NULL
                    AND l.kw_product_qty != 0
                    AND l.subtotal_before_discount != 0'''

    @property
    def _table_query(self):
        return '%s %s %s %s' % (self._select(), self._from_sale(),
                                self._where(), self._group_by_sale())
