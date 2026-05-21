import logging
import os
import pathlib
import random
import re
import string

from lxml import etree

from odoo import models

_logger = logging.getLogger(__name__)

_logger = logging.getLogger(__name__)


class WebsitePage(models.Model):
    _inherit = "website.page"

    def download_footer(self):
        _footer_templates = [
            "website.template_footer_descriptive",
            "website.template_footer_centered",
            "website.template_footer_links",
            "website.template_footer_minimalist",
            "website.template_footer_contact",
            "website.template_footer_call_to_action",
            "website.template_footer_headline",
            # Default one, keep it last
            "website.footer_custom",
        ]

        id_ui_view_ids = self.env["ir.ui.view"].search(
            [("key", "in", _footer_templates)]
        )  # , ('module', '=', 'website.page')

        id_ui_view_id = self.env["ir.ui.view"]
        out_tree = etree.fromstring("<odoo></odoo>")
        module_name = "theme_nw"

        # if the footer got inherited before we use the inheriting one.
        # currently it only supports a replace xpath which replaces the whole footer
        relevant_id_ui_view_ids = self.env["ir.ui.view"]
        for id_ui_view_id in id_ui_view_ids:
            inherited = self.env["ir.ui.view"].search(
                [("inherit_id", "=", id_ui_view_id.id)]
            )
            if inherited:
                relevant_id_ui_view_ids += inherited
            else:
                relevant_id_ui_view_ids += id_ui_view_id

        for id_ui_view_id in relevant_id_ui_view_ids:
            if id_ui_view_id.active is True:
                xml_arch = etree.fromstring(id_ui_view_id.arch)
                website_data = etree.tostring(out_tree)
                # body = xml_arch.find("data")
                xml_arch.tag = "template"
                attributes = xml_arch.attrib
                # we inherit the original one
                attributes["inherit_id"] = id_ui_view_id.key
                splitted = id_ui_view_id.key.split(".")
                if splitted:
                    name_only = splitted[-1]
                attributes["id"] = f"{module_name}." + name_only
                out_tree.append(xml_arch)

        app_folder = self.get_app_root_folder()
        app_root_folder = os.path.join(app_folder, f"{module_name}/views")

        model = "website_templates"
        save_path = f"{app_root_folder}/{model}.xml"
        with open(save_path, "wb") as f:
            website_data = etree.tostring(out_tree)
            f.write(website_data)
        if id_ui_view_id:
            _logger.info("print")
        #    self.env["ir.ui.view"].browse(id_model_data_id.id)
        else:
            _logger.warning("no footer found")

    def get_xml_of_view(self, rec):
        model_name = rec.model

        if not model_name:
            model_name = "website.page"
        fields = [
            "name",
            "type",
            "url",
            "website_indexed",
            "is_published",
            "key",
            "arch",
        ]
        # doc = etree.fromstring("<odoo></odoo>")
        # doc = etree.ElementTree(page)
        # models = self.env[model_name].search([])
        for record in rec:
            mid = record._get_external_ids().get(record.id, [False])
            if mid:
                xmlid = mid[0]
            else:
                xmlid = False
            if xmlid:
                pass
            else:
                letters = string.ascii_lowercase
                xmlid = "".join(random.choice(letters) for i in range(10))
            # Add the subelements
            recordElement = etree.Element(
                "record",
                id=xmlid,
                model=record._name,  # "res.partner"
            )
            #

            for field in fields:
                fieldname_partner = "parent_id"
                if field == fieldname_partner:
                    ir_model_data = self.env["ir.model.data"].search(
                        [
                            (
                                "model",
                                "=",
                                "forum.post.category",
                            ),  # "res.partner", "forum.post.category"
                            ("res_id", "=", record.parent_id.id),
                        ]
                    )
                    if ir_model_data.name:
                        fieldElement = etree.SubElement(
                            recordElement,
                            "field",
                            name=fieldname_partner,
                            ref=ir_model_data.name,
                        )
                    else:
                        pass
                        # raise UserError(self.env._("No record found"))
                elif field == "category_tag_ids":
                    reflist = []
                    for tag in record.category_tag_ids:
                        # ir_model_data = self.env["ir.model.data"].search(
                        #    [
                        #       (
                        #            "model",
                        #            "=",
                        #            "category.tag",
                        #        ),
                        #        ("res_id", "=", tag.id),
                        #    ]
                        # )
                        med = tag._get_external_ids().get(tag.id, [False])
                        if med:
                            xmlid = med[0]
                        else:
                            xmlid = False
                        if xmlid:
                            refstring = f"ref('{xmlid}')"
                            reflist.append(refstring)
                    if reflist:
                        reflist_str = ",".join(reflist)
                        fieldElement = etree.SubElement(
                            recordElement,
                            "field",
                            name="category_tag_ids",
                            eval=f"[(6,0,[{reflist_str}])]",
                        )

                    #        <field
                # name="category_tag_ids"
                # eval="[(6,0,[ref('bulletin_board_post.category_gastspiele')])]"
                # />
                elif field == "arch":
                    fieldElement = etree.SubElement(
                        recordElement, "field", name=field, type="xml"
                    )
                    el = record[field]
                    arch_tree = etree.fromstring(el)
                    fieldElement.append(arch_tree)
                else:
                    el = record[field]
                    if el:
                        fieldElement = etree.SubElement(
                            recordElement, "field", name=field
                        )
                        if isinstance(el, float):
                            el = str(el)
                        fieldElement.text = str(el)
        return recordElement

    def download_dep(self):
        base_url = self.env["ir.config_parameter"].sudo().get_param("web.base.url")
        base_url = base_url.replace("17069", "8069")
        image_url = ""
        image_url = base_url + image_url
        # headers = {
        #     "User-Agent": "Mozilla/5.0 (X11;
        # Linux x86_64; rv:60.0) Gecko/20100101 Firefox/60.0",
        #     "Accept": "text/html,application
        # /xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        #     "Accept-Language": "en-US,en;q=0.9",
        # }
        # img_data = requests.get(url=image_url, headers=headers).content

    def get_pictures(self, save_path):
        with open(save_path) as f:
            xml = f.read()

        uploaded_images = re.findall(r'(/web/image(?!/website).+?)(&quot|")', xml)

        # we get all the images that are uploaded in the system
        # we store the new save name and all the old names
        # as the system automatically creates multiple versions
        # depending on the use case.
        up_images = set()
        replace = {}
        for image_url in uploaded_images:
            image_url = image_url[0]
            stem = pathlib.Path(image_url).stem
            # if stem not in replace:
            #    replace[stem] = [image_url]
            # else:
            #   replace[stem].append(image_url)
            replace[image_url] = stem
            up_images.add(stem)

        for image_url in up_images:
            app_folder = self.get_app_root_folder()
            module_name = "theme_nw"

            app_root_folder = os.path.join(
                app_folder, f"{module_name}/static/src/img/website"
            )

            attachment_ids = self.env["ir.attachment"].search(
                [
                    ("name", "ilike", image_url),  # ("original_id", "=", False)
                ],
                limit=1,
            )
            if attachment_ids:
                attachment_id = attachment_ids[0]
            else:
                _logger.warning("stop")
            full_path = attachment_id._full_path(attachment_id.store_fname)

            with open(full_path, "rb") as handler:
                img_data = handler.read()

            with open(app_root_folder + "/" + attachment_id.name, "wb") as handler:
                handler.write(img_data)

            new_dict = {}
            for key, value in replace.items():
                model_name = "theme_nw"
                if value == image_url:
                    new_value = (
                        f"/{model_name}/static/src/img/website/{attachment_id.name}"
                    )
                    new_dict[key] = new_value
                # else:
                #    new_dict[key] = value
            replace.update(new_dict)

        # we remove the old image urls and replace them with the new ones
        for key, value in replace.items():
            xml = xml.replace(key, value)

        with open(save_path, "w") as f:
            f.write(xml)

    def get_xml_of_model(self, rec):
        model_name = rec.model

        if not model_name:
            model_name = "website.page"
        fields = [
            "name",
            "type",
            "url",
            "website_indexed",
            "is_published",
            "key",
            "arch",
        ]
        # doc = etree.fromstring("<odoo></odoo>")
        # doc = etree.ElementTree(page)
        # models = self.env[model_name].search([])
        for record in rec:
            mid = record._get_external_ids().get(record.id, [False])
            if mid:
                xmlid = mid[0]
            else:
                xmlid = False
            if xmlid:
                pass
            else:
                letters = string.ascii_lowercase
                xmlid = "".join(random.choice(letters) for i in range(10))
            # Add the subelements
            recordElement = etree.Element(
                "record",
                id=xmlid,
                model=record._name,  # "res.partner"
            )
            #

            for field in fields:
                fieldname_partner = "parent_id"
                if field == fieldname_partner:
                    ir_model_data = self.env["ir.model.data"].search(
                        [
                            (
                                "model",
                                "=",
                                "forum.post.category",
                            ),  # "res.partner", "forum.post.category"
                            ("res_id", "=", record.parent_id.id),
                        ]
                    )
                    if ir_model_data.name:
                        fieldElement = etree.SubElement(
                            recordElement,
                            "field",
                            name=fieldname_partner,
                            ref=ir_model_data.name,
                        )
                    else:
                        pass
                        # raise UserError(self.env._("No record found"))
                elif field == "category_tag_ids":
                    reflist = []
                    for tag in record.category_tag_ids:
                        # ir_model_data = self.env["ir.model.data"].search(
                        #    [
                        #       (
                        #            "model",
                        #            "=",
                        #            "category.tag",
                        #        ),
                        #        ("res_id", "=", tag.id),
                        #    ]
                        # )
                        med = tag._get_external_ids().get(tag.id, [False])
                        if med:
                            xmlid = med[0]
                        else:
                            xmlid = False
                        if xmlid:
                            refstring = f"ref('{xmlid}')"
                            reflist.append(refstring)
                    if reflist:
                        reflist_str = ",".join(reflist)
                        fieldElement = etree.SubElement(
                            recordElement,
                            "field",
                            name="category_tag_ids",
                            eval=f"[(6,0,[{reflist_str}])]",
                        )

                    #        <field
                # name="category_tag_ids"
                # eval="[(6,0,[ref('bulletin_board_post.category_gastspiele')])]"
                # />
                elif field == "arch":
                    fieldElement = etree.SubElement(
                        recordElement, "field", name=field, type="xml"
                    )
                    el = record[field]
                    arch_tree = etree.fromstring(el)
                    fieldElement.append(arch_tree)
                else:
                    el = record[field]
                    if el:
                        fieldElement = etree.SubElement(
                            recordElement, "field", name=field
                        )
                        if isinstance(el, float):
                            el = str(el)
                        fieldElement.text = str(el)
        return recordElement

    def get_app_root_folder(self):
        # file_open(
        #        f"{module_name}/data/website_data.xml", "w"
        #    ).read()
        current_path = os.path.dirname(os.path.abspath(__file__))
        # module_dir = os.path.join(current_path, "..")
        module_dir = os.path.split(current_path)[0]
        app_folder = os.path.split(module_dir)[0]

        return app_folder

    def export_pages(self, invoice_date=None):
        out_tree = etree.fromstring("<odoo></odoo>")

        for record in self:
            module_name = "theme_nw"

            res = self.get_xml_of_model(record)
            out_tree.append(res)

        app_folder = self.get_app_root_folder()
        app_root_folder = os.path.join(app_folder, f"{module_name}/data")

        model = "website_page"
        save_path = f"{app_root_folder}/{model}_data.xml"
        with open(save_path, "wb") as f:
            website_data = etree.tostring(out_tree)
            f.write(website_data)

        self.get_pictures(save_path)
        self.download_footer()
