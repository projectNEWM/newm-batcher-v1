

from src.datums import get_incentive_amount, queue_validity
from src.db_manager import DatabaseManager


class Sorting:
    """Handle all queue logic."""

    @staticmethod
    def fifo_sort(input_dict: dict) -> dict:
        """
        This function will do a fifo sort on the sale-order dictionary.
           Hash   Timestamp  TxIdx Incentive
        ( "acab", 123456789, 0,    1234 )

        Args:
            input_dict (dict): The sales are the keys and the orders are a list.

        Returns:
            dict: A fifo ordered sale-order dictionary.
        """
        # init the new sorted dict
        sorted_dict = {}

        # each sale needs to be ordered
        for key, value_list in input_dict.items():
            # sort by incentive amt then timestamp then by the tx_idx
            sorted_list = sorted(value_list, key=lambda x: (x[4], -x[3], x[1], x[2]))
            sorted_dict[key] = sorted_list

        return sorted_dict

    @staticmethod
    def fifo(db: DatabaseManager) -> dict:
        # query all the sale pointer tokens of valid sales
        sales = db.read_all_sale_tkns()

        # initialize the sale to order dictionary
        sale_to_order_dict = {}

        # there has to be at least one sale
        if len(sales) == 0:
            return {}

        # loop sales and create a dictionary of orders per sale
        for sale in sales:

            # there will be a list of orders for some sale
            sale_to_order_dict[sale] = []

            orders = db.read_all_queue(sale)

            # if there are no orders for this sale continue to the next one
            if len(orders) == 0:
                continue

            # loop the orders for some sale
            for order in orders:
                # order hash is the unique tag
                order_hash = order[0]
                # all the order data for this queue entry
                order_data = order[1]

                # try to validate the datum else continue to the next order
                if queue_validity(order_data['datum']) is False:
                    continue

                # get the incentive amount
                incentive_amt, priority = get_incentive_amount(order_data['datum'])
                # Sort by incentive amount (descending), then by timestamp and tx_idx
                #
                # (order hash, timestamp, tx idx, incentive)
                sale_to_order_dict[sale].append((order_hash, order_data['timestamp'], order_data['tx_idx'], incentive_amt, priority))

        # fifo the queue list per each sale
        return Sorting.fifo_sort(sale_to_order_dict)
