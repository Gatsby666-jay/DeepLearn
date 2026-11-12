#!/usr/bin/env python3
"""DeepLearn V3 canonical enums, ID rules and structural validators.

V2 definitions stay in deeplearn_rules.py unchanged; this module is the
executable single source of truth for V3-only structures.
"""
from __future__ import annotations

import re

from deeplearn_rules import ENUMS as V2_ENUMS, emit, err, is_int, load_json

SCHEMA_VERSION = 3
ID_PATTERNS = {
    "node": r"NODE-\d{3,}", "competency": r"COMP-\d{3,}",
    "profile": r"PROFILE-\d{3,}", "event": r"EVENT-\d{3,}",
    "task": r"TASK-\d{3,}", "practice_evidence": r"PEV-\d{3,}",
    "plan": r"PLAN-\d{3,}", "change": r"CHG-\d{3,}",
    "resource": r"RES-\d{3,}", "assessment": r"ARES-\d{3,}",
    "project": r"PROJECT-\d{3,}",
}
DATE_RE = re.compile(r"\d{4}-\d{2}-\d{2}")

ENUMS = {
    "knowledge_state": {"unexposed", "exposed_not_able", "understands",
                        "independent_application", "transfer_capable", "stable_long_term"},
    "teaching_modality": {"intuition", "derivation", "diagram", "code",
                          "experiment", "case", "socratic", "reverse_teaching"},
    "practice_type": {"concept", "derivation", "calculation", "code", "debug",
                      "experiment", "simulation", "engineering_design",
                      "project", "cross_domain_transfer"},
    "execution_status": {"executed", "theoretical", "simulated", "not_run"},
    "evidence_source": {"self_report", "model_inference", "objective_assessment"},
    "competency_evidence_type": {"independent_project", "design_decision_explanation",
                                 "anomaly_resolution", "parameter_tuning_verified",
                                 "debugging", "cross_scenario_transfer",
                                 "constrained_task_completion"},
    "proficiency_level": {"C0", "C1", "C2", "C3", "C4", "C5"},
    "relationship_type": {"prerequisite", "conceptual_similarity",
                          "mathematical_relation", "causal_relation",
                          "implementation_relation", "application_relation",
                          "contrast_relation"},
    "knowledge_source_type": {"established_definition", "mathematical_theorem",
                              "experimental_fact", "engineering_practice",
                              "model_assumption", "teaching_analogy"},
    "verification_status": {"verified", "unverified", "disputed", "needs_review"},
    "change_type": {"add_prerequisite", "fix_dependency", "merge_duplicate",
                    "split_node", "add_node", "update_mechanism"},
    "change_status": {"proposed", "applied", "rejected"},
    "reviewer": {"deterministic_check", "model_self_review", "human_review"},
    "subject_type": {"knowledge", "competency"},
    "retention_status": {"not_assessed", "at_risk", "stable", "forgotten"},
    "solution_visibility": {"hidden", "on_request", "after_attempt", "teaching_only"},
    "event_type": {"project_created", "classification_confirmed", "map_generated",
                   "graph_changed", "lesson_completed", "assessment_completed",
                   "mastery_updated", "misconception_found", "roadmap_changed",
                   "review_completed", "profile_updated", "competency_updated",
                   "practice_completed", "plan_revised", "graph_change_proposed",
                   "correction", "project_practice_completed"},
    "decision_flag": {"yes", "no"},
}

REQUIRED = {
    "learner_profile": {"profile_id", "project_id", "schema_version", "created_at"},
    "competency": {"competency_id", "name", "description", "required_knowledge",
                   "observable_behaviors", "performance_criteria",
                   "proficiency_levels", "schema_version", "created_at"},
    "competency_progress": {"project_id", "competency_id", "proficiency_level",
                            "confidence", "schema_version"},
    "learning_event": {"event_id", "project_id", "event_type", "occurred_at",
                       "schema_version"},
    "practice_task": {"exercise_id", "target_node_ids", "practice_type", "difficulty",
                      "task", "expected_output", "hints", "evaluation_criteria",
                      "solution_visibility", "schema_version", "created_at"},
    "practice_evidence": {"evidence_id", "project_id", "exercise_id", "scores",
                          "hint_level_used", "execution_status", "evidence_source",
                          "occurred_at", "schema_version"},
    "learning_plan": {"plan_id", "project_id", "version", "created_at", "goal",
                      "decision", "next_action", "reason", "schema_version"},
    "knowledge_graph_change": {"change_id", "affected_node_ids", "change_type",
                               "reason", "evidence", "confidence", "impact_scope",
                               "requires_reassessment", "status", "schema_version",
                               "created_at"},
    "resource": {"resource_id", "title", "resource_type", "relevant_node_ids",
                 "schema_version", "created_at"},
    "assessment_result": {"assessment_id", "project_id", "subject_type", "subject_id",
                          "level", "confidence", "evidence_ids", "reason", "reviewer",
                          "schema_version", "created_at"},
}

