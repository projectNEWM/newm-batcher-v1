import os

from src.address import pkh_from_address
from src.json_file import write
from src.redeemer import empty
from src.utility import create_folder_if_not_exists, parent_directory_path
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
        fee_value = Value({"lovelace": 505549})
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
        return sale_info, queue_info, batcher_info, refund_success_flag
