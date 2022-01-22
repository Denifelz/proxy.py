import os
import subprocess
from logged_groups import logged_group
from solana.publickey import PublicKey

SOLANA_URL = os.environ.get("SOLANA_URL", "http://localhost:8899")
EVM_LOADER_ID = os.environ.get("EVM_LOADER")
neon_cli_timeout = float(os.environ.get("NEON_CLI_TIMEOUT", "0.1"))

NEW_USER_AIRDROP_AMOUNT = int(os.environ.get("NEW_USER_AIRDROP_AMOUNT", "0"))
CONFIRMATION_CHECK_DELAY = float(os.environ.get("NEON_CONFIRMATION_CHECK_DELAY", "0.1"))
CONTINUE_COUNT_FACTOR = int(os.environ.get("CONTINUE_COUNT_FACTOR", "3"))
TIMEOUT_TO_RELOAD_NEON_CONFIG = int(os.environ.get("TIMEOUT_TO_RELOAD_NEON_CONFIG", "3600"))
MINIMAL_GAS_PRICE=int(os.environ.get("MINIMAL_GAS_PRICE", 1))*10**9
EXTRA_GAS = int(os.environ.get("EXTRA_GAS", "0"))
LOG_SENDING_SOLANA_TRANSACTION = os.environ.get("LOG_SENDING_SOLANA_TRANSACTION", "NO") == "YES"
LOG_NEON_CLI_DEBUG = os.environ.get("LOG_NEON_CLI_DEBUG", "NO") == "YES"
WRITE_TRANSACTION_COST_IN_DB = os.environ.get("WRITE_TRANSACTION_COST_IN_DB", "NO") == "YES"
RETRY_ON_BLOCKED = max(int(os.environ.get("RETRY_ON_BLOCKED", "32")), 1)
RETRY_ON_FAIL = int(os.environ.get("RETRY_ON_FAIL", "2"))
RETRY_ON_FAIL_ON_GETTING_CONFIRMED_TRANSACTION = max(int(os.environ.get("RETRY_ON_FAIL_ON_GETTING_CONFIRMED_TRANSACTION", "1000")), 1)


@logged_group("neon.proxy")
class solana_cli:
    def call(self, *args):
        try:
            cmd = ["solana",
                   "--url", SOLANA_URL,
                   ] + list(args)
            self.debug("Calling: " + " ".join(cmd))
            return subprocess.check_output(cmd, universal_newlines=True)
        except subprocess.CalledProcessError as err:
            self.error("ERR: solana error {}".format(err))
            raise


@logged_group("neon.proxy")
class neon_cli:
    def call(self, *args):
        try:
            cmd = ["neon-cli",
                   "--commitment=recent",
                   "--url", SOLANA_URL,
                   "--evm_loader={}".format(EVM_LOADER_ID),
                   ]\
                  + (["-vvv"] if LOG_NEON_CLI_DEBUG else [])\
                  + list(args)
            self.debug("Calling: " + " ".join(cmd))
            return subprocess.check_output(cmd, timeout=neon_cli_timeout, universal_newlines=True)
        except subprocess.CalledProcessError as err:
            self.error("ERR: neon-cli error {}".format(err))
            raise

    def version(self):
        try:
            cmd = ["neon-cli",
                   "--version"]
            self.debug("Calling: " + " ".join(cmd))
            return subprocess.check_output(cmd, timeout=neon_cli_timeout, universal_newlines=True).split()[1]
        except subprocess.CalledProcessError as err:
            self.error("ERR: neon-cli error {}".format(err))
            raise


def read_elf_params(out_dict):
    for param in neon_cli().call("neon-elf-params").splitlines():
        if param.startswith('NEON_') and '=' in param:
            v = param.split('=')
            out_dict[v[0]] = v[1]


ELF_PARAMS = {}
read_elf_params(ELF_PARAMS)
COLLATERAL_POOL_BASE = ELF_PARAMS.get("NEON_POOL_BASE")
ETH_TOKEN_MINT_ID: PublicKey = PublicKey(ELF_PARAMS.get("NEON_TOKEN_MINT"))
