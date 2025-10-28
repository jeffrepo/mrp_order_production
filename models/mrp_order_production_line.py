from odoo import api, fields, models, SUPERUSER_ID, _
from datetime import date
from datetime import datetime, timedelta
from odoo.exceptions import UserError, ValidationError
import logging


class QuemenOpLoteLinea(models.Model):
    _name = "mrp_order_production.op_lote_line"
    _rec_name = "product_id"

    lot_id = fields.Many2one("mrp_order_production.op_lote", "Lote")
    product_id = fields.Many2one('product.product','Producto',tracking=True)
    price_unit = fields.Float('Precio de venta',related="product_id.list_price")
    quantity = fields.Float('Cantidad',tracking=True)
    comment = fields.Char('Comentario')
    commnent = fields.Char('Comentario')
    elaboration_date = fields.Date('Fecha elaboracion',tracking=True)
    qty_label = fields.Float('Cantidad etiquetas', default=1)
    lot_state = fields.Selection(
        [('borrador', 'Borrador'), ('confirmado', 'Confirmado')],
        'Estado', readonly=True, copy=False, related='lot_id.state')
