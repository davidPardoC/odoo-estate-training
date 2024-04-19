from odoo import fields, models, api, exceptions


class RealStateProperty(models.Model):
    _name = "estate.property"
    _description = "Estate Propery"
    _order = "id desc"
    _sql_constraints = [('check_expected_price', 'CHECK(expected_price > 0)',
                         'The expected price must be positive.'), ('check_selling_price', 'CHECK(selling_price >= 0)', 'The selling price must be positive.')]

    name = fields.Char(required=True)
    description = fields.Text()
    postcode = fields.Char()
    date_availability = fields.Date(default=fields.Date(
    ).today().replace(month=fields.Date().today().month + 3))
    expected_price = fields.Float(required=True)
    selling_price = fields.Float(readonly=True)
    bedrooms = fields.Integer(default=2)
    living_area = fields.Integer()
    facades = fields.Integer()
    garage = fields.Boolean()
    garden = fields.Boolean()
    garden_area = fields.Integer()
    garden_orientation = fields.Selection(
        string='Type', selection=[('north', 'Nort')])
    active = fields.Boolean(default=True)
    state = fields.Selection(selection=[('new', 'New'), ('offer_received', 'Offer Received'), (
        'offer_accepted', 'Offer Accepted'), ('sold', 'Sold'), ('canceled', 'Canceled')], default='new')

    property_type_id = fields.Many2one('estate.property.type')

    buyer_id = fields.Many2one('res.partner')

    salesperson_id = fields.Many2one(
        'res.users', default=lambda self: self.env.user)

    tag_ids = fields.Many2many('estate.property.tag')
    offers_ids = fields.One2many(
        'estate.property.offer', 'property_id', string="Offers")

    total_area = fields.Integer(compute="_compute_total_area", readonly=True)
    best_price = fields.Float(compute='_compute_best_price', readonly=True)

    @api.depends("garden_area", "living_area")
    def _compute_total_area(self):
        for record in self:
            record.total_area = record.garden_area + record.living_area

    @api.depends("offers_ids.price")
    def _compute_best_price(self):
        for record in self:
            record.best_price = max(
                record.offers_ids.mapped("price"), default=0)

    # only from view context
    @api.onchange("garden")
    def _onchange_garden(self):
        if self.garden is True:
            self.garden_area = 10
            self.garden_orientation = 'north'
        else:
            self.garden_area = 0
            self.garden_orientation = ''

    def action_sold(self):
        for record in self:
            if record.state != 'canceled':
                record.state = 'sold'
            else:
                raise exceptions.UserError(
                    "You can't sell a canceled property")
        return True

    def action_cancel(self):
        for record in self:
            if record.state != 'sold':
                record.state = 'canceled'
            else:
                raise exceptions.UserError("You can't cancel a sold property")
        return True

    @api.constrains("selling_price")
    def _check_selling_price(self):
        for record in self:
            if record.selling_price < record.expected_price * 0.9:
                raise exceptions.ValidationError(
                    "The selling price is too low.")

    @api.ondelete(at_uninstall=False)
    def prevent_delete(self):
        for record in self:
            if record.state not in ('new', 'canceled'):
                raise exceptions.UserError(
                    "You can't delete a property that is not new or canceled.")
        return super().unlink()
