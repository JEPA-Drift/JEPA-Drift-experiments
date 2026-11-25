"""Tests of tools/prune_graph_ghosts.py on synthetic temporary graphs only, never on the project."""
import hashlib
import json
import subprocess
import sys
from pathlib import Path

TOOL = Path(__file__).resolve().parents[1] / "tools" / "prune_graph_ghosts.py"


def node(node_id, source_file=None):
    """Synthetic node carrying an optional source_file."""
    entry = {"id": node_id, "label": node_id, "file_type": "code"}
    if source_file is not None:
        entry["source_file"] = source_file
    return entry


def write_graph(root, nodes, links=(), hyperedges=()):
    """Write graphify-out/graph.json under root and return its path."""
    out = root / "graphify-out"
    out.mkdir(parents=True, exist_ok=True)
    path = out / "graph.json"
    path.write_text(
        json.dumps({"nodes": list(nodes), "links": list(links), "hyperedges": list(hyperedges)}),
        encoding="utf-8",
    )
    return path


def run(root, *extra):
    """Run the pruner against root and return the completed process."""
    return subprocess.run(
        [sys.executable, str(TOOL), "--root", str(root), *extra],
        capture_output=True,
        text=True,
    )


def test_prunes_missing_sources_only(tmp_path):
    """Ghost nodes, their links and their hyperedges go; existing and source-less nodes stay."""
    (tmp_path / "keep.py").write_text("x = 1\n", encoding="utf-8")
    path = write_graph(
        tmp_path,
        [node("keep", "keep.py"), node("ghost", "gone/x.py"), node("free")],
        [{"source": "keep", "target": "free"}, {"source": "keep", "target": "ghost"}],
        [{"nodes": ["keep", "ghost"]}, {"nodes": ["keep"]}],
    )
    result = run(tmp_path)
    assert result.returncode == 0, result.stderr
    assert "pruned 1 nodes, 1 links, 1 hyperedges (kept 2 nodes)" in result.stdout
    graph = json.loads(path.read_text(encoding="utf-8"))
    assert [entry["id"] for entry in graph["nodes"]] == ["keep", "free"]
    assert graph["links"] == [{"source": "keep", "target": "free"}]
    assert graph["hyperedges"] == [{"nodes": ["keep"]}]


def test_absolute_source_file_is_tested_as_is(tmp_path):
    """An existing absolute source_file keeps its node, a missing one is pruned."""
    present = tmp_path / "abs.py"
    present.write_text("x = 1\n", encoding="utf-8")
    path = write_graph(tmp_path, [node("abs", str(present)), node("ghost", str(tmp_path / "nope.py"))])
    result = run(tmp_path)
    assert result.returncode == 0, result.stderr
    assert [entry["id"] for entry in json.loads(path.read_text(encoding="utf-8"))["nodes"]] == ["abs"]


def test_dry_run_leaves_the_file_unchanged(tmp_path):
    """--dry-run reports the counts and leaves graph.json byte-identical."""
    (tmp_path / "keep.py").write_text("x = 1\n", encoding="utf-8")
    path = write_graph(tmp_path, [node("keep", "keep.py"), node("ghost", "gone.py")])
    before = hashlib.sha256(path.read_bytes()).hexdigest()
    result = run(tmp_path, "--dry-run")
    assert result.returncode == 0, result.stderr
    assert "would prune 1 nodes, 0 links, 0 hyperedges (kept 1 nodes)" in result.stdout
    assert hashlib.sha256(path.read_bytes()).hexdigest() == before


def test_second_run_is_a_no_op(tmp_path):
    """A pruned graph reports no ghost nodes on the next run."""
    (tmp_path / "keep.py").write_text("x = 1\n", encoding="utf-8")
    write_graph(tmp_path, [node("keep", "keep.py"), node("ghost", "gone.py")])
    assert run(tmp_path).returncode == 0
    result = run(tmp_path)
    assert result.returncode == 0, result.stderr
    assert result.stdout.strip() == "no ghost nodes"


def test_missing_graph_exits_one(tmp_path):
    """An absent graph.json is reported on stderr and exits 1."""
    result = run(tmp_path)
    assert result.returncode == 1
    assert "cannot read" in result.stderr
