import pytest

from pynand.core import Bus
from pynand.nand_components.and_ import and_
from pynand.simulator import Simulator


@pytest.mark.parametrize(
    "inputs, outputs",
    [
        [dict(a=0, b=0), dict(q=0)],
        [dict(a=0, b=1), dict(q=0)],
        [dict(a=1, b=0), dict(q=0)],
        [dict(a=1, b=1), dict(q=1)],
    ],
)
def test_and(inputs, outputs):
    input_buses = {i: Bus() for i in inputs}
    component = and_(*input_buses.values())
    simulator = Simulator(component)
    for k, v in inputs.items():
        input_bus = input_buses[k]
        simulator.status[input_bus] = v
    simulator.status.commit()
    simulator.steps(2)
    for k, v in outputs.items():
        output_bus = component.outputs[k]
        assert simulator.status[output_bus] == v
