import subprocess
from collections import defaultdict
import pprint

source = open("examples/hello.bf")
result = open("out.asm", "w")

result.write("format ELF64 executable 3\n")
result.write("segment readable executable\n")
result.write("entry main\n\n")
result.write("main:\n")
result.write("\txor r8, r8\n")

# Prefind matching parenthesis, we could throw an error here
matches: dict[int, dict[str, int]] = defaultdict(dict)
op_br_count = 0
cl_br_count = 0
src = source.read()
for i in range(len(src)):
    match src[i]:
        case "[":
            matches[op_br_count]["["] = i
            op_br_count += 1
        case "]":
            cl_br_count += 1
            matches[cl_br_count]["]"] = i
pp = pprint.PrettyPrinter(depth=4)
pp.pprint(matches)

op_br_count = 0
cl_br_count = 0
# for char in src:
#     match char:
#         case ">":
#             result.write("\tcall next\n")
#         case "<":
#             result.write("\tcall previous\n")
#         case "+":
#             result.write("\tcall increment\n")
#         case "-":
#             result.write("\tcall decrement\n")
#         case ".":
#             result.write("\tcall output\n")
#         case ",":
#             result.write("\tcall input\n")
#         # The jumping instructions need data to be passed
#         case "[":
#             op_br_count += 1
#             result.write("\tlea r9, [arr + r8]\n") 
#             result.write("\tmovzx r10, byte [r9]\n")
#             result.write("\ttest r10, r10\n")
#             result.write(f"\tjz cl_br{matches[op_br_count]["]"]}\n")
#             result.write(f"op_br{matches[op_br_count]["["]}:\n") 
#         case "]":
#             cl_br_count += 1
#             result.write("\tlea r9, [arr + r8]\n") 
#             result.write("\tmovzx r10, byte [r9]\n")
#             result.write("\ttest r10, r10\n")
#             result.write(f"\tjnz op_br{matches[cl_br_count]["["]}\n")
#             result.write(f"cl_br{matches[cl_br_count]["]"]}:\n") 


# Sys exit
result.write("\txor  rdi, rdi\n")
result.write("\tmov  rax, 60\n")
result.write("\tsyscall\n\n")

# > instruction
result.write("next:\n")
result.write("\tadd r8, 4\n")
result.write("\tret\n\n")

# < instruction
result.write("previous:\n")
result.write("\tsub r8, 4\n")
result.write("\tret\n\n")

# + instruction
result.write("increment:\n")
result.write("\tlea r9, [arr + r8]\n")
result.write("\tinc byte [r9]\n")
result.write("\tret\n\n")

# - instruction
result.write("decrement:\n")
result.write("\tlea r9, [arr + r8]\n")
result.write("\tdec byte [r9]\n")
result.write("\tret\n\n")

# . instruction
result.write("output:\n")
result.write("\tlea rdi, [arr + r8]\n")
result.write("\tmov rax, 1\n")
result.write("\tmov rdx, rax\n")
result.write("\tmov rsi, rdi\n")
result.write("\tmov rdi, 1\n")
result.write("\tmov rax, 1\n")
result.write("\tsyscall\n")
result.write("\tret\n\n")

# , instruction
result.write("input:\n")
result.write("\t; TODO\n")
result.write("\tret\n\n")

# Create cells
result.write("segment readable writeable\n")
result.write("arr_size = 30000\n")
result.write("arr db arr_size dup (0)")

source.close()
result.close()

subprocess.run(["fasm", "out.asm"], stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)
# subprocess.run(["fasm", "out.asm"])

subprocess.run("./out")
