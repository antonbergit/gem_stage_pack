import logging

from odoo import models, fields, _

_logger = logging.getLogger(__name__)


class KwGemServiceReportPayerInvoice(models.Model):
    _name = 'kw.gem.report.service.payer.invoice'
    _auto = False
    _description = 'Report on Services/Payers (with invoices)'

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
        sol.id AS id,
        sol.product_id AS product_id,
        sol.order_partner_id AS payer_id,
        sol.order_id AS order_id,
        so.name AS name,
        so.kw_stage AS kw_stage,
        so.kw_archive_date AS archive_date,
        so.date_order AS date,
        payroll.code_id AS service_code,
        payroll.doctor1_id AS doctor_1,
        payroll.doctor2_id AS doctor_2,
        so.create_uid AS create_uid,
        so.create_date AS create_date,
        so.write_uid AS write_uid,
        so.write_date AS write_date,
        rp.gender AS gender,
        so.partner_id AS partner_id,
        so.kw_agreement_id AS agreement_id,
        sol.kw_report_payer_agreement_id AS payer_agreement_id,
        sol.kw_report_company_type AS company_type,
        so.kw_report_clinical_diagnosis AS clinical_diagnosis_id,
        so.kw_sending_organization AS sending_organization,
        so.kw_surgery_name_id AS surgery_name_id,
        so.kw_clinical_diagnose_id AS icd,
        so.kw_surgery_date AS surgery_date,
        so.kw_total_containers AS total_containers,
        so.kw_total_cassettes AS total_cassettes,
        so.kw_total_slides AS total_slides,
        so.kw_questionnaire_text AS questionnaire,
        so.kw_microscopy_text AS microscopy,
        CASE WHEN so.kw_report_sample_names = '' THEN NULL else
            so.kw_report_sample_names END AS sample_names,
        so.user_id AS user_id,
        so.invoice_status,
        so.kw_responsible_assistant AS res_lab_assist,
        so.kw_conclusion_started_by AS user_create_by,
        so.kw_report_sample_qty AS sample_qty,
        so.kw_report_cassette_qty AS cassette_qty,
        so.kw_report_slide_qty AS slide_qty,
        so.kw_conclusion_completed_by AS user_complete_by,
        so.kw_conclusion_completion_date AS conclusion_date,
        so.kw_report_month_end_date AS month_end_date,
        so.kw_patient_id AS patient_id,
        EXTRACT(YEAR FROM age(NOW(), rp.birthday)) AS years_old_on_report,
        EXTRACT(YEAR FROM age(so.kw_conclusion_completion_date, rp.birthday))
            AS years_old_on_conclusion,
        COUNT(DISTINCT sol.product_id) AS number_of_services,
        CASE WHEN so.kw_report_qty_examinations = NULL THEN 0 else
        so.kw_report_qty_examinations END AS examtype_numbers,
        CASE WHEN so.kw_report_examination_names = '' or
            so.kw_report_examination_names is NULL THEN '' else
            so.kw_report_examination_names END AS examination_names,
        CASE WHEN so.kw_report_all_service_name = '' or
            so.kw_report_all_service_name is NULL THEN NULL else
            so.kw_report_all_service_name END AS names_of_services,
        CASE WHEN so.kw_report_received_material = '' or
            so.kw_report_received_material is NULL THEN NULL else
            so.kw_report_received_material END AS received_material,
        SUM(sol.subtotal_before_discount) AS subtotal_before_discount,
        SUM(CAST(sol.kw_discount_amount AS numeric(10, 2)))
            AS total_discount_amount,
        SUM(CASE WHEN sol.price_total IS NOT NULL
            THEN sol.price_total else 0 END) AS total_service,
        SUM(CASE WHEN sol.order_partner_id = so.kw_patient_id
            THEN sol.price_total else 0 END) AS total_patient,
        SUM(CASE WHEN sol.price_total IS NOT NULL
            THEN sol.price_total else 0 END) AS total_payers,
        '' AS payments_sum_str,
        SUM(CASE WHEN sol.order_partner_id = so.kw_patient_id
        THEN sol.price_total else 0 END) AS payments_amount_due,
        sol.kw_report_invoiced_amount_for_other AS invoiced_amount_for_other,
        sol.kw_report_not_invoiced_amount_for_other
            AS not_invoiced_amount_for_other,
        CASE WHEN am.state = 'posted' THEN am.name ELSE NULL END
            AS invoice_number,
        CASE WHEN am.state = 'posted' THEN am.invoice_date ELSE NULL END
            AS invoice_date,
        am.state AS invoice_state
        """
        for field in fields_.values():
            select_ += field
        return select_

    def _from_sale(self, from_clause=''):
        from_ = """
            FROM sale_order_line sol
                LEFT JOIN sale_order so
                    ON so.id = sol.order_id
                LEFT JOIN res_partner rp
                    ON so.kw_patient_id = rp.id
                LEFT JOIN kw_gem_payroll payroll
                    ON sol.id = payroll.sale_order_line_id
                LEFT JOIN sale_order_line_invoice_rel solir
                    ON sol.id = solir.order_line_id
                LEFT JOIN account_move_line aml
                    ON aml.id = solir.invoice_line_id
                LEFT JOIN account_move am ON am.id = aml.move_id
                    AND (am.state = 'posted' OR am.state IS NULL)
            %s
            """ % from_clause
        return from_

    def _where(self):
        return """
            WHERE sol.display_type IS NULL
            AND sol.product_id IS NOT NULL
            AND sol.kw_product_qty != 0
            AND (aml.parent_state != 'cancel'
                OR aml.parent_state IS NULL)"""

    def _group_by_sale(self, groupby=''):
        groupby_ = """
               GROUP BY
               so.id,
               so.partner_id,
               so.kw_clinical_diagnose_id,
               rp.gender,
               rp.birthday,
               sol.id,
               sol.product_id,
               payroll.code_id,
               payroll.doctor1_id,
               payroll.doctor2_id,
               am.state,
               am.name,
               am.invoice_date
               %s
           """ % (groupby)
        return groupby_

    @property
    def _table_query(self):
        return '%s %s %s %s' % (self._select(), self._from_sale(),
                                self._where(), self._group_by_sale())
