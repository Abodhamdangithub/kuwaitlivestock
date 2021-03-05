# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
from datetime import date, datetime


class OpenPurchase(models.Model):
    _name = 'open.purchase'
    _rec_name = 'order_number'

    order_number = fields.Char(string="التسلسل", readonly=True)
    name = fields.Char(string="اسم الارسالية")
    purchase_id = fields.Many2one('purchase.order', string="طلبية الشراء", readonly=True)
    open_purchase_line_ids = fields.One2many('open.purchase.line', 'open_purchase_id', string="open_purchase_line_ids",readonly=True)
    invoice_ids = fields.One2many('account.move', 'open_purchase_id',domain="[('state','in',['draft','posted'])]", string="invoice_ids")
    type = fields.Selection([('normal', 'عادي'), ('comm', 'بالعمولة'), ('sharing', 'بالمشاركة')], default='normal', required=True,
                            tracking=True, copy=False)
    date = fields.Date(string=" تاريخ الانشاء", default=datetime.now())
    date_close = fields.Date(string=" تاريخ الاغلاق")
    type_comm = fields.Selection([('nsbeh', 'نسبة'), ('qty', 'حسب الكمية')], string='نوع العمولة',copy=False)
    comm = fields.Integer(string="النسبة (%)")
    comm_on_qty = fields.Float(string="عمولة الوحدة")
    amount_comm = fields.Float(string="قيمة العمولة", compute='_compute_amount_comm', store=True)
    amount_sales = fields.Float(string="مجموع المبيعات", compute='_compute_amount_sales', store=True)
    amount_outlay = fields.Float(string="مجموع المصاريف", compute='_compute_amount_outlay', store=True)
    amount_win = fields.Float(string="مجموع الربح", compute='_compute_amount_win_or_lose', store=True)
    amount_lose = fields.Float(string="مجموع الخسارة", compute='_compute_amount_win_or_lose', store=True)
    state = fields.Selection([('draft', 'فتح'), ('closed', 'مغلق')], default='draft', required=True, tracking=True,
                             copy=False)
    account_move_id = fields.Many2one('account.move',string="القيد",readonly=True)
    account_id = fields.Many2one('account.account',string="حساب الربح أو الخسارة", readonly=True)
    journal_id = fields.Many2one('account.journal',string="اليومية", readonly=True)
    have_moved = fields.Boolean(string="يحتوي قيود محاسبية")
    amount_supplier = fields.Float(string="صافي المورد", default=0.0,readonly=True)
    try_sales_id = fields.Many2one('try.sales',string="try.sales", invisible=True)
    product_available_qty = fields.Char(string="المنتج والكمية المتاحة", compute='_compute_product_available_qty')

    payment_ids = fields.One2many('account.payment', 'open_purchase_payment_id', string="Payments")
    amount_payment = fields.Float(string="مجموع الدفعات", compute='_compute_amount_payment', store=True)
    amount_not_paid = fields.Float(string="المبلغ المتبقي", compute='_compute_amount_payment', store=True)


    all_sum_of_amount_of_comm = fields.Float(string="مجموع عمولات الدلال كاملا", compute='_compute_all_sum_of_amount_of_comm',store=True)
    @api.depends("open_purchase_line_ids.sum_of_amount_of_comm","open_purchase_line_ids")
    def _compute_all_sum_of_amount_of_comm(self):
        for me in self:
            sum = 0.0
            for line in me.open_purchase_line_ids:
                sum += line.sum_of_amount_of_comm
            me.all_sum_of_amount_of_comm = sum

    def get_invoices_data(self):
        data = []
        for inv in self.invoice_ids:
            for inv_line in inv.invoice_line_ids:
                is_here = False
                for l in data:
                    if l['product_id'] == inv_line.product_id.name:
                        l['quantity'] += inv_line.quantity
                        l['price_unit'] += inv_line.price_unit
                        l['price_subtotal'] += inv_line.price_subtotal
                        is_here = True

                if not is_here:
                    dict_data = {'product_id': inv_line.product_id.name, 'quantity': inv_line.quantity,
                                 'price_unit': inv_line.price_unit, 'price_subtotal': inv_line.price_subtotal}
                    data.append(dict_data)
        print ("data",data)
        for d in data:
            d['price_unit'] = round(d['price_subtotal'] / d['quantity'], 3)

        return data














    def action_open_purchase_register_payment(self):
        result = self.env['account.payment']\
            .with_context(active_ids=self.ids, active_model='open.purchase', active_id=self.id,default_payment_type='outbound',default_open_purchase_payment_id=self.id,default_partner_id = self.purchase_id.partner_id.id)\
            .action_register_payment()
        print ("result",result)
        return result















    def _compute_product_available_qty(self):
        for me in self:
            strings = ""
            for line in me.open_purchase_line_ids:
                strings += line.product_id.name +' ['+ str(line.qty_available) + '], '
            me.product_available_qty = strings


    def name_get(self):
        res = []
        for record in self:
            res.append((record.id, "%s %s" % (record.order_number, record.product_available_qty)))
        return res

    def cancel_create_entry(self):
        self.account_move_id.button_draft()
        lines = self.env['account.move.line'].search([('move_id', '=', self.account_move_id.id)])
        lines.unlink()
        self.have_moved = False



    def create_entry(self):
        if self.amount_win > 0.0:
            amount_win_lose_debit = 0.0
            amount_win_lose_credit = self.amount_win
            amount_win_lose_debit2 = self.amount_win
            amount_win_lose_credit2 = 0.0

        elif self.amount_lose > 0.0:
            amount_win_lose_debit = self.amount_lose
            amount_win_lose_credit = 0.0
            amount_win_lose_debit2 = 0.0
            amount_win_lose_credit2 = self.amount_lose

        if not self.account_move_id:
            move_line_vals = []
            line1 = (0, 0, {'name': self.name,'debit': self.amount_supplier ,'credit': 0,'account_id': self.purchase_id.partner_id.property_account_payable_id.id,'partner_id': self.purchase_id.partner_id.id})
            line2 = (0, 0, {'name': self.name,'debit': 0,'credit': self.amount_supplier ,'account_id': self.journal_id.default_debit_account_id.id ,'partner_id': self.purchase_id.partner_id.id})
            move_line_vals.append(line1)
            move_line_vals.append(line2)

            if self.type != "comm":
                line3 = (0, 0, {'name': self.name,'debit': amount_win_lose_debit,'credit': amount_win_lose_credit,'account_id':self.purchase_id.partner_id.property_account_payable_id.id ,'partner_id': self.purchase_id.partner_id.id})
                line4 = (0, 0, {'name': self.name,'debit': amount_win_lose_debit2,'credit': amount_win_lose_credit2,'account_id': self.account_id.id ,'partner_id': self.purchase_id.partner_id.id})
                move_line_vals.append(line3)
                move_line_vals.append(line4)

            move_vals = {
                "date": self.date,
                "journal_id": self.journal_id.id,
                "line_ids": move_line_vals,
            }
            new_move_id = self.env['account.move'].create(move_vals)
            new_move_id.post()
            self.account_move_id = new_move_id.id
        else:
            self.account_move_id.button_draft()
            move_line_vals = []
            line1 = (0, 0, {'name': self.name,'debit': self.amount_supplier ,'credit': 0,'account_id': self.purchase_id.partner_id.property_account_payable_id.id,'partner_id': self.purchase_id.partner_id.id})
            line2 = (0, 0, {'name': self.name,'debit': 0,'credit': self.amount_supplier ,'account_id': self.journal_id.default_debit_account_id.id ,'partner_id': self.purchase_id.partner_id.id})
            move_line_vals.append(line1)
            move_line_vals.append(line2)

            if self.type != "comm":
                line3 = (0, 0, {'name': self.name,'debit': amount_win_lose_debit,'credit': amount_win_lose_credit,'account_id':self.purchase_id.partner_id.property_account_payable_id.id ,'partner_id': self.purchase_id.partner_id.id})
                line4 = (0, 0, {'name': self.name,'debit': amount_win_lose_debit2,'credit': amount_win_lose_credit2,'account_id': self.account_id.id ,'partner_id': self.purchase_id.partner_id.id})
                move_line_vals.append(line3)
                move_line_vals.append(line4)
            self.account_move_id.line_ids = move_line_vals
            self.account_move_id.post()

        self.have_moved = True

    @api.model
    def create(self, vals):
        if 'order_number' not in vals:
            vals['order_number'] = self.env['ir.sequence'].next_by_code('open.purchase')
        return super(OpenPurchase, self).create(vals)

    def open_this(self):
        for line in self.open_purchase_line_ids:
            line.state = 'draft'
            line.amount_win = 0.0
            line.amount_not_win = 0.0
            self.date_close = False
            self.amount_supplier = 0
        self.state = "draft"

    def close_this(self):
        for line in self.open_purchase_line_ids:
            # if self.type == "comm":
            #     comm = self.amount_comm
            # else:
            #     comm = 0.0
            # if self.type == "sharing":
            #     shar = 2
            # else:
            #     shar = 1
            #
            # res = line.price_all_sales - (line.price_unit_purchase_orginal * line.qty_not) - self.amount_outlay - comm
            # if res >= 0.0:
            #     line.amount_win = (res/shar)
            #     line.amount_not_win = 0.0
            # else:
            #     line.amount_win = 0.0
            #     line.amount_not_win = (res * -1)/shar
            if line.qty_available != 0:
                raise UserError(_('لا يمكنك اغلاق الارسالية الا عندما تصبح الكميات المتاحة 0 '))
            if self.type == "comm":
                self.amount_win = 0.0
                self.amount_lose = 0.0
            line.state = 'closed'

        self.date_close = datetime.now()
        if self.type == "comm":
            self.amount_supplier = self.amount_sales - self.amount_comm - self.amount_outlay
        elif self.type == "sharing":
            if self.amount_win > 0.0:
                self.amount_supplier = self.amount_sales - self.amount_win - self.amount_outlay
            elif self.amount_lose > 0.0:
                self.amount_supplier = self.amount_sales + self.amount_lose - self.amount_outlay
        else:
            result = self.amount_sales - (self.purchase_id.amount_total + self.amount_outlay)
            if result > 0 :
                self.amount_win = result
                self.amount_lose = 0.0
            else:
                self.amount_lose = result * -1
                self.amount_win = 0.0
        self.state = "closed"
        if self.type == "comm":
            self.amount_win = self.amount_comm
        if self.type in ['comm','sharing']:
            for order_line in self.purchase_id.order_line:
                ex = self.amount_outlay
                qty_all = 0.0
                for open_lines in self.open_purchase_line_ids:
                    ex -= open_lines.sum_of_invoice_ids
                    qty_all += open_lines.qty_not
                if qty_all != 0.0:
                    res4 = ex / qty_all
                else:
                    res4 = 0.0
                for open_lines in self.open_purchase_line_ids:
                    if order_line.product_id.id == open_lines.product_id.id:
                        #order_line.product_qty = open_lines.qty_sales
                        order_line.product_qty = open_lines.qty_sales + open_lines.qty_talef
                        order_line.price_unit = ((open_lines.price_all_sales - (open_lines.price_all_sales* (self.comm/100)) - open_lines.sum_of_invoice_ids - (res4*open_lines.qty_not)) /(open_lines.qty_sales + open_lines.qty_talef))

        if not self.purchase_id.invoice_ids and self.type in ['comm', 'sharing']:
            return self.purchase_id.action_view_invoice()
        elif self.purchase_id.invoice_ids and self.type in ['comm', 'sharing']:
            for order_line in self.purchase_id.order_line:
                for inv in self.purchase_id.invoice_ids:
                    if inv.state == "posted":
                        inv.button_draft()
                    for inv_live in inv.invoice_line_ids:
                        if order_line.product_id.id == inv_live.product_id.id:
                            inv_live.quantity = order_line.product_qty
                            inv_live.price_unit = order_line.price_unit

    @api.depends("type", "type_comm", "comm", "comm_on_qty", "open_purchase_line_ids.qty_sales", "open_purchase_line_ids", "open_purchase_line_ids.price_all_sales", "all_sum_of_amount_of_comm")
    def _compute_amount_comm(self):
        for me in self:
            if me.type_comm == "nsbeh":
                sum = 0.0
                for line in me.open_purchase_line_ids:
                    sum += (me.comm / 100) * line.price_all_sales
                me.amount_comm = sum - me.all_sum_of_amount_of_comm
            elif me.type_comm == "qty":
                sum = 0.0
                for line in me.open_purchase_line_ids:
                    sum += me.comm_on_qty * line.qty_sales
                me.amount_comm = sum - me.all_sum_of_amount_of_comm


    # @api.depends("open_purchase_line_ids", "open_purchase_line_ids.amount_win")
    # def _compute_amount_win(self):
    #     for me in self:
    #         sum = 0.0
    #         for line in me.open_purchase_line_ids:
    #             sum += line.amount_win
    #         me.amount_win = sum
    #
    # @api.depends("open_purchase_line_ids", "open_purchase_line_ids.amount_win")
    # def _compute_amount_lose(self):
    #     for me in self:
    #         sum = 0.0
    #         for line in me.open_purchase_line_ids:
    #             sum += line.amount_not_win
    #         me.amount_lose = sum


    @api.depends("open_purchase_line_ids", "open_purchase_line_ids.price_all_sales")
    def _compute_amount_sales(self):
        for me in self:
            sum = 0.0
            for line in me.open_purchase_line_ids:
                sum += line.price_all_sales
            me.amount_sales = sum

    @api.depends("invoice_ids", "invoice_ids.amount_total", "invoice_ids.state")
    def _compute_amount_outlay(self):
        for me in self:
            sum = 0.0
            for line in me.invoice_ids:
                sum += line.amount_total
            me.amount_outlay = sum

    def unlink(self):
        for open in self:
            if open.amount_comm > 0 or open.amount_sales > 0 or open.amount_outlay > 0:
                raise UserError(_('لا يمكنك حذف الارسالية '))
            return super(OpenPurchase, self).unlink()

    @api.depends("payment_ids", "payment_ids.amount", "payment_ids.state", "state")
    def _compute_amount_payment(self):
        for me in self:

            sum = 0.0
            for line in me.payment_ids:
                if line.state not in ['draft','cancelled']:
                    sum += line.amount
            me.amount_payment = sum
            me.amount_not_paid = me.amount_supplier - sum


