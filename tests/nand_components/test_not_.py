import pytest

from pynand.nand_components.not_ import not_
from pynand.helpers import simulate_component_fn


@pytest.mark.parametrize(
    "inputs, outputs",
    [
        [dict(a=0), dict(q=1)],
        [dict(a=1), dict(q=0)],
    ],
)
def test_not_with_single_bit_bus(inputs, outputs, only_nand):
    assert simulate_component_fn(not_, inputs, only_nand=only_nand) == outputs


def test_nand_with_multi_bit_bus(only_nand):
    inputs = dict(a=0b0101110)
    outputs = dict(q=0b1010001)
    actual = simulate_component_fn(not_, inputs, input_bus_sizes=7, only_nand=only_nand)
    assert actual == outputs