SCORE_DIMENSIONS = ("result_correctness", "reasoning", "method", "independence",
                    "anomaly_handling", "constraint_satisfaction", "explainability")


def check_id(value, kind, errors, where):
    if not isinstance(value, str) or not re.fullmatch(ID_PATTERNS[kind], value):
        err(errors, "invalid_id", f"{where}: {kind} ID 格式非法 {value!r}")


def check_common(obj, key, errors, where):
    if obj.get("schema_version") != SCHEMA_VERSION:
        err(errors, "invalid_schema_version", f"{where}: schema_version 必须为 {SCHEMA_VERSION}")
    missing = sorted(REQUIRED[key] - set(obj))
    if missing:
        err(errors, "missing_fields", f"{where}: 缺少必填字段 {', '.join(missing)}")
    for field in ("created_at", "occurred_at", "updated_at", "last_assessed"):
        value = obj.get(field)
        if value is not None and (not isinstance(value, str) or not DATE_RE.fullmatch(value)):
            err(errors, "invalid_date", f"{where}: {field} 必须是 YYYY-MM-DD 或 null")
    if not obj.get("source") and not obj.get("evidence_refs") and key not in (
            "learner_profile", "competency_progress", "learning_plan"):
        err(errors, "missing_source", f"{where}: 必须有 source 或 evidence_refs")


def validate_profile(obj, errors, where="profile"):
    check_common(obj, "learner_profile", errors, where)
    check_id(obj.get("profile_id"), "profile", errors, where)
    prefs = obj.get("learning_preferences", {})
    if not isinstance(prefs, dict):
        err(errors, "invalid_type", f"{where}: learning_preferences 必须是对象")
    else:
        for modality, spec in prefs.items():
            if modality not in ENUMS["teaching_modality"]:
                err(errors, "invalid_enum", f"{where}: 未知教学表征 {modality}")
            if isinstance(spec, dict) and not 0 <= spec.get("weight", 0) <= 5:
                err(errors, "invalid_range", f"{where}: {modality}.weight 必须在 0–5")
    for i, state in enumerate(obj.get("knowledge_states", []) or []):
        if not isinstance(state, dict) or state.get("state") not in ENUMS["knowledge_state"]:
            err(errors, "invalid_enum", f"{where}: knowledge_states[{i}].state 非法")


def validate_competency(obj, errors, where="competency"):
    check_common(obj, "competency", errors, where)
    check_id(obj.get("competency_id"), "competency", errors, where)
    levels = obj.get("proficiency_levels", [])
    if not isinstance(levels, list) or set(levels) != ENUMS["proficiency_level"]:
        err(errors, "invalid_enum", f"{where}: proficiency_levels 必须覆盖 C0–C5")
    for field in ("required_knowledge", "observable_behaviors", "performance_criteria"):
        if not isinstance(obj.get(field), list) or not obj[field]:
            err(errors, "missing_fields", f"{where}: {field} 不能为空")


def validate_competency_progress(obj, errors, where="competency_progress"):
    check_common(obj, "competency_progress", errors, where)
    check_id(obj.get("competency_id"), "competency", errors, where)
    if obj.get("proficiency_level") not in ENUMS["proficiency_level"]:
        err(errors, "invalid_enum", f"{where}: proficiency_level 非法")
    if obj.get("confidence") not in V2_ENUMS["confidence"]:
        err(errors, "invalid_enum", f"{where}: confidence 非法")


def validate_event(obj, errors, where="event"):
    check_common(obj, "learning_event", errors, where)
    check_id(obj.get("event_id"), "event", errors, where)
    if obj.get("event_type") not in ENUMS["event_type"]:
        err(errors, "invalid_enum", f"{where}: event_type 非法")


def validate_practice_task(obj, errors, where="task"):
    check_common(obj, "practice_task", errors, where)
    check_id(obj.get("exercise_id"), "task", errors, where)
    if obj.get("practice_type") not in ENUMS["practice_type"]:
        err(errors, "invalid_enum", f"{where}: practice_type 非法")
    if not is_int(obj.get("difficulty")) or not 1 <= obj["difficulty"] <= 5:
        err(errors, "invalid_range", f"{where}: difficulty 必须 1–5")
    hints = obj.get("hints")
    if not isinstance(hints, list) or len(hints) != 3 or not all(hints):
        err(errors, "invalid_hints", f"{where}: 必须恰好 3 级非空提示")
    if obj.get("solution_visibility") not in ENUMS["solution_visibility"]:
        err(errors, "invalid_enum", f"{where}: solution_visibility 非法")
    if not isinstance(obj.get("evaluation_criteria"), list) or not obj["evaluation_criteria"]:
        err(errors, "missing_fields", f"{where}: evaluation_criteria 不能为空")


