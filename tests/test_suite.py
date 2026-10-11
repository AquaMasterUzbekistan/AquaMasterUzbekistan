"""Automated test suite using standard library unittest."""

import unittest
from app.services.calculator_service import CalculatorService
from app.utils.validators import (
    is_valid_scientific_name,
    sanitize_search_query,
    is_positive_number,
    validate_telegram_id,
)
from app.utils.formatting import (
    format_aggression,
    format_difficulty,
    format_reliability,
)
from app.models.species import (
    AggressionLevel,
    DifficultyLevel,
    ReliabilityLevel,
)


class TestCalculators(unittest.TestCase):
    def test_volume(self):
        self.assertEqual(CalculatorService.volume(100, 40, 50), 200.0)
        self.assertEqual(CalculatorService.volume(60, 30, 35), 63.0)
        self.assertEqual(CalculatorService.volume(30, 30, 30), 27.0)

    def test_water_change(self):
        self.assertEqual(CalculatorService.water_change(200, 25), 50.0)
        self.assertEqual(CalculatorService.water_change(100, 30), 30.0)
        self.assertEqual(CalculatorService.water_change(150, 0), 0.0)

    def test_heater_wattage(self):
        self.assertEqual(CalculatorService.heater_wattage(20), "25 W")
        self.assertEqual(CalculatorService.heater_wattage(50), "50 W")
        self.assertEqual(CalculatorService.heater_wattage(100), "100 W")
        self.assertEqual(CalculatorService.heater_wattage(200), "200 W")
        self.assertEqual(CalculatorService.heater_wattage(300), "300 W")
        self.assertEqual(CalculatorService.heater_wattage(550), "2 × 300 W")

    def test_filter_flow(self):
        self.assertEqual(CalculatorService.filter_flow(200, 4), 800.0)
        self.assertEqual(CalculatorService.filter_flow(100, 6), 600.0)

    def test_stocking_estimate(self):
        self.assertEqual(CalculatorService.stocking_estimate(100, 5.0), 10)
        self.assertEqual(CalculatorService.stocking_estimate(100, 0), 10)

    def test_salt_dosage(self):
        self.assertEqual(CalculatorService.salt_dosage(100, 1.0), 100.0)
        self.assertEqual(CalculatorService.salt_dosage(50, 3.0), 150.0)

    def test_feeding_estimate(self):
        self.assertIn("g/kun", CalculatorService.feeding_estimate(10, 5.0))
        self.assertEqual(CalculatorService.feeding_estimate(0, 5.0), "Ma'lumot yetarli emas.")


class TestValidators(unittest.TestCase):
    def test_scientific_names(self):
        self.assertTrue(is_valid_scientific_name("Pseudotropheus demasoni"))
        self.assertTrue(is_valid_scientific_name("Symphysodon discus"))
        self.assertFalse(is_valid_scientific_name("Demasoni"))
        self.assertFalse(is_valid_scientific_name(""))

    def test_sanitization(self):
        self.assertEqual(sanitize_search_query("  Discus  "), "Discus")
        self.assertEqual(sanitize_search_query("select * from species;--"), "select * from species")

    def test_numbers(self):
        self.assertTrue(is_positive_number("10"))
        self.assertTrue(is_positive_number("2.5"))
        self.assertFalse(is_positive_number("0"))
        self.assertFalse(is_positive_number("-1"))
        self.assertFalse(is_positive_number("abc"))

    def test_telegram_id(self):
        self.assertTrue(validate_telegram_id(123456789))
        self.assertFalse(validate_telegram_id(0))
        self.assertFalse(validate_telegram_id(-1))


class TestFormatting(unittest.TestCase):
    def test_enums(self):
        self.assertIn("Tinch", format_aggression(AggressionLevel.PEACEFUL))
        self.assertIn("Boshlang'ich", format_difficulty(DifficultyLevel.BEGINNER))
        self.assertIn("Ilmiy manba bilan tasdiqlangan", format_reliability(ReliabilityLevel.SCIENTIFIC))


if __name__ == "__main__":
    unittest.main()
