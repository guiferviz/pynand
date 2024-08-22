from wirednand.core import Bus, Component, Status, component, simulation


@component
def nand(a: Bus, b: Bus) -> dict[str, Bus]:
    if len(a) != len(b):
        raise ValueError(f"Bus sizes do not match: {a=} != {b=}.")
    return {"q": Bus(len(a))}


@simulation(nand)
def nand_simulation(component: Component, status: Status):
    a, b = component.inputs["a"], component.inputs["b"]
    q = component.outputs["q"]
    status[q] = ~(status[a] & status[b])
