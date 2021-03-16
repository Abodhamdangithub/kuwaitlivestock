# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError

class ReportsKuwait(models.Model):
    _name = 'reports.kuwait'


    type = fields.Selection( [('stock','تقرير المخزون'),('sales','المبيعات'),('partner_balance','ذمم العملاء'),('supplier_balance','ذمم الموردين')],string="التقرير",required=True)
    by = fields.Selection( [('product','المنتج'),('lines','سطور المبيعات')],string="حسب")
    from_date = fields.Date(string="From Date")
    to_date = fields.Date(string="To Date")

    product_ids = fields.Many2many('product.product',string="المنتج")


    def get_stock_quant_data(self):
        product_send = []
        product_ids = self.env['product.product'].search([])
        for product in product_ids:
            select = "select  (select name from product_template where id = (select product_tmpl_id from product_product where id = quant.product_id )) as product,quantity ,(select name from stock_location where id = quant.location_id) as location from stock_quant as quant where product_id = %d and (select usage from stock_location where id = quant.location_id) = 'internal'" % (product.id)
            self.env.cr.execute(select)
            result = self.env.cr.dictfetchall()
            if len(result) > 0:
                product_send.append([result[0]['product'],result[0]['location'],result[0]['quantity']])
        return product_send


    def get_sales_by_product_data(self):
        product_send = []
        if self.product_ids:
            products = self.product_ids.ids

            product_ids = self.env['product.product'].search([('id','in',products)])
        else:
            product_ids = self.env['product.product'].search([])
        for product in product_ids:
            select = "select  COALESCE(sum(product_uom_qty),0) as product_uom_qty , COALESCE(sum(price_subtotal),0) as price_subtotal from sale_order_line  as line where product_id = %s and (select date_order from sale_order where id = line.order_id) >= %r and (select date_order from sale_order where id = line.order_id) <= %r and (select state from sale_order where id = line.order_id) <> 'cancel'"% (product.id,str(self.from_date),str(self.to_date))
            self.env.cr.execute(select)
            result = self.env.cr.dictfetchall()
            print ("result",result)
            if result[0]['product_uom_qty'] > 0:
                product_send.append([product.name,result[0]['product_uom_qty'],result[0]['price_subtotal']])
        return product_send

    def get_sales_by_lines_data(self):
        product_send = []
        if self.product_ids:
            products = self.product_ids.ids

            product_ids = self.env['product.product'].search([('id','in',products)])
        else:
            product_ids = self.env['product.product'].search([])

        for product in product_ids:
            select = "select  (select name from sale_order where id = line.order_id) as order_name,COALESCE(product_uom_qty,0) as product_uom_qty ,COALESCE(price_unit,0) as price_unit , COALESCE(price_subtotal,0) as price_subtotal from sale_order_line  as line where product_id = %s and (select date_order from sale_order where id = line.order_id) >= %r and (select date_order from sale_order where id = line.order_id) <= %r and (select state from sale_order where id = line.order_id) <> 'cancel'"% (product.id,str(self.from_date),str(self.to_date))
            self.env.cr.execute(select)
            result = self.env.cr.dictfetchall()
            print ("result",result)
            if len(result) > 0:
                for r in result:
                    product_send.append([product.name,r['order_name'],r['product_uom_qty'],r['price_unit'],r['price_subtotal']])
        return product_send


    def get_partner_balance_data(self):
        partner_send = []
        partner_ids = self.env['res.partner'].search([('customer_rank','>',0)])

        sum = 0.0
        for partner in partner_ids:
            print (partner.customer_rank)
            if partner.balance_partner > 0 or partner.balance_partner < 0:
                partner_send.append([partner.name,partner.balance_partner])
                sum += partner.balance_partner
        partner_send.append(['المجموع', sum])
        return partner_send


    def get_supplier_balance_data(self):
        partner_send = []
        partner_ids = self.env['res.partner'].search([('supplier_rank','>',0)])
        sum = 0.0
        for partner in partner_ids:
            if partner.balance_partner > 0 or partner.balance_partner < 0:
                partner_send.append([partner.name,partner.balance_partner])
                sum += partner.balance_partner
        partner_send.append(['المجموع', sum])
        return partner_send
