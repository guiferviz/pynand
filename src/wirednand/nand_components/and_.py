from wirednand.core import Bus, Component, Status, component, simulation

from .nand import nand
from .not_ import not_


@component
def and_(a: Bus, b: Bus) -> dict[str, Bus]:
    nand1 = nand(a, b)
    not1 = not_(nand1.outputs["q"])
    return {"q": not1.outputs["q"]}


@simulation(and_)
def and_simulation(component: Component, status: Status):
    a, b = component.inputs["a"], component.inputs["b"]
    q = component.outputs["q"]
    status[q] = status[a] & status[b]
