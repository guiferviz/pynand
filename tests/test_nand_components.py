import pytest

from wirednand.core import Bus
from wirednand.nand_components import And, Nand, Not
from wirednand.simulator import Simulator


@pytest.mark.parametrize(
    "a, b, out",
    [
        (False, False, True),
        (False, True, True),
        (True, False, True),
        (True, True, False),
    ],
)
def test_nand(a, b, out):
    a_bus, b_bus = Bus(), Bus()
    component = Nand(a_bus, b_bus)
    simulator = Simulator(component)
    simulator.wires[a_bus.wires[0]] = a
    simulator.wires[b_bus.wires[0]] = b
    simulator.step()
    out_bus = component.outputs["out"]
    assert simulator.wires[out_bus.wires[0]] == out


@pytest.mark.parametrize(
    "a, out",
    [
        (False, True),
        (True, False),
    ],
)
def test_not(a, out):
    a_bus = Bus()
    component = Not(a_bus)
    simulator = Simulator(component)
    simulator.wires[a_bus.wires[0]] = a
    simulator.step()
    out_bus = component.outputs["out"]
    assert simulator.wires[out_bus.wires[0]] == out


@pytest.mark.parametrize(
    "a, b, out",
    [
        (False, False, False),
        (False, True, False),
        (True, False, False),
        (True, True, True),
    ],
)
def test_and(a, b, out):
    a_bus, b_bus = Bus(), Bus()
    component = And(a_bus, b_bus)
    simulator = Simulator(component)
    simulator.wires[a_bus.wires[0]] = a
    simulator.wires[b_bus.wires[0]] = b
    simulator.steps(2)
    out_bus = component.outputs["out"]
    assert simulator.wires[out_bus.wires[0]] == out
