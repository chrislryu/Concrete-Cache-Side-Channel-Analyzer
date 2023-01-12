import subprocess
import time

start = time.time()

p = subprocess.Popen(['gdb', 'build/X86/gem5.debug'], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

p.stdin.write('\n'.encode())

p.stdin.write('run --debug-break=106471026500 configs/examples/blowfish.py < test/input\n'.encode())

for _ in range(200):
    p.stdin.write('f 2\n'.encode())

    p.stdin.write('p cacheDump()\n'.encode())

    p.stdin.write('p schedRelBreak(1)\n'.encode())

    p.stdin.write('c\n'.encode())

    p.stdin.flush()

p.stdin.flush()

print(p.communicate())

end = time.time()

print(end - start)