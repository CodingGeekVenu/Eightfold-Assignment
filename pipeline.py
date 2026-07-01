import json
import os
import uuid
from typing import Dict, List, Any, Optional

from models import CanonicalProfile, create_empty_canonical
from normalize import normalize_phone, normalize_skill

# Source Weights for Confidence Rollup
WEIGHT_ATS = 0.8
WEIGHT_GITHUB = 0.7

def load_ats_source(file_path: str) -> List[Dict[str, Any]]:
    """Detects issues and extracts raw payloads from the ATS source file."""
    if not os.path.exists(file_path) or os.path.getsize(file_path) == 0:
        print(f"[WARNING] Detect Stage: ATS source '{file_path}' is missing or empty. Skipping.")
        return []
    try:
        with open(file_path, 'r') as f:
            data = json.load(f)
            if not isinstance(data, list):
                print("[WARNING] Extract Stage: ATS payload must be a JSON array. Skipping.")
                return []
            return data
    except json.JSONDecodeError:
        print(f"[WARNING] Detect Stage: ATS source '{file_path}' contains malformed JSON. Skipping.")
        return []

def load_github_source(file_path: str) -> Optional[Dict[str, Any]]:
    """Detects issues and extracts raw payload from the GitHub API source file."""
    if not os.path.exists(file_path) or os.path.getsize(file_path) == 0:
        print(f"[WARNING] Detect Stage: GitHub source '{file_path}' is missing or empty. Skipping.")
        return None
    try:
        with open(file_path, 'r') as f:
            data = json.load(f)
            if not isinstance(data, dict):
                print("[WARNING] Extract Stage: GitHub payload must be a JSON object. Skipping.")
                return None
            return data
    except json.JSONDecodeError:
        print(f"[WARNING] Detect Stage: GitHub source '{file_path}' contains malformed JSON. Skipping.")
        return None

def add_provenance(profile: CanonicalProfile, field: str, source: str, method: str):
    """Helper to append to the provenance array."""
    profile.provenance.append({"field": field, "source": source, "method": method})

def merge_and_build_profile(ats_data: List[Dict], github_data: Dict) -> CanonicalProfile:
    """Merges sources, resolves conflicts, and tracks provenance."""
    profile = create_empty_canonical()
    
    # For MVP, we assume the first ATS record and the GitHub record match.
    ats = ats_data[0] if ats_data else {}
    gh = github_data or {}
    
    # 1. Candidate ID (Deterministic UUID5 based on email)
    primary_email = ""
    if ats.get("emails"):
        primary_email = ats["emails"][0].lower()
    elif gh.get("email"):
        primary_email = gh["email"].lower()
        
    if primary_email:
        profile.candidate_id = str(uuid.uuid5(uuid.NAMESPACE_URL, primary_email))
    else:
        name = ats.get("name", "")
        phones = ats.get("phones", [])
        phone = phones[0] if phones else ""
        if name or phone:
            fallback_string = f"{name}_{phone}".lower()
            profile.candidate_id = str(uuid.uuid5(uuid.NAMESPACE_URL, fallback_string))
        else:
            profile.candidate_id = str(uuid.uuid4()) # Fallback

    # 2. Name & Contact (ATS wins on contact info per design doc)
    if ats.get("name"):
        profile.full_name = ats["name"].title()
        add_provenance(profile, "full_name", "ats_input.json", "exact_extraction")
    
    if ats.get("emails"):
        profile.emails = sorted(list(set(ats["emails"])))
        add_provenance(profile, "emails", "ats_input.json", "exact_extraction")
        
    if ats.get("phones"):
        normalized_phones = [normalize_phone(p) for p in ats["phones"] if p]
        profile.phones = sorted(list(set(normalized_phones)))
        add_provenance(profile, "phones", "ats_input.json", "normalized_E164")

    # 3. Experience (ATS)
    if ats.get("history"):
        for job in ats["history"]:
            profile.experience.append({
                "company": job.get("company"),
                "title": job.get("title"),
                "start": job.get("start_date"),
                "end": job.get("end_date") if job.get("end_date") else "Present",
                "summary": job.get("description")
            })
        add_provenance(profile, "experience", "ats_input.json", "exact_extraction")
        
        # Simple MVP Years Experience calc with date clamping
        valid_roles = 0
        for job in profile.experience:
            start = job["start"]
            end = job["end"]
            if start and end and end != "Present" and end < start:
                continue
            valid_roles += 1
        profile.years_experience = valid_roles * 2 # Mocking 2 years per role for speed

    # 4. Skills & Links (GitHub wins on Technical per design doc)
    if gh.get("languages"):
        sorted_canonical_skills = sorted(list(set(normalize_skill(lang) for lang in gh["languages"])))
        for norm_lang in sorted_canonical_skills:
            profile.skills.append({
                "name": norm_lang, 
                "confidence": WEIGHT_GITHUB, 
                "sources": ["github_input.json"]
            })
        add_provenance(profile, "skills", "github_input.json", "normalized_canonical")
    
    if gh.get("blog"):
        profile.links.portfolio = gh["blog"]
        add_provenance(profile, "links.portfolio", "github_input.json", "exact_extraction")
        
    if gh.get("bio"):
        profile.headline = gh["bio"]
        add_provenance(profile, "headline", "github_input.json", "exact_extraction")

    # 5. Overall Confidence Calculation
    # Based on the design doc: sum of (Presence * Weight) / Sum of Weights
    total_weight = 0
    earned_weight = 0
    
    # If ATS contributed contact/history
    if profile.emails or profile.experience:
        total_weight += WEIGHT_ATS
        earned_weight += WEIGHT_ATS
    # If GitHub contributed skills
    if profile.skills:
        total_weight += WEIGHT_GITHUB
        earned_weight += WEIGHT_GITHUB
        
    profile.overall_confidence = round(earned_weight / total_weight, 2) if total_weight > 0 else 0.0

    return profile
