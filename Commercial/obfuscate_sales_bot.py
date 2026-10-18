# Copyright © 2026 Mythara Labs LLC. All rights reserved.

"""
PyArmor Obfuscation Script for Sales Bot IP Protection
======================================================

Packaging/dev tool: runs PyArmor over the sales bot sources so a
distributable bundle can be produced without shipping plain sources.

Honest framing:
- Obfuscation raises the bar against casual copying; it does NOT make
  code "unreadable", "unstealable", or immune to reverse engineering.
- PyArmor emits obfuscated bytecode + runtime, not plain .pyc files.
- Nothing here ships or invoices anything — it just builds the bundle.

Run:
    python3 obfuscate_sales_bot.py            # full run (needs PyArmor)
    python3 obfuscate_sales_bot.py --check    # preflight: report what would happen
"""

import argparse
import shutil
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).parent

FILES_TO_PROTECT = [
    "sales_bot_with_soul.py",
    "sales_bot_ssip_governance.py",
    "autonomous_sales_bot.py",
    "email_assistant.py",
]


def find_pyarmor() -> Path | None:
    """Locate the pyarmor executable, or None if not installed."""
    return shutil.which("pyarmor")


def preflight(base_dir: Path = HERE) -> dict:
    """
    Preflight check (no changes, no subprocess): report PyArmor availability
    and which source files are present. Testable without PyArmor installed.
    """
    pyarmor = find_pyarmor()
    files = {
        name: (base_dir / name).exists()
        for name in FILES_TO_PROTECT
    }
    return {
        "pyarmor_found": pyarmor is not None,
        "pyarmor_path": pyarmor,
        "files": files,
        "ready": pyarmor is not None and all(files.values()),
    }


def obfuscate_sales_bot(output_dir: Path | None = None,
                        base_dir: Path = HERE,
                        dry_run: bool = False) -> dict:
    """
    Run PyArmor over FILES_TO_PROTECT.

    Args:
        output_dir: where to write obfuscated output (default: <base>/dist)
        base_dir:   where the source files live (default: this file's dir)
        dry_run:   when True, only report what would be done (no subprocess)

    Returns a result dict with per-file outcomes:
        {"ok": bool, "files": {name: {"status": "ok|failed|skipped", ...}}, ...}
    """
    print("=" * 80)
    print("🔒 SALES BOT PACKAGING - PyArmor Obfuscation")
    print("=" * 80)

    output_dir = Path(output_dir) if output_dir else (base_dir / "dist")

    report = preflight(base_dir)

    print("\n📁 Source files:")
    for name, present in report["files"].items():
        print(f"   {'✅' if present else '❌'} {name}" + ("" if present else " (missing — will be skipped)"))

    if dry_run:
        # Dry-run is testable without PyArmor installed
        print(f"\n[dry-run] Would obfuscate present files into: {output_dir}")
        return {"ok": True, "dry_run": True, "files": {
            name: {"status": "would_run" if present else "skipped"}
            for name, present in report["files"].items()
        }}

    if not report["pyarmor_found"]:
        print("\n❌ PyArmor not installed or not in PATH.")
        print("   Install with: pip install pyarmor")
        print("   (PyArmor is a third-party tool; see https://pyarmor.dashingsoft.com/)")
        return {"ok": False, "reason": "pyarmor_missing", "files": {}}

    print(f"\n✅ PyArmor found: {report['pyarmor_path']}")

    print("\n🔒 Obfuscating...")
    outcomes: dict = {}
    any_failed = False

    for name, present in report["files"].items():
        if not present:
            print(f"   ⏭️  Skipping {name} (not found)")
            outcomes[name] = {"status": "skipped"}
            continue

        print(f"\n   🔐 Obfuscating {name}...")
        result = subprocess.run(
            ["pyarmor", "gen", "--output", str(output_dir), str(base_dir / name)],
            capture_output=True,
            text=True,
        )
        if result.returncode == 0:
            print(f"   ✅ {name} → {output_dir}/")
            outcomes[name] = {"status": "ok"}
        else:
            print(f"   ❌ Failed: {result.stderr.strip() or result.stdout.strip()}")
            outcomes[name] = {"status": "failed", "detail": result.stderr.strip()}
            any_failed = True

    ok = (not any_failed) and output_dir.exists()
    if ok:
        print("\n📦 Obfuscated bundle ready:")
        print(f"   Location: {output_dir.absolute()}")
        print("\n   ⚠️  Reminder: obfuscation raises the bar against casual")
        print("   copying — it does not make reverse engineering impossible.")
    else:
        print("\n❌ Obfuscation incomplete — see failures above.")

    return {"ok": ok, "output_dir": str(output_dir), "files": outcomes}


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(
        description="Obfuscate sales bot sources with PyArmor (packaging tool)."
    )
    parser.add_argument("--check", action="store_true",
                        help="Preflight only: report PyArmor + file availability.")
    parser.add_argument("--dry-run", action="store_true",
                        help="Report what would be done without running PyArmor.")
    parser.add_argument("--output", default=None,
                        help="Output directory (default: <script dir>/dist).")
    args = parser.parse_args(argv)

    if args.check:
        report = preflight()
        print("PyArmor:", "found" if report["pyarmor_found"] else "NOT FOUND")
        for name, present in report["files"].items():
            print(f"  {'✅' if present else '❌'} {name}")
        print("Ready:", "yes" if report["ready"] else "no")
        return 0 if report["ready"] else 1

    result = obfuscate_sales_bot(
        output_dir=Path(args.output) if args.output else None,
        dry_run=args.dry_run,
    )

    print("\n" + "=" * 80)
    if result["ok"]:
        print("✅ OBFUSCATION COMPLETE")
    else:
        print("❌ OBFUSCATION INCOMPLETE - see above")
    print("=" * 80)
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
