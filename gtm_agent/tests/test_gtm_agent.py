import unittest
from unittest.mock import patch

from gtm_agent.gtm_agent import send_prospect_email


class SendProspectEmailTest(unittest.TestCase):
    def test_disqualified_prospect_is_blocked(self):
        prospect = {
            "prospect_id": "LEAD-50001",
            "name": "Priya Nair",
            "email": "priya@example.com",
        }
        with patch(
            "gtm_agent.gtm_agent.data_service.get_prospect_record",
            return_value={"disqualified": True},
        ):
            result = send_prospect_email.func(
                prospect, "Subject", "Body", None, {"email": "rep@example.com"}
            )

        self.assertEqual(result["status"], "blocked")
        self.assertNotIn("message_id", result)

    def test_qualified_prospect_sends_normally(self):
        prospect = {
            "prospect_id": "LEAD-50002",
            "name": "Alex Smith",
            "email": "alex@example.com",
        }
        with patch(
            "gtm_agent.gtm_agent.data_service.get_prospect_record",
            return_value={"disqualified": False},
        ):
            result = send_prospect_email.func(
                prospect, "Subject", "Body", None, {"email": "rep@example.com"}
            )

        self.assertEqual(result["status"], "sent")
        self.assertIn("message_id", result)


if __name__ == "__main__":
    unittest.main()
