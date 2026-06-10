"""Visualization Engine: PNG (matplotlib), interactive HTML (PyVis), GraphML."""
from __future__ import annotations

import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")  # headless rendering
import matplotlib.patches as mpatches  # noqa: E402
import matplotlib.pyplot as plt  # noqa: E402
import networkx as nx  # noqa: E402

from taskflow.logging_config import get_logger  # noqa: E402

logger = get_logger(__name__)

_ACTION_COLORS = {
    "navigate": "#4C78A8",
    "locate": "#72B7B2",
    "pick": "#54A24B",
    "place": "#E45756",
    "inspect": "#F58518",
    "move": "#B279A2",
    "scan": "#FF9DA6",
    "sort": "#9D755D",
    "transfer": "#EECA3B",
}
_DEFAULT_COLOR = "#BAB0AC"


def _layered_positions(graph: nx.DiGraph) -> dict[str, tuple[float, float]]:
    """Deterministic left-to-right layered layout based on topological generations."""
    if not nx.is_directed_acyclic_graph(graph):
        return nx.spring_layout(graph, seed=42)
    pos: dict[str, tuple[float, float]] = {}
    for x, generation in enumerate(nx.topological_generations(graph)):
        nodes = sorted(generation)
        n = len(nodes)
        for i, node in enumerate(nodes):
            y = 0.0 if n == 1 else (n - 1) / 2.0 - i
            pos[node] = (float(x) * 2.2, y * 1.6)
    return pos


class GraphVisualizationService:
    """Renders the Task Flow Graph into publication-quality artifacts."""

    def render_png(self, graph: nx.DiGraph, path: Path) -> Path:
        path.parent.mkdir(parents=True, exist_ok=True)
        pos = _layered_positions(graph)
        n = max(graph.number_of_nodes(), 1)
        fig, ax = plt.subplots(figsize=(max(10, 2.4 * n), 6.5), dpi=150)

        node_colors = [
            _ACTION_COLORS.get(graph.nodes[v].get("action", ""), _DEFAULT_COLOR)
            for v in graph.nodes
        ]
        sequential = [(u, v) for u, v, d in graph.edges(data=True) if not d.get("conditional")]
        conditional = [(u, v) for u, v, d in graph.edges(data=True) if d.get("conditional")]

        nx.draw_networkx_nodes(
            graph, pos, ax=ax, node_size=2600, node_color=node_colors,
            edgecolors="#333333", linewidths=1.2,
        )
        nx.draw_networkx_edges(
            graph, pos, ax=ax, edgelist=sequential, arrows=True, arrowsize=22,
            width=1.8, edge_color="#555555", node_size=2600,
            connectionstyle="arc3,rad=0.05",
        )
        nx.draw_networkx_edges(
            graph, pos, ax=ax, edgelist=conditional, arrows=True, arrowsize=22,
            width=1.8, edge_color="#E45756", style="dashed", node_size=2600,
            connectionstyle="arc3,rad=0.12",
        )
        nx.draw_networkx_labels(
            graph, pos, ax=ax,
            labels={v: f"{v}\n{graph.nodes[v].get('action', '')}" for v in graph.nodes},
            font_size=9, font_weight="bold", font_color="white",
        )
        edge_labels = {
            (u, v): d.get("condition") or ""
            for u, v, d in graph.edges(data=True)
            if d.get("conditional")
        }
        if edge_labels:
            nx.draw_networkx_edge_labels(
                graph, pos, ax=ax, edge_labels=edge_labels, font_size=8,
                font_color="#B03030",
            )
        # Description captions under each node
        for v, (x, y) in pos.items():
            desc = graph.nodes[v].get("description", "")
            if desc:
                ax.text(x, y - 0.55, _wrap(desc, 22), ha="center", va="top", fontsize=7.5,
                        color="#333333")

        handles = [
            mpatches.Patch(color=c, label=a)
            for a, c in _ACTION_COLORS.items()
            if any(graph.nodes[v].get("action") == a for v in graph.nodes)
        ]
        if conditional:
            handles.append(
                mpatches.Patch(facecolor="white", edgecolor="#E45756", hatch="--",
                               label="conditional edge")
            )
        if handles:
            ax.legend(handles=handles, loc="upper left", fontsize=8, frameon=False)

        ax.set_title(graph.graph.get("instruction", "Task Flow Graph"), fontsize=11, pad=14)
        ax.axis("off")
        ax.margins(0.12)
        fig.tight_layout()
        fig.savefig(path, bbox_inches="tight")
        plt.close(fig)
        logger.info("PNG written to %s", path)
        return path

    def render_html(self, graph: nx.DiGraph, path: Path) -> Path:
        from pyvis.network import Network

        path.parent.mkdir(parents=True, exist_ok=True)
        net = Network(
            height="720px", width="100%", directed=True, bgcolor="#FFFFFF",
            cdn_resources="remote", heading=graph.graph.get("instruction", "Task Flow Graph"),
        )
        net.set_options(json.dumps({
            "layout": {"hierarchical": {"enabled": True, "direction": "LR",
                                         "sortMethod": "directed", "levelSeparation": 220}},
            "physics": {"enabled": False},
            "edges": {"arrows": {"to": {"enabled": True}}, "smooth": True},
            "interaction": {"hover": True, "navigationButtons": True, "zoomView": True},
        }))
        for v, data in graph.nodes(data=True):
            tooltip = (
                f"id: {v}\naction: {data.get('action')}\n"
                f"description: {data.get('description')}\n"
                f"condition: {data.get('condition') or '-'}\n"
                f"metadata: {json.dumps(data.get('metadata', {}))}"
            )
            net.add_node(
                v, label=f"{v}\n{data.get('action', '')}", title=tooltip, shape="box",
                color=_ACTION_COLORS.get(data.get("action", ""), _DEFAULT_COLOR),
                font={"color": "white", "face": "monospace"},
            )
        for u, v, data in graph.edges(data=True):
            net.add_edge(
                u, v,
                color="#E45756" if data.get("conditional") else "#555555",
                dashes=bool(data.get("conditional")),
                label=data.get("condition") or "",
                title=f"type: {data.get('dependency_type')}",
            )
        net.write_html(str(path), open_browser=False, notebook=False)
        logger.info("HTML written to %s", path)
        return path

    def export_graphml(self, graph: nx.DiGraph, path: Path) -> Path:
        """GraphML export compatible with Gephi / Neo4j import tooling.

        GraphML supports only primitive attribute values, so ``metadata`` is
        serialized to a JSON string and ``None`` conditions become "".
        """
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
                conditional=bool(data.get("conditional", False)),
                condition=str(data.get("condition") or ""),
            )
        nx.write_graphml(export, path)
        logger.info("GraphML written to %s", path)
        return path


def _wrap(text: str, width: int) -> str:
    words, lines, cur = text.split(), [], ""
    for w in words:
        if len(cur) + len(w) + 1 > width:
            lines.append(cur)
            cur = w
        else:
            cur = f"{cur} {w}".strip()
    if cur:
        lines.append(cur)
    return "\n".join(lines)
