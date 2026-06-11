import unittest
from unittest.mock import patch

from app.routers.itinerary import (
    ItineraryRequest,
    _build_fallback_itinerary,
    _normalize_generated_itinerary,
    generate_itinerary,
)


class ItineraryRequestTests(unittest.TestCase):
    def test_legacy_duration_labels_are_parsed(self):
        self.assertEqual(ItineraryRequest(duration="7 Hari").duration, 7)
        self.assertEqual(ItineraryRequest(duration="3d2n").duration, 3)

    def test_legacy_budget_label_is_parsed(self):
        request = ItineraryRequest(budget="Rp 500rb-1jt/hari")
        self.assertEqual(request.budget, 750_000)


class ItineraryGenerationTests(unittest.TestCase):
    def test_fallback_matches_requested_day_count(self):
        request = ItineraryRequest(
            destination="Sikunir",
            duration=10,
            budget=750_000,
            guests=2,
            interests=["Sunrise"],
        )

        result = _build_fallback_itinerary(request)

        self.assertEqual(len(result["days"]), 10)
        self.assertEqual(result["meta"]["requestedDays"], 10)
        self.assertEqual(result["days"][0]["activities"][1]["location"], "Sikunir")

    def test_normalizer_fills_missing_days_and_supports_legacy_items(self):
        request = ItineraryRequest(duration=5)
        fallback = _build_fallback_itinerary(request)
        generated = {
            "days": [
                {
                    "day": 1,
                    "items": [
                        {
                            "time": "09:00",
                            "title": "Telaga Warna",
                            "desc": "Datang pagi.",
                            "type": "attraction",
                        }
                    ],
                }
            ]
        }

        result = _normalize_generated_itinerary(generated, fallback, "gemini")

        self.assertEqual(len(result["days"]), 5)
        self.assertEqual(result["days"][0]["activities"][0]["name"], "Telaga Warna")
        self.assertTrue(result["days"][4]["activities"])


class ItineraryEndpointTests(unittest.IsolatedAsyncioTestCase):
    async def test_endpoint_fallback_preserves_requested_duration(self):
        class PredictorStub:
            models_loaded = False

        async def live_weather_stub():
            return 13.0, 0.0

        request = ItineraryRequest(
            destination="Telaga Warna",
            duration=7,
            budget=750_000,
            guests=3,
            interests=["Alam", "Fotografi"],
        )

        from fastapi import Request
        from unittest.mock import MagicMock
        mock_request = MagicMock(spec=Request)
        mock_request.client = MagicMock()
        mock_request.client.host = "127.0.0.1"
        mock_request.scope = {"type": "http", "client": ("127.0.0.1", 1234)}

        with (
            patch("app.routers.itinerary._live_temp_precip_mm", live_weather_stub),
            patch("app.routers.itinerary.get_predictor", return_value=PredictorStub()),
            patch("app.routers.itinerary._get_client", return_value=None),
            patch.dict("os.environ", {"NVIDIA_API_KEY": ""}),
        ):
            result = await generate_itinerary(req=request, request=mock_request)

        self.assertEqual(len(result["days"]), 7)
        self.assertEqual(result["meta"]["source"], "dita_engine")


if __name__ == "__main__":
    unittest.main()
