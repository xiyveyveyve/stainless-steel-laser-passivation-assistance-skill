#!/usr/bin/env python3
"""Exercise the actual v1.1 template and fail-closed lifecycle checks."""
import importlib.util
import tempfile
from pathlib import Path
import yaml

ROOT = Path(__file__).resolve().parents[1]


def main():
    spec = importlib.util.spec_from_file_location("analysis_validator", ROOT / "scripts/validate-analysis-record.py")
    validator = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(validator)
    template = yaml.safe_load((ROOT / "references/auditable-analysis-record.template.yaml").read_text(encoding="utf-8"))
    template["request"]["text"] = "SYNTHETIC lifecycle contract check, not scientific research"
    template["evidence"][0]["text"] = "SYNTHETIC placeholder, not real experimental evidence"
    with tempfile.TemporaryDirectory(prefix="state-contract-") as folder:
        path = Path(folder) / "record.yaml"
        path.write_text(yaml.safe_dump(template, allow_unicode=True), encoding="utf-8")
        errors = validator.validate(path, require_state=True)
        if errors:
            print("ERROR: v1.1 template failed: " + "; ".join(errors))
            return 1
        for forbidden in ("reviewed", "validated"):
            template["artifact_state"]["artifact_status"] = forbidden
            path.write_text(yaml.safe_dump(template, allow_unicode=True), encoding="utf-8")
            if not validator.validate(path, require_state=True):
                print(f"ERROR: unsupported {forbidden} promotion accepted")
                return 1
    legacy = ROOT / "evals/fixtures/valid-analysis-record.yaml"
    if validator.validate(legacy) or not validator.validate(legacy, require_state=True):
        print("ERROR: legacy compatibility boundary failed")
        return 1
    print("VALID: v1.1 template/state defaults, rejected promotion and explicit legacy boundary")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
