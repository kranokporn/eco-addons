# -*- coding: utf-8 -*-
from datetime import datetime
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


INCOME_TAX_FORM = [('pnd1', 'PND1'),
                   ('pnd3', 'PND3'),
                   ('pnd3a', 'PND3a'),
                   ('pnd53', 'PND53'),
                   ('pnd54', 'PND54')]


WHT_CERT_INCOME_TYPE = [('1', '1. เงินเดือน ค่าจ้าง ฯลฯ 40(1)'),
                        ('2', '2. ค่าธรรมเนียม ค่านายหน้า ฯลฯ 40(2)'),
                        ('3', '3. ค่าแห่งลิขสิทธิ์ ฯลฯ 40(3)'),
                        ('5', '5. ค่าจ้างทำของ ค่าบริการ ฯลฯ 3 เตรส'),
                        ('6', '6. ค่าบริการ/ค่าสินค้าภาครัฐ'),
                        ('7', '7. ค่าจ้างทำของ ค่ารับเหมา'),
                        ('8', '8. ธุรกิจพาณิชย์ เกษตร อื่นๆ')]


TAX_PAYER = [('withholding', 'Withholding'),
             ('paid_one_time', 'Paid One Time')]


class WithholdingTaxCert(models.Model):
    _name = 'withholding.tax.cert'

    name = fields.Char(
        string='Number',
        readonly=True,
        related='payment_id.name',
        store=True,
        size=500,
    )
    date = fields.Date(
        string='Date',
        required=True,
        readonly=True,
        copy=False,
        states={'draft': [('readonly', False)]},
    )
    state = fields.Selection(
        [('draft', 'Draft'),
         ('done', 'Done'),
         ('cancel', 'Cancelled')],
        string='Status',
        default='draft',
        copy=False,
    )
    payment_id = fields.Many2one(
        'account.payment',
        string='Payment',
        copy=False,
    )
    company_partner_id = fields.Many2one(
        'res.partner',
        string='Company',
        readonly=True,
        copy=False,
    )
    supplier_partner_id = fields.Many2one(
        'res.partner',
        string='Supplier',
        required=True,
        readonly=True,
        states={'draft': [('readonly', False)]},
        copy=False,
    )
    company_taxid = fields.Char(
        related='company_partner_id.vat',
        string='Company Tax ID',
        readonly=True,
    )
    supplier_taxid = fields.Char(
        related='supplier_partner_id.vat',
        string='Supplier Tax ID',
        readonly=True,
    )
    supplier_address = fields.Char(
        string='Supplier Address',
        compute='_compute_address',
        readonly=True,
    )
    company_address = fields.Char(
        string='Company Address',
        compute='_compute_address',
        readonly=True,
    )
    income_tax_form = fields.Selection(
        INCOME_TAX_FORM,
        string='Income Tax Form',
        required=True,
        copy=False,
    )
    wht_line = fields.One2many(
        'withholding.tax.cert.line',
        'cert_id',
        string='Withholding Line',
        readonly=True,
        states={'draft': [('readonly', False)]},
        copy=False,
    )
    sequence = fields.Integer(
        string='WHT Sequence',
        readonly=True,
        copy=False,
        help="Running sequence for the same period. Reset every period",
    )
    period_id = fields.Many2one(
        comodel_name='date.range',
        string='Period',
        domain=[('type_id.name', '=', 'Period')],
        required=True,
    )
    tax_payer = fields.Selection(
        TAX_PAYER,
        string='Tax Payer',
        default='withholding',
        required=True,
        readonly=True,
        states={'draft': [('readonly', False)]},
        copy=False,
    )
    # _sql_constraints = [
    #     ('wht_seq_unique',
    #      'unique (period_id, sequence, income_tax_form)',
    #      'WHT Sequence must be unique!'),
    # ]

    # Computed fields to be displayed in WHT Cert.
    x_voucher_number = fields.Char(compute='_compute_cert_fields')
    x_date_value = fields.Date(compute='_compute_cert_fields')
    x_company_name = fields.Char(compute='_compute_cert_fields')
    x_supplier_name = fields.Char(compute='_compute_cert_fields')
    x_company_taxid = fields.Char(compute='_compute_cert_fields')
    x_supplier_taxid = fields.Char(compute='_compute_cert_fields')
    x_supplier_address = fields.Char(compute='_compute_cert_fields')
    x_company_address = fields.Char(compute='_compute_cert_fields')
    x_pnd1 = fields.Char(compute='_compute_cert_fields')
    x_pnd3 = fields.Char(compute='_compute_cert_fields')
    x_pnd53 = fields.Char(compute='_compute_cert_fields')
    x_sequence_display = fields.Char(compute='_compute_cert_fields')
    x_withholding = fields.Char(compute='_compute_cert_fields')
    x_paid_one_time = fields.Char(compute='_compute_cert_fields')
    x_total_base = fields.Float(compute='_compute_cert_fields')
    x_total_tax = fields.Float(compute='_compute_cert_fields')
    x_type_1_base = fields.Float(compute='_compute_cert_fields')
    x_type_1_tax = fields.Float(compute='_compute_cert_fields')
    x_type_2_base = fields.Float(compute='_compute_cert_fields')
    x_type_2_tax = fields.Float(compute='_compute_cert_fields')
    x_type_3_base = fields.Float(compute='_compute_cert_fields')
    x_type_3_tax = fields.Float(compute='_compute_cert_fields')
    x_type_5_base = fields.Float(compute='_compute_cert_fields')
    x_type_5_tax = fields.Float(compute='_compute_cert_fields')
    x_type_5_desc = fields.Char(compute='_compute_cert_fields')
    x_type_6_base = fields.Float(compute='_compute_cert_fields')
    x_type_6_tax = fields.Float(compute='_compute_cert_fields')
    x_type_6_desc = fields.Char(compute='_compute_cert_fields')
    x_type_7_base = fields.Float(compute='_compute_cert_fields')
    x_type_7_tax = fields.Float(compute='_compute_cert_fields')
    x_type_7_desc = fields.Char(compute='_compute_cert_fields')
    x_type_8_base = fields.Float(compute='_compute_cert_fields')
    x_type_8_tax = fields.Float(compute='_compute_cert_fields')
    x_type_8_desc = fields.Char(compute='_compute_cert_fields')
    x_signature = fields.Char(compute='_compute_cert_fields')

    @api.multi
    def _compute_cert_fields(self):
        for rec in self:
            company = self.env.user.company_id.partner_id
            supplier = rec.supplier_partner_id
            rec.x_voucher_number = rec.voucher_id.number
            rec.x_date_value = rec.date
            rec.x_company_name = company.name
            rec.x_supplier_name = ' '.join(list(
                filter(lambda l: l is not False, [supplier.title.name,
                                                  supplier.name])))
            rec.x_company_taxid = \
                company.vat and len(company.vat) == 13 and company.vat or ''
            rec.x_supplier_taxid = \
                supplier.vat and len(supplier.vat) == 13 and supplier.vat or ''
            rec.x_supplier_address = rec.supplier_address
            rec.x_company_address = rec.company_address
            rec.x_pnd1 = rec.income_tax_form == 'pnd1' and 'X' or ''
            rec.x_pnd3 = rec.income_tax_form == 'pnd3' and 'X' or ''
            rec.x_pnd53 = rec.income_tax_form == 'pnd53' and 'X' or ''
            rec.x_sequence_display = rec.sequence_display
            rec.x_withholding = \
                rec.tax_payer == 'withholding' and 'X' or ''
            rec.x_paid_one_time = \
                rec.tax_payer == 'paid_one_time' and 'X' or ''
            rec.x_total_base = rec._get_summary_by_type('base')
            rec.x_total_tax = rec._get_summary_by_type('tax')
            rec.x_type_1_base = rec._get_summary_by_type('base', '1')
            rec.x_type_1_tax = rec._get_summary_by_type('tax', '1')
            rec.x_type_2_base = rec._get_summary_by_type('base', '2')
            rec.x_type_2_tax = rec._get_summary_by_type('tax', '2')
            rec.x_type_3_base = rec._get_summary_by_type('base', '3')
            rec.x_type_3_tax = rec._get_summary_by_type('tax', '3')
            rec.x_type_5_base = rec._get_summary_by_type('base', '5')
            rec.x_type_5_tax = rec._get_summary_by_type('tax', '5')
            rec.x_type_5_desc = rec._get_summary_by_type('desc', '5')
            rec.x_type_6_base = rec._get_summary_by_type('base', '6')
            rec.x_type_6_tax = rec._get_summary_by_type('tax', '6')
            rec.x_type_6_desc = rec._get_summary_by_type('desc', '6')
            rec.x_type_7_base = rec._get_summary_by_type('base', '7')
            rec.x_type_7_tax = rec._get_summary_by_type('tax', '7')
            rec.x_type_7_desc = rec._get_summary_by_type('desc', '7')
            rec.x_type_8_base = rec._get_summary_by_type('base', '8')
            rec.x_type_8_tax = rec._get_summary_by_type('tax', '8')
            rec.x_type_8_desc = rec._get_summary_by_type('desc', '8')
            rec.x_signature = rec.create_uid.display_name

    @api.multi
    @api.depends('supplier_partner_id', 'company_partner_id')
    def _compute_address(self):
        for rec in self:
            rec.company_address = 'XXXXXXXXXXX'
            rec.supplier_address = 'YYYYYYYYYYYY'

    @api.model
    def _prepare_wht_line(self, voucher):
        wht_lines = []
        for line in voucher.tax_line_wht:
            vals = {
                'voucher_tax_id': line.id,
                'invoice_id': line.invoice_id.id,
                'wht_cert_income_type': line.wht_cert_income_type,
                'wht_cert_income_desc': line.wht_cert_income_desc,
                'base': -line.base,
                'amount': -line.amount,
            }
            wht_lines.append((0, 0, vals))
        return wht_lines

    @api.model
    def default_get(self, fields):
        res = super().default_get(fields)
        active_model = self._context.get('active_model')
        active_id = self._context.get('active_id')
        if active_model == 'account.voucher':
            voucher = self.env[active_model].browse(active_id)
            company_partner = self.env.user.company_id.partner_id
            supplier = voucher.partner_id
            res['voucher_id'] = voucher.id
            res['date'] = voucher.date_value
            res['company_partner_id'] = company_partner.id
            res['supplier_partner_id'] = supplier.id
            res['income_tax_form'] = (voucher.income_tax_form or
                                      supplier.income_tax_form)
            res['tax_payer'] = (voucher.tax_payer or False)
            res['wht_line'] = self._prepare_wht_line(voucher)
        return res

    @api.multi
    def action_draft(self):
        self.write({'state': 'draft'})
        return True

    @api.multi
    def action_done(self):
        self._assign_wht_sequence()
        self.write({'state': 'done'})
        return True

    @api.multi
    def action_cancel(self):
        self.write({'state': 'cancel'})
        return True

    @api.multi
    def _assign_wht_sequence(self):
        """ Only if not assigned, this method will assign next sequence """
        Period = self.env['account.period']
        for cert in self:
            if not cert.income_tax_form:
                raise ValidationError(_("No Income Tax Form selected, "
                                        "can not assign WHT Sequence"))
            if cert.sequence:
                continue
            period = Period.find(cert.date)[:1]
            sequence = \
                cert._get_next_wht_sequence(cert.income_tax_form, period)
            cert.write({'sequence': sequence})

    @api.multi
    def _get_summary_by_type(self, column, ttype='all'):
        self.ensure_one()
        wht_lines = self.wht_line
        if ttype != 'all':
            wht_lines = wht_lines.filtered(lambda l:
                                           l.wht_cert_income_type == ttype)
        if column == 'base':
            return round(sum([x.base for x in wht_lines]), 2)
        if column == 'tax':
            return round(sum([x.amount for x in wht_lines]), 2)
        if column == 'desc':
            descs = [x.wht_cert_income_desc for x in wht_lines]
            descs = filter(lambda x: x and x != '', descs)
            desc = ', '.join(descs)
            return desc

    @api.model
    def _prepare_address(self, partner):
        # TODO: XXX
        address_list = [partner.street, partner.street2, partner.city,
                        partner.township_id.name, partner.district_id.name,
                        partner.province_id.name, partner.zip, ]
        address_list = filter(lambda x: x is not False and x != '',
                              address_list)
        return ' '.join(address_list).strip()


class WithholdingTaxCertLine(models.Model):
    _name = 'withholding.tax.cert.line'

    cert_id = fields.Many2one(
        'withholding.tax.cert',
        string='WHT Cert',
        index=True,
    )
    wht_cert_income_type = fields.Selection(
        WHT_CERT_INCOME_TYPE,
        string='Type of Income',
        required=True,
    )
    wht_cert_income_desc = fields.Char(
        string='Income Description',
        size=500,
        required=False,
    )
    base = fields.Float(
        string='Base Amount',
        readonly=False,
    )
    amount = fields.Float(
        string='Tax Amount',
        readonly=False,
    )

    @api.onchange('wht_cert_income_type')
    def _onchange_wht_cert_income_type(self):
        if self.wht_cert_income_type:
            select_dict = dict(WHT_CERT_INCOME_TYPE)
            self.wht_cert_income_desc = select_dict[self.wht_cert_income_type]
        else:
            self.wht_cert_income_desc = False