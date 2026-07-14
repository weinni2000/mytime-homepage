{
    "name": "Orbital Timeline",
    "version": "19.0.1.0.0",
    "summary": "Interactive radial orbital timeline on the website",
    "author": "mytime.click",
    "category": "Website",
    "license": "LGPL-3",
    "depends": ["website"],
    "data": [
        "security/ir.model.access.csv",
        "views/orbital_timeline_item_views.xml",
        "views/orbital_timeline_templates.xml",
    ],
    "demo": [
        "demo/orbital_timeline_item_demo.xml",
    ],
    "assets": {
        "web.assets_frontend": [
            "orbital_timeline/static/src/orbital_timeline/orbital_timeline.scss",
            "orbital_timeline/static/src/orbital_timeline/orbital_timeline.xml",
            "orbital_timeline/static/src/orbital_timeline/orbital_timeline.js",
            "orbital_timeline/static/src/portfolio.scss",
            "orbital_timeline/static/src/portfolio.xml",
            "orbital_timeline/static/src/portfolio.js",
        ],
    },
    "application": False,
    "installable": True,
}
