# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import _, models


class StockPicking(models.Model):
    _inherit = "stock.picking"

    def _action_done(self):
        # Only DropShip pickings
        for pick in self.filtered(
                lambda x: x.location_dest_id.usage == "customer").sudo():
            purchase = pick.sale_id.auto_purchase_order_id
            if not purchase:
                continue
            for move_line in pick.move_line_ids:
                sale_line_id = move_line.move_id.sale_line_id
                po_moves = sale_line_id.auto_purchase_line_id.move_ids
                if not sale_line_id.auto_purchase_line_id:
                    po_moves = purchase.order_line.mapped("move_ids")
                po_move_lines = po_moves.mapped(
                    "move_line_ids").filtered(lambda line: line.product_id.id ==
                                              move_line.product_id.id)
                for po_move_line in po_move_lines:
                    if not (po_move_line.lot_id or po_move_line.lot_name):
                        po_move_line.lot_name = move_line.lot_name
                        if move_line.lot_id:
                            po_move_line.lot_id = move_line.lot_id.copy(
                                dict(name=move_line.lot_id.name,
                                     company_id=po_move_line.company_id.id))
                        break
        return super()._action_done()
