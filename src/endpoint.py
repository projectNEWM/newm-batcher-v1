import copy
import os
import subprocess

from src.address import pkh_from_address
from src.cli import (calculate_min_fee, get_latest_slot_number,
                     query_ref_script_size, query_slot_number, txid)
from src.datums import (bundle_to_value, cost_to_value, get_number_of_bundles,
                        incentive_to_value, to_address)
from src.json_file import write
from src.redeemer import empty, token, tokens
from src.tx_simulate import (calculate_total_fee, convert_execution_unit,
                             get_cbor_from_file, get_index_in_order,
                             purchase_simulation, refund_simulation,
                             sort_lexicographically,
                             transaction_simulation_ogmios)
from src.utility import parent_directory_path, sha3_256
from src.utxo_manager import UTxOManager
from src.value import Value


class Endpoint:

    @staticmethod
    def purchase(utxo: UTxOManager, config: dict, logger=None) -> tuple[UTxOManager, bool]:
        """
        Purchase endpoint between the sale and the queue entry.

        Args:
            utxo (UTxOManager): The utxo manager for all the contracts
            config (dict): The batcher configuration
            logger (optional): The logger if required

        Returns:
            tuple[UTxOManager, bool]: The utxo manager for the contracts and the success boolean
        """
        # usd policy id
        usd_policy_id = "555344"

        # set success flag to false
        purchase_success_flag = False

        # the cardano cli path
        cli_path = config['cli_path']

        # reference UTxOs for the scripts
        data_ref_utxo = utxo.data.txid
        oracle_ref_utxo = utxo.oracle.txid
        sale_ref_utxo = config['sale_ref_utxo']
        queue_ref_utxo = config['queue_ref_utxo']
        vault_ref_utxo = config['vault_ref_utxo']

        # batcher pkh for signing
        batcher_address = config['batcher_address']
        batcher_pkh = pkh_from_address(batcher_address)

        # collat pkh for signing
        collat_address = config['collat_address']
        collat_pkh = pkh_from_address(collat_address)

        # Lets assume this is the upper bound
        fee = 1000000
        fee_value = Value({"lovelace": fee})
        sale_execution_units = "(0, 0)"
        queue_execution_units = "(0, 0)"
        vault_execution_units = "(0, 0)"

        # The parent directory for relative pathing
        parent_dir = parent_directory_path()

        # The protocol file needs to be inside of the tmp directory
        protocol_file_path = os.path.join(parent_dir, "tmp/protocol.json")
        out_file_path = os.path.join(parent_dir, "tmp/tx.draft")

        # redeemer for purchase
        write(empty(0), "tmp/purchase-redeemer.json")
        sale_redeemer_file_path = os.path.join(parent_dir, "tmp/purchase-redeemer.json")
        queue_redeemer_file_path = os.path.join(parent_dir, "tmp/purchase-redeemer.json")
        vault_redeemer_file_path = os.path.join(parent_dir, "tmp/add-tokens-redeemer.json")

        # datums for purchase
        sale_datum = utxo.sale.datum
        sale_is_using_usd = sale_datum['fields'][2]['fields'][0]['bytes'] == usd_policy_id
        write(sale_datum, "tmp/sale-datum.json")
        queue_datum = utxo.queue.datum
        write(queue_datum, "tmp/queue-datum.json")
        vault_datum = utxo.vault.datum
        write(vault_datum, "tmp/vault-datum.json")
        oracle_datum = utxo.oracle.datum
        data_datum = utxo.data.datum

        # datum paths
        sale_datum_file_path = os.path.join(parent_dir, "tmp/sale-datum.json")
        queue_datum_file_path = os.path.join(parent_dir, "tmp/queue-datum.json")
        vault_datum_file_path = os.path.join(parent_dir, "tmp/vault-datum.json")

        # profit vault
        usd_profit_margin = data_datum['fields'][7]['fields'][5]['int']
        newm_usd_price = oracle_datum['fields'][0]['fields'][0]['map'][0]['v']['int']
        profit_payment_pid = data_datum['fields'][7]['fields'][3]['bytes']
        profit_payment_tkn = data_datum['fields'][7]['fields'][4]['bytes']
        profit_payment_amt = usd_profit_margin // newm_usd_price
        profit_value = Value({profit_payment_pid: {profit_payment_tkn: profit_payment_amt}})

        # queue incentive
        incentive_value = incentive_to_value(queue_datum)

        # sale bundle and cost
        bundle_value = bundle_to_value(sale_datum)
        # if we are not using usd equivalent then just use the cost data else do the conversion
        if sale_is_using_usd is False:
            cost_value = cost_to_value(sale_datum)
        else:
            cost_amt = sale_datum['fields'][2]['fields'][2]['int'] // newm_usd_price
            cost_value = Value({profit_payment_pid: {profit_payment_tkn: cost_amt}})

        # current values
        batcher_value = utxo.batcher.value
        sale_value = utxo.sale.value
        queue_value = utxo.queue.value
        vault_value = utxo.vault.value

        # if set to zero then no profit
        if usd_profit_margin == 0:
            write(tokens([]), "tmp/add-tokens-redeemer.json")
            vault_out_value = copy.deepcopy(vault_value)
        else:
            write(tokens([token(profit_payment_pid, profit_payment_tkn, profit_payment_amt)]), "tmp/add-tokens-redeemer.json")
            vault_out_value = copy.deepcopy(vault_value) + copy.deepcopy(profit_value)

        # the number of bundles going to the queue entry
        number_of_bundles = get_number_of_bundles(
            queue_datum, sale_datum, sale_value)
        # must have at least 1 bundle
        if number_of_bundles == 0:
            logger.warning("Number of bundles left is zero") if logger is not None else None
            return utxo, purchase_success_flag

        # total cost being paid
        total_cost_value = number_of_bundles * copy.deepcopy(cost_value)
        # total bundle being recieived
        total_bundle_value = number_of_bundles * copy.deepcopy(bundle_value)

        # if total cost value not in queue then fail
        if queue_value.contains(total_cost_value) is False:
            logger.warning("Queue value does not contain total cost") if logger is not None else None
            return utxo, purchase_success_flag

        # if incentive not in queue then fail
        if queue_value.contains(incentive_value) is False:
            logger.warning("Queue value does not contain incentive") if logger is not None else None
            return utxo, purchase_success_flag

        combined_value = copy.deepcopy(incentive_value) + copy.deepcopy(total_cost_value) + copy.deepcopy(profit_value)
        if queue_value.contains(combined_value) is False:
            logger.warning("Queue value does not contain incentive + cost + profit") if logger is not None else None
            return utxo, purchase_success_flag

        # if bundle not in sale then fail
        if sale_value.contains(total_bundle_value) is False:
            logger.warning("Sale value does not contain total bundle") if logger is not None else None
            return utxo, purchase_success_flag

        # calculate the outbound values for sale, queue, and batcher
        sale_out_value = copy.deepcopy(sale_value) + copy.deepcopy(total_cost_value) - copy.deepcopy(total_bundle_value)

        if sale_out_value.has_negative_entries() is True:
            logger.warning("Sale value has negative values") if logger is not None else None
            return utxo, purchase_success_flag
        queue_out_value = copy.deepcopy(queue_value) - copy.deepcopy(total_cost_value) + copy.deepcopy(total_bundle_value) - copy.deepcopy(incentive_value) - copy.deepcopy(fee_value) - copy.deepcopy(profit_value)

        if queue_out_value.has_negative_entries() is True:
            logger.warning("Queue value has negative values") if logger is not None else None
            return utxo, purchase_success_flag
        batcher_out_value = copy.deepcopy(batcher_value) + copy.deepcopy(incentive_value)

        # timeunits
        delta = 60
        # start and end unix times
        start_time = oracle_datum['fields'][0]['fields'][0]['map'][1]['v']['int']
        end_time = oracle_datum['fields'][0]['fields'][0]['map'][2]['v']['int']
        # start and end slots
        start_slot = query_slot_number(config['socket_path'], start_time, config['network'], cli_path, delta)
        end_slot = query_slot_number(config['socket_path'], end_time, config['network'], cli_path, -delta)
        latest_slot_number = get_latest_slot_number(config['socket_path'], 'tmp/tip.json', config['network'], cli_path)

        # will fail due to time validation logic
        if end_slot - latest_slot_number <= 0:
            logger.warning(f"Purchase Oracle: {abs(end_slot - latest_slot_number) / 60:.2f} minutes late") if logger is not None else None
            return utxo, purchase_success_flag

        # if true then the oracle is required
        is_oracle_required = usd_profit_margin != 0 or sale_is_using_usd is True

        func = [
            cli_path, 'conway', "transaction", "build-raw",
            "--protocol-params-file", protocol_file_path,
            "--out-file", out_file_path,
            "--tx-in-collateral", config['collat_utxo'],
        ]
        if is_oracle_required is True:
            func += [
                "--invalid-before", str(start_slot),
                "--invalid-hereafter", str(end_slot),
                "--read-only-tx-in-reference", oracle_ref_utxo,
            ]
        func += [
            "--read-only-tx-in-reference", data_ref_utxo,
            "--tx-in", utxo.batcher.txid,
            "--tx-in", utxo.sale.txid,
            "--spending-tx-in-reference", sale_ref_utxo,
            "--spending-plutus-script-v3",
            "--spending-reference-tx-in-inline-datum-present",
            "--spending-reference-tx-in-execution-units", sale_execution_units,
            "--spending-reference-tx-in-redeemer-file", sale_redeemer_file_path,
            "--tx-in", utxo.queue.txid,
            "--spending-tx-in-reference", queue_ref_utxo,
            "--spending-plutus-script-v3",
            "--spending-reference-tx-in-inline-datum-present",
            "--spending-reference-tx-in-execution-units", queue_execution_units,
            "--spending-reference-tx-in-redeemer-file", queue_redeemer_file_path,
        ]
        if usd_profit_margin != 0:
            func += [
                "--tx-in", utxo.vault.txid,
                "--spending-tx-in-reference", vault_ref_utxo,
                "--spending-plutus-script-v3",
                "--spending-reference-tx-in-inline-datum-present",
                "--spending-reference-tx-in-execution-units", vault_execution_units,
                "--spending-reference-tx-in-redeemer-file", vault_redeemer_file_path,
                "--tx-out", vault_out_value.to_output(config['vault_address']),
                "--tx-out-inline-datum-file", vault_datum_file_path,
            ]
        func += [
            "--tx-out", sale_out_value.to_output(config['sale_address']),
            "--tx-out-inline-datum-file", sale_datum_file_path,
            "--tx-out", queue_out_value.to_output(config['queue_address']),
            "--tx-out-inline-datum-file", queue_datum_file_path,
            "--tx-out", batcher_out_value.to_output(batcher_address),
            "--required-signer-hash", batcher_pkh,
            "--required-signer-hash", collat_pkh,
            "--fee", str(fee)
        ]

        # this saves to out file
        p = subprocess.Popen(func, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        _, errors = p.communicate()

        logger.debug(f"Purchase Build Errors: {errors}") if logger is not None else None

        if "Command failed" in errors.decode():
            return utxo, purchase_success_flag

        # At this point we should be able to simulate the tx draft
        cborHex = get_cbor_from_file(out_file_path)
        if config['use_ogmios'] is True:
            execution_units = transaction_simulation_ogmios(cborHex, utxo, config)
        else:
            execution_units = purchase_simulation(cborHex, utxo, config)
        if execution_units == [{}]:
            logger.critical(f"Purchase Validation Failed: {utxo.queue.txid}") if logger is not None else None
            return utxo, purchase_success_flag

        # return utxo, purchase_success_flag
        # sort the inputs lexicograhpically so the execution units can be mapped
        ordered_list = sort_lexicographically(utxo.sale.txid, utxo.queue.txid, utxo.vault.txid)

        # At this point we should be able to calculate the total fee
        script_inputs = [
            utxo.batcher.txid,
            config['collat_utxo'],
            utxo.vault.txid,
            vault_ref_utxo,
            utxo.sale.txid,
            sale_ref_utxo,
            utxo.queue.txid,
            queue_ref_utxo,
            oracle_ref_utxo,
            data_ref_utxo,
        ]
        script_sizes = query_ref_script_size(config['socket_path'], config["network"], script_inputs, cli_path)
        tx_fee = calculate_min_fee(out_file_path, protocol_file_path, cli_path, script_sizes)
        total_fee = calculate_total_fee(tx_fee, execution_units)

        fee_value = Value({"lovelace": total_fee})
        sale_execution_units = convert_execution_unit(execution_units[get_index_in_order(ordered_list, utxo.sale.txid)])
        queue_execution_units = convert_execution_unit(execution_units[get_index_in_order(ordered_list, utxo.queue.txid)])
        vault_execution_units = convert_execution_unit(execution_units[get_index_in_order(ordered_list, utxo.vault.txid)])

        if logger is not None:
            logger.debug(f"script sizes: {script_sizes}")
            logger.debug(f"tx fee: {tx_fee}")
            logger.debug(f"total fee: {total_fee}")
            logger.debug(f"sale units: {sale_execution_units}")
            logger.debug(f"queue units: {queue_execution_units}")
            logger.debug(f"vault units: {vault_execution_units}")

        # At this point we should be able to rebuild the tx draft
        queue_out_value = copy.deepcopy(queue_value) - copy.deepcopy(total_cost_value) + copy.deepcopy(total_bundle_value) - copy.deepcopy(incentive_value) - copy.deepcopy(fee_value) - copy.deepcopy(profit_value)

        func = [
            cli_path, 'conway', "transaction", "build-raw",
            "--protocol-params-file", protocol_file_path,
            "--out-file", out_file_path,
            "--tx-in-collateral", config['collat_utxo'],
        ]
        if is_oracle_required is True:
            func += [
                "--invalid-before", str(start_slot),
                "--invalid-hereafter", str(end_slot),
                "--read-only-tx-in-reference", oracle_ref_utxo,
            ]
        func += [
            "--read-only-tx-in-reference", data_ref_utxo,
            "--tx-in", utxo.batcher.txid,
            "--tx-in", utxo.sale.txid,
            "--spending-tx-in-reference", sale_ref_utxo,
            "--spending-plutus-script-v3",
            "--spending-reference-tx-in-inline-datum-present",
            "--spending-reference-tx-in-execution-units", sale_execution_units,
            "--spending-reference-tx-in-redeemer-file", sale_redeemer_file_path,
            "--tx-in", utxo.queue.txid,
            "--spending-tx-in-reference", queue_ref_utxo,
            "--spending-plutus-script-v3",
            "--spending-reference-tx-in-inline-datum-present",
            "--spending-reference-tx-in-execution-units", queue_execution_units,
            "--spending-reference-tx-in-redeemer-file", queue_redeemer_file_path,
        ]
        if usd_profit_margin != 0:
            func += [
                "--tx-in", utxo.vault.txid,
                "--spending-tx-in-reference", vault_ref_utxo,
                "--spending-plutus-script-v3",
                "--spending-reference-tx-in-inline-datum-present",
                "--spending-reference-tx-in-execution-units", vault_execution_units,
                "--spending-reference-tx-in-redeemer-file", vault_redeemer_file_path,
                "--tx-out", vault_out_value.to_output(config['vault_address']),
                "--tx-out-inline-datum-file", vault_datum_file_path,
            ]
        func += [
            "--tx-out", sale_out_value.to_output(config['sale_address']),
            "--tx-out-inline-datum-file", sale_datum_file_path,
            "--tx-out", queue_out_value.to_output(config['queue_address']),
            "--tx-out-inline-datum-file", queue_datum_file_path,
            "--tx-out", batcher_out_value.to_output(batcher_address),
            "--required-signer-hash", batcher_pkh,
            "--required-signer-hash", collat_pkh,
            "--fee", str(total_fee)
        ]

        # this saves to out file
        p = subprocess.Popen(func, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        _, _ = p.communicate()

        # should be good to go
        purchase_success_flag = True

        intermediate_txid = txid(out_file_path, cli_path)

        if usd_profit_margin != 0:
            utxo.vault.txid = intermediate_txid + "#0"
            utxo.vault.value = vault_out_value

        utxo.sale.txid = intermediate_txid + "#0" if usd_profit_margin == 0 else intermediate_txid + "#1"
        utxo.sale.value = sale_out_value

        utxo.queue.txid = intermediate_txid + "#1" if usd_profit_margin == 0 else intermediate_txid + "#2"
        utxo.queue.value = queue_out_value

        utxo.batcher.txid = intermediate_txid + "#2" if usd_profit_margin == 0 else intermediate_txid + "#3"
        utxo.batcher.value = batcher_out_value

        return utxo, purchase_success_flag

    @staticmethod
    def refund(utxo: UTxOManager, config: dict, logger=None) -> tuple[UTxOManager, bool]:
        """
        Refund endpoint between the sale and the queue entry.

        Args:
            utxo (UTxOManager): The utxo manager for all the contracts
            config (dict): The batcher configuration
            logger (optional): The logger if required

        Returns:
            tuple[UTxOManager, bool]: The utxo manager for the contracts and the success boolean
        """
        # usd policy id
        usd_policy_id = "555344"

        # the cardano cli path
        cli_path = config['cli_path']

        #
        refund_success_flag = False

        # reference UTxOs for the scripts
        data_ref_utxo = utxo.data.txid
        oracle_ref_utxo = utxo.oracle.txid
        queue_ref_utxo = config['queue_ref_utxo']

        # batcher pkh for signing
        batcher_address = config['batcher_address']
        batcher_pkh = pkh_from_address(batcher_address)

        # collat pkh for signing
        collat_address = config['collat_address']
        collat_pkh = pkh_from_address(collat_address)

        fee = 1000000
        fee_value = Value({"lovelace": fee})
        queue_execution_units = '(0, 0)'

        # The parent directory for relative pathing
        parent_dir = parent_directory_path()

        # The protocol file needs to be inside of the tmp directory
        protocol_file_path = os.path.join(parent_dir, "tmp/protocol.json")
        out_file_path = os.path.join(parent_dir, "tmp/tx.draft")

        # queue refund redeemer
        write(empty(1), "tmp/refund-redeemer.json")
        queue_redeemer_file_path = os.path.join(parent_dir, "tmp/refund-redeemer.json")

        # datums for refund
        queue_datum = utxo.queue.datum
        oracle_datum = utxo.oracle.datum
        sale_datum = utxo.sale.datum
        data_datum = utxo.data.datum

        # queue entry owner address
        owner_address = to_address(queue_datum, config["network"])

        # queue incentive
        incentive_value = incentive_to_value(queue_datum)

        batcher_value = utxo.batcher.value
        queue_value = utxo.queue.value

        sale_is_using_usd = sale_datum['fields'][2]['fields'][0]['bytes'] == usd_policy_id
        usd_profit_margin = data_datum['fields'][7]['fields'][5]['int']
        # if true then the oracle is required
        is_oracle_required = usd_profit_margin != 0 or sale_is_using_usd is True

        # if incentive not in queue then fail
        if queue_value.contains(incentive_value) is False:
            logger.warning("Queue value does not contain incentive") if logger is not None else None
            return utxo, refund_success_flag

        # calculate the outbound values for sale, queue, and batcher
        queue_out_value = copy.deepcopy(queue_value) - copy.deepcopy(incentive_value) - copy.deepcopy(fee_value)
        if queue_out_value.has_negative_entries() is True:
            logger.warning("Queue value has negative values") if logger is not None else None
            return utxo, refund_success_flag

        batcher_out_value = copy.deepcopy(batcher_value) + copy.deepcopy(incentive_value)

        # time units
        delta = 60
        start_slot = query_slot_number(config['socket_path'], oracle_datum['fields'][0]['fields'][0]['map'][1]['v']['int'], config['network'], cli_path, delta)
        end_slot = query_slot_number(config['socket_path'], oracle_datum['fields'][0]['fields'][0]['map'][2]['v']['int'], config['network'], cli_path, -delta)
        latest_slot_number = get_latest_slot_number(config['socket_path'], 'tmp/tip.json', config['network'], cli_path)

        # will fail due to time validation logic
        if end_slot - latest_slot_number <= 0:
            logger.warning(f"Refund Oracle: {abs(end_slot - latest_slot_number) / 60:.2f} minutes late") if logger is not None else None
            return utxo, refund_success_flag

        func = [
            cli_path, 'conway', 'transaction', 'build-raw',
            '--protocol-params-file', protocol_file_path,
            '--out-file', out_file_path,
            "--tx-in-collateral", config['collat_utxo'],
        ]
        if is_oracle_required is True:
            func += [
                "--invalid-before", str(start_slot),
                "--invalid-hereafter", str(end_slot),
                '--read-only-tx-in-reference', oracle_ref_utxo,
            ]
        func += [
            '--read-only-tx-in-reference', data_ref_utxo,
            '--read-only-tx-in-reference', utxo.sale.txid,
            "--tx-in", utxo.batcher.txid,
            '--tx-in', utxo.queue.txid,
            '--spending-tx-in-reference', queue_ref_utxo,
            '--spending-plutus-script-v3',
            '--spending-reference-tx-in-inline-datum-present',
            '--spending-reference-tx-in-execution-units', queue_execution_units,
            '--spending-reference-tx-in-redeemer-file', queue_redeemer_file_path,
            "--tx-out", batcher_out_value.to_output(batcher_address),
            '--tx-out', queue_out_value.to_output(owner_address),
            '--required-signer-hash', batcher_pkh,
            "--required-signer-hash", collat_pkh,
            '--fee', str(fee)
        ]

        # this saves to out file
        p = subprocess.Popen(func, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        _, errors = p.communicate()

        logger.debug(f"Refund Build Errors: {errors}") if logger is not None else None

        if "Command failed" in errors.decode():
            return utxo, refund_success_flag
        # At this point we should be able to simulate the tx draft
        cborHex = get_cbor_from_file(out_file_path)
        if config['use_ogmios'] is True:
            execution_units = transaction_simulation_ogmios(cborHex, utxo, config)
        else:
            execution_units = refund_simulation(cborHex, utxo, config)
        if execution_units == [{}]:
            logger.critical(f"Refund Validation Failed: {utxo.queue.txid}") if logger is not None else None
            return utxo, refund_success_flag

        # sort the inputs lexicograhpically so the execution units can be mapped
        ordered_list = sort_lexicographically(utxo.queue.txid)

        # At this point we should be able to calculate the total fee
        script_inputs = [
            utxo.batcher.txid,
            config['collat_utxo'],
            oracle_ref_utxo,
            data_ref_utxo,
            utxo.sale.txid,
            utxo.queue.txid,
            queue_ref_utxo,
        ]
        script_sizes = query_ref_script_size(config['socket_path'], config["network"], script_inputs, cli_path)
        tx_fee = calculate_min_fee(out_file_path, protocol_file_path, cli_path, script_sizes)
        total_fee = calculate_total_fee(tx_fee, execution_units)

        fee_value = Value({"lovelace": total_fee})
        queue_execution_units = convert_execution_unit(execution_units[get_index_in_order(ordered_list, utxo.queue.txid)])

        if logger is not None:
            logger.debug(f"script sizes: {script_sizes}")
            logger.debug(f"tx fee: {tx_fee}")
            logger.debug(f"total fee: {total_fee}")
            logger.debug(f"queue units: {queue_execution_units}")

        # At this point we should be able to rebuild the tx draft
        queue_out_value = copy.deepcopy(queue_value) - copy.deepcopy(incentive_value) - copy.deepcopy(fee_value)

        func = [
            cli_path, 'conway', 'transaction', 'build-raw',
            '--protocol-params-file', protocol_file_path,
            '--out-file', out_file_path,
            "--tx-in-collateral", config['collat_utxo'],
        ]
        if is_oracle_required is True:
            func += [
                "--invalid-before", str(start_slot),
                "--invalid-hereafter", str(end_slot),
                '--read-only-tx-in-reference', oracle_ref_utxo,
            ]
        func += [
            '--read-only-tx-in-reference', data_ref_utxo,
            '--read-only-tx-in-reference', utxo.sale.txid,
            "--tx-in", utxo.batcher.txid,
            '--tx-in', utxo.queue.txid,
            '--spending-tx-in-reference', queue_ref_utxo,
            '--spending-plutus-script-v3',
            '--spending-reference-tx-in-inline-datum-present',
            '--spending-reference-tx-in-execution-units', queue_execution_units,
            '--spending-reference-tx-in-redeemer-file', queue_redeemer_file_path,
            "--tx-out", batcher_out_value.to_output(batcher_address),
            '--tx-out', queue_out_value.to_output(owner_address),
            '--required-signer-hash', batcher_pkh,
            "--required-signer-hash", collat_pkh,
            '--fee', str(total_fee)
        ]

        # this saves to out file
        p = subprocess.Popen(func, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        _, _ = p.communicate()

        # everything should be good to go
        refund_success_flag = True

        intermediate_txid = txid(out_file_path, cli_path)

        utxo.batcher.txid = intermediate_txid + "#0"
        utxo.batcher.value = batcher_out_value

        return utxo, refund_success_flag

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

        # the cardano cli path
        cli_path = config['cli_path']

        # empty batcher utxos list
        if len(batcher_infos) == 0:
            return None, profit_success_flag

        if len(batcher_infos) == 1:
            return batcher_infos[0], profit_success_flag

        # batcher pkh for signing
        batcher_address = config['batcher_address']
        batcher_pkh = pkh_from_address(batcher_address)

        # The parent directory for relative pathing
        parent_dir = parent_directory_path()

        # The protocol file needs to be inside of the tmp directory
        protocol_file_path = os.path.join(parent_dir, "tmp/protocol.json")
        out_file_path = os.path.join(parent_dir, "tmp/tx.draft")

        fee = 1000000
        fee_value = Value({"lovelace": fee})

        # send back 5 ada and the batcher token
        batcher_tkn = ""

        # empty value for summing
        total_batcher_value = Value({})

        # there will be many batcher utxos to spend
        tx_in_list = []
        returning_batcher_info = None
        found_batcher_policy = False
        found_batcher_profit = False

        # loop all the inputs
        for batcher_info in batcher_infos:
            # assume only one utxo has the batcher policy
            if batcher_info['value'].exists(config["batcher_policy"]):

                # if it doesnt meet the threshold then just return the utxo with the batcher policy
                if not batcher_info['value'].meets_threshold():
                    return batcher_info, profit_success_flag

                # it does meet the threshold
                returning_batcher_info = copy.deepcopy(batcher_info)
                found_batcher_policy = True
                batcher_tkn = batcher_info['value'].get_token(config["batcher_policy"])

            else:

                # only do the profit if some other utxo contains at least 5 ada
                if batcher_info['value'].contains(Value({"lovelace": 5000000})):
                    found_batcher_profit = True

            # sum all the values together
            total_batcher_value += copy.deepcopy(batcher_info['value'])
            tx_in_list.append("--tx-in")
            tx_in_list.append(batcher_info['txid'])

        # if the policy was never found then return
        if found_batcher_policy is False:
            return returning_batcher_info, profit_success_flag

        # if the policy was found but the profit payment utxo wasnt then return
        if found_batcher_policy is True and found_batcher_profit is False:
            return returning_batcher_info, profit_success_flag

        # the profit is the total value minus the fee and the default batcher value
        batcher_out_value = Value({"lovelace": 5000000, config["batcher_policy"]: {batcher_tkn: 1}})
        batcher_profit_value = copy.deepcopy(total_batcher_value) - copy.deepcopy(batcher_out_value) - copy.deepcopy(fee_value)

        func = [
            cli_path, 'conway', 'transaction', 'build-raw',
            '--protocol-params-file', protocol_file_path,
            '--out-file', out_file_path,
        ]
        func += tx_in_list
        func += [
            "--tx-out", batcher_out_value.to_output(batcher_address),
            "--tx-out", batcher_profit_value.to_output(config['profit_address']),
            '--required-signer-hash', batcher_pkh,
            '--fee', str(fee)
        ]

        # this saves to out file
        p = subprocess.Popen(func, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        p.communicate()

        # lets estimate the fee here
        tx_fee = calculate_min_fee(out_file_path, protocol_file_path, cli_path)
        fee_value = Value({"lovelace": tx_fee})

        batcher_profit_value = copy.deepcopy(total_batcher_value) - copy.deepcopy(batcher_out_value) - copy.deepcopy(fee_value)

        # rebuild the tx with the correct fee
        func = [
            cli_path, 'conway', 'transaction', 'build-raw',
            '--protocol-params-file', protocol_file_path,
            '--out-file', out_file_path,
        ]
        func += tx_in_list
        func += [
            "--tx-out", batcher_out_value.to_output(batcher_address),
            "--tx-out", batcher_profit_value.to_output(config['profit_address']),
            '--required-signer-hash', batcher_pkh,
            '--fee', str(tx_fee)
        ]

        # this saves to out file
        p = subprocess.Popen(func, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        p.communicate()

        # check output / errors, if all good assume true here
        profit_success_flag = True

        intermediate_txid = txid(out_file_path, cli_path)
        tag = sha3_256(intermediate_txid + "#0")
        returning_batcher_info['tag'] = tag
        returning_batcher_info['txid'] = intermediate_txid + "#0"
        returning_batcher_info['value'] = copy.deepcopy(batcher_out_value)

        return returning_batcher_info, profit_success_flag
