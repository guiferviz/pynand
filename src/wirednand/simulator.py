from wirednand.core import Component, Wire, extract_elemental_components


class Simulator:
    def __init__(self, component: Component):
        self.component = component
        self.elemental_components = extract_elemental_components(component)
        assert all(i.name == "Nand" for i in self.elemental_components)
        wires: dict[Wire, int] = dict()
        for i in self.elemental_components:
            for j in i.inputs["a"].wires:
                wires[j] = False
            for j in i.inputs["b"].wires:
                wires[j] = False
            for j in i.outputs["out"].wires:
                wires[j] = False
        self.wires = wires

    def step(self):
        outputs: dict[Wire, int] = self.wires.copy()
        for i in self.elemental_components:
            a_wires = i.inputs["a"].wires
            b_wires = i.inputs["b"].wires
            out_wires = i.outputs["out"].wires
            for a, b, out in zip(a_wires, b_wires, out_wires):
                a, b = self.wires[a], self.wires[b]
                outputs[out] = not (a and b)
        self.wires = outputs

    def steps(self, n: int):
        for _ in range(n):
            self.step()
