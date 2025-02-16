from odoo import models
from odoo.http import request
      
class ProductTemplate(models.Model):
    _inherit = 'product.template'

    def _get_combination_info(self, combination=False, product_id=False, add_qty=1, pricelist=False, parent_combination=False, only_template=False):
        
        combination_info = super(ProductTemplate, self)._get_combination_info(
            combination=combination, product_id=product_id, add_qty=add_qty, pricelist=pricelist,
            parent_combination=parent_combination, only_template=only_template)

        if not self.env.context.get('website_sale_stock_get_quantity'):
            return combination_info

        if combination_info['product_id']:
            product = self.env['product.product'].sudo().browse(combination_info['product_id'])
            website = self.env['website'].get_current_website()
            
            #Suma a free_qty con qty_manofacture
            free_qty = product.with_context(warehouse=website._get_warehouse_available()).free_qty + product.with_context(warehouse=website._get_warehouse_available()).qty_bom_available_get()
            
            has_stock_notification = product._has_stock_notification(self.env.user.partner_id) \
                                     or request \
                                     and product.id in request.session.get('product_with_stock_notification_enabled',
                                                                           set())
            stock_notification_email = request and request.session.get('stock_notification_email', '')
            combination_info.update({
                'free_qty': free_qty,
                'product_type': product.type,
                'product_template': self.id,
                'available_threshold': self.available_threshold,
                'cart_qty': product._get_cart_qty(website),
                'uom_name': product.uom_id.name,
                'allow_out_of_stock_order': self.allow_out_of_stock_order,
                'show_availability': self.show_availability,
                'out_of_stock_message': self.out_of_stock_message,
                'has_stock_notification': has_stock_notification,
                'stock_notification_email': stock_notification_email,
            })
        else:
            product_template = self.sudo()
            combination_info.update({
                'free_qty': 0,
                'product_type': product_template.type,
                'allow_out_of_stock_order': product_template.allow_out_of_stock_order,
                'available_threshold': product_template.available_threshold,
                'product_template': product_template.id,
                'cart_qty': 0,
            })

        return combination_info
