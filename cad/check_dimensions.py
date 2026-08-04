"""Print V2 STL bounds; exits non-zero when a part exceeds the A1 limits."""
from pathlib import Path
import re, sys

root = Path(__file__).resolve().parent / "stl_v2"
failed = False
for path in sorted(root.glob("*.stl")):
    vertices = []
    for line in path.read_text(encoding="ascii", errors="ignore").splitlines():
        m = re.match(r"\s*vertex\s+([-0-9.]+)\s+([-0-9.]+)\s+([-0-9.]+)", line)
        if m: vertices.append(tuple(float(x) for x in m.groups()))
    if not vertices:
        continue
    size = tuple(round(max(v[i] for v in vertices) - min(v[i] for v in vertices), 2) for i in range(3))
    print(f"{path.name}: {size[0]} x {size[1]} x {size[2]} mm")
    failed |= any(x > 256 for x in size)
if failed:
    sys.exit("A1 limit exceeded")
