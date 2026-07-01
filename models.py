from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional

@dataclass
class Location:
    city: Optional[str] = None
    region: Optional[str] = None
    country: Optional[str] = None

@dataclass
class Links:
    linkedin: Optional[str] = None
    github: Optional[str] = None
    portfolio: Optional[str] = None
    other: List[str] = field(default_factory=list)

@dataclass
class CanonicalProfile:
    candidate_id: str = ""
    full_name: str = ""
    emails: List[str] = field(default_factory=list)
    phones: List[str] = field(default_factory=list)
    location: Location = field(default_factory=Location)
    links: Links = field(default_factory=Links)
    headline: Optional[str] = None
    years_experience: Optional[float] = None
    skills: List[Dict[str, Any]] = field(default_factory=list)
    experience: List[Dict[str, Any]] = field(default_factory=list)
    education: List[Dict[str, Any]] = field(default_factory=list)
    provenance: List[Dict[str, str]] = field(default_factory=list)
    overall_confidence: float = 0.0

def create_empty_canonical() -> CanonicalProfile:
    """Generates a perfectly shaped, empty canonical candidate profile template."""
    return CanonicalProfile()

def validate_profile(output: Dict) -> bool:
    """Validates the output profile to ensure it doesn't break critical constraints."""
    if not isinstance(output, dict):
        raise ValueError("Final profile must be a dictionary.")
    
    # Check overall_confidence if present
    conf = output.get("overall_confidence")
    if conf is not None:
        if not isinstance(conf, (int, float)) or not (0.0 <= conf <= 1.0):
            raise ValueError(f"overall_confidence must be a float between 0.0 and 1.0. Got: {conf}")
            
    # Check years_experience if present
    exp = output.get("years_experience")
    if exp is not None:
        if not isinstance(exp, (int, float)) or exp < 0:
            raise ValueError(f"years_experience cannot be negative. Got: {exp}")
            
    return True
