import os
import re
import subprocess

from config import CONFIG_PATH, PCLI_PATH, LOG_FILE
from tools.other import read_mnemonics, run_command


def create_tmux_session(session_name, script_path, pcli_path, config_path, log_file, mnemonic):
    command = f'tmux new-session -d -s {session_name} "python3 {script_path} {pcli_path} {config_path} {log_file} \\"{mnemonic}\\""'
    result = subprocess.run(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if result.returncode != 0:
        print(f"Ошибка при создании сеанса tmux: {result.stderr}")
    else:
        print(f"Сеанс tmux '{session_name}' создан успешно.")


if __name__ == '__main__':
    mnemonics = read_mnemonics(path='data/mnemonic.txt')

    for mnemonic in mnemonics:
        if os.path.exists(CONFIG_PATH):
            os.remove(CONFIG_PATH)

        import_command = f'{PCLI_PATH} init soft-kms import-phrase'
        run_command(import_command, input_text=mnemonic)

        address_output = run_command(f'{PCLI_PATH} view address')
        address_regex = re.compile(r'penumbra1[0-9a-zA-Z]+')
        address_match = address_regex.search(address_output)
        if address_match:
            address = address_match.group(0)
        else:
            print("Ошибка: не удалось получить адрес.")
            exit(1)

        script_path = os.path.abspath('tools/tmux.py')

        create_tmux_session(address, script_path, PCLI_PATH, CONFIG_PATH, LOG_FILE, mnemonic)
