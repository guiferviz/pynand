import pytest

from pynand.nand_components.nand import nand
from pynand.helpers import simulate_component_fn


@pytest.mark.parametrize(
    "inputs, outputs",
    [
        [dict(a=0, b=0), dict(q=1)],
        [dict(a=0, b=1), dict(q=1)],
        [dict(a=1, b=0), dict(q=1)],
        [dict(a=1, b=1), dict(q=0)],
    ],
)
def test_nand_with_single_bit_buses(inputs, outputs):
    assert simulate_component_fn(nand, inputs) == outputs


def test_nand_with_multi_bit_buses():
    inputs = dict(a=0b1100, b=0b1010)
    outputs = dict(q=0b0111)
    actual = simulate_component_fn(nand, inputs, input_bus_sizes=4)
    assert actual == outputs
