from odoo import models, fields, api, exceptions
from datetime import timedelta


class EstatePropertyOffer(models.Model):
    _name = 'estate.property.offer'
    _description = 'estate.property.offer'
    _order = "price desc"
    _sql_constraints = [('check_price', 'CHECK(price > 0)',
                         'The price must be positive.')]

    price = fields.Float()
    validity = fields.Integer(default=7)

    status = fields.Selection(
        selection=[('accepted', 'Accepted'), ('refused', 'Refused')], copy=False)
    partner_id = fields.Many2one('res.partner', required=True)
    property_id = fields.Many2one('estate.property')

    property_type_id = fields.Many2one("estate.property.type",
                                       related='property_id.property_type_id',  string="Property Type", store=True)

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

    def action_accept(self):
        if "accepted" in self.mapped("property_id.offers_ids.status"):
            raise exceptions.UserError("An offer as already been accepted.")

        for record in self:
            record.property_id.buyer_id = record.partner_id
            record.property_id.selling_price = record.price
            record.property_id.state = 'offer_accepted'
            record.status = 'accepted'
        return True

    def action_refuse(self):
        for record in self:
            record.status = 'refused'
            return True

    @api.model
    def create(self, values):
        current_offer_price = values.get('price')
        best_price = self.env['estate.property'].browse(
            values['property_id']).best_price
        if current_offer_price < best_price:
            raise exceptions.UserError(
                "The price of the offer is too low. The best price is {}".format(best_price))
        record = super().create(values)
        record.property_id.state = 'offer_received'
        return record
