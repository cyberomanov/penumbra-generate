import csv
import os
import re

from config import NUM_WALLETS, CONFIG_PATH, PCLI_PATH, GENERATED_PATH
from tools.other import run_command

if __name__ == '__main__':
    results = []

    mnemonic_regex = re.compile(r'YOUR PRIVATE SEED PHRASE:\n\n\s*(.*)\n\nSave this in a safe place!', re.DOTALL)
    viewing_key_regex = re.compile(r'full_viewing_key = "(.*)"')
    spend_key_regex = re.compile(r'spend_key = "(.*)"')
    address_regex = re.compile(r'penumbra1[0-9a-zA-Z]+')

    for i in range(NUM_WALLETS):
        if os.path.exists(CONFIG_PATH):
            os.remove(CONFIG_PATH)

        init_output = run_command(f'{PCLI_PATH} init soft-kms generate')
        mnemonic_match = mnemonic_regex.search(init_output)
        if mnemonic_match:
            mnemonic = mnemonic_match.group(1).strip()

        with open(CONFIG_PATH, 'r') as config_file:
            config_content = config_file.read()

        viewing_key_match = viewing_key_regex.search(config_content)
        spend_key_match = spend_key_regex.search(config_content)
        if viewing_key_match and spend_key_match:
            viewing_key = viewing_key_match.group(1).strip()
            spend_key = spend_key_match.group(1).strip()

        address_output = run_command(f'{PCLI_PATH} view address')

        address_match = address_regex.search(address_output)
        if address_match:
            address = address_match.group(0).strip()

        results.append({
            'id': i + 1,
            'mnemonic': mnemonic,
            'address': address,
            'viewing_key': viewing_key,
            'spend_key': spend_key
        })

    csv_columns = ['id', 'mnemonic', 'address', 'viewing_key', 'spend_key']

    if not os.path.exists(os.path.dirname(GENERATED_PATH)):
        os.makedirs(os.path.dirname(GENERATED_PATH))

    with open(GENERATED_PATH, 'a') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=csv_columns)
        writer.writeheader()
        for data in results:
            writer.writerow(data)

    print(f"\nresult path: {GENERATED_PATH}.")
