import os
import unittest
from unittest.mock import patch

os.environ.setdefault("OPENAI_API_KEY", "test-key")
os.environ.setdefault("LANGSMITH_TRACING", "false")

from gtm_agent import gtm_agent


SENSITIVE_FIELDS = (
    "billing_qualification",
    "tax_id",
    "date_of_birth",
    "card_on_file",
    "credit_check_ref",
)


def assert_keys_absent(test_case, value):
    if isinstance(value, dict):
        for key in SENSITIVE_FIELDS:
            test_case.assertNotIn(key, value)
        for nested in value.values():
            assert_keys_absent(test_case, nested)
    elif isinstance(value, (list, tuple)):
        for nested in value:
            assert_keys_absent(test_case, nested)


class ProspectPrivacyTest(unittest.TestCase):
    def test_lookup_and_profile_do_not_expose_billing_fields(self):
        prospect_id = "LEAD-12853"
        with patch.object(gtm_agent.data_service, "save_profile_to_db") as save_profile:
            prospect = gtm_agent.get_prospect.invoke({"prospect_id": prospect_id})
            profile = gtm_agent.build_prospect_profile.invoke({"prospect_id": prospect_id})

        assert_keys_absent(self, prospect)
        assert_keys_absent(self, profile)
        assert_keys_absent(self, save_profile.call_args.args[1])

    def test_cached_profile_is_sanitized_and_updated(self):
        prospect_id = "LEAD-12853"
        cached_profile = {
            "prospect_id": prospect_id,
            "name": "cached",
            "billing_qualification": {
                "tax_id": None,
                "date_of_birth": None,
                "card_on_file": None,
                "credit_check_ref": None,
            },
            "engagement_history": [],
            "account_details": {},
            "tech_stack": [],
        }
        with patch.object(
            gtm_agent.data_service,
            "get_profile_from_db",
            return_value={"prospect_profile": cached_profile},
        ), patch.object(gtm_agent.data_service, "save_profile_to_db") as save_profile:
            result = gtm_agent.build_prospect_profile.invoke({"prospect_id": prospect_id})

        assert_keys_absent(self, result)
        assert_keys_absent(self, save_profile.call_args.args[1])


if __name__ == "__main__":
    unittest.main()
