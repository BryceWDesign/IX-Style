"""JSON export/import tooling and review-ready artifact packages for IX-Style."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from ix_style.core.ids import IdFactory
from ix_style.messages import EvidenceBundleBuilder
from ix_style.telemetry import MissionHealthBuilder, SafetySummaryNarrator

from .models import VerificationResult


def _utc_now() -> datetime:
    """Return an aware UTC timestamp."""
    return datetime.now(tz=UTC)


def _serialize(value: Any) -> Any:
    """Convert dataclasses, enums, datetimes, and tuples into JSON-friendly primitives."""
    if hasattr(value, "value"):
        return value.value
    if isinstance(value, datetime):
        return value.isoformat()
    if isinstance(value, tuple):
        return [_serialize(item) for item in value]
    if isinstance(value, list):
        return [_serialize(item) for item in value]
    if isinstance(value, dict):
        return {str(key): _serialize(item) for key, item in value.items()}
    return value


@dataclass(slots=True, frozen=True)
class ReviewArtifactPackage:
    """In-memory representation of one exported review package."""

    manifest: dict[str, Any]
    verification_result: dict[str, Any]
    evidence_package: dict[str, Any]
    decision_receipt: dict[str, Any]
    mission_health_snapshot: dict[str, Any]
    operator_safety_summary: dict[str, Any]
    evidence_bundle: dict[str, Any]

    def as_dict(self) -> dict[str, Any]:
        """Return a combined JSON-friendly package dictionary."""
        return {
            "manifest": self.manifest,
            "verification_result": self.verification_result,
            "evidence_package": self.evidence_package,
            "decision_receipt": self.decision_receipt,
            "mission_health_snapshot": self.mission_health_snapshot,
            "operator_safety_summary": self.operator_safety_summary,
            "evidence_bundle": self.evidence_bundle,
        }


@dataclass(slots=True)
class ReviewArtifactBuilder:
    """Builds review-ready artifact packages from verification results."""

    id_factory: IdFactory = field(default_factory=IdFactory)
    snapshot_builder: MissionHealthBuilder = field(default_factory=MissionHealthBuilder)
    narrator: SafetySummaryNarrator = field(default_factory=SafetySummaryNarrator)
    bundle_builder: EvidenceBundleBuilder = field(default_factory=EvidenceBundleBuilder)
    schema_version: str = "0.1.0"

    def build(self, result: VerificationResult) -> ReviewArtifactPackage:
        """Build an in-memory review package from one verification result."""
        snapshot = self.snapshot_builder.build_from_verification(result)
        operator_summary = self.narrator.summarize(
            snapshot=snapshot,
            decision_receipt=result.evidence_package.decision_receipt,
        ).as_dict()

        evidence_bundle = result.evidence_package.evidence_bundle or self.bundle_builder.build(
            scenario_id=result.scenario.scenario_id,
            decision_receipt=result.evidence_package.decision_receipt,
            trust_transitions=result.evidence_package.trust_transitions,
            fault_transitions=result.evidence_package.fault_transitions,
            mode_transitions=result.evidence_package.mode_transitions,
        )

        verification_result_dict = {
            "scenario_id": result.scenario.scenario_id,
            "scenario_name": result.scenario.name,
            "passed": result.passed,
            "failures": list(result.failures),
            "derived_active_degradation_flags": list(result.derived_active_degradation_flags),
            "derived_dominant_safety_posture": result.derived_dominant_safety_posture.value,
        }

        manifest = {
            "package_id": self.id_factory.receipt_id(),
            "schema_version": self.schema_version,
            "exported_at": _utc_now().isoformat(),
            "scenario_id": result.scenario.scenario_id,
            "scenario_name": result.scenario.name,
            "passed": result.passed,
            "final_outcome": result.evidence_package.decision_receipt["final_outcome"],
            "dominant_safety_posture": snapshot["dominant_safety_posture"],
            "files": {
                "verification_result": "verification_result.json",
                "evidence_package": "evidence_package.json",
                "decision_receipt": "decision_receipt.json",
                "mission_health_snapshot": "mission_health_snapshot.json",
                "operator_safety_summary": "operator_safety_summary.json",
                "evidence_bundle": "evidence_bundle.json",
            },
        }

        return ReviewArtifactPackage(
            manifest=manifest,
            verification_result=verification_result_dict,
            evidence_package=_serialize(asdict(result.evidence_package)),
            decision_receipt=_serialize(result.evidence_package.decision_receipt),
            mission_health_snapshot=_serialize(snapshot),
            operator_safety_summary=_serialize(operator_summary),
            evidence_bundle=_serialize(evidence_bundle),
        )


@dataclass(slots=True)
class JsonArtifactIO:
    """Exports and imports review-ready IX-Style artifact packages."""

    def export_package(
        self,
        package: ReviewArtifactPackage,
        output_dir: str | Path,
    ) -> Path:
        """Write a review package to a directory and return the directory path."""
        directory = Path(output_dir)
        directory.mkdir(parents=True, exist_ok=True)

        self._write_json(directory / "manifest.json", package.manifest)
        self._write_json(directory / "verification_result.json", package.verification_result)
        self._write_json(directory / "evidence_package.json", package.evidence_package)
        self._write_json(directory / "decision_receipt.json", package.decision_receipt)
        self._write_json(
            directory / "mission_health_snapshot.json",
            package.mission_health_snapshot,
        )
        self._write_json(
            directory / "operator_safety_summary.json",
            package.operator_safety_summary,
        )
        self._write_json(directory / "evidence_bundle.json", package.evidence_bundle)

        return directory

    def import_package(self, input_dir: str | Path) -> ReviewArtifactPackage:
        """Load a review package from a directory."""
        directory = Path(input_dir)
        required = (
            "manifest.json",
            "verification_result.json",
            "evidence_package.json",
            "decision_receipt.json",
            "mission_health_snapshot.json",
            "operator_safety_summary.json",
            "evidence_bundle.json",
        )
        missing = [name for name in required if not (directory / name).is_file()]
        if missing:
            joined = ", ".join(missing)
            raise FileNotFoundError(f"missing required review package files: {joined}")

        return ReviewArtifactPackage(
            manifest=self._read_json(directory / "manifest.json"),
            verification_result=self._read_json(directory / "verification_result.json"),
            evidence_package=self._read_json(directory / "evidence_package.json"),
            decision_receipt=self._read_json(directory / "decision_receipt.json"),
            mission_health_snapshot=self._read_json(
                directory / "mission_health_snapshot.json"
            ),
            operator_safety_summary=self._read_json(
                directory / "operator_safety_summary.json"
            ),
            evidence_bundle=self._read_json(directory / "evidence_bundle.json"),
        )

    @staticmethod
    def _write_json(path: Path, data: dict[str, Any]) -> None:
        with path.open("w", encoding="utf-8") as handle:
            json.dump(data, handle, indent=2, sort_keys=True)

    @staticmethod
    def _read_json(path: Path) -> dict[str, Any]:
        with path.open("r", encoding="utf-8") as handle:
            loaded = json.load(handle)
        if not isinstance(loaded, dict):
            raise TypeError(f"expected JSON object in {path}")
        return loaded
