import numpy as np
from sksundae.common import RichResult, _format_float_10


def test_RichResult():

    result = RichResult()
    assert result._order_keys == []
    assert repr(result) == 'RichResult()'

    class NewResult(RichResult):
        pass

    result = NewResult()
    assert repr(result) == 'NewResult()'

    class OrderedResult(RichResult):
        _order_keys = ['first', 'second',]

    new = NewResult(second=None, first=None)
    ordered = OrderedResult(second=None, first=None)
    assert new.__dict__ == ordered.__dict__
    assert repr(new) != repr(ordered)


def test_format_float_10():
    assert _format_float_10(np.inf) == '       inf'
    assert _format_float_10(-np.inf) == '      -inf'
    assert _format_float_10(np.nan) == '       nan'

    assert _format_float_10(0.123456789) == ' 1.235e-01'
    assert _format_float_10(1.234567890) == ' 1.235e+00'
    assert _format_float_10(1234.567890) == ' 1.235e+03'
