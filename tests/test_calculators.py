"""Unit tests for Aquarium Calculator Service."""

from __future__ import annotations

import unittest
from app.services.calculator_service import CalculatorService


class TestCalculatorFunctions(unittest.TestCase):
    def test_volume_calculation(self):
        # 100cm x 40cm x 50cm = 200,000 cm³ = 200 Liters
        self.assertEqual(CalculatorService.volume(100, 40, 50), 200.0)
        # 60cm x 30cm x 35cm = 63,000 cm³ = 63 Liters
        self.assertEqual(CalculatorService.volume(60, 30, 35), 63.0)
        # Cube: 30cm x 30cm x 30cm = 27 Liters
        self.assertEqual(CalculatorService.volume(30, 30, 30), 27.0)

    def test_water_change_calculation(self):
        # 200 Liters, 25% change = 50 Liters
        self.assertEqual(CalculatorService.water_change(200, 25), 50.0)
        # 100 Liters, 30% change = 30 Liters
        self.assertEqual(CalculatorService.water_change(100, 30), 30.0)
        # 0% and 100%
        self.assertEqual(CalculatorService.water_change(150, 0), 0.0)
        self.assertEqual(CalculatorService.water_change(150, 100), 150.0)

    def test_heater_wattage(self):
        self.assertEqual(CalculatorService.heater_wattage(20), "25 W")
        self.assertEqual(CalculatorService.heater_wattage(45), "50 W")
        self.assertEqual(CalculatorService.heater_wattage(80), "100 W")
        self.assertEqual(CalculatorService.heater_wattage(140), "150 W")
        self.assertEqual(CalculatorService.heater_wattage(190), "200 W")
        self.assertEqual(CalculatorService.heater_wattage(280), "300 W")
        self.assertEqual(CalculatorService.heater_wattage(550), "2 × 300 W")

    def test_filter_flow(self):
        # 200 Liters with 4x turnover = 800 L/h
        self.assertEqual(CalculatorService.filter_flow(200, 4), 800.0)
        # 100 Liters with 6x turnover = 600 L/h
        self.assertEqual(CalculatorService.filter_flow(100, 6), 600.0)

    def test_stocking_estimate(self):
        # 100 Liters, 5cm fish -> 100 / (5 * 2) = 10 fish
        self.assertEqual(CalculatorService.stocking_estimate(100, 5.0), 10)
        # Zero or negative size handles gracefully
        self.assertEqual(CalculatorService.stocking_estimate(100, 0), 10)

    def test_salt_dosage(self):
        # 100 Liters, 1 ppt (1g/L) = 100g
        self.assertEqual(CalculatorService.salt_dosage(100, 1.0), 100.0)
        # 50 Liters, 3 ppt (3g/L) = 150g
        self.assertEqual(CalculatorService.salt_dosage(50, 3.0), 150.0)

    def test_feeding_estimate(self):
        self.assertIn("g/kun", CalculatorService.feeding_estimate(10, 5.0))
        self.assertEqual(CalculatorService.feeding_estimate(0, 5.0), "Ma'lumot yetarli emas.")


if __name__ == "__main__":
    unittest.main()
