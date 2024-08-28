import asyncio
import json

import websockets


async def connect_to_websocket(cbor_hex: str, additional_utxo_set: list[list[dict]]):
    host = "ws://127.0.0.1:1337"

    async with websockets.connect(host) as websocket:
        event = {
            "jsonrpc": "2.0",
            "method": "evaluateTransaction",
            "params": {
                "transaction": {
                    "cbor": cbor_hex
                },
                "additionalUtxo": additional_utxo_set
            },
            "id": None
        }

        await websocket.send(json.dumps(event))
        response = await websocket.recv()
        return json.loads(response)


def ogmios_simulate(cbor_hex: str, additional_utxo_set: list[list[dict]]):
    return asyncio.run(connect_to_websocket(cbor_hex, additional_utxo_set))