class OpenPurchaseLine(models.Model):
    _name = 'open.purchase.line'
    _rec_name = 'product_id'

    open_purchase_id = fields.Many2one('open.purchase', readonly=True)
    purchase_order_line = fields.Many2one('purchase.order.line', readonly=True)
    product_id = fields.Many2one('product.product', string="المنتج", required=True)
    qty_not = fields.Float(string="الكمية الفعلية", required=True, compute='_compute_qty_not')
    qty_talef = fields.Float(string="الكمية التالفة (النافق)",readonly=True)
    qty = fields.Float(string="الكمية المتبقية", readonly=True, compute='_compute_qty', store=True)
    price_unit_purchase_orginal = fields.Float(string="سعر وحدة الشراء الاصلي", invisible=True)
    price_unit_purchase = fields.Float(string="سعر وحدة الشراء",  compute='_compute_price_unit',store=True)
    price_unit_purchase_talef = fields.Float(string="سعر وحدة الشراء حسبة التالف فقط مخفي",  compute='_compute_price_unit_purchase_talef',store=True)
    price_unit_purchase_out = fields.Float(string="حسبة المصاريف مخفي",  compute='_compute_price_unit_purchase_out',store=True)

    price_unit_purchase_PursubSale = fields.Float(string="التكلفة ",  compute='_compute_price_all_sales',store=True)

    sale_order_line_ids = fields.One2many('sale.order.line', 'open_purchas_line_id', string="سطور طلبيات المبيعات")
    stock_scrap_ids = fields.One2many('stock.scrap', 'open_purchase_line_id', string="Stock Scrap")
    qty_sales = fields.Float(string="كمية المبيعات", readonly=True, compute='_compute_qty_sales', store=True)
    price_all_sales = fields.Float(string="قيمة المبيعات", readonly=True, compute='_compute_price_all_sales',
                                   store=True)
    qty_available = fields.Float(string="الكمية المتاحة", readonly=True, compute='_compute_qty_available', store=True)
    amount_win = fields.Float(string="قيمة الربح", readonly=True)
    amount_not_win = fields.Float(string="قيمة الخسارة", readonly=True)
    state = fields.Selection([('draft', 'فتح'), ('closed', 'مغلق')], default='draft', required=True, tracking=True,
                             copy=False)
    invoice_ids = fields.One2many('account.move', 'open_purchase_line_id', string="invoice_ids")
    sum_of_invoice_ids = fields.Float(string="مجموع الصاريف", compute='_compute_sum_of_invoice_ids',store=True)


    sum_of_amount_of_comm = fields.Float(string="مجموع عمولات الدلال", compute='_compute_sum_of_amount_of_comm',store=True)
    @api.depends("sale_order_line_ids.amount_of_comm","sale_order_line_ids")
    def _compute_sum_of_amount_of_comm(self):
        for me in self:
            sum = 0.0
            for order_line in me.sale_order_line_ids:
                sum += order_line.amount_of_comm
            me.sum_of_amount_of_comm = sum

    @api.depends('qty_not', "qty_talef")
    def _compute_qty(self):
        for me in self:
            me.qty = me.qty_not - me.qty_talef

    def _get_pay_view_form(self):
        self.ensure_one()
        data_obj = self.env['ir.model.data']
        return data_obj.get_object('open_purchase', 'stock_scrap_open_form')
    def action_stock_scrap(self):
        view = self._get_pay_view_form()
        return {
            'name': _("Stock Scrap"),
            'view_mode': 'form',
            'view_id': view.id,
            'view_type': 'form',
            'res_model': 'stock.scrap',
            'type': 'ir.actions.act_window',
            'nodestroy': True,
           'target': 'new',
            'domain': '[]',
            'context': {
                'default_product_id': self.product_id.id,
                'default_open_purchase_line_id': self.id,
            }
        }


    @api.depends('qty', "qty_sales")
    def _compute_qty_available(self):
        for me in self:
            me.qty_available = me.qty - me.qty_sales


    @api.depends( 'open_purchase_id.type','price_unit_purchase_out','price_unit_purchase_talef','qty_talef', 'open_purchase_id.amount_outlay', 'purchase_order_line.price_unit')
    def _compute_price_unit(self):
        for me in self:
            me.price_unit_purchase = me.price_unit_purchase_out + me.price_unit_purchase_talef



    @api.depends( 'open_purchase_id.type', 'open_purchase_id.amount_outlay')
    def _compute_price_unit_purchase_out(self):
        for me in self:
            if me.qty > 0:
                qty = me.qty
            elif me.qty == 0:
                qty = 1

            sum_qty_all = 0.0
            sum_outlay_lines = 0.0
            for line in me.open_purchase_id.open_purchase_line_ids:
                sum_outlay_lines += line.sum_of_invoice_ids
                sum_qty_all += line.qty
            if sum_qty_all == 0.0:
                sum_qty_all = 1
            outlayline = (me.open_purchase_id.amount_outlay - sum_outlay_lines) / sum_qty_all
            outlayline += line.sum_of_invoice_ids / qty
            me.price_unit_purchase_out  = outlayline
            #me.price_unit_purchase_out += line.sum_of_invoice_ids / qty

    @api.depends('open_purchase_id.type','qty_talef', 'purchase_order_line.price_unit')
    def _compute_price_unit_purchase_talef(self):
        for me in self:
            if me.qty_available == 0.0:
                av = 1
            else:
                av = me.qty_available
            if me.price_unit_purchase_talef == 0.0:
                me.price_unit_purchase_talef = me.purchase_order_line.price_unit
            else:
                me.price_unit_purchase_talef = me.price_unit_purchase_talef +  (me.price_unit_purchase_talef/ av)  + (me.price_unit_purchase_out/av)

    @api.depends('invoice_ids','invoice_ids.invoice_line_ids','invoice_ids.invoice_line_ids.quantity','invoice_ids.invoice_line_ids.price_unit','invoice_ids.amount_total')
    def _compute_sum_of_invoice_ids(self):
        for me in self:
            sum = 0.0
            for inv in self.invoice_ids:
                sum += inv.amount_total
            me.sum_of_invoice_ids = sum

    @api.depends('purchase_order_line.qty_received')
    def _compute_qty_not(self):
        for me in self:
            me.qty_not = me.purchase_order_line.qty_received


    @api.depends("sale_order_line_ids.product_uom_qty","sale_order_line_ids.qty_lock", "sale_order_line_ids.order_id.state")
    def _compute_qty_sales(self):
        for me in self:
            sum = 0.0
            for order_line in me.sale_order_line_ids:
                if order_line.order_id.state != 'cancel':
                    sum += order_line.qty_lock
            me.qty_sales = sum

    @api.depends("price_unit_purchase","sale_order_line_ids.product_uom_qty", "sale_order_line_ids.price_unit", "sale_order_line_ids.order_id.state")
    def _compute_price_all_sales(self):
        for me in self:
            sum = 0.0
            for order_line in me.sale_order_line_ids:
                if order_line.order_id.state != 'cancel':
                    #sum += order_line.product_uom_qty * order_line.price_unit
                    sum += order_line.price_subtotal + order_line.amount_of_comm
            me.price_all_sales = sum


            if me.qty_sales == 0.0:
                qts = 1
            else:
                qts = me.qty_sales
            res = (me.price_all_sales ) - ((me.price_unit_purchase_out + me.price_unit_purchase_talef) * qts)
            if me.qty_available == 0.0:
                av = 1
            else:
                av = me.qty_available


            if me.qty_sales == 0.0:
                me.price_unit_purchase_PursubSale = me.price_unit_purchase
            else:
                me.price_unit_purchase_PursubSale = me.price_unit_purchase + (res * -1 / av)


    # @api.depends('qty_sales', 'price_unit_purchase')
    # def _compute_price_unit_purchase_PursubSale(self):
    #     for me in self:
    #         if me.qty_sales == 0.0:
    #             qts = 1
    #         else:
    #             qts = me.qty_sales
    #         res = (me.price_all_sales / qts) - ((me.price_unit_purchase_out + me.price_unit_purchase_talef))
    #         if me.qty_available == 0.0:
    #             av = 1
    #         else:
    #             av = me.qty_available
    #         if me.qty_sales == 0.0:
    #             me.price_unit_purchase_PursubSale = me.price_unit_purchase
    #         else:
    #             me.price_unit_purchase_PursubSale = me.price_unit_purchase + (res*-1  / av)
