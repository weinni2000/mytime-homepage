# Upgrade 19.0 -> 20.0

## homepage_nw

### Technical summary

| Change | Why | Odoo source |
|---|---|---|
| Version reset to `20.0.1.0.0` | Upgrade convention | - |
| QWeb `t-set` before `t-call` -> t-call attributes (`name="expr"`, `name.f="literal"`) | New t-call syntax; applied with `odoo-bin upgrade_code --from 19.0` | [586463a5e261](https://github.com/odoo/odoo/commit/586463a5e261) |
| Dropped `from odoo import registry` / registry asserts; re-browse website after installs | `odoo` is now a PEP 420 namespace package (no `odoo/__init__.py`) | [8b3480b39740](https://github.com/odoo/odoo/commit/8b3480b39740) |
| `pycompat.to_text(etree.tostring(el))` -> `etree.tostring(el, encoding="unicode")` | `odoo.tools.pycompat` removed | [080bbf6153a0](https://github.com/odoo/odoo/commit/080bbf6153a0) |
| `field.get_translation_dictionary(...)` -> `StoredTranslations._get_translation_dictionary(field, ...)` | Translation mapping logic moved off the field | [5dc06dc6b213](https://github.com/odoo/odoo/commit/5dc06dc6b213) |
| Website logo copied as `BinaryBytes(...)` instead of `logo.decode()` / attachment rebinding | Binary fields return `BinaryValue` (raw content) | [41fe2ebdb9cc](https://github.com/odoo/odoo/commit/41fe2ebdb9cc), [2113526bcf8e](https://github.com/odoo/odoo/commit/2113526bcf8e), [c60cffd5b654](https://github.com/odoo/odoo/commit/c60cffd5b654) |
| `website.default_website` -> `base.default_website` in data | `website` model skeleton and default record moved to `base` | [ae81b6f60746](https://github.com/odoo/odoo/commit/ae81b6f60746) |
| Removed dead `template_footer_opt` (inherited `website.snippet_options`, pointed at `theme_test_custo`) | QWeb snippet options removed (moved to JS html_builder); option never worked here | [55d5144deecd](https://github.com/odoo/odoo/commit/55d5144deecd) |
| `get_current_website()` -> `env.website` / `host_id` / `base.default_website` + `website_id` in context | Helper removed | [2545a833c8e4](https://github.com/odoo/odoo/commit/2545a833c8e4) |
| `web_editor.assets` -> `website.assets` for palette SCSS customisation | Model moved with the web_editor split | [e45d44097f7c](https://github.com/odoo/odoo/commit/e45d44097f7c) |
| Catch `requests.RequestException` around IAP calls (`custom_resources`, OLG) | `iap_jsonrpc` no longer raises `AccessError` | [fda2dbd211c8](https://github.com/odoo/odoo/commit/fda2dbd211c8) |
| Custom footers keep `id="footer"` | New `website.footer_cookie_policy_link` anchors on `//div[@id='footer']` | [eaf214f7de87](https://github.com/odoo/odoo/commit/eaf214f7de87) |
| Logo data field `type="base64"` -> `type="bytes"` | `base64` deprecated in data files | [41fe2ebdb9cc](https://github.com/odoo/odoo/commit/41fe2ebdb9cc), [425f0374392c](https://github.com/odoo/odoo/commit/425f0374392c) |
| `ir.config_parameter.get_param` -> `get_str` | `get_param`/`set_param` removed | [a4f2879697a7](https://github.com/odoo/odoo/commit/a4f2879697a7) |

### Data migration

No custom migration script is needed. The `website.default_website` ->
`base.default_website` xmlid rename on existing databases is handled by
Odoo's own upgrade (odoo/upgrade#10378, referenced by ae81b6f60746). No
fields or models of this module changed.

### Functional test scenarios

1. Install `homepage_nw` on a fresh database: the default website is
   named `weingartmair.eu` and uses the bundled logo.
2. Main menu shows Home, Contact and Impressum and opens the module's pages.
3. Footer shows the custom contact footer, plus the cookie policy link
   when the cookies bar is enabled.
4. Without internet / IAP, installation still succeeds (IAP warnings are
   logged and AI text generation is skipped).
5. Theme palette `default-1` is applied (`website.assets` SCSS customisation).
