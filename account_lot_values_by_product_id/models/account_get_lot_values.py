from odoo import models, fields, api
from odoo.tools import float_is_zero
from collections import defaultdict
import logging

_logger = logging.getLogger(__name__)


class AccountMoveLotValues(models.Model):
    _name = 'account.move'
    _inherit = 'account.move'

    def _get_lot_values(self, product_id):
        """ Get lots values from product id """
        self.ensure_one()

        sale_orders = self.mapped('invoice_line_ids.sale_line_ids.order_id')
        stock_move_lines = sale_orders.mapped('picking_ids.move_lines.move_line_ids')

        # Get the other customer invoices and refunds.
        ordered_invoice_ids = sale_orders.mapped('invoice_ids')\
            .filtered(lambda i: i.state not in ['draft', 'cancel'])\
            .sorted(lambda i: (i.invoice_date, i.id))

        # Get the position of self in other customer invoices and refunds.
        self_index = None
        i = 0
        for invoice in ordered_invoice_ids:
            if invoice.id == self.id:
                self_index = i
                break
            i += 1

        # Get the previous invoice if any.
        previous_invoices = ordered_invoice_ids[:self_index]
        last_invoice = previous_invoices[-1] if len(previous_invoices) else None

        # Get the incoming and outgoing sml between self.invoice_date and the previous invoice (if any).
        write_dates = [wd for wd in self.invoice_line_ids.mapped('write_date') if wd]
        self_datetime = max(write_dates) if write_dates else None
        last_write_dates = last_invoice and [wd for wd in last_invoice.invoice_line_ids.mapped('write_date') if wd]
        last_invoice_datetime = max(last_write_dates) if last_write_dates else None

        def _filter_incoming_sml(ml):
            _logger.info(ml.state)
            _logger.info(ml.location_id.usage)
            _logger.info(ml.lot_id)
            _logger.info(last_invoice_datetime)
            _logger.info(ml.date)
            _logger.info(self_datetime)

            if ml.state == 'done' and ml.location_id.usage == 'customer' and ml.lot_id:
                if last_invoice_datetime:
                    return last_invoice_datetime <= ml.date <= self_datetime
                else:
                    return ml.date <= self_datetime
            return False

        def _filter_outgoing_sml(ml):
            _logger.info(ml.state)
            _logger.info(ml.location_dest_id.usage)
            _logger.info(ml.lot_id)
            _logger.info(last_invoice_datetime)
            _logger.info(ml.date)
            _logger.info(self_datetime)
            if ml.state == 'done' and ml.location_dest_id.usage == 'customer' and ml.lot_id:
                if last_invoice_datetime:
                    return last_invoice_datetime <= ml.date <= self_datetime
                else:
                    return ml.date <= self_datetime
            return False
        _logger.info("**** Before ****")
        _logger.info(stock_move_lines)
        incoming_sml = stock_move_lines.filtered(_filter_incoming_sml)
        outgoing_sml = stock_move_lines.filtered(_filter_outgoing_sml)
        _logger.info("**** IN SML ****")
        _logger.info(incoming_sml)
        _logger.info("**** OUT SML ****")
        _logger.info(outgoing_sml)
        # Prepare and return lot_values
        qties_per_lot = defaultdict(lambda: 0)
        if self.move_type == 'out_refund':
            for ml in outgoing_sml:
                qties_per_lot[ml.lot_id] -= ml.product_uom_id._compute_quantity(ml.qty_done, ml.product_id.uom_id)
            for ml in incoming_sml:
                qties_per_lot[ml.lot_id] += ml.product_uom_id._compute_quantity(ml.qty_done, ml.product_id.uom_id)
        else:
            for ml in outgoing_sml:
                qties_per_lot[ml.lot_id] += ml.product_uom_id._compute_quantity(ml.qty_done, ml.product_id.uom_id)
            for ml in incoming_sml:
                qties_per_lot[ml.lot_id] -= ml.product_uom_id._compute_quantity(ml.qty_done, ml.product_id.uom_id)
        lot_values = []
        for lot_id, qty in qties_per_lot.items():
            _logger.info("Lot ID {}".format(lot_id))
            if float_is_zero(qty, precision_rounding=lot_id.product_id.uom_id.rounding):
                continue
            if product_id == lot_id.product_id:
                lot_values.append({
                    'product_name': lot_id.product_id.display_name,
                    'product_id': lot_id.product_id,
                    'quantity': self.env['ir.qweb.field.float'].value_to_html(qty, {'precision': self.env['decimal.precision'].precision_get('Product Unit of Measure')}),
                    'uom_name': lot_id.product_uom_id.name,
                    'lot_name': lot_id.name,
                    # The lot id is needed by localizations to inherit the method and add custom fields on the invoice's report.
                    'lot_id': lot_id.id,
                    'use_date': lot_id.use_date or False
                })
        return lot_values
