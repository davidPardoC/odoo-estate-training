from odoo import models, fields


class EstatePropertyTag(models.Model):
    _name = 'estate.property.tag'
    _description = 'Estate Property Tag'
    _sql_constraints = [('check_name', 'unique(name)',
                         'The name of the tag must be unique.')]
    _order = "name desc"

    name = fields.Char(required=True)
    color = fields.Integer("Color Index")
