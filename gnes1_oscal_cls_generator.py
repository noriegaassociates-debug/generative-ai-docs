"""
GNES-1 Sensor Cortex OSCAL + CLS Ledger Generator
Posture: ALL_SIM_NO_CLAIM
Artifact: GNES1-SC-MICROCERAMIC-SENSOR-CORTEX-V1.0
"""
import hashlib
import json
import os
import uuid
from datetime import datetime, timezone

POSTURE = "ALL_SIM_NO_CLAIM"
ARTIFACT_ID = "GNES1-SC-MICROCERAMIC-SENSOR-CORTEX-V1.0"
OUTPUT_DIR = "./gnes1_oscal_cls_bundle"
OSCAL_VERSION = "1.1.2"


def canonical_json(obj):
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("utf-8")


def sha3_384(obj):
    return hashlib.sha3_384(canonical_json(obj)).hexdigest()


def utc_now():
    return datetime.now(timezone.utc).isoformat()


def make_cls_block(event_type, payload, prev_hash=None):
    payload_hash = sha3_384(payload)
    block = {
        "block_id": str(uuid.uuid4()),
        "timestamp_utc": utc_now(),
        "posture": POSTURE,
        "event_type": event_type,
        "prev_hash": prev_hash or "GENESIS",
        "payload_hash_sha3_384": payload_hash,
        "payload_summary": f"{event_type} generated for {ARTIFACT_ID}",
        "payload": payload,
        "attestation_class": "AC-I_SIMULATED",
        "signature_status": "HiC_or_device_attestation_pending"
    }
    block["block_hash_sha3_384"] = sha3_384(block)
    return block


# Sensor Registry — canonical IDs; SC-02/04/06/07/13/15 split A/B to resolve prior duplicates
_SENSORS = [
    # P0 — safety-critical, fail-closed gate trigger
    {"id": "SC-01",  "name": "Core Temperature Alpha",        "tier": "P0", "gate": "GATE_THERMAL_TRUTH",        "unit": "K"},
    {"id": "SC-02A", "name": "Core Temperature Beta-A",       "tier": "P0", "gate": "GATE_THERMAL_TRUTH",        "unit": "K"},
    {"id": "SC-02B", "name": "Core Temperature Beta-B",       "tier": "P0", "gate": "GATE_THERMAL_TRUTH",        "unit": "K"},
    {"id": "SC-03",  "name": "Chamber Pressure Primary",      "tier": "P0", "gate": "GATE_PRESSURE_BOUNDARY",    "unit": "Pa"},
    {"id": "SC-04A", "name": "Chamber Pressure Secondary-A",  "tier": "P0", "gate": "GATE_PRESSURE_BOUNDARY",    "unit": "Pa"},
    {"id": "SC-04B", "name": "Chamber Pressure Secondary-B",  "tier": "P0", "gate": "GATE_PRESSURE_BOUNDARY",    "unit": "Pa"},
    {"id": "SC-05",  "name": "Salt Inventory Sensor Alpha",   "tier": "P0", "gate": "GATE_SALT_INVENTORY",       "unit": "ppm"},
    {"id": "SC-06A", "name": "Salt Inventory Sensor Beta-A",  "tier": "P0", "gate": "GATE_SALT_INVENTORY",       "unit": "ppm"},
    {"id": "SC-06B", "name": "Salt Inventory Sensor Beta-B",  "tier": "P0", "gate": "GATE_SALT_INVENTORY",       "unit": "ppm"},
    # P1 — process-critical, SDS-validated
    {"id": "SC-07A", "name": "Radiation Monitor Alpha-A",     "tier": "P1", "gate": "GATE_RAD_NUCLEAR",          "unit": "Sv/h"},
    {"id": "SC-07B", "name": "Radiation Monitor Alpha-B",     "tier": "P1", "gate": "GATE_RAD_NUCLEAR",          "unit": "Sv/h"},
    {"id": "SC-08",  "name": "Chemical Purity Sensor",        "tier": "P1", "gate": "GATE_CHEM_PURITY",          "unit": "ppb"},
    {"id": "SC-09",  "name": "Autonomy Environment Monitor",  "tier": "P1", "gate": "GATE_AUTONOMY_ENV",         "unit": "index"},
    {"id": "SC-10",  "name": "Structural Load Cell Alpha",    "tier": "P1", "gate": "GATE_STRUCTURAL_INTEGRITY", "unit": "MPa"},
    # P2 — mission-support, advisory
    {"id": "SC-11",  "name": "Ambient Humidity Advisory",     "tier": "P2", "gate": "GATE_AUTONOMY_ENV",         "unit": "%RH"},
    {"id": "SC-12",  "name": "Vibration Monitor",             "tier": "P2", "gate": "GATE_STRUCTURAL_INTEGRITY", "unit": "g"},
    {"id": "SC-13A", "name": "Flow Rate Sensor Alpha-A",      "tier": "P2", "gate": "GATE_CHEM_PURITY",          "unit": "L/min"},
    {"id": "SC-13B", "name": "Flow Rate Sensor Alpha-B",      "tier": "P2", "gate": "GATE_CHEM_PURITY",          "unit": "L/min"},
    {"id": "SC-14",  "name": "EMI Field Monitor",             "tier": "P2", "gate": "GATE_AUTONOMY_ENV",         "unit": "dBm"},
    {"id": "SC-15A", "name": "Acoustic Emission Sensor-A",    "tier": "P2", "gate": "GATE_STRUCTURAL_INTEGRITY", "unit": "dB"},
    {"id": "SC-15B", "name": "Acoustic Emission Sensor-B",    "tier": "P2", "gate": "GATE_STRUCTURAL_INTEGRITY", "unit": "dB"},
]

