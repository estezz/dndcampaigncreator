import pytest
from classA import A
from classB import B
from unittest.mock import patch


@patch("classA.A")
def test_b(mock_a):
    mock_a.do_a.return_value = "cat"
    
    b  = B()
    b.a = mock_a
    value = b.do_b()
    print(value)
    assert value == "dog"