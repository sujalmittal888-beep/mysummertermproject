"""Visualization Engine: proper flowchart PNG (matplotlib), interactive HTML (PyVis), GraphML."""
from __future__ import annotations

import json
import textwrap
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.patches as mpatches
import matplotlib.patheffects as pe
import matplotlib.pyplot as plt
import networkx as nx
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch, Polygon

from taskflow.logging_config import get_logger

logger = get_logger(__name__)

# ── Palette ───────────────────────────────────────────────────────────────────
_ACTION_COLORS = {
    "navigate":  "#2563EB",
    "locate":    "#0891B2",
    "pick":      "#16A34A",
    "place":     "#DC2626",
    "inspect":   "#9333EA",
    "scan":      "#D97706",
    "sort":      "#0D9488",
    "transfer":  "#7C3AED",
    "move":      "#DB2777",
    "assemble":  "#EA580C",
    "verify":    "#059669",
    "deliver":   "#B45309",
}
_DEFAULT_COLOR  = "#475569"
_BG_COLOR       = "#FFFFFF"
_EDGE_COLOR     = "#94A3B8"
_COND_COLOR     = "#F43F5E"
_TEXT_COLOR     = "#FFFFFF"
_FONT           = "DejaVu Sans"

# node dimensions (in data units)
_W, _H    = 2.6, 0.78   # rectangle width / height
_DW, _DH  = 2.0, 0.90   # diamond half-widths
_X_GAP    = 3.8          # horizontal gap between layers
_Y_GAP    = 1.5          # vertical gap between parallel nodes


def _layered_pos(graph: nx.DiGraph) -> dict[str, tuple[float, float]]:
    """Left-to-right topological layout; parallel nodes stacked vertically."""
    if not nx.is_directed_acyclic_graph(graph):
        # fallback – shouldn't happen after validation
        gens = list(nx.topological_generations(graph))
    else:
        gens = list(nx.topological_generations(graph))

    pos: dict[str, tuple[float, float]] = {}
    for x_idx, gen in enumerate(gens):
        nodes = sorted(gen)
        n = len(nodes)
        for y_idx, node in enumerate(nodes):
            y = -y_idx * _Y_GAP + (n - 1) * _Y_GAP / 2
            pos[node] = (x_idx * _X_GAP, y)
    return pos


def _is_decision(graph: nx.DiGraph, node: str) -> bool:
    """A node is a decision if it has any conditional outgoing edges."""
    return any(d.get("conditional") for _, _, d in graph.out_edges(node, data=True))


def _draw_rect(ax: plt.Axes, cx: float, cy: float, color: str,
               label: str, sublabel: str = "") -> None:
    box = FancyBboxPatch(
        (cx - _W / 2, cy - _H / 2), _W, _H,
        boxstyle="round,pad=0.06",
        linewidth=1.4,
        edgecolor="white",
        facecolor=color,
        zorder=3,
    )
    ax.add_patch(box)
    # shadow
    shadow = FancyBboxPatch(
        (cx - _W / 2 + 0.04, cy - _H / 2 - 0.04), _W, _H,
        boxstyle="round,pad=0.06",
        linewidth=0,
        facecolor="#00000022",
        zorder=2,
    )
    ax.add_patch(shadow)
    ax.text(cx, cy + (0.10 if sublabel else 0), label,
            ha="center", va="center", fontsize=8.5, fontweight="bold",
            color=_TEXT_COLOR, zorder=4, fontfamily=_FONT)
    if sublabel:
        ax.text(cx, cy - 0.18, sublabel,
                ha="center", va="center", fontsize=6.8,
                color="rgba(255,255,255,0.8)" if False else "#FFFFFFCC",
                zorder=4, fontfamily=_FONT, style="italic")


def _draw_diamond(ax: plt.Axes, cx: float, cy: float, color: str, label: str) -> None:
    hw, hh = _DW / 2, _DH / 2
    pts = [(cx, cy + hh), (cx + hw, cy), (cx, cy - hh), (cx - hw, cy)]
    diamond = Polygon(pts, closed=True, facecolor=color, edgecolor="white",
                      linewidth=1.4, zorder=3)
    ax.add_patch(diamond)
    shadow_pts = [(cx + 0.04, cy + hh - 0.04), (cx + hw + 0.04, cy - 0.04),
                  (cx + 0.04, cy - hh - 0.04), (cx - hw + 0.04, cy - 0.04)]
    shadow = Polygon(shadow_pts, closed=True, facecolor="#00000022",
                     linewidth=0, zorder=2)
    ax.add_patch(shadow)
    wrapped = "\n".join(textwrap.wrap(label, 14))
    ax.text(cx, cy, wrapped, ha="center", va="center",
            fontsize=8, fontweight="bold", color=_TEXT_COLOR, zorder=4, fontfamily=_FONT)


