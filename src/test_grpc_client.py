from __future__ import print_function

import logging

import asyncio
import grpc
from lib import kraken_pb2 
from lib import kraken_pb2_grpc


async def send():
    # NOTE(gRPC Python Team): .close() is possible on a channel and should be
    # used in circumstances in which the with statement does not fit the needs
    # of the code.
    port = 5051
    async with grpc.aio.insecure_channel("localhost: %d" % port) as channel:
        stub = kraken_pb2_grpc.KrakenMessageStub(channel)
        response = await stub.Send(kraken_pb2.KrakenMessageRequest(kind="test", provider="test_client", payload="{\"message\":\"Hello World\"}"))
    logging.info("Kraken client received: status_code=%d" % response.status)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(send())