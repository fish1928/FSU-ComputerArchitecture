#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Single-file Python translation of the provided C++ pipeline simulator.
Original sources referenced in chat.
"""
from __future__ import annotations
import sys
import argparse
from dataclasses import dataclass, field
from enum import IntEnum
from typing import List, Optional

# -----------------------------
# Enums & constants
# -----------------------------
class InstructionType(IntEnum):
    NOP = 0
    ADD = 1
    SUB = 2
    MULT = 3
    DIV = 4
    LW = 5
    SW = 6
    BNEZ = 7

instructionNames = ["*", "ADD", "SUB", "MULT", "DIV", "LW", "SW", "BNEZ"]

class Stage(IntEnum):
    FETCH = 0
    DECODE = 1
    EXEC = 2
    MEM = 3
    WB = 4
    NONE = 5

stageNames = ["FETCH", "DECODE", "EXEC", "MEM", "WB", "NONE"]

# -----------------------------
# Register model (kept for parity)
# -----------------------------
@dataclass
class Register:
    dataValue: int = 0
    registerNumber: int = -1
    registerName: str = ""

# 16-register file (unused in current sim logic, present for parity)
registerFile: List[Register] = [Register() for _ in range(16)]

# -----------------------------
# Instruction
# -----------------------------
@dataclass
class Instruction:
    type: InstructionType = InstructionType.NOP
    dest: int = -1
    src1: int = -1
    src2: int = -1
    stage: Stage = Stage.NONE

    @staticmethod
    def from_string(s: str) -> "Instruction":
        tokens = s.split()
        if not tokens:
            return Instruction()
        opcode = tokens[0].upper()
        m = {
            "ADD": InstructionType.ADD,
            "SUB": InstructionType.SUB,
            "MULT": InstructionType.MULT,
            "DIV": InstructionType.DIV,
            "LW": InstructionType.LW,
            "SW": InstructionType.SW,
            "BNEZ": InstructionType.BNEZ,
        }
        itype = m.get(opcode, InstructionType.NOP)
        dest = src1 = src2 = -1
        # Expecting forms like: "ADD r1 r2 r3" (space separated)
        def regnum(tok: str) -> int:
            tok = tok.strip()
            if tok.startswith("r") or tok.startswith("R"):
                tok = tok[1:]
            try:
                return int(tok)
            except ValueError:
                return -1
        if len(tokens) > 1:
            dest = regnum(tokens[1])
        if len(tokens) > 2:
            src1 = regnum(tokens[2])
        if len(tokens) > 3:
            src2 = regnum(tokens[3])
        # SW and BNEZ have 2 sources, no dest
        if itype in (InstructionType.SW, InstructionType.BNEZ):
            src2 = src1
            src1 = dest
            dest = -1
        return Instruction(itype, dest, src1, src2, Stage.NONE)

    def print_str(self) -> str:
        t = self.type
        if t == InstructionType.NOP:
            return f"{instructionNames[t]:<9}"
        elif t in (InstructionType.SW, InstructionType.BNEZ):
            return f"{instructionNames[t]} r{self.src1} r{self.src2}"
        elif t == InstructionType.LW:
            return f"{instructionNames[t]} r{self.dest} r{self.src1}"
        else:
            return f"{instructionNames[t]} r{self.dest} r{self.src1} r{self.src2}"

# -----------------------------
# Application: program & PC
# -----------------------------
@dataclass
class Application:
    instructions: List[Instruction] = field(default_factory=list)
    PC: int = 0

    @staticmethod
    def load_from_file(path: str) -> "Application":
        prog: List[Instruction] = []
        try:
            with open(path, "r", encoding="utf-8") as f:
                for line in f:
                    s = line.strip()
                    if not s:
                        break
                    prog.append(Instruction.from_string(s))
        except OSError as e:
            print(f"Failed to open file {path}: {e}")
            return Application()
        print("Read file completed!!")
        app = Application(prog, 0)
        app.printApplication()
        return app

    def printApplication(self) -> None:
        print("Printing Application:")
        for inst in self.instructions:
            print(inst.print_str())

    def getNextInstruction(self) -> Instruction:
        if self.PC < len(self.instructions):
            inst = self.instructions[self.PC]
            self.PC += 1
            return inst
        return Instruction()  # NOP beyond end

# -----------------------------
# Pipeline stages
# -----------------------------
@dataclass
class PipelineStage:
    stageType: Stage = Stage.NONE
    inst: Optional[Instruction] = field(default_factory=Instruction)

    def clear(self) -> None:
        self.inst = None

    def addInstruction(self, newInst: Optional[Instruction]) -> None:
        self.inst = newInst
        if self.inst is not None:
            self.inst.stage = self.stageType

    def printStage(self) -> str:
        if self.inst is None:
            return "\t"  # empty slot
        return "\t" + self.inst.print_str()

# -----------------------------
# Pipeline
# -----------------------------
class Pipeline:
    def __init__(self, application: Application):
        self.pipeline: List[PipelineStage] = [
            PipelineStage(Stage.FETCH, Instruction()),
            PipelineStage(Stage.DECODE, Instruction()),
            PipelineStage(Stage.EXEC, Instruction()),
            PipelineStage(Stage.MEM, Instruction()),
            PipelineStage(Stage.WB, Instruction()),
        ]
        self.cycleTime: int = 0
        self.forwardingWindowWidth: int = 0
        self.application: Application = application
        self.forwarding: bool = False
        self.printPipeline()  # header row (cycle 0)

    # Data hazard detection between ID (DECODE) and later stages
    def hasDependency(self) -> bool:
        dec = self.pipeline[Stage.DECODE]
        if dec.inst is None or dec.inst.type == InstructionType.NOP:
            return False
        for i in (Stage.EXEC, Stage.MEM, Stage.WB):
            st = self.pipeline[i]
            if st.inst is None:
                continue
            if st.inst.type == InstructionType.NOP:
                continue
            # RAW hazard
            if st.inst.dest != -1 and (st.inst.dest == dec.inst.src1 or st.inst.dest == dec.inst.src2):
                # The C++ provided skeleton leaves forwarding behavior to be filled.
                # We mirror that: if any window width is used, we still stall.
                if self.forwarding and self.forwardingWindowWidth in (1, 2):
                    # TODO: implement actual forwarding windows; keeping parity with original (stall)
                    return True
                # forwarding disabled or unsupported width -> stall
                return True
        return False

    def cycle(self) -> None:
        self.cycleTime += 1
        # WB
        self.pipeline[Stage.WB].clear()
        # MEM -> WB
        self.pipeline[Stage.WB].addInstruction(self.pipeline[Stage.MEM].inst)
        # MEM
        self.pipeline[Stage.MEM].clear()
        # EXEC -> MEM
        self.pipeline[Stage.MEM].addInstruction(self.pipeline[Stage.EXEC].inst)
        # EXEC
        self.pipeline[Stage.EXEC].clear()

        # Hazard check between ID and later stages
        if self.hasDependency():
            # insert bubble into EXEC
            self.pipeline[Stage.EXEC].addInstruction(Instruction())
            return

        # ID -> EXEC
        self.pipeline[Stage.EXEC].addInstruction(self.pipeline[Stage.DECODE].inst)
        # ID
        self.pipeline[Stage.DECODE].clear()
        # IF -> ID
        self.pipeline[Stage.DECODE].addInstruction(self.pipeline[Stage.FETCH].inst)
        # IF
        self.pipeline[Stage.FETCH].clear()
        self.pipeline[Stage.FETCH].addInstruction(self.application.getNextInstruction())

    def done(self) -> bool:
        for st in self.pipeline:
            if st.inst is not None and st.inst.type != InstructionType.NOP:
                return False
        return True

    def printPipeline(self) -> None:
        if self.cycleTime == 0:
            print("Cycle\tIF\t\tID\t\tEXEC\t\tMEM\t\tWB")
        line = [str(self.cycleTime)]
        for st in self.pipeline:
            line.append(st.printStage())
        print("".join(line))

# -----------------------------
# CLI
# -----------------------------

def parse_args(argv: List[str]) -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Pipeline simulator (Python)")
    p.add_argument("-i", metavar="FILE", dest="file", default="instruction.txt")
    p.add_argument("-f", dest="forwarding", action="store_true", help="enable forwarding (logic stubbed as in original)")
    p.add_argument("-w", dest="width", type=int, default=0, help="forwarding window width (0,1,2)")
    # Back-compat: if an extra positional integer is present after options, treat as width
    p.add_argument("width_positional", nargs="?", type=int)
    return p.parse_args(argv)


def main(argv: List[str]) -> int:
    ns = parse_args(argv)
    print(ns)
    fileName = ns.file
    forwarding = ns.forwarding
    width = ns.width
    if ns.width_positional is not None:
        width = ns.width_positional

    if width < 0 or width >= 3:
        print("Error: forwarding window width must be 0, 1, or 2", file=sys.stderr)
        return 2

    print(f"Loading application...{fileName}")
    app = Application.load_from_file(fileName)
    print("Initializing pipeline...")
    pl = Pipeline(app)
    pl.forwarding = forwarding
    pl.forwardingWindowWidth = width

    while True:
        pl.cycle()
        pl.printPipeline()
        if pl.done():
            break
    print(f"Completed in {pl.cycleTime - 1} cycles")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))

