/** @odoo-module **/
import { Component, useState, useRef, onMounted, onWillUnmount } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";

class OrbitalTimeline extends Component {
    static template = "orbital_timeline.OrbitalTimeline";

    setup() {
        this.orm = useService("orm");

        this.state = useState({
            items: [],
            expandedItems: {},
            rotationAngle: 0,
            autoRotate: true,
            pulseEffect: {},
            activeNodeId: null,
            loading: true,
        });

        this._rotationTimer = null;
        this.containerRef = useRef("container");
        this.orbitRef = useRef("orbit");

        onMounted(async () => {
            await this._loadData();
            this._startRotation();
        });

        onWillUnmount(() => {
            this._stopRotation();
        });
    }

    async _loadData() {
        try {
            const items = await this.orm.searchRead(
                "orbital.timeline.item",
                [],
                [
                    "name",
                    "date",
                    "content",
                    "category",
                    "icon",
                    "related_item_ids",
                    "status",
                    "energy",
                    "sequence",
                ],
                { order: "sequence asc, id asc" }
            );
            this.state.items = items;
        } catch (e) {
            console.error("OrbitalTimeline: failed to load data", e);
        } finally {
            this.state.loading = false;
        }
    }

    _startRotation() {
        if (this._rotationTimer) return;
        this._rotationTimer = setInterval(() => {
            if (this.state.autoRotate) {
                this.state.rotationAngle = Number(
                    ((this.state.rotationAngle + 0.3) % 360).toFixed(3)
                );
            }
        }, 50);
    }

    _stopRotation() {
        if (this._rotationTimer) {
            clearInterval(this._rotationTimer);
            this._rotationTimer = null;
        }
    }

    handleContainerClick(ev) {
        if (ev.target === this.containerRef.el || ev.target === this.orbitRef.el) {
            this.state.expandedItems = {};
            this.state.activeNodeId = null;
            this.state.pulseEffect = {};
            this.state.autoRotate = true;
        }
    }

    toggleItem(id) {
        const wasExpanded = !!this.state.expandedItems[id];
        if (!wasExpanded) {
            this.state.expandedItems = { [id]: true };
            this.state.activeNodeId = id;
            this.state.autoRotate = false;
            const pulse = {};
            this._getRelatedIds(id).forEach((rid) => {
                pulse[rid] = true;
            });
            this.state.pulseEffect = pulse;
            this._centerViewOnNode(id);
        } else {
            this.state.expandedItems = {};
            this.state.activeNodeId = null;
            this.state.autoRotate = true;
            this.state.pulseEffect = {};
        }
    }

    _centerViewOnNode(nodeId) {
        const idx = this.state.items.findIndex((i) => i.id === nodeId);
        const total = this.state.items.length;
        this.state.rotationAngle = 270 - (idx / total) * 360;
    }

    _getRelatedIds(itemId) {
        const item = this.state.items.find((i) => i.id === itemId);
        return item ? item.related_item_ids : [];
    }

    _isRelatedToActive(itemId) {
        if (!this.state.activeNodeId) return false;
        return this._getRelatedIds(this.state.activeNodeId).includes(itemId);
    }

    // ---- Template helpers ----

    nodeStyle(item, index) {
        const total = this.state.items.length;
        const angle = ((index / total) * 360 + this.state.rotationAngle) % 360;
        const radian = (angle * Math.PI) / 180;
        const x = 200 * Math.cos(radian);
        const y = 200 * Math.sin(radian);
        const expanded = !!this.state.expandedItems[item.id];
        const zIndex = expanded ? 200 : Math.round(100 + 50 * Math.cos(radian));
        const opacity = expanded
            ? 1
            : Math.max(0.4, Math.min(1, 0.4 + 0.6 * ((1 + Math.sin(radian)) / 2)));
        return `transform: translate(${x}px, ${y}px); z-index: ${zIndex}; opacity: ${opacity};`;
    }

    auraStyle(item) {
        const size = item.energy * 0.5 + 40;
        const offset = (size - 40) / 2;
        return `width: ${size}px; height: ${size}px; left: -${offset}px; top: -${offset}px;`;
    }

    nodeBtnClass(item) {
        if (this.state.expandedItems[item.id]) return "ot-node-btn ot-node-btn--expanded";
        if (this._isRelatedToActive(item.id)) return "ot-node-btn ot-node-btn--related";
        return "ot-node-btn";
    }

    auraPulseClass(item) {
        return "ot-aura" + (this.state.pulseEffect[item.id] ? " ot-aura--pulsing" : "");
    }

    titleClass(item) {
        return "ot-node-title" + (this.state.expandedItems[item.id] ? " ot-node-title--active" : "");
    }

    iconClass(icon) {
        const map = {
            calendar: "fa fa-calendar",
            code: "fa fa-code",
            "file-text": "fa fa-file-text",
            user: "fa fa-user",
            clock: "fa fa-clock-o",
            link: "fa fa-link",
            bolt: "fa fa-bolt",
        };
        return map[icon] || "fa fa-circle";
    }

    statusLabel(status) {
        if (status === "completed") return "COMPLETE";
        if (status === "in-progress") return "IN PROGRESS";
        return "PENDING";
    }

    statusBadgeClass(status) {
        if (status === "completed") return "ot-badge ot-badge--completed";
        if (status === "in-progress") return "ot-badge ot-badge--in-progress";
        return "ot-badge ot-badge--pending";
    }

    getRelatedItem(relId) {
        return this.state.items.find((i) => i.id === relId);
    }
}

registry.category("public_components").add("orbital_timeline.orbital_timeline", OrbitalTimeline);
