{
    'name': 'Advance & Retention Invoice for Contracting',
    'version': '8.0.1.0.0',
    'category': 'Accounting',
    'summary': 'Manage Advance Payments and Retention Amounts on Invoices for Contracting Companies',
    'description': """
        This module is designed for contracting companies and adds:
        - Advance Payment Amount field on invoices
        - Retention Amount field on invoices
        - Auto-creates corresponding journal lines
        - Updates totals
        - Displays fields in invoice report
    """,
    'author': 'Nooh Suliman',
    'website': 'https://www.linkedin.com/in/nooh-suliman/',
    'depends': ['account'],
    'images': ['static/description/banner.png'],
    'data': [
        'security/ir.model.access.csv',
        'views/account_move_views.xml',
        'views/report_invoice.xml',
        'views/res_partner_view.xml',
    ],
    'installable': True,
    'application': True,
    'license': 'OPL-1',
    'price': 10,
    'currency': 'USD',
}