SENSOR_REGISTRY = {
    "artifact_id": ARTIFACT_ID,
    "posture": POSTURE,
    "sensors": _SENSORS,
    "registry_hash_sha3_384": sha3_384(_SENSORS),
}

# Gate Map
_GATES = {
    "GATE_THERMAL_TRUTH":        ["SC-01", "SC-02A", "SC-02B"],
    "GATE_PRESSURE_BOUNDARY":    ["SC-03", "SC-04A", "SC-04B"],
    "GATE_SALT_INVENTORY":       ["SC-05", "SC-06A", "SC-06B"],
    "GATE_RAD_NUCLEAR":          ["SC-07A", "SC-07B"],
    "GATE_CHEM_PURITY":          ["SC-08", "SC-13A", "SC-13B"],
    "GATE_AUTONOMY_ENV":         ["SC-09", "SC-11", "SC-14"],
    "GATE_STRUCTURAL_INTEGRITY": ["SC-10", "SC-12", "SC-15A", "SC-15B"],
}

GATE_MAP = {
    "artifact_id": ARTIFACT_ID,
    "posture": POSTURE,
    "gates": _GATES,
    "hic_policy": "ALL_ACTUATION_REQUIRES_HUMAN_APPROVAL",
    "fail_mode": "FAIL_CLOSED",
    "gate_map_hash_sha3_384": sha3_384(_GATES),
}

# OSCAL Component Definition (NIST SP 800-53 Rev 5)
OSCAL_COMPONENT_DEF = {
    "component-definition": {
        "uuid": str(uuid.uuid4()),
        "metadata": {
            "title": "GNES-1 Microceramic Sensor Cortex Component Definition",
            "last-modified": utc_now(),
            "version": "1.0.0",
            "oscal-version": OSCAL_VERSION,
            "posture": POSTURE,
        },
        "components": [
            {
                "uuid": str(uuid.uuid4()),
                "type": "hardware",
                "title": ARTIFACT_ID,
                "description": (
                    "GNES-1 Sensor Cortex: Microceramic sensor array with SHA3-384 integrity chain, "
                    "tiered authority (P0/P1/P2), and Human-in-Command actuation policy. "
                    "ALL_SIM_NO_CLAIM."
                ),
                "control-implementations": [
                    {
                        "uuid": str(uuid.uuid4()),
                        "source": "https://csrc.nist.gov/publications/detail/sp/800-53/rev-5/final",
                        "description": "NIST SP 800-53 Rev 5 control implementations for GNES-1 Sensor Cortex",
                        "implemented-requirements": [
                            {
                                "uuid": str(uuid.uuid4()),
                                "control-id": "AU-3",
                                "description": (
                                    "Event Content: CLS ledger blocks contain block_id, timestamp_utc, "
                                    "posture, event_type, prev_hash, payload_hash_sha3_384, "
                                    "attestation_class, and signature_status."
                                ),
                            },
                            {
                                "uuid": str(uuid.uuid4()),
                                "control-id": "AU-8",
                                "description": (
                                    "Time Stamps: All CLS blocks include UTC ISO-8601 timestamps via "
                                    "utc_now(); temporal ordering enforced by chained prev_hash."
                                ),
                            },
                            {
                                "uuid": str(uuid.uuid4()),
                                "control-id": "SI-7",
                                "description": (
                                    "Software, Firmware, and Information Integrity: SHA3-384 hash chain "
                                    "ensures tamper-evidence across registry, gate map, OSCAL documents, "
                                    "and all CLS ledger blocks."
                                ),
                            },
                            {
                                "uuid": str(uuid.uuid4()),
                                "control-id": "SC-12",
                                "description": (
                                    "Cryptographic Key Establishment and Management: SHA3-384 (FIPS 202) "
                                    "used for all integrity verification; no symmetric keys; "
                                    "HiC_or_device_attestation_pending for all signature fields."
                                ),
                            },
                            {
                                "uuid": str(uuid.uuid4()),
                                "control-id": "CM-6",
                                "description": (
                                    "Configuration Settings: Sensor registry and gate map are locked at "
                                    "generation time with SHA3-384 registry_hash and gate_map_hash; "
                                    "changes require a new ledger entry."
                                ),
                            },
                        ],
                    }
                ],
            }
        ],
    }
}