def _node_border(pos: dict, node: str, graph: nx.DiGraph,
                 direction: str = "right") -> tuple[float, float]:
    """Return the connection point on a node boundary toward `direction`."""
    cx, cy = pos[node]
    is_d = _is_decision(graph, node) or _node_is_decision_target(graph, node)
    hw = (_DW / 2) if is_d else (_W / 2)
    hh = (_DH / 2) if is_d else (_H / 2)
    if direction == "right":  return (cx + hw, cy)
    if direction == "left":   return (cx - hw, cy)
    if direction == "top":    return (cx, cy + hh)
    if direction == "bottom": return (cx, cy - hh)
    return (cx, cy)


def _node_is_decision_target(graph: nx.DiGraph, node: str) -> bool:
    return _is_decision(graph, node)


class GraphVisualizationService:

    def render_png(self, graph: nx.DiGraph, path: Path) -> Path:
        path.parent.mkdir(parents=True, exist_ok=True)

        if not nx.is_directed_acyclic_graph(graph):
            logger.warning("Graph has cycles — forcing DAG for visualization")
            graph = nx.DiGraph(graph)  # copy; visual only

        pos = _layered_pos(graph)
        n_layers = len(set(x for x, _ in pos.values())) if pos else 1
        n_nodes  = graph.number_of_nodes()
        max_parallel = max(
            (sum(1 for v in pos if abs(pos[v][0] - x) < 0.1)
             for x in set(p[0] for p in pos.values())),
            default=1,
        )

        fig_w = max(12, n_layers * _X_GAP + 3)
        fig_h = max(6, max_parallel * _Y_GAP + 3)
        fig, ax = plt.subplots(figsize=(fig_w, fig_h), dpi=150)
        fig.patch.set_facecolor(_BG_COLOR)
        ax.set_facecolor(_BG_COLOR)

        # ── Draw edges first (behind nodes) ──────────────────────────────
        for u, v, data in graph.edges(data=True):
            xu, yu = pos[u]
            xv, yv = pos[v]
            is_cond = data.get("conditional", False)
            color   = _COND_COLOR if is_cond else _EDGE_COLOR

            # exit from right side of u, enter left side of v
            x_start = xu + (_DW / 2 if _is_decision(graph, u) else _W / 2)
            x_end   = xv - (_DW / 2 if _is_decision(graph, v) else _W / 2)
            y_start = yu
            y_end   = yv

            style = "Simple,tail_width=1.5,head_width=8,head_length=6"
            ax.annotate(
                "", xy=(x_end, y_end), xytext=(x_start, y_start),
                arrowprops=dict(
                    arrowstyle="-|>",
                    color=color,
                    lw=1.6,
                    connectionstyle="arc3,rad=0.0" if abs(y_end - y_start) < 0.05
                                    else f"arc3,rad={0.15 * (1 if y_end < y_start else -1)}",
                ),
                zorder=1,
            )

            # edge label (YES / NO / condition text)
            cond_label = data.get("condition") or ""
            if is_cond and cond_label:
                mx = (x_start + x_end) / 2
                my = (y_start + y_end) / 2 + 0.18
                ax.text(mx, my, cond_label.upper(), fontsize=7.5, ha="center",
                        color=_COND_COLOR, fontweight="bold", zorder=5, fontfamily=_FONT,
                        bbox=dict(boxstyle="round,pad=0.15", facecolor="white",
                                  edgecolor=_COND_COLOR, linewidth=0.8, alpha=0.9))

        # ── Draw nodes ────────────────────────────────────────────────────
        for node, data in graph.nodes(data=True):
            cx, cy = pos[node]
            color   = _ACTION_COLORS.get(data.get("action", ""), _DEFAULT_COLOR)
            label   = f"{node} · {data.get('action', '').upper()}"
            desc    = data.get("description", "")
            short   = textwrap.shorten(desc, width=28, placeholder="…")

            if _is_decision(graph, node):
                _draw_diamond(ax, cx, cy, color, label)
            else:
                _draw_rect(ax, cx, cy, color, label, short)

        # ── Legend ────────────────────────────────────────────────────────
        used_actions = {graph.nodes[v].get("action", "") for v in graph.nodes}
        handles = [
            mpatches.Patch(color=c, label=a.capitalize())
            for a, c in _ACTION_COLORS.items() if a in used_actions
        ]
        if any(d.get("conditional") for _, _, d in graph.edges(data=True)):
            handles.append(mpatches.Patch(color=_COND_COLOR, label="Conditional"))
        if handles:
            ax.legend(handles=handles, loc="upper left", fontsize=8,
                      frameon=True, framealpha=0.9, edgecolor="#E2E8F0")

        # ── Title ─────────────────────────────────────────────────────────
        title = graph.graph.get("instruction", "Task Flow Graph")
        ax.set_title(textwrap.shorten(title, 90, placeholder="…"),
                     fontsize=10, pad=14, color="#1E293B", fontfamily=_FONT)

        ax.autoscale()
        ax.margins(0.15)
        ax.axis("off")
        fig.tight_layout()
        fig.savefig(path, bbox_inches="tight", facecolor=_BG_COLOR)
        plt.close(fig)
        logger.info("PNG written to %s", path)
        return path

    def render_html(self, graph: nx.DiGraph, path: Path) -> Path:
        from pyvis.network import Network

        path.parent.mkdir(parents=True, exist_ok=True)
        net = Network(
            height="600px", width="100%", directed=True,
            bgcolor="#F8FAFC", cdn_resources="remote",
            heading="",
        )
        net.set_options(json.dumps({
            "layout": {
                "hierarchical": {
                    "enabled": True,
                    "direction": "LR",
                    "sortMethod": "directed",
                    "levelSeparation": 200,
                    "nodeSpacing": 120,
                    "treeSpacing": 160,
                }
            },
            "physics": {"enabled": False},
            "edges": {
                "arrows": {"to": {"enabled": True, "scaleFactor": 0.8}},
                "smooth": {"type": "curvedCW", "roundness": 0.1},
                "color": {"inherit": False},
                "font": {"size": 11, "color": "#EF4444", "face": "Inter"},
                "width": 2,
            },
            "nodes": {
                "shape": "box",
                "borderWidth": 0,
                "shadow": {"enabled": True, "color": "rgba(0,0,0,0.15)", "size": 8},
                "font": {"size": 13, "color": "#FFFFFF", "face": "Inter", "bold": True},
                "margin": 12,
            },
            "interaction": {
                "hover": True,
                "navigationButtons": True,
                "zoomView": True,
                "tooltipDelay": 100,
            },
        }))

        for v, data in graph.nodes(data=True):
            color  = _ACTION_COLORS.get(data.get("action", ""), _DEFAULT_COLOR)
            is_dec = _is_decision(graph, v)
            tooltip = (
                f"<b>{v}</b><br>"
                f"Action: {data.get('action', '')}<br>"
                f"Description: {data.get('description', '')}<br>"
                f"Condition: {data.get('condition') or '—'}<br>"
                f"Metadata: {json.dumps(data.get('metadata', {}))}"
            )
            net.add_node(
                v,
                label=f"{v}\n{data.get('action', '').upper()}",
                title=tooltip,
                shape="diamond" if is_dec else "box",
                color={"background": color, "border": color, "highlight": {"background": color}},
                font={"color": "#FFFFFF", "face": "Inter", "size": 13},
                borderWidthSelected=2,
                size=20 if is_dec else 16,
            )

        for u, v, data in graph.edges(data=True):
            is_cond = data.get("conditional", False)
            net.add_edge(
                u, v,
                color=_COND_COLOR if is_cond else "#94A3B8",
                dashes=is_cond,
                label=data.get("condition") or "",
                width=2,
                title=f"type: {data.get('dependency_type', 'sequential')}",
            )

        net.write_html(str(path), open_browser=False, notebook=False)
        logger.info("HTML written to %s", path)
        return path

    def export_graphml(self, graph: nx.DiGraph, path: Path) -> Path:
        path.parent.mkdir(parents=True, exist_ok=True)
        export = nx.DiGraph(**{k: str(v) for k, v in graph.graph.items()})
        for v, data in graph.nodes(data=True):
            export.add_node(
                v,
                task_id=str(data.get("task_id", v)),
                action=str(data.get("action", "")),
                description=str(data.get("description", "")),
                condition=str(data.get("condition") or ""),
                metadata=json.dumps(data.get("metadata", {})),
            )
        for u, v, data in graph.edges(data=True):
            export.add_edge(
                u, v,
                dependency_type=str(data.get("dependency_type", "sequential")),
                conditional=str(data.get("conditional", False)),
                condition=str(data.get("condition") or ""),
            )
        nx.write_graphml(export, path)
        logger.info("GraphML written to %s", path)
        return path
