import os
import re
import sys
import threading

from config import CONFIG_PATH, PCLI_PATH, LOG_FILE
from tools.other import run_command, run_command_and_log, tail_log_file

if __name__ == '__main__':
    if len(sys.argv) < 1:
        print("Использование: python3 tmux.py <mnemonic>")
        exit(1)

    mnemonic = sys.argv[1]

    if os.path.exists(CONFIG_PATH):
        os.remove(CONFIG_PATH)

    import_command = f'{PCLI_PATH} init soft-kms import-phrase'
    run_command(import_command, input_text=mnemonic)

    balance_output = run_command(f'{PCLI_PATH} view balance')

    balance_penumbra_regex = re.compile(r'# 0\s+(\d+)penumbra')
    balance_penumbra_match = balance_penumbra_regex.search(balance_output)

    has_mpenumbra = 'mpenumbra' in balance_output

    event = threading.Event()

    if balance_penumbra_match:
        balance = int(balance_penumbra_match.group(1))
        if balance >= 100:
            contribute_amount = balance - 1
            print(f"Баланс: {balance} penumbra, вклад в церемонию: {contribute_amount} penumbra")

            ceremony_command = f'{PCLI_PATH} ceremony contribute --phase 2 --bid {contribute_amount}penumbra'
            threading.Thread(target=run_command_and_log, args=(ceremony_command, LOG_FILE, event)).start()
            tail_log_file(LOG_FILE, event)
        else:
            print(f"Баланс недостаточен для церемонии. Текущий баланс: {balance} penumbra")
    elif has_mpenumbra:
        print("Найден mpenumbra, отправка транзакции с 0penumbra")

        ceremony_command = f'{PCLI_PATH} ceremony contribute --phase 2 --bid 0penumbra'
        threading.Thread(target=run_command_and_log, args=(ceremony_command, LOG_FILE, event)).start()
        tail_log_file(LOG_FILE, event)
    else:
        print("Баланс не найден или ошибка при чтении баланса.")
