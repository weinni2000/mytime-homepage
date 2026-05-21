/** @odoo-module **/
import { Component } from "@odoo/owl";
import { registry } from "@web/core/registry";

const highlights = [
    {
        title: "OCA Contributions",
        description:
            "Open-source Odoo modules published on apps.odoo.com · active contributor to the Odoo Community Association.",
    },
    {
        title: "Latest Project",
        description:
            "Schwarzes-Brett.info · a hyperlocal community news platform for Austria.",
    },
    {
        title: "Availability",
        description:
            "Open for Odoo module development and consulting · remote across EU.",
    },
];

const socialLinks = [
    {
        label: "LinkedIn",
        handle: "Nikolaus Weingartmair",
        href: "https://www.linkedin.com/in/nikolaus-weingartmair-58036933/",
        icon: "fa-linkedin",
    },
    {
        label: "GitHub",
        handle: "weinni2000",
        href: "https://github.com/weinni2000",
        icon: "fa-github",
    },
    {
        label: "mytime.click",
        handle: "hello@mytime.click",
        href: "https://mytime.click",
        icon: "fa-globe",
    },
    {
        label: "Lisi Grün",
        handle: "lisigruen.at",
        href: "https://lisigruen.at",
        icon: "fa-leaf",
    },
];

class PortfolioBlock extends Component {
    static template = "orbital_timeline.PortfolioBlock";

    setup() {
        this.highlights = highlights;
        this.socialLinks = socialLinks;
    }
}

registry.category("public_components").add("orbital_timeline.portfolio_block", PortfolioBlock);
