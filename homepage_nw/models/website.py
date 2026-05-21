# Part of Odoo. See LICENSE file for full copyright and licensing details.

import json
import logging
import re

import requests
from lxml import etree, html

from odoo import api, models, registry
from odoo.exceptions import AccessError
from odoo.tools import pycompat
from odoo.tools.translate import xml_translate

_logger = logging.getLogger(__name__)


class Website(models.Model):
    _inherit = "website"

    @api.model
    def configurator_apply_simple(self, **kwargs):  # noqa: C901
        website = self.get_current_website()
        theme_name = kwargs["theme_name"]
        theme = self.env["ir.module.module"].search([("name", "=", theme_name)])
        theme._generate_primary_snippet_templates()
        # <PATCH>
        # redirect_url = theme.button_choose_theme()
        redirect_url = "/"
        # </PATCH>

        # Force to refresh env after install of module
        assert self.env.registry is registry()

        website.configurator_done = True

        # Enable tour
        tour_asset_id = self.env.ref("website.configurator_tour")
        tour_asset_id.copy(
            {"key": tour_asset_id.key, "website_id": website.id, "active": True}
        )

        # Set logo from generated attachment or from company's logo
        logo_attachment_id = kwargs.get("logo_attachment_id")
        company = website.company_id
        if logo_attachment_id:
            attachment = self.env["ir.attachment"].browse(logo_attachment_id)
            attachment.write(
                {
                    "res_model": "website",
                    "res_field": "logo",
                    "res_id": website.id,
                }
            )
        elif not logo_attachment_id and not company.uses_default_logo:
            website.logo = company.logo.decode("utf-8")

        # Configure the color palette
        selected_palette = kwargs.get("selected_palette")
        if selected_palette:
            Assets = self.env["web_editor.assets"]
            selected_palette_name = (
                selected_palette if isinstance(selected_palette, str) else "base-1"
            )
            Assets.make_scss_customization(
                "/website/static/src/scss/options/user_values.scss",
                {"color-palettes-name": f"'{selected_palette_name}'"},
            )
            if isinstance(selected_palette, list):
                Assets.make_scss_customization(
                    "/website/static/src/scss/options/colors/user_color_palette.scss",
                    {
                        f"o-color-{i}": color
                        for i, color in enumerate(selected_palette, 1)
                    },
                )

        # Update CTA
        cta_data = website.get_cta_data(
            kwargs.get("website_purpose"), kwargs.get("website_type")
        )
        if cta_data["cta_btn_text"]:
            xpath_view = "website.snippets"
            parent_view = (
                self.env["website"]
                .with_context(website_id=website.id)
                .viewref(xpath_view)
            )
            self.env["ir.ui.view"].create(
                {
                    "name": parent_view.key + " CTA",
                    "key": parent_view.key + "_cta",
                    "inherit_id": parent_view.id,
                    "website_id": website.id,
                    "type": "qweb",
                    "priority": 32,
                    "arch_db": f"""
                    <data>
                        <xpath expr="//t[@t-set='cta_btn_href']" position="replace">
                            <t t-set="cta_btn_href">{cta_data["cta_btn_href"]}</t>
                        </xpath>
                        <xpath expr="//t[@t-set='cta_btn_text']" position="replace">
                            <t t-set="cta_btn_text">{cta_data["cta_btn_text"]}</t>
                        </xpath>
                    </data>
                """,
                }
            )
            try:
                view_id = self.env["website"].viewref("website.header_call_to_action")
                if view_id:
                    el = etree.fromstring(view_id.arch_db)
                    btn_cta_el = el.xpath("//a[hasclass('btn_cta')]")
                    if btn_cta_el:
                        btn_cta_el[0].attrib["href"] = cta_data["cta_btn_href"]
                        btn_cta_el[0].text = cta_data["cta_btn_text"]
                    view_id.with_context(website_id=website.id).write(
                        {"arch_db": etree.tostring(el)}
                    )
            except ValueError as e:
                _logger.warning(e)

        # Configure the features
        features = self.env["website.configurator.feature"].browse(
            kwargs.get("selected_features")
        )

        menu_company = self.env["website.menu"]
        if (
            len(features.filtered("menu_sequence")) > 5
            and len(features.filtered("menu_company")) > 1
        ):
            menu_company = self.env["website.menu"].create(
                {
                    "name": self.env._("Company"),
                    "parent_id": website.menu_id.id,
                    "website_id": website.id,
                    "sequence": 40,
                }
            )

        pages_views = {}
        modules = self.env["ir.module.module"]
        module_data = {}
        for feature in features:
            add_menu = bool(feature.menu_sequence)
            if feature.module_id:
                if feature.module_id.state != "installed":
                    modules += feature.module_id
                if add_menu:
                    if feature.module_id.name != "website_blog":
                        module_data[feature.feature_url] = {
                            "sequence": feature.menu_sequence
                        }
                    else:
                        blogs = module_data.setdefault("#blog", [])
                        blogs.append(
                            {"name": feature.name, "sequence": feature.menu_sequence}
                        )
            elif feature.page_view_id:
                result = self.env["website"].new_page(
                    name=feature.name,
                    add_menu=add_menu,
                    page_values=dict(url=feature.feature_url, is_published=True),
                    menu_values=add_menu
                    and {
                        "url": feature.feature_url,
                        "sequence": feature.menu_sequence,
                        "parent_id": feature.menu_company
                        and menu_company.id
                        or website.menu_id.id,
                    },
                    template=feature.page_view_id.key,
                )
                pages_views[feature.iap_page_code] = result["view_id"]

        if modules:
            modules.button_immediate_install()
            assert self.env.registry is registry()

        self.env["website"].browse(website.id).configurator_set_menu_links(
            menu_company, module_data
        )

        # We need to refresh the environment of the website because we installed
        # some new module and we need the overrides of these new menus e.g. for
        # the call to `get_cta_data`.
        website = self.env["website"].browse(website.id)

        # Update footers links, needs to be done after "Features" addition to go
        # through module overrides of `configurator_get_footer_links`.
        footer_links = website.configurator_get_footer_links()
        footer_ids = [
            "website.template_footer_contact",
            "website.template_footer_headline",
            "website.footer_custom",
            "website.template_footer_links",
            "website.template_footer_minimalist",
        ]
        for footer_id in footer_ids:
            try:
                view_id = self.env["website"].viewref(footer_id)
                if view_id:
                    # Deliberately hardcode dynamic code inside the view arch,
                    # it will be transformed into static nodes after a save/edit
                    # thanks to the t-ignore in parents node.
                    arch_string = etree.fromstring(view_id.arch_db)
                    el = arch_string.xpath("//t[@t-set='configurator_footer_links']")[0]
                    el.attrib["t-value"] = json.dumps(footer_links)
                    view_id.with_context(website_id=website.id).write(
                        {"arch_db": etree.tostring(arch_string)}
                    )
            except Exception as e:
                # The xml view could have been modified in the backend, we don't
                # want the xpath error to break the configurator feature
                _logger.warning(e)

        # Load suggestion from iap for selected pages
        industry_id = kwargs["industry_id"]
        custom_resources = self._website_api_rpc(
            "/api/website/2/configurator/custom_resources/%s"
            % (industry_id if industry_id > 0 else ""),
            {"theme": theme_name},
        )

        # Generate text for the pages
        requested_pages = set(pages_views.keys()).union({"homepage"})
        configurator_snippets = website.get_theme_configurator_snippets(theme_name)
        industry = kwargs["industry_name"]

        IrQweb = self.env["ir.qweb"].with_context(
            website_id=website.id, lang=website.default_lang_id.code
        )
        snippets_cache = {}
        translated_content = {}

        def _compute_placeholder(term):
            return xml_translate.get_text_content(term).strip()

        def _render_snippet(key):
            # Using this avoids rendering the same snippet multiple times
            data = snippets_cache.get(key)
            if data:
                return data

            render = IrQweb._render(key, cta_data)

            terms = []
            xml_translate(terms.append, render)
            placeholders = [_compute_placeholder(term) for term in terms]

            if text_must_be_translated_for_openai:
                # Check if terms are translated.
                translation_dictionary = (
                    self.env["website.page"]
                    ._fields["arch_db"]
                    .get_translation_dictionary(
                        str(IrQweb._render(key, cta_data, lang="en_US")),
                        {text_generation_target_lang: str(render)},
                    )
                )
                # Remove all numeric keys.
                translation_dictionary = {
                    k: v
                    for k, v in translation_dictionary.items()
                    if not _compute_placeholder(k).isnumeric()
                }
                for from_lang_term, to_lang_terms in translation_dictionary.items():
                    translated_content[from_lang_term] = to_lang_terms[
                        text_generation_target_lang
                    ]

            data = (render, placeholders)
            snippets_cache[key] = data
            return data

        text_generation_target_lang = self.get_current_website().default_lang_id.code
        # If the target language is not English, we need a good translation
        # coverage. But if the target lang is en_XX it's ok to have en_US text.
        text_must_be_translated_for_openai = not text_generation_target_lang.startswith(
            "en_"
        )
        generated_content = {}
        for page_code in requested_pages - {"privacy_policy"}:
            snippet_list = configurator_snippets.get(page_code, [])
            for snippet in snippet_list:
                render, placeholders = _render_snippet(
                    f"website.configurator_{page_code}_{snippet}"
                )
                for placeholder in placeholders:
                    generated_content[placeholder] = ""
        if text_must_be_translated_for_openai:
            nb_terms_translated = len(
                [k for k, v in translated_content.items() if k != v]
            )
            nb_terms_total = len(translated_content)
        else:
            nb_terms_translated = len(generated_content)
            nb_terms_total = len(generated_content)
        translated_ratio = nb_terms_translated / nb_terms_total
        _logger.debug(
            "Ratio of translated content: %s%% (%s/%s)",
            translated_ratio * 100,
            nb_terms_translated,
            nb_terms_total,
        )

        if translated_ratio > 0.8:
            try:
                database_id = (
                    self.env["ir.config_parameter"].sudo().get_param("database.uuid")
                )
                response = self._OLG_api_rpc(
                    "/api/olg/1/generate_placeholder",
                    {
                        "placeholders": list(generated_content.keys()),
                        "lang": website.default_lang_id.name,
                        "industry": industry,
                        "database_id": database_id,
                    },
                )
                name_replace_parser = re.compile(r"XXXX", re.MULTILINE)
                for key in generated_content:
                    if response.get(key):
                        generated_content[key] = name_replace_parser.sub(
                            website.name, response[key], 0
                        )
            except AccessError as e:
                # If IAP is broken continue normally (without generating text)
                _logger.warning(e)
        else:
            _logger.info(
                (
                    "Skip AI text generation because "
                    "translation coverage is too low (%s%%)"
                ),
                translated_ratio * 100,
            )

        # Configure the pages
        for page_code in requested_pages:
            snippet_list = configurator_snippets.get(page_code, [])
            if page_code == "homepage":
                # <PATCH>
                # page_view_id = self.with_context(website_id=website.id).viewref(
                #    "website.homepage"
                # )
                # page_view_id = self.with_context(website_id=website.id).viewref(
                #    "homepage_nw.landing_page"
                # )
                # </PATCH>
                pass
            else:
                self.env["ir.ui.view"].browse(pages_views[page_code])
            rendered_snippets = []
            nb_snippets = len(snippet_list)
            for i, snippet in enumerate(snippet_list, start=1):
                try:
                    render, placeholders = _render_snippet(
                        f"website.configurator_{page_code}_{snippet}"
                    )

                    # Fill rendered block with AI text
                    render = xml_translate(
                        lambda x: generated_content.get(_compute_placeholder(x), x),
                        render,
                    )

                    el = html.fromstring(render)

                    # Add the data-snippet attribute to identify the snippet
                    # for compatibility code
                    el.attrib["data-snippet"] = snippet

                    # Tweak the shape of the first snippet to connect it
                    # properly with the header color in some themes
                    if i == 1:
                        shape_el = el.xpath("//*[hasclass('o_we_shape')]")
                        if shape_el:
                            shape_el[0].attrib["class"] += (
                                " o_header_extra_shape_mapping"
                            )

                    # Tweak the shape of the last snippet to connect it
                    # properly with the footer color in some themes
                    if i == nb_snippets:
                        shape_el = el.xpath("//*[hasclass('o_we_shape')]")
                        if shape_el:
                            shape_el[0].attrib["class"] += (
                                " o_footer_extra_shape_mapping"
                            )
                    rendered_snippet = pycompat.to_text(etree.tostring(el))
                    rendered_snippets.append(rendered_snippet)
                except ValueError as e:
                    _logger.warning(e)
            # <PATCH>
            # page_view_id.save(
            #    value=f'<div class="oe_structure">{"".join(rendered_snippets)}</div>',
            #    xpath="(//div[hasclass('oe_structure')])[last()]",
            # )
            # </PATCH>

        # Configure the images
        images = custom_resources.get("images", {})
        names = (
            self.env["ir.model.data"]
            .search(
                [
                    ("name", "=ilike", f"configurator\\_{website.id}\\_%"),
                    ("module", "=", "website"),
                    ("model", "=", "ir.attachment"),
                ]
            )
            .mapped("name")
        )
        for name, image_src in images.items():
            try:
                display_name = name.split(".")[1]
            except Exception as e:
                _logger.warning(e)
                display_name = ""
            extn_identifier = f"configurator_{website.id}_{display_name}"
            if extn_identifier in names:
                continue
            try:
                response = requests.get(image_src, timeout=3)
                response.raise_for_status()
            except Exception as e:
                _logger.warning("Failed to download image: %s.\n%s", image_src, e)
            else:
                attachment = self.env["ir.attachment"].create(
                    {
                        "name": name,
                        "website_id": website.id,
                        "key": name,
                        "type": "binary",
                        "raw": response.content,
                        "public": True,
                    }
                )
                self.env["ir.model.data"].create(
                    {
                        "name": extn_identifier,
                        "module": "website",
                        "model": "ir.attachment",
                        "res_id": attachment.id,
                        "noupdate": True,
                    }
                )

        def fallback_create_missing_industry_image(image_name, fallback_img_name):
            """If an industry did not specify an image, this method allows that
            specific image to be using the same image as another fallback one.
            """
            image_name = f"website.{image_name}"
            if (
                image_name not in images.keys()
                and f"website.{fallback_img_name}" in images.keys()
            ):
                try:
                    website_name = image_name.split(".")[1]
                except Exception as e:
                    _logger.warning(e)
                    website_name = ""
                extn_identifier = f"configurator_{website.id}_{website_name}"
                if extn_identifier not in names:
                    attachment = self.env["ir.attachment"].create(
                        {
                            "name": image_name,
                            "website_id": website.id,
                            "key": image_name,
                            "type": "binary",
                            "raw": self.env.ref(
                                f"website.configurator_{website.id}_{fallback_img_name}"
                            ).raw,
                            "public": True,
                        }
                    )
                    self.env["ir.model.data"].create(
                        {
                            "name": extn_identifier,
                            "module": "website",
                            "model": "ir.attachment",
                            "res_id": attachment.id,
                            "noupdate": True,
                        }
                    )

        try:
            # TODO: Remove this try/except, safety net because it was merged
            #       to close to OXP.
            fallback_create_missing_industry_image(
                "s_banner_default_image_2", "s_image_text_default_image"
            )
            fallback_create_missing_industry_image(
                "s_banner_default_image_3", "s_product_list_default_image_1"
            )
        except Exception as e:
            _logger.warning(e)

        return {"url": redirect_url, "website_id": website.id}
