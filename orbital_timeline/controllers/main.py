from odoo import http
from odoo.http import request


class OrbitalTimeline(http.Controller):
    @http.route(
        "/orbital_frontend_view",
        auth="public",
        website=True,
        sitemap=True,
    )
    def orbital_timeline(self, **kwargs):
        return request.render("orbital_timeline.orbital_timeline_page")

    @http.route(
        "/portfolio",
        auth="public",
        website=True,
        sitemap=True,
    )
    def portfolio(self, **kwargs):
        return request.render("orbital_timeline.portfolio_page")
