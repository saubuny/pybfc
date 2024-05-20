import subprocess
from collections import defaultdict
import argparse

parser = argparse.ArgumentParser(prog="pybfc", description="A brainfuck compiler")
parser.add_argument("filename")
parser.add_argument("-r", "--run", action="store_true")
parser.add_argument("-a", "--asm", action="store_true")
parser.add_argument("-o", "--optimize", action="store_true")
parser.add_argument("-e", "--errors", action="store_true")
args = parser.parse_args()

source = open(args.filename)
result = open("out.asm", "w")

result.write("format ELF64 executable 3\n")
result.write("segment readable executable\n")
result.write("entry main\n\n")
result.write("main:\n")
result.write("\txor r8, r8\n")

src = source.read()

matches: dict[int, int] = defaultdict(int)
stack: list[int] = []
for i in range(len(src)):
    if src[i] == "[":
        stack.append(i)
    elif src[i] == "]":
        matches[stack.pop()] = i

for i in range(len(src)):
    match src[i]:
        case ">":
            result.write("\tadd r8, 4\n")
        case "<":
            result.write("\tsub r8, 4\n")
        case "+":
            result.write("\tlea r9, [arr + r8]\n")
            result.write("\tinc byte [r9]\n")
        case "-":
            result.write("\tlea r9, [arr + r8]\n")
            result.write("\tdec byte [r9]\n")
        case ".":
            result.write("\tlea rdi, [arr + r8]\n")
            result.write("\tmov rax, 1\n")
            result.write("\tmov rdx, rax\n")
            result.write("\tmov rsi, rdi\n")
            result.write("\tmov rdi, 1\n")
            result.write("\tmov rax, 1\n")
            result.write("\tsyscall\n")
        case ",":
            result.write("\tlea rdi, [arr + r8]\n")
            result.write("\tmov rax, 1\n")
            result.write("\tmov rdx, rax\n")
            result.write("\tmov rsi, rdi\n")
            result.write("\tmov rdi, 1\n")
            result.write("\tmov rax, 0\n")
            result.write("\tsyscall\n")
        case "[":
            result.write("\tlea r9, [arr + r8]\n")
            result.write("\tmovzx r10, byte [r9]\n")
            result.write("\ttest r10, r10\n")
            result.write(f"\tjz cl_br{matches[i]}\n")
            result.write(f"op_br{i}:\n")
        case "]":
            j = None
            for key, value in matches.items():
                if value == i:
                    j = key
            # TODO: Implement proper compiler errors
            assert j is not None, "unmatched parenthesis"
            result.write("\tlea r9, [arr + r8]\n")
            result.write("\tmovzx r10, byte [r9]\n")
            result.write("\ttest r10, r10\n")
            result.write(f"\tjnz op_br{j}\n")
            result.write(f"cl_br{matches[j]}:\n")


# Sys exit
result.write("\txor rdi, rdi\n")
result.write("\tmov rax, 60\n")
result.write("\tsyscall\n\n")

# Create cells
result.write("segment readable writeable\n")
result.write("arr_size = 30000\n")
result.write("arr db arr_size dup (0)")

source.close()
result.close()

print("[INFO] Compiling")
res = subprocess.run(
    ["fasm", "out.asm"], stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT
)
if res.returncode != 0:
    print(f"[ERROR] Error {res.returncode} from fasm")
else:
    if not args.asm:
        subprocess.run(["rm", "out.asm"])
    if args.run:
        print("[INFO] Running")
        subprocess.run("./out")
