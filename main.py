import argparse
import json
import logging
from dataclasses import asdict

from pipeline import load_ats_source, load_github_source, merge_and_build_profile
from config_engine import apply_config
from models import validate_profile

def main():
    parser = argparse.ArgumentParser(description="Multi-Source Candidate Data Transformer")
    parser.add_argument("--ats", required=True, help="Path to ATS JSON source")
    parser.add_argument("--github", required=True, help="Path to GitHub JSON source")
    parser.add_argument("--config", required=True, help="Path to runtime configuration JSON")
    parser.add_argument("--output", default="final_profile.json", help="Path to save output")
    
    args = parser.parse_args()
    
    logging.basicConfig(level=logging.INFO, format="[%(levelname)s] %(message)s")
    
    logging.info(f"Ingesting ATS data from {args.ats}...")
    ats_data = load_ats_source(args.ats)
    
    logging.info(f"Ingesting GitHub data from {args.github}...")
    github_data = load_github_source(args.github)
    
    logging.info("Merging and resolving conflicts...")
    canonical_profile_model = merge_and_build_profile(ats_data, github_data)
    canonical_profile = asdict(canonical_profile_model)
    
    logging.info(f"Applying runtime config from {args.config}...")
    try:
        with open(args.config, 'r') as f:
            config = json.load(f)
    except Exception as e:
        logging.error(f"Error loading config: {e}")
        return
        
    try:
        final_output = apply_config(canonical_profile, config)
    except ValueError as ve:
        logging.error(f"Config Engine Error: {ve}")
        return
        
    logging.info("Validating final output constraints...")
    try:
        validate_profile(final_output)
    except ValueError as ve:
        logging.error(f"Validation Error: {ve}")
        return
    
    # Save Output
    with open(args.output, 'w') as f:
        json.dump(final_output, f, indent=2)
        
    logging.info(f"Success! Profile saved to {args.output}")

if __name__ == "__main__":
    main()
