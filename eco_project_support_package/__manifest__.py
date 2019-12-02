# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)


{
    'name': 'Ecosoft Project Support Package',
    'version': '12.0.2.0.0',
    'author': 'Ecosoft',
    'license': 'AGPL-3',
    'category': 'Project',
    'depends': [
        'project',
        'analytic',
        'hr_timesheet',
        'product_email_template'
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/hr_timesheet_views.xml',
        'views/project_views.xml'
    ],
    'installable': True,
    'development_status': 'alpha',
    'maintainers': ['Saran Lim.'],
 }