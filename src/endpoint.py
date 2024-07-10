import os
import subprocess

from src.address import pkh_from_address
from src.cli import txid
from src.datums import (bundle_to_value, cost_to_value, get_number_of_bundles,
                        incentive_to_value, to_address)
from src.json_file import write
from src.redeemer import empty
from src.utility import parent_directory_path, sha3_256
from src.value import Value


class Endpoint:

    @staticmethod
    def purchase(sale_info: dict, queue_info: dict, batcher_info: dict, config: dict) -> tuple[dict, dict, dict, bool]:
        """
        Purchase endpoint between the sale and the queue entry.

        Args:
            sale_info (dict): The sale information
            queue_info (dict): The queue entry information
            batcher_info (dict): The batcher information
            config (dict): The batcher configuration

        Returns:
            tuple[dict, dict, dict, bool]: The sale, queue, batcher info, and a success flag.
        """
        # set success flag to false
        purchase_success_flag = False

        # reference UTxOs for the scripts
        data_ref_utxo = config['data_ref_utxo']
        sale_ref_utxo = config['sale_ref_utxo']
        queue_ref_utxo = config['queue_ref_utxo']

        # batcher pkh for signing
        batcher_pkh = pkh_from_address(config['batcher_address'])

        # HARDCODE FEE FOR NOW, NEED WAY TO ESITMATE THESE UNITS BETTER
        fee = 505549
        fee_value = Value({"lovelace": fee})
        sale_execution_units = "(290266843, 618944)"
        queue_execution_units = "(687212169, 2506909)"

        # The parent directory for relative pathing
        parent_dir = parent_directory_path()

        # The protocol file needs to be inside of the tmp directory
        protocol_file_path = os.path.join(parent_dir, "tmp/protocol.json")
        out_file_path = os.path.join(parent_dir, "tmp/tx.draft")

        # redeemer for purchase
        write(empty(0), "tmp/purchase-redeemer.json")
        sale_redeemer_file_path = os.path.join(parent_dir, "tmp/purchase-redeemer.json")
        queue_redeemer_file_path = os.path.join(parent_dir, "tmp/purchase-redeemer.json")

        # datums for purchase
        sale_datum = sale_info['datum']
        write(sale_datum, "tmp/sale-datum.json")
        queue_datum = queue_info['datum']
        write(queue_datum, "tmp/queue-datum.json")
        sale_datum_file_path = os.path.join(parent_dir, "tmp/sale-datum.json")
        queue_datum_file_path = os.path.join(parent_dir, "tmp/queue-datum.json")

        # queue incentive
        incentive_value = incentive_to_value(queue_datum)
        # sale bundle and cost
        bundle_value = bundle_to_value(sale_datum)
        cost_value = cost_to_value(sale_datum)

        # current values
        batcher_value = batcher_info['value']
        sale_value = sale_info['value']
        queue_value = queue_info['value']

        # the number of bundles going to the queue entry
        number_of_bundles = get_number_of_bundles(
            queue_datum, sale_datum, sale_value)
        # must have at least 1 bundle
        if number_of_bundles == 0:
            return sale_info, queue_info, batcher_info, purchase_success_flag

        # total cost being paid
        total_cost_value = number_of_bundles * cost_value
        # total bundle being recieived
        total_bundle_value = number_of_bundles * bundle_value

        # if total cost value not in queue then fail
        if not queue_value.contains(total_cost_value):
            return sale_info, queue_info, batcher_info, purchase_success_flag

        # if incentive not in queue then fail
        if not queue_value.contains(incentive_value):
            return sale_info, queue_info, batcher_info, purchase_success_flag

        # if bundle not in sale then fail
        if not sale_value.contains(total_bundle_value):
            return sale_info, queue_info, batcher_info, purchase_success_flag

        # calculate the outbound values for sale, queue, and batcher
        sale_out_value = sale_value + total_cost_value - total_bundle_value
        queue_out_value = queue_value - total_cost_value + total_bundle_value - incentive_value - fee_value
        batcher_out_value = batcher_value + incentive_value

        func = [
            "cardano-cli", "transaction", "build-raw",
            "--babbage-era",
            "--protocol-params-file", protocol_file_path,
            "--out-file", out_file_path,
            "--tx-in-collateral", batcher_info['txid'],
            "--read-only-tx-in-reference", data_ref_utxo,
            "--tx-in", batcher_info['txid'],
            "--tx-in", sale_info['txid'],
            "--spending-tx-in-reference", sale_ref_utxo,
            "--spending-plutus-script-v2",
            "--spending-reference-tx-in-inline-datum-present",
            "--spending-reference-tx-in-execution-units", sale_execution_units,
            "--spending-reference-tx-in-redeemer-file", sale_redeemer_file_path,
            "--tx-in", queue_info['txid'],
            "--spending-tx-in-reference", queue_ref_utxo,
            "--spending-plutus-script-v2",
            "--spending-reference-tx-in-inline-datum-present",
            "--spending-reference-tx-in-execution-units", queue_execution_units,
            "--spending-reference-tx-in-redeemer-file", queue_redeemer_file_path,
            "--tx-out", batcher_out_value.to_output(config['batcher_address']),
            "--tx-out", sale_out_value.to_output(config['sale_address']),
            "--tx-out-inline-datum-file", sale_datum_file_path,
            "--tx-out", queue_out_value.to_output(config['queue_address']),
            "--tx-out-inline-datum-file", queue_datum_file_path,
            "--required-signer-hash", batcher_pkh,
            "--fee", str(fee)
        ]

        # this saves to out file
        p = subprocess.Popen(func, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        output, errors = p.communicate()

        print('output', output)
        print('errors', errors)

        # check output / errors, if all good assume true here
        purchase_success_flag = True

        intermediate_txid = txid(out_file_path)

        queue_info['txid'] = intermediate_txid + "#2"
        queue_info['value'] = queue_out_value

        sale_info['txid'] = intermediate_txid + "#1"
        sale_info['value'] = sale_out_value

        batcher_info['txid'] = intermediate_txid + "#0"
        batcher_info['value'] = batcher_out_value

        return sale_info, queue_info, batcher_info, purchase_success_flag

    @staticmethod
    def refund(sale_info: dict, queue_info: dict, batcher_info: dict, config: dict) -> tuple[dict, dict, dict, bool]:
        """
        Refund endpoint between the sale and the queue entry.

        Args:
            sale_info (dict): The sale information
            queue_info (dict): The queue entry information
            batcher_info (dict): The batcher information
            config (dict): The batcher configuration

        Returns:
            tuple[dict, dict, dict, bool]: The sale, queue, batcher info, and a success flag.
        """
        refund_success_flag = False

        # reference UTxOs for the scripts
        data_ref_utxo = config['data_ref_utxo']
        queue_ref_utxo = config['queue_ref_utxo']

        # batcher pkh for signing
        batcher_pkh = pkh_from_address(config['batcher_address'])

        fee = 350000
        fee_value = Value({"lovelace": fee})
        execution_units = '(400000000, 1500000)'

        # The parent directory for relative pathing
        parent_dir = parent_directory_path()

        # The protocol file needs to be inside of the tmp directory
        protocol_file_path = os.path.join(parent_dir, "tmp/protocol.json")
        out_file_path = os.path.join(parent_dir, "tmp/tx.draft")

        # queue refund redeemer
        write(empty(1), "tmp/refund-redeemer.json")
        queue_redeemer_file_path = os.path.join(parent_dir, "tmp/refund-redeemer.json")

        # datums for refund
        queue_datum = queue_info['datum']

        # queue entry owner address
        owner_address = to_address(queue_datum, config["network"])

        # queue incentive
        incentive_value = incentive_to_value(queue_datum)

        batcher_value = batcher_info['value']
        queue_value = queue_info['value']

        # if incentive not in queue then fail
        if not queue_value.contains(incentive_value):
            return sale_info, queue_info, batcher_info, refund_success_flag

        # calculate the outbound values for sale, queue, and batcher
        queue_out_value = queue_value - incentive_value - fee_value
        batcher_out_value = batcher_value + incentive_value

        func = [
            'cardano-cli', 'transaction', 'build-raw',
            '--babbage-era',
            '--protocol-params-file', protocol_file_path,
            '--out-file', out_file_path,
            "--tx-in-collateral", batcher_info['txid'],
            '--read-only-tx-in-reference', data_ref_utxo,
            '--read-only-tx-in-reference', sale_info['txid'],
            "--tx-in", batcher_info['txid'],
            '--tx-in', queue_info['txid'],
            '--spending-tx-in-reference', queue_ref_utxo,
            '--spending-plutus-script-v2',
            '--spending-reference-tx-in-inline-datum-present',
            '--spending-reference-tx-in-execution-units', execution_units,
            '--spending-reference-tx-in-redeemer-file', queue_redeemer_file_path,
            "--tx-out", batcher_out_value.to_output(config['batcher_address']),
            '--tx-out', queue_out_value.to_output(owner_address),
            '--required-signer-hash', batcher_pkh,
            '--fee', str(fee)
        ]

        # this saves to out file
        p = subprocess.Popen(func, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        output, errors = p.communicate()

        print('output', output)
        print('errors', errors)

        # do someting
        refund_success_flag = True

        intermediate_txid = txid(out_file_path)

        queue_info['txid'] = intermediate_txid + "#1"
        queue_info['value'] = queue_out_value

        batcher_info['txid'] = intermediate_txid + "#0"
        batcher_info['value'] = batcher_out_value

        return sale_info, queue_info, batcher_info, refund_success_flag

    @staticmethod
    def profit(batcher_infos: list[dict], config: dict) -> tuple[dict, bool]:
        """
        Allows the batcher to auto send out a profit utxo inside of a transaction using extra utxos.

        Args:
            batcher_infos (list[dict]): All the batcher Utxos
            config (dict): The batcher configuration

        Returns:
            tuple[dict, bool]: The UTxO with the batcher token and a success flag
        """
        profit_success_flag = False

        # empty batcher utxos list
        if len(batcher_infos) == 0:
            return None, profit_success_flag

        if len(batcher_infos) == 1:
            return batcher_infos[0], profit_success_flag

        # batcher pkh for signing
        batcher_pkh = pkh_from_address(config['batcher_address'])

        # The parent directory for relative pathing
        parent_dir = parent_directory_path()

        # The protocol file needs to be inside of the tmp directory
        protocol_file_path = os.path.join(parent_dir, "tmp/protocol.json")
        out_file_path = os.path.join(parent_dir, "tmp/tx.draft")

        fee = 350000
        fee_value = Value({"lovelace": fee})

        # send back 5 ada and the batcher token
        batcher_out_value = Value({"lovelace": 5000000, config["batcher_policy"]: {config["batcher_asset"]: 1}})

        # empty value for summing
        total_batcher_value = Value({})

        # there will be many batcher utxos to spend
        tx_in_list = []
        returning_batcher_info = None
        found_batcher_policy = False
        found_batcher_profit = False
        for batcher_info in batcher_infos:
            # assume only one utxo has the batcher policy
            if batcher_info['value'].exists(config["batcher_policy"]):
                # if it doesnt meet the threshold then fail
                if not batcher_info['value'].meets_threshold():
                    return batcher_info, profit_success_flag

                returning_batcher_info = batcher_info.copy()
                found_batcher_policy = True
            else:
                # only do the profit if some other utxo contains at least 5 ada
                if batcher_info['value'].contains(Value({"lovelace": 5000000})):
                    found_batcher_profit = True
            total_batcher_value += batcher_info['value']
            tx_in_list.append("--tx-in")
            tx_in_list.append(batcher_info['txid'])
        # if the policy was never found then return
        if found_batcher_policy is False:
            return returning_batcher_info, profit_success_flag
        # if the policy was found but the profit payment utxo wasnt then return
        if found_batcher_policy is True and found_batcher_profit is False:
            return returning_batcher_info, profit_success_flag
        # here we have the batcher policy and the profit payment utxo

        # the profit is the total value minus the fee and the default batcher value
        batcher_profit_value = total_batcher_value - batcher_out_value - fee_value

        func = [
            'cardano-cli', 'transaction', 'build-raw',
            '--babbage-era',
            '--protocol-params-file', protocol_file_path,
            '--out-file', out_file_path,
        ]
        func += tx_in_list
        func += [
            "--tx-out", batcher_out_value.to_output(config['batcher_address']),
            "--tx-out", batcher_profit_value.to_output(config['profit_address']),
            '--required-signer-hash', batcher_pkh,
            '--fee', str(fee)
        ]
        # this saves to out file
        p = subprocess.Popen(func, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        p.communicate()

        # check output / errors, if all good assume true here
        profit_success_flag = True

        intermediate_txid = txid(out_file_path)
        tag = sha3_256(intermediate_txid + "#0")
        returning_batcher_info['tag'] = tag
        returning_batcher_info['txid'] = intermediate_txid + "#0"
        returning_batcher_info['value'] = batcher_out_value

        return returning_batcher_info, profit_success_flag
