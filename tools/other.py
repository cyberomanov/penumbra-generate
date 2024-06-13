import os
import subprocess
import time
from collections import deque


def read_mnemonics(path: str = 'data/mnemonic.txt'):
    with open(path) as file:
        not_empty = [line for line in file.read().splitlines() if line and not line.startswith('# ')]
    return not_empty


def run_command(command, input_text=None):
    result = subprocess.run(
        command,
        input=input_text,
        shell=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    return result.stdout


def run_command_and_log(command, log_file, event, input_text=None):
    script_command = f'script -q -c "{command}" {log_file}'
    process = subprocess.Popen(
        script_command,
        shell=True,
        stdin=subprocess.PIPE,
        text=True
    )
    if input_text:
        process.stdin.write(input_text)
        process.stdin.close()
    process.wait()
    event.set()


def tail_log_file(log_file, event):
    event.wait()
    with open(log_file, 'r') as f:
        f.seek(0, os.SEEK_END)
        buffer = deque(maxlen=3)
        while True:
            line = f.readline().strip()
            if line:
                buffer.append(line)
                os.system('clear')
                for buf_line in buffer:
                    print(buf_line)
            else:
                time.sleep(1)
                f.seek(0, os.SEEK_END)
