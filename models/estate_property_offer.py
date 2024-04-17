from odoo import models, fields, api
from datetime import timedelta


class EstatePropertyOffer(models.Model):
    _name = 'estate.property.offer'
    _description = 'estate.property.offer'

    price = fields.Float()
    status = fields.Selection(
        selection=[('accepted', 'Accepted'), ('refused', 'Refused')], copy=False)
    partner_id = fields.Many2one('res.partner')
    property_id = fields.Many2one('estate.property')
    validity = fields.Integer(default=7)
    date_deadline = fields.Date(
        inverse="_inverse_date_deadline", compute="_compute_date_dead_line")

    def _inverse_date_deadline(self):
        for record in self:
            if not record.create_date:
                record.date_deadline = fields.Date().today()
            else:
                record.date_deadline = fields.Date().today().replace(day=record.validity)

    @api.depends('validity')
    def _compute_date_dead_line(self):
        for record in self:
            record.date_deadline = fields.Date().today() + timedelta(days=record.validity)
