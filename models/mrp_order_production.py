from odoo import api, fields, models, SUPERUSER_ID, _
from datetime import date
from datetime import datetime, timedelta
from odoo.exceptions import UserError, ValidationError
import logging
import pytz

class StockPicking(models.Model):
    _inherit = "stock.picking"

    lot_id = fields.Many2one('mrp_order_production.op_lote','Lote')
    
class OrderLote(models.Model):
    _name = "mrp_order_production.op_lote"
    # _inherit = ['mail.thread', 'mail.activity.mixin', 'utm.mixin']

    name = fields.Char('Nombre', required=True, copy=False, readonly=True, index=True, default=lambda self: _('New'), tracking=True)
    date = fields.Date('Fecha', tracking=True)
    date_mrp_production = fields.Date('Fecha producción', tracking=True)
    product_ids = fields.One2many('mrp_order_production.op_lote_line', 'lot_id', string="Productos", tracking=True)
    reference = fields.Char('Referencia', tracking=True)
    state = fields.Selection(
        [('borrador', 'Borrador'), ('proceso','Proceso'),('confirmado', 'Confirmado')],
        'Estado', readonly=True, copy=False, default='borrador', tracking=True)
    order_ids = fields.One2many('mrp.production','lot_id', string="Ordenes")
    picking_ids = fields.One2many('stock.picking','lot_id', string="Traslados")
    
    @api.model
    def create(self, vals):
        if vals.get('name', _('New')) == _('New'):
            seq_date = None
            if 'company_id' in vals:
                vals['name'] = self.env['ir.sequence'].with_context(force_company=vals['company_id']).next_by_code(
                    'mrp_order_production_lot.op_lote', sequence_date=seq_date) or _('New')
            else:
                vals['name'] = self.env['ir.sequence'].next_by_code('mrp_order_production.op_lote', sequence_date=seq_date) or _('New')

        result = super(OrderLote, self).create(vals)
        return result

    def process_lot(self):
        for lot in self:
            if lot.product_ids:
                for line in lot.product_ids:
                    date_planed_start = datetime.fromisoformat(lot.date_mrp_production.isoformat() + ' 06:00:00')
                    if line.product_id.bom_ids:
                        mrp_order = {
                            # 'name': line.lot_id.name,
                            'product_id': line.product_id.id,
                            'product_uom_id': line.product_id.uom_id.id,
                            'qty_producing': line.quantity,
                            'product_qty': line.quantity,
                            'bom_id': line.product_id.bom_ids[0].id,
                            'origin': line.lot_id.name,
                            'date_start': date_planed_start,
                        }
                        mrp_order_id = self.env['mrp.production'].create(mrp_order)
    
                        mrp_order_id._compute_move_raw_ids()
                        mrp_order_id.set_qty_producing()
                        mrp_order_id._compute_move_finished_ids()
                        
                        mrp_order_id.write({'lot_id': lot.id})
                    else:
                        picking_id = self.env['stock.picking'].create({
                        'picking_type_id': 26,
                        'location_id': 8,
                        'origin': line.lot_id.name,
                        'location_dest_id': 24, })

                        lineas_transferencia_id = self.env['stock.move.line'].create({
                        'picking_id': picking_id.id,
                        'product_id': line.product_id.id,
                        'qty_done': line.quantity,
                        #'product_uom_qty': line.quantity,
                        #'product_uom_id': lista_id[lneas]['product_uom_id'],
                        'location_id': 8,
                        'location_dest_id': 24,
                        'qty_done': line.quantity,
                        })
                        picking_id.write({'lot_id': lot.id})
            lot.write({'state': "proceso"})
            
    def confirm_lot(self):
        for lot in self:
            if lot.order_ids:
                for mrp_order in lot.order_ids:
                    mrp_order.button_mark_done()
            if lot.picking_ids:
                for line in picking_ids:
                    line.button_validate()
            lot.write({'state': "confirmado"})
        return True

class MrpProduction(models.Model):
    _inherit = 'mrp.production'

    lot_id = fields.Many2one('mrp_order_production.op_lote','Lote')
