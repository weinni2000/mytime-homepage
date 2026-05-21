def pre_init_hook(env):
    """Prepare new partner_bank_id computed field.

    Add column to avoid MemoryError on an existing Odoo instance
    with lots of data.

    partner_bank_id on account.move.line requires payment_order_ok to be True
    which it won't be as it's newly introduced - nothing to compute.
    (see AccountMoveLine._compute_partner_bank_id() in models/account_move_line.py
    and AccountMove._compute_payment_order_ok() in models/account_move.py)
    """


def post_init_hook(env):
    kwargs = {
        "selected_features": [1],
        "industry_id": 2171,
        "industry_name": "marketing agency",
        "selected_palette": "default-1",
        "theme_name": "theme_clean",
        "website_purpose": "get_leads",
        "website_type": "business",
    }

    env["website"].configurator_apply_simple(**kwargs)
