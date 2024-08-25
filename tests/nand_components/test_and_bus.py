import pytest

from pynand.nand_components.and_bus import and_bus
from pynand.helpers import simulate_component_fn


def test_and_bus_fails_with_single_bit_bus(only_nand):
    with pytest.raises(ValueError, match="At least 2 input wires are required"):
        simulate_component_fn(and_bus, dict(a=0), only_nand=only_nand)


@pytest.mark.parametrize(
    "bus_size, inputs, outputs, steps",
    [
        [2, dict(a=0b01), dict(q=0), 2],
        [3, dict(a=0b110), dict(q=0), 4],
        [4, dict(a=0b1111), dict(q=1), 6],
    ],
)
def test_and_bus_with_multi_bit_buses(bus_size, inputs, outputs, steps, only_nand):
    actual = simulate_component_fn(
        and_bus, inputs, input_bus_sizes=bus_size, steps=steps, only_nand=only_nand
    )
    assert actual == outputs
