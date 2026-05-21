{
    "name": "demo",
    "summary": """
        Short (1 phrase/line) summary of the module's purpose, used as
        subtitle on modules listing or apps.openerp.com""",
    "author": "mytime.click",
    "website": "https://github.com/OCA/partner-contact",
    "category": "Uncategorized",
    "version": "18.0.1.0",
    "license": "AGPL-3",
    "depends": [
        "base",
        "website",
        "theme_clean",
    ],
    "data": [
        "data/website_data.xml",
        "data/website_page_data.xml",
        "data/website_header.xml",
        "data/website_footer.xml",
        "views/footer.xml",
        "data/website_menu.xml",
    ],
    "pre_init_hook": "pre_init_hook",
    "post_init_hook": "post_init_hook",
}
