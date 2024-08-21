import pytest

from wirednand.core import (
    Bus,
    component,
    extract_elemental_components,
    is_elemental,
)


@pytest.fixture
def elemental_component():
    @component
    def elemental(a: Bus) -> dict[str, Bus]:
        return dict(out=Bus(len(a)))

    return elemental


@pytest.fixture
def composed_component(elemental_component):
    @component
    def composed(a: Bus) -> dict[str, Bus]:
        e1 = elemental_component(a)
        e2 = elemental_component(e1.outputs["out"])
        return dict(out=e2.outputs["out"])

    return composed


@pytest.fixture
def nested_component(composed_component):
    @component
    def nested(a: Bus) -> dict[str, Bus]:
        c = composed_component(a)
        return dict(out=c.outputs["out"])

    return nested


def test_is_elemental(elemental_component):
    assert is_elemental(elemental_component(Bus()))


def test_is_not_elemental(composed_component):
    assert not is_elemental(composed_component(Bus()))


def test_extract_elemental_components(composed_component):
    component = composed_component(Bus())
    components = extract_elemental_components(component)
    assert len(components) == 2
    assert set(components) == set(component.subcomponents)


def test_extract_elemental_components_nested(nested_component):
    component = nested_component(Bus())
    components = extract_elemental_components(component)
    assert len(components) == 2
    assert set(components) == set(component.subcomponents[0].subcomponents)
