"""
Show morphological siblings for a given word via suffix erosion.

Output is written to a file. Default location is /tmp/gngrams-lookup/erosion_<word>.txt.

Usage:
    poetry run python scripts/erosion.py <word> [--sort freq|alpha] [--with-freq] [--min-tf N] [--output PATH]

Examples:
    poetry run python scripts/erosion.py homogenous
    poetry run python scripts/erosion.py generate --sort freq
    poetry run python scripts/erosion.py generate --sort freq --with-freq
    poetry run python scripts/erosion.py generate --sort freq --with-freq --min-tf 100000
    poetry run python scripts/erosion.py generate --output /tmp/gngrams-lookup/my-output.txt
"""

import argparse
import sys
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from gngram_lookup import erosion_cluster, frequency


def _lcp_len(a: str, b: str) -> int:
    """Length of the longest common prefix between a and b."""
    for i, (x, y) in enumerate(zip(a, b)):
        if x != y:
            return i
    return min(len(a), len(b))


def _build_tree_lines(
    input_word: str,
    results: list[tuple[str, int]],
    with_freq: bool,
    anchor_tf: int | None = None,
    color: bool = False,
) -> list[str]:
    """Render results as an indented prefix tree with vertically aligned numbers.

    Groups words by the length of their longest common prefix with input_word.
    Within each group, words that are prefixes of other words in the group are
    rendered as parents. Prefix groups nest inside each other by the same logic.
    Numbers are aligned to a single global column regardless of indent depth.

    If anchor_tf is provided, the input word itself is shown as the first line
    (with its frequency), aligned to the same column as all other entries.
    """
    INDENT = 4

    # Tag each word with its lcp depth relative to input_word
    tagged = [(w, tf, _lcp_len(w, input_word)) for w, tf in results]

    by_depth: dict[int, list[tuple[str, int]]] = defaultdict(list)
    for w, tf, d in tagged:
        by_depth[d].append((w, tf))

    depths = sorted(by_depth.keys())

    def parent_depth(d: int) -> int | None:
        smaller = [x for x in depths if x < d]
        return max(smaller) if smaller else None

    depth_level: dict[int, int] = {}
    for d in depths:
        pd = parent_depth(d)
        depth_level[d] = (depth_level[pd] + 1) if pd is not None else 0

    # First pass: collect (indent_level, text, tf_or_none) entries.
    # Anchor word always goes first at level 0; frequency shown only when with_freq=True.
    entries: list[tuple[int, str, int | None]] = []
    tf_to_show = anchor_tf if (with_freq and anchor_tf is not None) else None
    entries.append((0, input_word, tf_to_show))
    entries.append((-1, "", None))  # blank separator

    def collect_group(d: int) -> None:
        level = depth_level[d]
        if d < len(input_word):
            entries.append((level, input_word[:d] + "-", None))

        group_words = by_depth[d]
        tf_map = {w: tf for w, tf in group_words}
        all_w = list(tf_map)

        def word_parent(w: str) -> str | None:
            # Only nest under a parent that is at least as frequent — avoids
            # rare forms (e.g. Latin "disciplina") parenting common words.
            matches = [c for c in all_w if c != w and w.startswith(c) and tf_map[c] >= tf_map[w]]
            return max(matches, key=len) if matches else None

        roots: list[tuple[str, int]] = []
        children_map: dict[str, list[tuple[str, int]]] = defaultdict(list)
        for w, tf in group_words:
            p = word_parent(w)
            if p is None:
                roots.append((w, tf))
            else:
                children_map[p].append((w, tf))

        word_level = level + 1
        for w, tf in roots:
            entries.append((word_level, w, tf))
            for cw, ctf in children_map.get(w, []):
                entries.append((word_level + 1, cw, ctf))

        for cd in [x for x in depths if parent_depth(x) == d]:
            collect_group(cd)

    for d in [d for d in depths if parent_depth(d) is None]:
        collect_group(d)

    # Color codes — applied only to terminal output; widths always computed on raw text.
    RESET = "\033[0m"    if color else ""
    LABEL = "\033[1m"    if color else ""   # bold          — group headers (simpl-, simplifi-)
    WORD  = "\033[36m"   if color else ""   # cyan           — word entries
    VAL   = "\033[1;33m" if color else ""   # bold yellow    — frequencies

    def _color_text(text: str) -> str:
        c = LABEL if text.endswith("-") else WORD
        return f"{c}{text}{RESET}"

    if not with_freq:
        return [
            "" if level < 0 else " " * (level * INDENT) + _color_text(text)
            for level, text, _ in entries
        ]

    # Second pass: compute a single global column so all numbers align.
    # Use raw text lengths (no escape codes) so alignment is unaffected by color.
    col = max(level * INDENT + len(text) for level, text, _ in entries if level >= 0) + 2

    lines = []
    for level, text, tf in entries:
        if level < 0:
            lines.append("")
            continue
        indent = " " * (level * INDENT)
        pos = level * INDENT + len(text)   # raw length for padding
        colored = _color_text(text)
        if tf is None:
            lines.append(indent + colored)
        else:
            lines.append(f"{indent}{colored}{' ' * (col - pos)}{VAL}{tf:>12,}{RESET}")
    return lines


def main() -> None:
    parser = argparse.ArgumentParser(description="Show morphological siblings for a word via suffix erosion.")
    parser.add_argument("word", help="Word to find siblings for")
    parser.add_argument(
        "--sort",
        choices=["alpha", "freq"],
        default="alpha",
        help="Sort order: alphabetical (default) or by corpus frequency",
    )
    parser.add_argument(
        "--with-freq",
        action="store_true",
        help="Show corpus frequency alongside each word",
    )
    parser.add_argument(
        "--min-tf",
        type=int,
        default=0,
        metavar="N",
        help="Minimum corpus frequency to include a word (default: 0 = all)",
    )
    parser.add_argument(
        "--output",
        metavar="PATH",
        help="Output file or directory (default: /tmp/gngrams-lookup/erosion_<word>.txt)",
    )
    args = parser.parse_args()

    TMP_DIR = Path("/tmp/gngrams-lookup")

    # Always fetch with_freq=True internally so tree builder has freq data
    results = erosion_cluster(args.word, sort_by=args.sort, with_freq=True, min_tf=args.min_tf)

    # Resolve output path
    filename = f"erosion_{args.word.lower()}.txt"
    if args.output:
        out = Path(args.output)
        if out.is_dir() or str(args.output).endswith("/"):
            out.mkdir(parents=True, exist_ok=True)
            out = out / filename
    else:
        TMP_DIR.mkdir(parents=True, exist_ok=True)
        out = TMP_DIR / filename

    if not results:
        out.write_text(f"No siblings found for {args.word!r}\n")
        print(f"No siblings found for {args.word!r}")
        print(f"Written to {out}")
        return

    freq = frequency(args.word)
    anchor_tf = freq["sum_tf"] if freq else 0

    color = sys.stdout.isatty()
    lines = _build_tree_lines(args.word, results, with_freq=args.with_freq, anchor_tf=anchor_tf, color=color)
    plain = _build_tree_lines(args.word, results, with_freq=args.with_freq, anchor_tf=anchor_tf, color=False) if color else lines

    out.write_text("\n".join(plain) + "\n")
    print("\n".join(lines))
    print(f"\n{len(results)} results written to {out}")


if __name__ == "__main__":
    main()
