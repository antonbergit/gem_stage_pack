import logging

from odoo import models, fields, _

_logger = logging.getLogger(__name__)


class AccountInvoiceReport(models.Model):
    _name = 'kw.gem.service.report.payer'
    _auto = False
    _description = 'Report on Services/Payers (1 service - number of payers)'

    payer_agreement_id = fields.Many2one(
        comodel_name='agreement', string="All Payers' Agreement", )
    company_type = fields.Selection(
        string='Payer Type',
        selection=[('person', 'Individual'), ('company', 'Company')], )
    payer_id = fields.Many2one(comodel_name='res.partner', string="Payers")
    product_id = fields.Many2one(
        comodel_name='product.product', string="Service Name")
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
    received_material = fields.Char(string="Materials from Initial Document")
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
    invoiced_amount_for_other = fields.Float(
        string="Invoiced Amount to Other Payers", )
    not_invoiced_amount_for_other = fields.Float(
        string="Not Invoiced Amount to Other Payers", )
    payments_sum_str = fields.Char(string="Payment Made by Patient", )
    payments_amount_due = fields.Float(string="Patient's Amount Due", )
    doctor_1 = fields.Many2one(comodel_name='res.users')
    doctor_2 = fields.Many2one(comodel_name='res.users')
    service_code = fields.Many2one(
        comodel_name='kw.gem.codes', string="Service code")
    invoice_number = fields.Char()
    invoice_date = fields.Date()

    def _select(self, fields_=None):
        return self._select_sale(fields_)

    def _select_sale(self, fields_=None):
        if not fields_:
            fields_ = {}
        select_ = """SELECT
        l.id as id,
        l.product_id as product_id,
        l.order_partner_id as payer_id,
        l.order_id as order_id,
        s.name as name,
        s.kw_stage as kw_stage,
        s.kw_archive_date as archive_date,
        s.date_order as date,
        payroll.code_id as service_code,
        payroll.doctor1_id as doctor_1,
        payroll.doctor2_id as doctor_2,
        s.create_uid as create_uid,
        s.create_date as create_date,
        s.write_uid as write_uid,
        s.write_date as write_date,
        rp.gender as gender,
        s.partner_id as partner_id,
        s.kw_agreement_id as agreement_id,
        l.kw_report_payer_agreement_id as payer_agreement_id,
        l.kw_report_company_type as company_type,
        s.kw_report_clinical_diagnosis as clinical_diagnosis_id,
        s.kw_sending_organization as sending_organization,
        s.kw_surgery_name_id as surgery_name_id,
        s.kw_clinical_diagnose_id as icd,
        s.kw_surgery_date as surgery_date,
        s.kw_total_containers as total_containers,
        s.kw_total_cassettes as total_cassettes,
        s.kw_total_slides as total_slides,
        s.kw_questionnaire_text as questionnaire,
        s.kw_microscopy_text as microscopy,
        CASE WHEN s.kw_report_sample_names = '' then NULL else
            s.kw_report_sample_names END as sample_names,
        s.user_id as user_id,
        s.invoice_status,
        s.kw_responsible_assistant as res_lab_assist,
        s.kw_conclusion_started_by as user_create_by,
        s.kw_report_sample_qty as sample_qty,
        s.kw_report_cassette_qty as cassette_qty,
        s.kw_report_slide_qty as slide_qty,
        s.kw_conclusion_completed_by as user_complete_by,
        s.kw_conclusion_completion_date as conclusion_date,
        s.kw_report_month_end_date as month_end_date,
        s.kw_patient_id as patient_id,
        EXTRACT(YEAR FROM age(NOW(), rp.birthday)) as years_old_on_report,
        EXTRACT(YEAR FROM age(s.kw_conclusion_completion_date, rp.birthday))
            as years_old_on_conclusion,
        COUNT(DISTINCT l.product_id) as number_of_services,
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
        SUM(l.subtotal_before_discount) as subtotal_before_discount,
        SUM(CAST(l.kw_discount_amount AS numeric(10, 2)))
            as total_discount_amount,
        SUM(CASE WHEN l.price_total IS NOT NULL then l.price_total else 0 END)
            as total_service,
        SUM(CASE WHEN l.order_partner_id = s.kw_patient_id
            then l.price_total else 0 END) as total_patient,
        SUM(CASE WHEN l.price_total IS NOT NULL then l.price_total else 0 END)
            as total_payers,
        '' as payments_sum_str,
        SUM(CASE WHEN l.order_partner_id = s.kw_patient_id then l.price_total
            else 0 END) as payments_amount_due,
        l.kw_report_invoiced_amount_for_other as invoiced_amount_for_other,
        l.kw_report_not_invoiced_amount_for_other
            as not_invoiced_amount_for_other,
        '' as invoice_number,
        '' as invoice_date
        """
        for field in fields_.values():
            select_ += field
        return select_

    def _from_sale(self, from_clause=''):
        from_ = """
            FROM sale_order_line l
            LEFT JOIN sale_order s ON s.id = l.order_id
            LEFT JOIN res_partner rp ON s.kw_patient_id = rp.id
            LEFT JOIN kw_gem_payroll payroll
                ON payroll.service_id = l.product_id
            %s
           """ % from_clause
        return from_

    def _where(self):
        return '''
            WHERE l.display_type IS NULL
            AND l.product_id IS NOT NULL
            AND s.id = payroll.sale_order_id
            AND l.kw_product_qty != 0'''

    def _group_by_sale(self, groupby=''):
        groupby_ = """
               GROUP BY
               s.id,
               rp.gender,
               rp.birthday,
               s.partner_id,
               s.kw_clinical_diagnose_id,
               l.id,
               l.product_id,
               payroll.code_id,
               payroll.doctor1_id,
               payroll.doctor2_id
               %s
           """ % (groupby)
        return groupby_

    @property
    def _table_query(self):
        return '%s %s %s %s' % (self._select(), self._from_sale(),
                                self._where(), self._group_by_sale())