# OSCAL SSP Stub
OSCAL_SSP_STUB = {
    "system-security-plan": {
        "uuid": str(uuid.uuid4()),
        "metadata": {
            "title": "GNES-1 Sensor Cortex System Security Plan (Stub)",
            "last-modified": utc_now(),
            "version": "0.1.0-stub",
            "oscal-version": OSCAL_VERSION,
            "posture": POSTURE,
            "status": "DRAFT_SIM_ONLY",
        },
        "system-characteristics": {
            "system-name": "GNES-1 AKT 55KS Sensor Cortex",
            "description": "Simulated PECVD chamber sensor cortex for GNES-1 mission. ALL_SIM_NO_CLAIM.",
            "security-impact-level": {
                "security-objective-confidentiality": "moderate",
                "security-objective-integrity": "high",
                "security-objective-availability": "high",
            },
            "authorization-boundary": {
                "description": (
                    "Simulated boundary encompassing sensor array, CLS ledger, "
                    "and OSCAL documentation bundle."
                )
            },
        },
        "control-implementation": {
            "description": "Control implementations are stubs referencing the Component Definition.",
            "implemented-requirements": [
                {
                    "control-id": ctrl,
                    "status": "planned",
                    "attestation_class": "AC-I_SIMULATED",
                }
                for ctrl in ["AU-3", "AU-8", "SI-7", "SC-12", "CM-6"]
            ],
        },
    }
}


def generate_bundle():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    written = {}

    def write_json(name, obj):
        path = os.path.join(OUTPUT_DIR, name)
        with open(path, "w", encoding="utf-8") as fh:
            json.dump(obj, fh, indent=2)
        written[name] = path

    write_json("GNES1_sensor_registry.json", SENSOR_REGISTRY)
    write_json("GNES1_gate_map.json", GATE_MAP)
    write_json("GNES1_OSCAL_component_definition.json", OSCAL_COMPONENT_DEF)
    write_json("GNES1_OSCAL_ssp_stub.json", OSCAL_SSP_STUB)

    # CLS Ledger — block 0: genesis, block 1: OSCAL emit
    genesis_payload = {
        "artifact_id": ARTIFACT_ID,
        "registry_hash": SENSOR_REGISTRY["registry_hash_sha3_384"],
        "gate_map_hash": GATE_MAP["gate_map_hash_sha3_384"],
        "posture": POSTURE,
        "event": "GENESIS_REGISTRY_LOCK",
    }
    b0 = make_cls_block("GENESIS_REGISTRY_LOCK", genesis_payload)

    oscal_payload = {
        "artifact_id": ARTIFACT_ID,
        "oscal_component_hash": sha3_384(OSCAL_COMPONENT_DEF),
        "oscal_ssp_hash": sha3_384(OSCAL_SSP_STUB),
        "controls": ["AU-3", "AU-8", "SI-7", "SC-12", "CM-6"],
        "posture": POSTURE,
        "event": "OSCAL_DOCUMENT_EMIT",
    }
    b1 = make_cls_block("OSCAL_DOCUMENT_EMIT", oscal_payload, prev_hash=b0["block_hash_sha3_384"])

    ledger = {
        "artifact_id": ARTIFACT_ID,
        "posture": POSTURE,
        "chain": [b0, b1],
        "chain_length": 2,
    }
    write_json("GNES1_CLS_ledger_chain.json", ledger)

    # Manifest — per-file raw-bytes SHA3-384 + manifest self-hash
    manifest = {
        "artifact_id": ARTIFACT_ID,
        "posture": POSTURE,
        "generated_utc": utc_now(),
        "files": {},
    }
    for fname, fpath in written.items():
        with open(fpath, "rb") as fh:
            manifest["files"][fname] = {
                "path": fpath,
                "sha3_384": hashlib.sha3_384(fh.read()).hexdigest(),
            }
    manifest["manifest_self_hash_sha3_384"] = sha3_384(manifest)

    manifest_path = os.path.join(OUTPUT_DIR, "MANIFEST.json")
    with open(manifest_path, "w", encoding="utf-8") as fh:
        json.dump(manifest, fh, indent=2)

    print(f"[GNES-1 OSCAL+CLS] Bundle written to {OUTPUT_DIR}/")
    print(f"  Posture        : {POSTURE}")
    print(f"  Sensors        : {len(_SENSORS)}")
    print(f"  Gates          : {len(_GATES)}")
    print(f"  Registry hash  : {SENSOR_REGISTRY['registry_hash_sha3_384'][:40]}...")
    print(f"  Gate map hash  : {GATE_MAP['gate_map_hash_sha3_384'][:40]}...")
    print(f"  Genesis block  : {b0['block_hash_sha3_384'][:40]}...")
    print(f"  OSCAL block    : {b1['block_hash_sha3_384'][:40]}...")
    print(f"  Manifest hash  : {manifest['manifest_self_hash_sha3_384'][:40]}...")
    print(f"  Files written  : {len(written) + 1}")


if __name__ == "__main__":
    generate_bundle()
