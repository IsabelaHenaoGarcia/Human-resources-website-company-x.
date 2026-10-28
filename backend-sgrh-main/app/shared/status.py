STATUS_TRANSITIONS: dict[str, dict[str, set[str]]] = {
    "candidate": {"draft": {"in_process"}, "in_process": {"approved", "rejected"}, "approved": {"hired"}},
    "employee": {"active": {"on_leave", "inactive", "retired"}, "on_leave": {"active"}},
    "contract": {"draft": {"active", "cancelled"}, "active": {"finished", "cancelled"}},
    "affiliation": {"pending": {"in_progress"}, "in_progress": {"completed", "rejected"}},
    "payroll_period": {"draft": {"in_review"}, "in_review": {"approved"}, "approved": {"closed"}},
    "payroll_settlement": {"generated": {"reviewed"}, "reviewed": {"approved"}},
    "contributions": {"generated": {"reviewed"}, "reviewed": {"exported"}},
    "offboarding": {"draft": {"in_process"}, "in_process": {"completed"}},
    "contract_settlement": {"generated": {"reviewed"}, "reviewed": {"approved"}, "approved": {"paid"}},
    "certificate": {"requested": {"generated"}, "generated": {"delivered"}},
    "evaluation": {"scheduled": {"completed"}, "completed": {"closed"}},
    "improvement_plan": {"open": {"in_progress"}, "in_progress": {"closed"}},
}


def transition_allowed(entity: str, current: str, target: str) -> bool:
    if current == target:
        return True
    return target in STATUS_TRANSITIONS.get(entity, {}).get(current, set())

