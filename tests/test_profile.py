"""Unit tests for the profile's deterministic, dependency-free generator."""

import copy
import unittest

from scripts.profile import ProfileError, load_profile, render, validate


class ProfileTests(unittest.TestCase):
    def setUp(self):
        self.profile = load_profile()

    def test_render_is_deterministic(self):
        self.assertEqual(render(self.profile), render(copy.deepcopy(self.profile)))

    def test_rejects_duplicate_specializations(self):
        data = copy.deepcopy(self.profile)
        data["specializations"].append(copy.deepcopy(data["specializations"][0]))
        with self.assertRaises(ProfileError):
            validate(data)

    def test_rejects_unknown_keys(self):
        data = copy.deepcopy(self.profile)
        data["unapproved_field"] = "not accepted"
        with self.assertRaises(ProfileError):
            validate(data)

    def test_rejects_blank_text(self):
        data = copy.deepcopy(self.profile)
        data["name"] = "  "
        with self.assertRaises(ProfileError):
            validate(data)

    def test_rejects_boolean_schema_version(self):
        data = copy.deepcopy(self.profile)
        data["schema_version"] = True
        with self.assertRaises(ProfileError):
            validate(data)


if __name__ == "__main__":
    unittest.main()
