from pynand.core import (
    Component,
    Status,
    extract_components_with_simulation,
    simulation_registry,
)


class Simulator:
    def __init__(self, component: Component):
        self.root_component = component
        self.components_to_simulate = extract_components_with_simulation(
            component
        )
        status = Status()
        for i in self.components_to_simulate:
            for j in i.inputs.values():
                status[j] = 0
            for j in i.outputs.values():
                status[j] = 0
        self.status = status

    def step(self):
        for i in self.components_to_simulate:
            simulation_registry[i.name](i, self.status)
        self.status.commit()

    def steps(self, n: int):
        for _ in range(n):
            self.step()
