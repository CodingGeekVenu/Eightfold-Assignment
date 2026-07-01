import unittest
import os
import json
from datetime import datetime

from pipeline import load_ats_source, merge_and_build_profile, parse_date
from normalize import normalize_phone

class TestPipeline(unittest.TestCase):
    
    def test_bad_ats_json_graceful_degradation(self):
        """Test that malformed or unexpected ATS JSON degrades gracefully without crashing."""
        # bad_ats.json exists in the project and is an object instead of an array
        result = load_ats_source("bad_ats.json")
        self.assertEqual(result, [])
        
        # Non-existent file should also degrade gracefully
        result2 = load_ats_source("does_not_exist.json")
        self.assertEqual(result2, [])

    def test_normalize_phone_e164(self):
        """Test that phones are formatted into E164 properly."""
        self.assertEqual(normalize_phone("+1 (415) 555-2671"), "+14155552671")
        self.assertEqual(normalize_phone("415-555-2671"), "+14155552671") # 10 digits US fallback
        self.assertEqual(normalize_phone("+44 20 7123 1234"), "+442071231234")
        self.assertIsNone(normalize_phone(None))

    def test_years_experience_math(self):
        """Test that date parsing, clamping, and overlapping intervals work safely."""
        ats_data = [{
            "emails": ["test@example.com"],
            "history": [
                {
                    "start_date": "2020-01",
                    "end_date": "2021-01"
                },
                {
                    # Overlaps with the above entirely
                    "start_date": "2020-06",
                    "end_date": "2020-12"
                },
                {
                    # Invalid chronological order (end < start) -> Should be ignored
                    "start_date": "2019-01",
                    "end_date": "2018-01"
                },
                {
                    # Valid addition
                    "start_date": "2022-01",
                    "end_date": "2023-01"
                }
            ]
        }]
        
        profile = merge_and_build_profile(ats_data, {})
        
        # Job 1: 12 months
        # Job 2: overlap (ignored in final math)
        # Job 3: ignored (invalid)
        # Job 4: 12 months
        # Total: 24 months = 2.0 years
        self.assertEqual(profile.years_experience, 2.0)

if __name__ == "__main__":
    unittest.main()
