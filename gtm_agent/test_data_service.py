import os
import unittest

from . import data_service

os.environ.setdefault("OPENAI_API_KEY", "test-key")

from .gtm_agent import build_prospect_profile


class UpdateProspectInfoTest(unittest.TestCase):
    def test_update_persists_to_record_and_invalidates_profile_cache(self):
        prospect_id = "LEAD-39002"
        original_stack = list(data_service.PROSPECTS[prospect_id]["tech_stack"])
        data_service._PROFILES.pop(prospect_id, None)
        try:
            build_prospect_profile.invoke({"prospect_id": prospect_id})

            result = data_service.update_prospect_info(prospect_id, "Terraform")

            self.assertTrue(result["updated"])
            self.assertIn("Terraform", data_service.fetch_tech_stack(prospect_id))
            profile = build_prospect_profile.invoke({"prospect_id": prospect_id})
            self.assertIn("Terraform", profile["prospect_profile"]["tech_stack"])
        finally:
            data_service.PROSPECTS[prospect_id]["tech_stack"] = original_stack
            data_service._PROFILES.pop(prospect_id, None)


if __name__ == "__main__":
    unittest.main()
