# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import _, models


class StockPicking(models.Model):
    _inherit = "stock.picking"

    def _action_done(self):
        # Only DropShip pickings
        for pick in self.filtered(
            lambda x: x.location_dest_id.usage == "customer"
        ).sudo():
            for move_line in pick.move_line_ids:
                sale_line_id = move_line.move_id.sale_line_id
                po_move_lines = sale_line_id.auto_purchase_line_id.move_ids.mapped(
                    "move_line_ids"
                )
                for po_move_line in po_move_lines:
                    if po_move_line.product_id.id == move_line.product_id.id and not (po_move_line.lot_id or po_move_line.lot_name):
                        if move_line.lot_id:
                            po_move_line.lot_id = move_line.lot_id
                            move_line.lot_id.write({'company_ids': [(4, po_move_line.company_id.id, 0)]})
                        po_move_line.lot_name = move_line.lot_name
                        break
        return super()._action_done()
