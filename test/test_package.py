from unittest import TestCase
import warnings
warnings.simplefilter('always')


class PackageTest(TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_query_deprecation(self):
        "Test that importing redcap introduces a DeprecationWarning"
        with warnings.catch_warnings(record=True) as w:
            # This should generate a DeprecationWarning
            import redcap
            # http://docs.python.org/2/library/warnings.html#testing-warnings
            self.assertTrue(issubclass(w[-1].category, DeprecationWarning))
            self.assertIn("Query & QueryGroup will be removed", str(w[-1].message))
