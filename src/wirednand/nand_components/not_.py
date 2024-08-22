from wirednand.core import Bus, Component, Status, component, simulation

from .nand import nand


@component
def not_(a: Bus) -> dict[str, Bus]:
    return {"q": nand(a, a).outputs["q"]}


@simulation(not_)
def not_simulation(component: Component, status: Status):
    a = component.inputs["a"]
    q = component.outputs["q"]
    status[q] = ~status[a]
