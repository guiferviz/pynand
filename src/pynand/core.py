from __future__ import annotations

from functools import wraps
from types import TracebackType
from typing import Callable, ParamSpec, TypeVar, overload

T = TypeVar("T", bound="ComponentMeta")
P = ParamSpec("P")
R = TypeVar("R")


class ComponentMeta(type):
    def __call__(cls: type[T], *args, **kwargs) -> T:
        instance = super().__call__(*args, **kwargs)
        if ComponentContext.current_context is not None:
            ComponentContext.current_context.register(instance)
        return instance


class Wire:
    pass


class Bus:
    def __init__(self, wires: int | list[Wire] = 1) -> None:
        if isinstance(wires, int):
            if wires <= 0:
                raise ValueError("A bus should have a positive number of wires")
            self.wires = [Wire() for _ in range(wires)]
        else:
            self.wires = wires

    def __len__(self) -> int:
        return len(self.wires)

    def __str__(self) -> str:
        return f"Bus[{len(self)}]"


class Component(metaclass=ComponentMeta):
    def __init__(
        self,
        name: str,
        subcomponents: list[Component] | None = None,
    ) -> None:
        self.name = name
        self.inputs: dict[str, Bus] = {}
        self.outputs: dict[str, Bus] = {}
        self.subcomponents: list[Component] = subcomponents or []

    def add_input(self, name: str, bus: Bus) -> None:
        self.inputs[name] = bus

    def add_output(self, name: str, bus: Bus) -> None:
        self.outputs[name] = bus

    def add_subcomponent(self, subcomponent: Component) -> None:
        self.subcomponents.append(subcomponent)

    def __str__(self, level: int = 0) -> str:
        indent = "  " * level
        inputs_str = ", ".join(self.inputs.keys())
        outputs_str = ", ".join(self.outputs.keys())
        subcomponents_str = "\n".join(
            sub.__str__(level + 1) for sub in self.subcomponents
        )
        return (
            f"{indent}Component(Name: {self.name}, Inputs: [{inputs_str}], Outputs: [{outputs_str}])"
            + (f",\n{subcomponents_str}" if self.subcomponents else "")
        )


class ComponentContext:
    current_context: ComponentContext | None = None

    def __init__(self) -> None:
        self.subcomponents = []

    def __enter__(self) -> ComponentContext:
        self.previous_context = ComponentContext.current_context
        ComponentContext.current_context = self
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> bool | None:
        ComponentContext.current_context = self.previous_context

    def register(self, component: Component) -> None:
        self.subcomponents.append(component)


def component(fn: Callable[P, dict[str, Bus]]) -> Callable[P, Component]:
    @wraps(fn)
    def wrapper(*args, **kwargs) -> Component:
        component = Component(name=fn.__name__)

        for name, wire in zip(fn.__code__.co_varnames, args):
            component.add_input(name, wire)

        with ComponentContext() as context:
            outputs = fn(*args, **kwargs)

        for subcomponent in context.subcomponents:
            component.add_subcomponent(subcomponent)

        for name, bus in outputs.items():
            component.add_output(name, bus)

        return component

    return wrapper


class Status:
    def __init__(self) -> None:
        self.current_values: dict[Wire, bool] = {}
        self.next_values: dict[Wire, bool] = {}

    @overload
    def __getitem__(self, item: Wire) -> bool: ...

    @overload
    def __getitem__(self, item: Bus) -> int: ...

    def __getitem__(self, item: Wire | Bus) -> bool | int:
        if isinstance(item, Wire):
            return self.current_values.get(item, False)
        result = 0
        for i, wire in enumerate(item.wires):
            if self.current_values[wire]:
                result |= 1 << i
        return result

    @overload
    def __setitem__(self, key: Wire, value: bool) -> None: ...

    @overload
    def __setitem__(self, key: Bus, value: int) -> None: ...

    def __setitem__(self, key: Wire | Bus, value: bool | int) -> None:
        if isinstance(key, Wire):
            if not isinstance(value, bool):
                raise TypeError(
                    "Value must be a bool when setting wire values.",
                )
            self.next_values[key] = value
        else:
            if isinstance(value, bool):
                raise TypeError(
                    "Value must be an int when settings bus values.",
                )
            for i, wire in enumerate(key.wires):
                self.next_values[wire] = ((1 << i) & value) > 0

    def commit(self) -> None:
        self.current_values.update(self.next_values)
        self.next_values.clear()


SimulationFunction = Callable[[Component, Status], None]


simulation_registry: dict[str, SimulationFunction] = {}


def simulation(
    fn: Callable,
) -> Callable[[SimulationFunction], SimulationFunction]:
    def decorator(sim_func: SimulationFunction) -> SimulationFunction:
        simulation_registry[fn.__name__] = sim_func
        return sim_func

    return decorator


def has_simulation(
    component: Component, simulation_functions: dict[str, SimulationFunction]
) -> bool:
    return component.name in simulation_functions


def extract_components_with_simulation(
    component: Component, simulation_functions: dict[str, SimulationFunction]
) -> list[Component]:
    extracted_components = []
    stack = [component]

    while stack:
        i = stack.pop()
        if has_simulation(i, simulation_functions):
            extracted_components.append(i)
        else:
            stack.extend(i.subcomponents)

    return extracted_components


class Simulator:
    def __init__(
        self,
        component: Component,
        simulation_functions: dict[
            str, SimulationFunction
        ] = simulation_registry,
    ) -> None:
        self.component = component
        self.components_to_simulate = extract_components_with_simulation(
            component, simulation_functions
        )
        if not self.components_to_simulate:
            raise ValueError(
                "At least one component with simulation function is needed"
            )
        status = Status()
        for i in self.components_to_simulate:
            for j in i.inputs.values():
                status[j] = 0
            for j in i.outputs.values():
                status[j] = 0
        self.status = status

    def step(self) -> None:
        for i in self.components_to_simulate:
            simulation_registry[i.name](i, self.status)
        self.status.commit()

    def steps(self, n: int) -> None:
        for _ in range(n):
            self.step()

    def set_input_values(self, inputs: dict[str, int]) -> None:
        for k, v in inputs.items():
            input_bus = self.component.inputs[k]
            self.status[input_bus] = v
        self.status.commit()

    def get_output_values(self) -> dict[str, int]:
        return {k: self.status[v] for k, v in self.component.outputs.items()}
