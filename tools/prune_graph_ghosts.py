"""Drop Graphify nodes whose source file no longer exists, then rewrite graph.json atomically.

`graphify update` re-extracts code and markdown but re-injects every node of the previous graph.json
that the new pass did not produce (graphify/watch.py, `_rebuild_code`), so the nodes of a deleted or
renamed file survive indefinitely. This tool evicts them before the rebuild: a node is a ghost when
its `source_file` is set and missing on disk. Nodes without `source_file` are kept, their links are
filtered to the surviving endpoints and the hyperedges referencing a dropped node are removed. The
file is rewritten only when something was removed, so a clean graph costs one read.
"""
import argparse
import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def is_ghost(source_file, root):
    """True when `source_file` is set and names no existing path, relative to root or absolute."""
    path = Path(source_file).expanduser()
    return not (path if path.is_absolute() else root / path).exists()


def prune(graph, root):
    """Remove ghost nodes, links without both endpoints and hyperedges citing a removed node."""
    nodes = graph.get("nodes", [])
    kept, dropped = [], set()
    for node in nodes:
        source_file = node.get("source_file")
        if source_file and is_ghost(source_file, root):
            dropped.add(node.get("id"))
        else:
            kept.append(node)
    counts = (0, 0, 0, len(nodes))
    if not dropped:
        return graph, counts
    kept_ids = {node.get("id") for node in kept}
    graph["nodes"] = kept
    links_key = "links" if "links" in graph else "edges"
    links = graph.get(links_key, [])
    kept_links = [link for link in links if link.get("source") in kept_ids and link.get("target") in kept_ids]
    if links_key in graph:
        graph[links_key] = kept_links
    hyperedges = graph.get("hyperedges", [])
    kept_hyperedges = [edge for edge in hyperedges if not dropped.intersection(edge.get("nodes", []))]
    if "hyperedges" in graph:
        graph["hyperedges"] = kept_hyperedges
    counts = (len(dropped), len(links) - len(kept_links), len(hyperedges) - len(kept_hyperedges), len(kept))
    return graph, counts


def main(argv=None):
    """Run the pruner; return 0 on success, 1 when the graph cannot be read."""
    parser = argparse.ArgumentParser(
        description="Drop Graphify nodes whose source_file no longer exists.",
    )
    parser.add_argument("--graph", default=None, help="defaults to <root>/graphify-out/graph.json")
    parser.add_argument("--root", default=str(ROOT), help="directory the relative source_file paths are resolved against")
    parser.add_argument("--dry-run", action="store_true", help="report the counts without writing")
    args = parser.parse_args(argv)
    root = Path(args.root)
    graph_path = Path(args.graph) if args.graph else root / "graphify-out" / "graph.json"
    try:
        graph = json.loads(graph_path.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        print(f"prune_graph_ghosts: cannot read {graph_path}: {exc}", file=sys.stderr)
        return 1
    pruned, (dropped, links, hyperedges, kept) = prune(graph, root)
    if not dropped:
        print("no ghost nodes")
        return 0
    if args.dry_run:
        print(f"would prune {dropped} nodes, {links} links, {hyperedges} hyperedges (kept {kept} nodes)")
        return 0
    tmp_path = graph_path.with_name(graph_path.name + ".tmp")
    tmp_path.write_text(json.dumps(pruned, indent=2), encoding="utf-8")
    os.replace(tmp_path, graph_path)
    print(f"pruned {dropped} nodes, {links} links, {hyperedges} hyperedges (kept {kept} nodes)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
