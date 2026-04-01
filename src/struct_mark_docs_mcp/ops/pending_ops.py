from pathlib import Path

from ..config import DocsConfig
from ..frontmatter_io import read_file
from ..validation import to_snake

_PRIORITY = {
    "broken_ref": 0,
    "broken_back_ref": 1,
    "inconsistent_back_ref": 2,
    "missing_abstract": 3,
    "overlimit_abstract": 4,
    "over_wc": 5,
}


def get_pending_actions(docs_dir: Path, config: DocsConfig) -> str:
    """Scan all .md files and emit a prioritised list of pending actions."""
    md_files = sorted(docs_dir.glob("*.md"), key=lambda f: f.name)
    key_to_name = {to_snake(f.stem): f.name for f in md_files}
    file_data = {f.name: read_file(docs_dir, f.name)[0] for f in md_files}

    actions: list[tuple[str, str]] = []

    for filename, fm in file_data.items():
        file_key = to_snake(Path(filename).stem)

        # File-level abstract
        lim0 = config.abstract_limit(0)
        if not fm.abstract.strip():
            actions.append(("missing_abstract", f"write abstract for {filename} (max {lim0} chars)"))
        elif len(fm.abstract) > lim0:
            actions.append(("overlimit_abstract", f"shorten abstract for {filename} ({len(fm.abstract)}/{lim0} chars)"))

        # TOC traversal
        for sec in fm.toc:
            lim1 = config.abstract_limit(1)
            p1 = sec.title
            if not sec.abstract.strip():
                actions.append(("missing_abstract", f"write abstract for '{p1}' in {filename} (max {lim1} chars)"))
            elif len(sec.abstract) > lim1:
                actions.append(("overlimit_abstract", f"shorten abstract for '{p1}' in {filename} ({len(sec.abstract)}/{lim1} chars)"))
            if sec.wc > config.section_wc_soft_limit:
                actions.append(("over_wc", f"section '{p1}' in {filename} is {sec.wc} words (limit {config.section_wc_soft_limit})"))

            for sub in sec.subsections:
                lim2 = config.abstract_limit(2)
                p2 = f"{sec.title}/{sub.title}"
                if not sub.abstract.strip():
                    actions.append(("missing_abstract", f"write abstract for '{p2}' in {filename} (max {lim2} chars)"))
                elif len(sub.abstract) > lim2:
                    actions.append(("overlimit_abstract", f"shorten abstract for '{p2}' in {filename} ({len(sub.abstract)}/{lim2} chars)"))
                if sub.wc > config.section_wc_soft_limit:
                    actions.append(("over_wc", f"subsection '{p2}' in {filename} is {sub.wc} words"))

                for subsub in sub.subsubsections:
                    lim3 = config.abstract_limit(3)
                    p3 = f"{sec.title}/{sub.title}/{subsub.title}"
                    if not subsub.abstract.strip():
                        actions.append(("missing_abstract", f"write abstract for '{p3}' in {filename} (max {lim3} chars)"))
                    elif len(subsub.abstract) > lim3:
                        actions.append(("overlimit_abstract", f"shorten abstract for '{p3}' in {filename} ({len(subsub.abstract)}/{lim3} chars)"))
                    if subsub.wc > config.section_wc_soft_limit:
                        actions.append(("over_wc", f"subsubsection '{p3}' in {filename} is {subsub.wc} words"))

        # Broken refs
        for ref_key in fm.refs:
            if ref_key not in key_to_name:
                actions.append(("broken_ref", f"broken ref '{ref_key}' in {filename} — no such file"))

        # Stale/inconsistent back_refs
        for back_key in fm.back_refs:
            if back_key not in key_to_name:
                actions.append(("broken_back_ref", f"stale back_ref '{back_key}' in {filename} — no such file"))
            else:
                src_fm = file_data[key_to_name[back_key]]
                if file_key not in src_fm.refs:
                    actions.append(("inconsistent_back_ref",
                        f"back_ref '{back_key}' in {filename} but {key_to_name[back_key]} "
                        f"doesn't list it in refs — run sync_header on {key_to_name[back_key]}"))

    if not actions:
        return "No pending actions. All files are consistent."

    actions.sort(key=lambda a: _PRIORITY[a[0]])
    lines = ["PENDING ACTIONS:"] + [f"  - {desc}" for _, desc in actions]
    return "\n".join(lines)
