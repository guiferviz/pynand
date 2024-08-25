from typing import Callable

from pynand.core import Bus, Component, Simulator, simulation_registry


def simulate_component_fn(
    component_fn: Callable[..., Component],
    inputs: dict[str, int],
    input_bus_sizes: dict[str, int] | int = 1,
    steps: int = 1,
    only_nand: bool = False,
) -> dict[str, int]:
    # Create input buses with specified sizes.
    if isinstance(input_bus_sizes, int):
        input_bus_sizes = {i: input_bus_sizes for i in inputs}
    input_buses = {name: Bus(size) for name, size in input_bus_sizes.items()}
    # Instantiate the component with the input buses.
    component = component_fn(*input_buses.values())
    # Create the simulator with the component.
    if only_nand:
        simulator = Simulator(component, {"nand": simulation_registry["nand"]})
    else:
        simulator = Simulator(component)
    simulator.set_input_values(inputs)
    simulator.steps(steps)
    return simulator.get_output_values()
