import os
import pathlib
from os import sep

folders = [
    "./ge_delivery_shipping_label_ge",
    "./ge_delivery_base",
    "./ge_printing_pdf",
    "./dpd_at_shipping_ns",
    "./shipping_backbone_ns",
    "ge_delivery_pdf_modification",
    "ge_delivery_base",
    "ge_delivery_post_at_integration",
    "ge_delivery_return_labels_base",
    "ge_delivery_post_at_return_labels",
    "ge_delivery_shipping_returns_unified",
    "ge_delivery_shipping_postprocessing",
    "dpd_at_shipping_ns",
    "shipping_backbone_ns",
]


def x(path):
    """Add a line return to trigger the pre-commit tasks"""
    with open(path, "a+") as f_load:  # pylint: disable=W1514
        f_load.write("\n")


exclude_list = ["ge_pos_open_cash", "shipping_backbone_ns", "dpd_at_shipping_ns"]

# for _folder in folders:
START = module_path = pathlib.Path(__file__).parent.parent.parent.absolute()
START = __file__.rsplit(sep, 1)[0] + sep
for dirpath, _dnames, fnames in os.walk(START):
    # if True and "bulletin_board" in dirpath:
    #    for enabled_folder in folders:
    #        if enabled_folder in dirpath:
    for f in fnames:
        for _ in exclude_list:
            if f.endswith((".py", ".xml", ".txt", ".js")):
                x(os.path.join(dirpath, f))
