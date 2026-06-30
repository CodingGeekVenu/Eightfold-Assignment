import re
from typing import Optional

# ==========================================
# CONSTANTS & MAPS
# ==========================================
SKILL_ALIAS_MAP = {
    "js": "JavaScript",
    "javascript": "JavaScript",
    "reactjs": "React",
    "react": "React",
    "python": "Python",
    "py": "Python"
}

COUNTRY_MAP = {
    "united states": "US",
    "usa": "US",
    "india": "IN",
    "united kingdom": "GB",
    "uk": "GB"
}

def normalize_phone(raw_phone: str) -> Optional[str]:
    """Forces phone numbers into E.164 format."""
    if not raw_phone: return None
    # Strip everything except digits and the plus sign
    cleaned = re.sub(r'[^\d+]', '', raw_phone)
    if not cleaned.startswith('+'):
        # MVP Fallback: Assume US +1 if exactly 10 digits
        digits_only = re.sub(r'\D', '', cleaned)
        if len(digits_only) == 10:
            return f"+1{digits_only}"
        return f"+{cleaned}"
    return cleaned

def normalize_skill(raw_skill: str) -> str:
    """Resolves skills to canonical names or standardizes format."""
    clean_skill = raw_skill.strip().lower()
    # Return the mapped Canonical name, or fallback to the stripped lowercase version
    return SKILL_ALIAS_MAP.get(clean_skill, clean_skill)
