from __future__ import annotations

from functools import wraps
from typing import Callable, ParamSpec, TypeVar

P = ParamSpec("P")
R = TypeVar("R")


class ComponentMeta(type):
    def __call__(cls, *args, **kwargs):
        instance = super().__call__(*args, **kwargs)
        if ComponentContext.current_context is not None:
            ComponentContext.current_context.register(instance)
        return instance


class Wire:
    pass


class Bus:
    def __init__(self, n_wires=1):
        if n_wires <= 0:
            raise ValueError("A bus should have a positive number of wires")
        self.wires = [Wire() for _ in range(n_wires)]

    def __len__(self):
        return len(self.wires)

    def __str__(self) -> str:
        return f"Bus[{len(self)}]"


class Component(metaclass=ComponentMeta):
    def __init__(self, name: str, subcomponents: list[Component] | None = None):
        self.name = name
        self.inputs: dict[str, Bus] = {}
        self.outputs: dict[str, Bus] = {}
        self.subcomponents: list[Component] = subcomponents or []

    def add_input(self, name: str, bus: Bus):
        self.inputs[name] = bus

    def add_output(self, name: str, bus: Bus):
        self.outputs[name] = bus

    def add_subcomponent(self, subcomponent: Component):
        self.subcomponents.append(subcomponent)

    def __str__(self, level=0) -> str:
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

    def __init__(self):
        self.subcomponents = []

    def __enter__(self):
        self.previous_context = ComponentContext.current_context
        ComponentContext.current_context = self
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        ComponentContext.current_context = self.previous_context

    def register(self, component: Component):
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


def is_elemental(component: Component) -> bool:
    return len(component.subcomponents) == 0


def extract_elemental_components(component: Component) -> list[Component]:
    elemental_components = []
    stack = [component]

    while stack:
        i = stack.pop()
        if is_elemental(i):
            elemental_components.append(i)
        stack.extend(i.subcomponents)

    return elemental_components
