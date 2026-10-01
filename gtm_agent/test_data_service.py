import copy
import os
import unittest

os.environ.setdefault("OPENAI_API_KEY", "test-key")

from gtm_agent import data_service
from gtm_agent.gtm_agent import build_prospect_profile


class UpdateProspectInfoTest(unittest.TestCase):
    def test_update_persists_and_invalidates_cached_profile(self):
        prospect_id = "LEAD-90001"
        original_record = copy.deepcopy(data_service.PROSPECTS[prospect_id])
        original_profile = data_service._PROFILES.pop(prospect_id, None)
        self.addCleanup(self._restore_state, prospect_id, original_record, original_profile)

        build_prospect_profile.invoke({"prospect_id": prospect_id})
        result = data_service.update_prospect_info(prospect_id, "Okta")

        self.assertIn("Okta", data_service.fetch_tech_stack(prospect_id))
        self.assertIn(
            "Okta",
            build_prospect_profile.invoke({"prospect_id": prospect_id})[
                "prospect_profile"
            ]["tech_stack"],
        )
        self.assertIn("Okta", result["tech_stack"])

    @staticmethod
    def _restore_state(prospect_id, original_record, original_profile):
        data_service.PROSPECTS[prospect_id] = original_record
        if original_profile is None:
            data_service._PROFILES.pop(prospect_id, None)
        else:
            data_service._PROFILES[prospect_id] = original_profile


if __name__ == "__main__":
    unittest.main()
