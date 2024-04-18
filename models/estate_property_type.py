from odoo import models, fields


class EstatePropertyType(models.Model):
    _name = 'estate.property.type'
    _description = "Type off property"

    name = fields.Char()
    property_ids = fields.One2many('estate.property', 'property_type_id')
