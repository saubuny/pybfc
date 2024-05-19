import subprocess

source = open("examples/hello.bf")
result = open("out.asm", "w")

result.write("format ELF64 executable 3\n\n")
result.write("segment readable executable\n\n")
result.write("entry main\n\n")
result.write("main:\n")

op_br_count = 0
cl_br_count = 0
total_br_count = 0  # Makes the labels unique
for char in source.read():
    match char:
        case ">":
            # Increment data pointer by one to next cell
            result.write("\tcall next\n")
        case "<":
            # Decrement data pointer by one to previous cell
            result.write("\tcall previous\n")
        case "+":
            # Increment byte at data pointer by one
            result.write("\tcall increment\n")
        case "-":
            # Decrement byte at data pointer by one
            result.write("\tcall decrement\n")
        case ".":
            # Output byte at data pointer in ASCII
            result.write("\tcall output\n")
        case ",":
            # Accept one byte of input to data pointer
            result.write("\tcall input\n")
        case "[":
            # Jump to after corresponding bracket if zero
            total_br_count += 1
            op_br_count += 1
            if cl_br_count > 0:
                cl_br_count -= 1
            result.write("\tcall open_bracket\n")
            result.write(f"op_br{op_br_count}_{total_br_count}:\n")
        case "]":
            # Jump to after previous bracket if nonzero
            total_br_count += 1
            cl_br_count = op_br_count
            op_br_count -= 1
            result.write("\tcall closed_bracket\n")
            result.write(f"cl_br{cl_br_count}_{total_br_count}:\n")


# Sys exit
result.write("\txor  rdi, rdi\n")
result.write("\tmov  rax, 60\n")
result.write("\tsyscall\n\n")

# > instruction
result.write("next:\n")
result.write("\tret\n\n")

# < instruction
result.write("previous:\n")
result.write("\tret\n\n")

# + instruction
result.write("increment:\n")
result.write("\tret\n\n")

# - instruction
result.write("decrement:\n")
result.write("\tret\n\n")

# . instruction
result.write("output:\n")
result.write("\tret\n\n")

# , instruction
result.write("input:\n")
result.write("\tret\n\n")

# [ instruction
result.write("open_bracket:\n")
result.write("\tret\n\n")

# ] instruction
result.write("closed_bracket:\n")
result.write("\tret\n\n")

source.close()
result.close()

subprocess.run(["fasm", "out.asm"], stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)
