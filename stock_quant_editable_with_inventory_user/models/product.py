from odoo import models, fields, api
import logging 
_logger = logging.getLogger(__name__)

class Product(models.Model):
    _name = "product.product"
    _inherit = 'product.product'
    
    def action_open_quants(self):
        if self.user_has_groups('stock.group_stock_manager') or self.user_has_groups('stock.group_stock_user'):
            _logger.info("Set inventory mode to True")
            self = self.with_context(inventory_mode=True)
            # Set default location id if multilocations is inactive
            if not self.user_has_groups('stock.group_stock_multi_locations'):
                user_company = self.env.company
                warehouse = self.env['stock.warehouse'].search(
                    [('company_id', '=', user_company.id)], limit=1
                )
                if warehouse:
                    self = self.with_context(default_location_id=warehouse.lot_stock_id.id)
        return super().action_open_quants()