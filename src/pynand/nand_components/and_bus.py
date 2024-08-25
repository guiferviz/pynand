from pynand.core import Bus, Component, Status, component, simulation
from pynand.nand_components.and_ import and_


@component
def and_bus(a: Bus) -> dict[str, Bus]:
    if len(a) < 2:
        raise ValueError("At least 2 input wires are required")
    q = Bus([a.wires[0]])
    for i in a.wires[1:]:
        q = and_(q, Bus([i])).outputs["q"]
    return {"q": q}


@simulation(and_bus)
def and_bus_simulation(component: Component, status: Status) -> None:
    a = component.inputs["a"]
    q = component.outputs["q"]
    # Create a bitmask with all bits set to 1.
    bitmask = (1 << len(a)) - 1
    status[q.wires[0]] = status[a] == bitmask
