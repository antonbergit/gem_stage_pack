{
    'name': 'GeoEvoMed Invoicing',
    'summary': '',

    'author': 'Kitworks Systems',
    'website': 'https://kitworks.systems/',

    'category': 'Customizations',
    'license': 'OPL-1',
    'version': '16.0.0.0.38',

    'depends': [
        'kw_gem_conclusion_survey',
        'account',
        'report_xlsx'
    ],

    'data': [
        'wizard/sale_make_invoice_advance_views.xml',

        'data/ir_cron_compute_fields.xml',
        'data/mail_template_data.xml',

        'security/security.xml',
        'security/ir.model.access.csv',

        'views/sale_report1_views.xml',
        'views/sale_report2_views.xml',
        'views/sale_report3_service_views.xml',
        'views/sale_report4_service_payer_views.xml',
        'views/sale_report5_service_payer_invoice_views.xml',
        'views/account_menuitem.xml',
        'views/account_views.xml',
        'views/sale_order_views.xml',
        'views/partner_views.xml',
        'views/mail_template_views.xml',
        'views/sale_order_restrict_edit_views.xml',

        'views/account_action_server.xml',

        'report/invoice_template1.xml',
        'report/invoice_template2_p1.xml',
        'report/invoice_template2_p2.xml',
        'report/account_report.xml',

    ]
}
