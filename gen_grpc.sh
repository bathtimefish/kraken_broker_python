#!/bin/sh

python -m grpc_tools.protoc -I./proto --python_out=./src/lib/ --pyi_out=./src/lib/ --grpc_python_out=./src/lib/ ./proto/kraken.proto