def validate_practice_evidence(obj, errors, where="evidence"):
    check_common(obj, "practice_evidence", errors, where)
    check_id(obj.get("evidence_id"), "practice_evidence", errors, where)
    check_id(obj.get("exercise_id"), "task", errors, where)
    if obj.get("execution_status") not in ENUMS["execution_status"]:
        err(errors, "invalid_enum", f"{where}: execution_status 非法")
    if obj.get("evidence_source") not in ENUMS["evidence_source"]:
        err(errors, "invalid_enum", f"{where}: evidence_source 非法")
    scores = obj.get("scores")
    if not isinstance(scores, dict):
        err(errors, "invalid_type", f"{where}: scores 必须是对象")
    else:
        for dim in SCORE_DIMENSIONS:
            value = scores.get(dim)
            if not is_int(value) or not 0 <= value <= 2:
                err(errors, "invalid_range", f"{where}: scores.{dim} 必须 0–2")
    if not is_int(obj.get("hint_level_used")) or not 0 <= obj["hint_level_used"] <= 3:
        err(errors, "invalid_range", f"{where}: hint_level_used 必须 0–3")


def validate_plan(obj, errors, where="plan"):
    check_common(obj, "learning_plan", errors, where)
    check_id(obj.get("plan_id"), "plan", errors, where)
    decision = obj.get("decision")
    required_decisions = {"current_problem", "next_node_id", "needs_review",
                          "needs_prerequisite_repair", "teaching_modality",
                          "practice_type", "enter_project_practice",
                          "allow_advance", "reason"}
    if not isinstance(decision, dict) or not required_decisions <= set(decision):
        err(errors, "invalid_decision", f"{where}: decision 缺少九项输出")
    elif not decision.get("reason"):
        err(errors, "missing_reason", f"{where}: 决策必须给理由")


def validate_change(obj, errors, where="change"):
    check_common(obj, "knowledge_graph_change", errors, where)
    check_id(obj.get("change_id"), "change", errors, where)
    for field, allowed in (("change_type", ENUMS["change_type"]),
                           ("status", ENUMS["change_status"])):
        if obj.get(field) not in allowed:
            err(errors, "invalid_enum", f"{where}: {field} 非法")
    evidence = obj.get("evidence")
    if not isinstance(evidence, list):
        err(errors, "invalid_type", f"{where}: evidence 必须是数组")
    elif obj.get("status") == "applied" and len(evidence) < 2:
        err(errors, "insufficient_evidence", f"{where}: 应用变更至少需 2 条独立证据")
    if not isinstance(obj.get("requires_reassessment"), bool):
        err(errors, "invalid_type", f"{where}: requires_reassessment 必须是布尔值")


def validate_resource(obj, errors, where="resource"):
    check_common(obj, "resource", errors, where)
    check_id(obj.get("resource_id"), "resource", errors, where)
    if obj.get("verification_status", "unverified") not in ENUMS["verification_status"]:
        err(errors, "invalid_enum", f"{where}: verification_status 非法")
    if obj.get("verification_status") == "verified" and not obj.get("last_verified"):
        err(errors, "invalid_verification", f"{where}: 标为 verified 必须有 last_verified")


def validate_assessment_result(obj, errors, where="assessment"):
    check_common(obj, "assessment_result", errors, where)
    check_id(obj.get("assessment_id"), "assessment", errors, where)
    if obj.get("subject_type") not in ENUMS["subject_type"]:
        err(errors, "invalid_enum", f"{where}: subject_type 非法")
    if obj.get("reviewer") not in ENUMS["reviewer"]:
        err(errors, "invalid_enum", f"{where}: reviewer 非法")
    if not isinstance(obj.get("evidence_ids"), list) or not obj["evidence_ids"]:
        err(errors, "missing_evidence", f"{where}: 必须有 evidence_ids")

VALIDATORS = {
    "learner_profile": validate_profile, "competency": validate_competency,
    "competency_progress": validate_competency_progress,
    "learning_event": validate_event, "practice_task": validate_practice_task,
    "practice_evidence": validate_practice_evidence,
    "learning_plan": validate_plan, "knowledge_graph_change": validate_change,
    "resource": validate_resource, "assessment_result": validate_assessment_result,
}
