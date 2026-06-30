import argparse
import json
from dataclasses import asdict

from pipeline import load_ats_source, load_github_source, merge_and_build_profile
from config_engine import apply_config

def main():
    parser = argparse.ArgumentParser(description="Multi-Source Candidate Data Transformer")
    parser.add_argument("--ats", required=True, help="Path to ATS JSON source")
    parser.add_argument("--github", required=True, help="Path to GitHub JSON source")
    parser.add_argument("--config", required=True, help="Path to runtime configuration JSON")
    parser.add_argument("--output", default="final_profile.json", help="Path to save output")
    
    args = parser.parse_args()
    
    print(f"[*] Ingesting ATS data from {args.ats}...")
    ats_data = load_ats_source(args.ats)
    
    print(f"[*] Ingesting GitHub data from {args.github}...")
    github_data = load_github_source(args.github)
    
    print("[*] Merging and resolving conflicts...")
    canonical_profile_model = merge_and_build_profile(ats_data, github_data)
    canonical_profile = asdict(canonical_profile_model)
    
    print(f"[*] Applying runtime config from {args.config}...")
    try:
        with open(args.config, 'r') as f:
            config = json.load(f)
    except Exception as e:
        print(f"[!] Error loading config: {e}")
        return
        
    try:
        final_output = apply_config(canonical_profile, config)
    except ValueError as ve:
        print(f"[!] Config Validation Error: {ve}")
        return
    
    # Save Output
    with open(args.output, 'w') as f:
        json.dump(final_output, f, indent=2)
        
    print(f"[+] Success! Profile saved to {args.output}")

if __name__ == "__main__":
    main()
