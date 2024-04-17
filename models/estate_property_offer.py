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
        compute="_compute_date_dead_line", inverse="_inverse_date_deadline")

    @api.depends('validity')
    def _compute_date_dead_line(self):
        for record in self:
            if record.create_date:
                record.date_deadline = record.create_date + \
                    timedelta(days=record.validity)
            else:
                record.date_deadline = fields.Date().today() + timedelta(days=record.validity)

    def _inverse_date_deadline(self):
        for record in self:
            delta = record.date_deadline - \
                (record.create_date.date() or fields.Date.now())
            record.validity = delta.days
