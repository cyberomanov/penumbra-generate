import csv
import os
import re
import subprocess

NUM_WALLETS = 5
PCLI_PATH = '/root/.cargo/bin/pcli'
CONFIG_PATH = '/root/.local/share/pcli/config.toml'
RESULT_PATH = 'result.csv'


def run_command(command):
    result = subprocess.run(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    return result.stdout


results = []

for i in range(NUM_WALLETS):
    try:
        os.remove(CONFIG_PATH)
    except:
        pass

    mnemonic_regex = re.compile(r'YOUR PRIVATE SEED PHRASE:\n\n\s*(.*)\n\nSave this in a safe place!', re.DOTALL)
    viewing_key_regex = re.compile(r'full_viewing_key = "(.*)"')
    spend_key_regex = re.compile(r'spend_key = "(.*)"')
    address_regex = re.compile(r'penumbra1[0-9a-zA-Z]+')

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


with open(RESULT_PATH, 'a') as csvfile:
    writer = csv.DictWriter(csvfile, fieldnames=csv_columns)
    writer.writeheader()
    for data in results:
        writer.writerow(data)

print(f"\nresult path: {RESULT_PATH}.")
