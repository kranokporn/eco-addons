from openerp import models, fields, api


class ReportVAT(models.TransientModel):
    _name = 'report.vat'
    _description = 'Wizard for report.vat'
    _inherit = 'xlsx.report'

    # Search Criteria
    company_id = fields.Many2one(
        comodel_name='res.company',
        default=lambda self: self.env.user.company_id,
        string='Company',
        required=True,
        ondelete='cascade',
    )
    tax_id = fields.Many2one(
        comodel_name='account.tax',
        string='Tax',
        required=True,
        domain=[('tax_exigibility', '=', 'on_invoice')],
    )
    account_id = fields.Many2one(
        comodel_name='account.account',
        string='Account',
        required=True,
    )
    period_id = fields.Many2one(
        comodel_name='date.range',
        string='Period',
        domain=[('type_id.name', '=', 'Period')],
        required=True,
    )
    date_from = fields.Date(
        string='From Date',
        required=True,
    )
    date_to = fields.Date(
        string='To Date',
        required=True,
    )

    # Report Result
    results = fields.Many2many(
        'account.vat.report',
        string='Results',
        compute='_compute_results',
        help='Use compute fields, so there is nothing store in database',
    )

    @api.onchange('tax_id')
    def _onchange_tax_id(self):
        self.account_id = self.tax_id.account_id

    @api.onchange('period_id')
    def _onchange_period_id(self):
        self.date_from = self.period_id.date_start
        self.date_to = self.period_id.date_end

    @api.multi
    def _compute_results(self):
        """ On the wizard, result will be computed and added to results line
        before export to excel, by using xlsx.export
        """
        self.ensure_one()
        Result = self.env['account.vat.report']
        domain = [('company_id', '=', self.company_id.id),
                  ('account_id', '=', self.account_id.id),
                  ('date', '>=', self.date_from),
                  ('date', '<=', self.date_to),
                  ]
        self.results = Result.search(domain)
