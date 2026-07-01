import re
from typing import Dict
from normalize import normalize_phone

def apply_config(profile: Dict, config: Dict) -> Dict:
    """Reshapes the canonical profile based on the runtime config."""
    output = {}
    on_missing = config.get("on_missing", "null")
    
    # Process requested fields dynamically
    for field_def in config.get("fields", []):
        target_path = field_def.get("path")
        source_path = field_def.get("from", target_path) # Default to path if 'from' is missing
        
        val = None
        # Minimal path resolution for the MVP (handling the specific array indices)
        match = re.match(r"^([a-zA-Z_]+)\[(\d+)\]$", source_path)
        if match:
            field_name = match.group(1)
            index = int(match.group(2))
            arr = profile.get(field_name)
            if isinstance(arr, list) and index < len(arr):
                val = arr[index]
            else:
                val = None
        elif source_path == "skills[].name" and profile.get("skills"):
            val = [s["name"] for s in profile["skills"]]
        else:
            val = profile.get(source_path)
        
        # Apply per-field normalization override if requested
        if val and field_def.get("normalize") == "E164":
            val = normalize_phone(val)
            
        # Handle Missing Values exactly as configured
        if not val:
            if on_missing == "omit":
                continue
            elif on_missing == "error":
                raise ValueError(f"Required field '{source_path}' is missing.")
            else:
                val = None
                
        output[target_path] = val
        
    # Toggle tracking metadata on/off
    if config.get("include_confidence"):
        output["overall_confidence"] = profile.get("overall_confidence")
    if config.get("include_provenance"):
        output["provenance"] = profile.get("provenance")
        
    return output
