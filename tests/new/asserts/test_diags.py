import unittest         # tests
import source.meta.ssDiagnostics as diags

global VERBOSE
VERBOSE = True
# VERBOSE = False

class DiagnosticsAudit(unittest.TestCase):
    def set_Up(self, *args):
        pass

    def test_diagnostics(self):
        print("\n".join(diags.output()))

if __name__ == "__main__":
    if VERBOSE:
        print("ANIMATIONS")
        print('.' * 70)

    unittest.main()
