from odoo import fields, models


class OrbitalTimelineItem(models.Model):
    _name = "orbital.timeline.item"
    _description = "Orbital Timeline Item"
    _order = "sequence, id"

    name = fields.Char(required=True)
    date = fields.Char(required=True, help="Display label, e.g. 'Jan 2024'")
    content = fields.Text()
    category = fields.Char()
    icon = fields.Selection(
        [
            ("calendar", "Calendar"),
            ("code", "Code"),
            ("file-text", "File Text"),
            ("user", "User"),
            ("clock", "Clock"),
            ("link", "Link"),
            ("bolt", "Bolt / Zap"),
        ],
        default="calendar",
        required=True,
    )
    related_item_ids = fields.Many2many(
        "orbital.timeline.item",
        "orbital_timeline_item_rel",
        "item_id",
        "related_id",
        string="Connected Nodes",
    )
    status = fields.Selection(
        [
            ("completed", "Completed"),
            ("in-progress", "In Progress"),
            ("pending", "Pending"),
        ],
        default="pending",
        required=True,
    )
    energy = fields.Integer(
        default=50,
        help="Energy level displayed on the node (0–100)",
    )
    sequence = fields.Integer(default=10)
    active = fields.Boolean(default=True)
