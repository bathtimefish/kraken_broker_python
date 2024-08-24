# Kraken Broker
IoTのためのデータ収集/ブローカー アプリケーション

![logo](./assets/kraken-logo-300.png)

# Introduction
Kraken BrokerはIoT向けのデータブローカーアプリケーションとして開発されました。[Kraken Collector](https://github.com/bathtimefish/kraken_collector)と組み合わせて利用することができます。

Kraken Collector/Brokerを利用するとエッジIoTセンサからHTTPやMQTT経由で送信されるデータをクラウドおよびオンプレミスな環境で受け取り、データの加工、データベースへの格納、ユーザーへの通知等の業務に応じた処理をデータドリブンで実現することができます。

Krakenでできることをよく使われている既存のサービスに例えるならば、AWS IoTとLambdaのシンプルな組み合わせに似ています。Kraken Collector/Brokerはそれをオープンソースでコンパクトに実装できます。
# Why Kraken?
私は長年クライアントのニーズに応じたIoTシステムの開発に携わってきました。その多くはAWS IoTやAzure IoT Hubなどのクラウドサービスが持つ豊富な機能によって開発可能なものでしたが、いくつかのプロジェクトにはそれらクラウドサービスがフィットしないものがありました。

"サブスクリプションコストを最小化したい"、"クラウドサービスが未だに信用できない"、"すべてのリソースを作業現場内で管理したい"など、クラウドサービスが持つスケーラビリティや安定性よりも運用コストや専有性を優先するニーズは特定の業種では未だに多くあります。

そして、そのような業種ほどセンシングテクノロジーやデータ蓄積を導入するメリットが大きい場合がありますが、クラウドサービスを利用した時点でそれらのニーズを叶えることができません。IoTをスタートするためにはセンサー、クラウド、アプリケーションなどに複数のコストと準備期間を費やす必要があり、特にクラウドの仕組みが大掛かりで too muchとなるケースが多くあります。

Krakenはこの問題を解決し、小さくIoTをスタートするために開発されました。Kraken Collector/BrokerはAWS IoTやLamdaを使って実現できるIoTの仕組みをRaspberry Piのような低リソースなコンピュータ上でオンプレミスに小さく動作させることができます。

Krakenの各機能は、私がIoTシステムを開発してきた中で利用してきた機能や体験の中でよく使ったもののみをコンパクトに実装しました。多機能性よりもIoTバックグランドシステムに必要最低限の機能を迅速に構築できることにフォーカスしています。

今までIoTが行き届いていなかった業務に対して、Krakenがそのメリットを届けられることを期待しています。

# Kraken Broker
Kraken Brokerは[Kraken Collector](https://github.com/bathtimefish/kraken_collector)からのデータを受信してデータの加工、データベースへの格納等のカスタム処理を実行するデータブローカーとして機能します。

あなたの業務に必要なデータ処理プロセスは[brokers](https://github.com/bathtimefish/kraken_broker_python/tree/main/src/brokers)の中のbrokerをカスタマイズすることで記述することができる他、全く新しいblockerを新規に作成することもできます。複数のblockerはイベントドリブンで起動し、データの種類に応じた非同期タスクを実行することができます。

Kraken Brokerは現在Python版が提供されていますが、今後その他の言語のバージョンも提供する予定です。

# Getting started
ここでは最初のチュートリアルとして、Kraken Collector/Broker をセットアップして起動し、最初のデータを受信してみます。

## Setup Broker
Brokerをcloneします
```
git clone https://github.com/bathtimefish/kraken_broker_python
kraken_broker_python
```

BlockerをSlackブローカーとして起動するための環境変数を設定します
```
export PYTHONDONTWRITEBYTECODE=1 \
export KRAKENB_DEBUG=1 \
export KRAKENB_GRPC_HOST=[::]:50051 \
export KRAKENB_SLACK_URL=[YOUR_SLACK_WEBHOOK_URL]
```

Blokerを起動します
```
python ./src/main.py
```

以下のようなログが表示されると起動が成功しています
```
INFO:root:gRPC server was started on `[::]:50051`
INFO:root:KRAKEN BROKER is running as debug mode.
```

## Setup Collector
Collectorをビルドします
```
git clone https://github.com/bathtimefish/kraken_collector
cd kraken_collector
cargo build
```

CollectorをWebhookレシーバとして起動するための環境変数を設定します
```
export KRKNC_BROKER_HOST=http://[::1]:50051 \
exoprt KRKNC_WEBHOOK_PATH=webhook \
export KRKNC_WEBHOOK_PORT=3000
```

Collectorを起動します
```
RUST_LOG=error,main=debug cargo run --bin main
```

以下のようなログが表示されると起動が成功しています
```
[2024-01-01T00:00:00Z INFO  main] KRAKEN Collector -- The Highlevel Data Collector -- boot squence start.
[2024-01-01T00:00:00Z DEBUG main::service] starting webhook collector service...
[2024-01-01T00:00:00Z DEBUG main::service] collector service started.
[2024-01-01T00:00:00Z DEBUG main::collectors::webhook] Webhook server was started that is listening on http://0.0.0.0:3000
```

## Send data to Collector
Collectorにデータを送信します
```
curl -X POST -H "Content-Type: application/json" -d '{"id":"101", "name":"env-sensor", "temp":"25.6", "hum":"52.4"}' http://localhost:3000/webhook
```

Slackで以下のようなメッセージが受信できたなら、Kraken Collector/Brokerは正常に動作しています
```
kind=collector, provider=webhook, payload={"id":"101", "name":"env-sensor", "temp":"25.6", "hum":"52.4"}
```

# Broker settings
Brokerの機能は環境変数で設定します。現在以下の環境変数が定義されています

- `KRAKENB_GRPC_HOST`
- `KRAKENB_INFLUXDB_HOST`
- `KRAKENB_INFLUXDB_API_TOKEN`
- `KRAKENB_INFLUXDB_ORG`
- `KRAKENB_INFLUXDB_BUCKET`
- `KRAKENB_REDIS_HOST`
- `KRAKENB_REDIS_PORT`
- `KRAKENB_REDIS_DB`
- `KRAKENB_REIDS_USER`
- `KRAKENB_REDIS_PASSWORD`
- `KRAKENB_MONGODB_HOST`
- `KRAKENB_WEBSOCKET_URL`
- `KRAKENB_SLACK_URL`

## for Collector
### KRAKENB_GRPC_HOST
gRPC ServerのURLを指定します。多くの場合次のような設定で良いはずです。

```
KRAKENB_GRPC_HOST=[::]:50051
```
## InfluxDB
[InfluxDB adapter](https://github.com/bathtimefish/kraken_broker_python/blob/main/src/adapters/influxdb.py)を利用する場合、`KRAKENB_INFLUXDB_HOST` `KRAKENB_INFLUXDB_API_TOKEN` `KRAKENB_INFLUXDB_ORG` `KRAKENB_INFLUXDB_BUCKET` を設定することで利用できます。
### KRAKENB_INFLUXDB_HOST
InfluxDBのホストURLを設定します。
### KRAKENB_INFLUXDB_API_TOKEN
InfluxDBのAPI Tokenを設定します。
### KRAKENB_INFLUXDB_ORG
InfluxDBのOrganizationを設定します。
### KRAKENB_INFLUXDB_BUCKET
InfluxDBのBacketを設定します。
## Redis
[Redis adapter](https://github.com/bathtimefish/kraken_broker_python/blob/main/src/adapters/redis.py)を利用する場合、`KRAKENB_REDIS_HOST` `KRAKENB_REDIS_PORT` `KRAKENB_REDIS_DB` `KRAKENB_REDIS_USER` `KRAKENB_REDIS_PASSWORD` を設定することで利用できます。
### KRAKENB_REDIS_HOST
RedisのホストURLを設定します。
### KRAKENB_REDIS_PORT
Redisのポート番号を設定します。
### KRAKENB_REDIS_DB
RedisのDB番号を設定します。
### KRAKENB_REDIS_USER
Redisのユーザー名を設定します。
### KRAKENB_REDIS_PASSWORD
Redisのパスワードを設定します。
## MongoDB
[MongoDB adapter]()を利用する場合、`KRAKENB_MONGODB_HOST`を設定することで利用できます。
### KRAKENB_MONGODB_HOST
MongoDBのホストURLを設定します。
## Websocket
[Websocket adapter](https://github.com/bathtimefish/kraken_broker_python/blob/main/src/adapters/websocket.py)を利用する場合、`KRAKENB_WEBSOCKET_URL`を設定することで利用できます。Websocket adapterはBrokerにWebsocket client機能を提供します。
### KRAKENB_WEBSOCKET_URL
Websocket ServerのURLを設定します。
## Slack
[Slack adapter](https://github.com/bathtimefish/kraken_broker_python/blob/main/src/adapters/slack.py)を利用する場合、`KRAKENB_SLACK_URL`を設定することで利用できます。Slack adapterはBrokerにSlack incomming webooks client機能を提供します。
### KRAKENB_SLACK_URL
Slack incomming webhooksのURLを設定します。

# Customising Broker