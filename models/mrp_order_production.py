from odoo import api, fields, models, SUPERUSER_ID, _
from datetime import date
from datetime import datetime, timedelta
from odoo.exceptions import UserError, ValidationError
import logging
import pytz

class OrderLote(models.Model):
    _name = "mrp_order_production.op_lote"
    # _inherit = ['mail.thread', 'mail.activity.mixin', 'utm.mixin']

    name = fields.Char('Nombre', required=True, copy=False, readonly=True, index=True, default=lambda self: _('New'), tracking=True)
    date = fields.Date('Fecha', tracking=True)
    date_mrp_production = fields.Date('Fecha producción', tracking=True)
    product_ids = fields.One2many('mrp_order_production.op_lote_line', 'lot_id', string="Productos", tracking=True)
    reference = fields.Char('Referencia', tracking=True)
    state = fields.Selection(
        [('borrador', 'Borrador'), ('confirmado', 'Confirmado')],
        'Estado', readonly=True, copy=False, default='borrador', tracking=True)

    @api.model
    def create(self, vals):
        if vals.get('name', _('New')) == _('New'):
            seq_date = None
            if 'company_id' in vals:
                vals['name'] = self.env['ir.sequence'].with_context(force_company=vals['company_id']).next_by_code(
                    'mrp_order_production_lot.op_lote', sequence_date=seq_date) or _('New')
            else:
                vals['name'] = self.env['ir.sequence'].next_by_code('mrp_order_production_lot.op_lote', sequence_date=seq_date) or _('New')

        result = super(OrderLote, self).create(vals)
        return result


    def confirm_lot(self):
        for lot in self:
            if lot.product_ids:
                for line in lot.product_ids:
                    date_planed_start = datetime.fromisoformat(lot.date_mrp_production.isoformat() + ' 06:00:00')
                    mrp_order = {
                        # 'name': line.lot_id.name,
                        'product_id': line.product_id.id,
                        'product_uom_id': line.product_id.uom_id.id,
                        'qty_producing': line.quantity,
                        'product_qty': line.quantity,
                        'bom_id': line.product_id.bom_ids.id,
                        'origin': line.lot_id.name,
                        'date_planned_start': date_planed_start,
                    }
                    mrp_order_id = self.env['mrp.production'].create(mrp_order)

                    mrp_order_id._onchange_move_raw()
                    mrp_order_id._onchange_move_finished()
            lot.write({'state': "confirmado"})
        return True
