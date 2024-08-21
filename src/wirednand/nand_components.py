from wirednand.core import Bus, component


@component
def Nand(a: Bus, b: Bus) -> dict[str, Bus]:
    if len(a) != len(b):
        raise ValueError(f"Bus {a=} does not match size of bus {b=}.")
    return dict(out=Bus(len(a)))


@component
def Not(a: Bus) -> dict[str, Bus]:
    nand = Nand(a, a)
    return dict(out=nand.outputs["out"])


@component
def And(a: Bus, b: Bus) -> dict[str, Bus]:
    nand = Nand(a, b)
    not_out = Not(nand.outputs["out"])
    return dict(out=not_out.outputs["out"])


@component
def SRFlipFlop(S: Bus, R: Bus) -> dict[str, Bus]:
    nand1 = Nand(S, Bus())
    nand2 = Nand(R, nand1.outputs["out"])
    return dict(Q=nand1.outputs["out"], Q_not=nand2.outputs["out"])
