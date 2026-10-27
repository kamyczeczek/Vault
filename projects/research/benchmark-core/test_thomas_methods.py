from thomas_methods import get_thomas_methods


def test_thomas_method_registry():
    methods = get_thomas_methods()
    assert {"persistence", "nlinear_a1", "nlinear_a10", "rff_h64",
            "subband_cA1", "subband_d1", "ridge_delay_recursive"}.issubset(methods)
    assert all(callable(method) for method in methods.values())
