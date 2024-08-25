import pytest

from pynand.nand_components.and_ import and_
from pynand.helpers import simulate_component_fn


@pytest.mark.parametrize(
    "inputs, outputs",
    [
        [dict(a=0, b=0), dict(q=0)],
        [dict(a=0, b=1), dict(q=0)],
        [dict(a=1, b=0), dict(q=0)],
        [dict(a=1, b=1), dict(q=1)],
    ],
)
def test_and_with_single_bit_buses(inputs, outputs, only_nand):
    assert simulate_component_fn(and_, inputs, steps=2, only_nand=only_nand) == outputs


def test_and_with_multi_bit_buses(only_nand):
    inputs = dict(a=0b1100, b=0b1010)
    outputs = dict(q=0b1000)
    actual = simulate_component_fn(
        and_, inputs, steps=2, input_bus_sizes=4, only_nand=only_nand
    )
    assert actual == outputs
