import pytest

from wirednand.core import (
    And,
    Bus,
    Clock,
    Nand,
    NandBus,
    Not,
    Or,
    Simulation,
    SRLatch,
    Wire,
    Xor,
    find_nands,
)


def test_find_nands():
    a = Wire()
    nand0 = Nand(a, a)
    nand1 = Nand(nand0.out, nand0.out)
    nands = find_nands([nand1])
    assert len(nands) == 2


@pytest.mark.parametrize(
    "a, b, out",
    [
        [0, 0, 1],
        [0, 1, 1],
        [1, 0, 1],
        [1, 1, 0],
    ],
)
def test_nand(a, b, out):
    a = Wire(default=bool(a))
    b = Wire(default=bool(b))
    nand = Nand(a, b)
    s = Simulation(nand).step()
    assert s[nand.out] == bool(out)


@pytest.mark.parametrize(
    "a, b, out",
    [
        [0, 0, 0],
        [0, 1, 0],
        [1, 0, 0],
        [1, 1, 1],
    ],
)
def test_and(a, b, out):
    a = Wire(default=bool(a))
    b = Wire(default=bool(b))
    and_ = And(a, b)
    s = Simulation(and_).steps(2)
    assert s[and_.out] == bool(out)


@pytest.mark.parametrize(
    "a, b, out",
    [
        [0, 0, 0],
        [0, 1, 1],
        [1, 0, 1],
        [1, 1, 1],
    ],
)
def test_or(a, b, out):
    a = Wire(default=bool(a))
    b = Wire(default=bool(b))
    or_ = Or(a, b)
    s = Simulation(or_).steps(2)
    assert s[or_.out] == bool(out)


@pytest.mark.parametrize(
    "a, b, out",
    [
        [0, 0, 0],
        [0, 1, 1],
        [1, 0, 1],
        [1, 1, 0],
    ],
)
def test_xor(a, b, out):
    a = Wire(default=bool(a))
    b = Wire(default=bool(b))
    xor_ = Xor(a, b)
    s = Simulation(xor_).steps(3)
    assert s[xor_.out] == bool(out)


@pytest.mark.parametrize(
    "a, out",
    [
        [0, 1],
        [1, 0],
    ],
)
def test_not(a, out):
    a = Wire(default=bool(a))
    not_ = Not(a)
    s = Simulation(not_).step()
    assert s[not_.out] == bool(out)


def test_clock():
    clock = Clock()
    s = Simulation(clock).step()
    for _ in range(2):
        assert s[clock.out]
        s.step()
        assert not s[clock.out]
        s.step()


@pytest.mark.parametrize(
    "s, r, q, q_, steps",
    [
        # s=0, r=0, invalid state!
        [0, 0, 0, 0, 0],
        [0, 0, 1, 1, 1],
        [0, 0, 1, 1, 2],
        # s=0, r=1
        [0, 1, 0, 0, 0],
        [0, 1, 1, 1, 1],
        [0, 1, 1, 0, 2],
        [0, 1, 1, 0, 3],
        # s=1, r=0
        [1, 0, 0, 0, 0],
        [1, 0, 1, 1, 1],
        [1, 0, 0, 1, 2],
        [1, 0, 0, 1, 3],
        # s=1, r=1, Invalid combination!
        # In real life, because electricity does not flow through both gates in
        # at the same time, it would eventually stabilise. In the simulator the
        # outputs would keep alternating at each step.
        [1, 1, 0, 0, 0],
        [1, 1, 1, 1, 1],
        [1, 1, 0, 0, 2],
        [1, 1, 1, 1, 3],
    ],
)
def test_sr_latch_step_by_step(s, r, q, q_, steps):
    s = Wire(default=bool(s))
    r = Wire(default=bool(r))
    sr_latch = SRLatch(s, r)
    sim = Simulation(sr_latch)
    sim.steps(steps)
    assert (sim[sr_latch.q], sim[sr_latch.q_]) == (bool(q), bool(q_))


def test_sr_latch_remembers_something():
    s = Wire()
    r = Wire()
    sr_latch = SRLatch(s, r)
    sim = Simulation(sr_latch)
    sim[s], sim[r] = False, True
    sim.steps(2)
    assert (sim[sr_latch.q], sim[sr_latch.q_]) == (True, False)
    sim[s], sim[r] = True, True
    sim.step()
    assert (sim[sr_latch.q], sim[sr_latch.q_]) == (True, False)
    sim[s], sim[r] = True, False
    sim.steps(2)
    assert (sim[sr_latch.q], sim[sr_latch.q_]) == (False, True)
    sim[s], sim[r] = True, True
    sim.step()
    assert (sim[sr_latch.q], sim[sr_latch.q_]) == (False, True)
    sim[s], sim[r] = False, True
    sim.steps(2)
    assert (sim[sr_latch.q], sim[sr_latch.q_]) == (True, False)


def test_flip_flop():
    pass


def test_and_simulation():
    a = Wire()
    b = Wire()
    and_ = And(a, b)
    s = Simulation([and_], {a: False, b: True})
    assert not s[and_.out]
    s.step()
    assert s[and_.out]
    s.step()
    # Avoid using `not s[and_.out]` as it is True when `s[and_.out]` is None.
    assert not s[and_.out]
    s = Simulation([and_], {a: True, b: True})
    assert not s[and_.out]
    s.step()
    assert s[and_.out]
    s.step()
    assert s[and_.out]


def test_nand_bus_simulation():
    a = Bus(2)
    b = Bus(2)
    nand = NandBus(a, b)
    s = Simulation([nand], {a[0]: False, a[1]: True, b[0]: True, b[1]: True})
    assert not s[nand.out[0]]
    assert not s[nand.out[1]]
    s.step()
    assert s[nand.out[0]]
    assert not s[nand.out[1]]
