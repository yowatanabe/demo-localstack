# LocalStack入門

## はじめに

今回は完全に趣味のトピックです。

以前からLocalStackを使ってみたいと思っていたので週末を利用して試してみました。





## LocalStack のインストール

LocalStack をインストールします。

MacOSはHomebrewからインストールします。

```bash
brew install localstack/tap/localstack-cli
```

次に **awslocal** と **tflocal** をインストールします。

awslocal と tflocal は、どちらも LocalStack 向けのラッパーコマンドで、AWSの操作をローカル環境で手軽に再現するために使います。

awslocal は AWS CLI を LocalStack のエンドポイントへ自動的に接続して実行し、tflocal は Terraform を LocalStack と連携させてプロバイダの接続先や各種エンドポイント設定を自動化します。これにより、毎回 --endpoint-url や細かなプロバイダ設定を書かずに、AWSリソースの作成・更新・検証をローカルで素早く試せます。


```bash
pip install awscli-local
pip install terraform-local
```

その他の環境は公式のインストールガイドを参照してください。

https://docs.localstack.cloud/aws/getting-started/installation/

https://docs.localstack.cloud/aws/integrations/aws-native-tools/aws-cli/#localstack-aws-cli-awslocal

https://docs.localstack.cloud/aws/integrations/infrastructure-as-code/terraform/#tflocal-wrapper-script








## 作成するアプリケーションの概要

Semgrepのスキャン結果をS3バケットにファイルをアップロードしたらDefectDojoにスキャン結果を送信するサーバーレスアプリケーションを想定します。

⭐️drawioの画像


アプリケーションのディレクトリ構成は以下のとおりです。

```none
.
├── build/                            # Lambda デプロイパッケージ（Git 管理外）
├── envs/                             # 環境別設定
│   ├── local/                        # LocalStack 開発環境
│   │   ├── main.tf                   # メインリソース定義（モジュール呼び出し）
│   │   ├── provider.tf               # LocalStack 用プロバイダー設定
│   │   ├── terraform.tfvars          # 環境固有変数（Git 管理外）
│   │   ├── terraform.tfvars.template # 変数テンプレート
│   │   └── variables.tf
│   ├── prd/                          # 本番環境（未使用）
│   └── stg/                          # ステージング環境（未使用）
├── modules/                          # 再利用可能な Terraform モジュール
│   ├── lambda/                       # Lambda 関数モジュール
│   │   ├── main.tf
│   │   ├── outputs.tf
│   │   └── variables.tf
│   └── s3/                           # S3 バケットモジュール
│       ├── main.tf
│       ├── outputs.tf
│       └── variables.tf
├── src/                              # アプリケーションコード
│   ├── handler.py
│   └── requirements.txt
├── Makefile                          # ビルド・デプロイ自動化
└── README.md
```

アプリケーションコードは以下を参考にしました。

https://semgrep.dev/docs/kb/integrations/defect-dojo-integration



完全なコードはこちらに公開しています。

https://github.com/yowatanabe/demo-localstack












## LocalStack を起動

```bash
# 起動
localstack start -d

# 確認
localstack status
```

実行例

```bash
$ localstack start -d

     __                     _______ __             __
    / /   ____  _________ _/ / ___// /_____ ______/ /__
   / /   / __ \/ ___/ __ `/ /\__ \/ __/ __ `/ ___/ //_/
  / /___/ /_/ / /__/ /_/ / /___/ / /_/ /_/ / /__/ ,<
 /_____/\____/\___/\__,_/_//____/\__/\__,_/\___/_/|_|

- LocalStack CLI: 4.9.1
- Profile: default
- App: https://app.localstack.cloud

[09:44:20] starting LocalStack in Docker mode 🐳                                                                                                                                                                               localstack.py:532
           preparing environment                                                                                                                                                                                               bootstrap.py:1315
           configuring container                                                                                                                                                                                               bootstrap.py:1324
           starting container                                                                                                                                                                                                  bootstrap.py:1334
[09:44:22] detaching                                                                                                                                                                                                           bootstrap.py:1338
$ localstack status
┌─────────────────┬───────────────────────────────────────────────────────┐
│ Runtime version │ 4.9.1                                                 │
│ Docker image    │ tag: latest, id: 8599a52616ea, 📆 2025-10-03T11:34:50 │
│ Runtime status  │ ✔ running (name: "localstack-main", IP: 172.17.0.2)   │
└─────────────────┴───────────────────────────────────────────────────────┘
$
```





## LocalStackにデプロイ

以下の手順で LocalStack 環境にデプロイします（**`make build` / `make apply` は Makefile で定義しています**）。

```bash
# ソースコードと依存関係をビルド
make build

# Terraformを使用してリソースを作成
make apply
```

`make build`コマンドは、Lambda関数のソースコードと必要なPythonパッケージを`build/`ディレクトリにパッケージ化します。具体的には、`src/handler.py`をコピーし、`src/requirements.txt`に記載された依存関係をインストールしてデプロイ可能な形式にします。

`make apply`コマンドは、Terraformを使用してLocalStack環境にLambda関数やその他のAWSリソースを作成します。内部的には`cd envs/local && tflocal init && tflocal apply`を実行し、Terraformを初期化してからリソースをデプロイします。









## リソースを確認

デプロイが完了したら、`awslocal`コマンドを使用してLocalStack環境に作成されたリソースを確認できます。以下のコマンドで、主要なリソースである S3バケットとLambda関数の設定を確認します。

```bash
$ awslocal s3 ls
2025-10-05 10:12:45 demo-local-bucket
```

```bash
$ awslocal lambda get-function-configuration --function-name demo-local-lambda
{
    "FunctionName": "demo-local-lambda",
    "FunctionArn": "arn:aws:lambda:ap-northeast-1:000000000000:function:demo-local-lambda",
    "Runtime": "python3.13",
    "Role": "arn:aws:iam::000000000000:role/demo-local-lambda-role",
    "Handler": "handler.lambda_handler",
    "CodeSize": 1705467,
    "Description": "",
    "Timeout": 60,
    "MemorySize": 256,
    "LastModified": "2025-10-05T01:12:45.628572+0000",
    "CodeSha256": "g+XTqfCpycJcG6voVPySfd026peimvqw3we7uN0g7Vk=",
    "Version": "$LATEST",
    "Environment": {
        "Variables": {
            "DOJO_TOKEN": "c8735e820ad74b12c137008dcd509b4fd53ebf1c",
            "DOJO_URL": "http://host.docker.internal:8080",
            "PRODUCT_NAME": "demo-app",
            "ENGAGEMENT_NAME": "demo-engagement",
            "ENVIRONMENT": "local"
        }
    },
    "TracingConfig": {
        "Mode": "PassThrough"
    },
    "RevisionId": "dda8aa9a-8e8e-4806-8b4d-619151c4a5bc",
    "State": "Active",
    "LastUpdateStatus": "Successful",
    "PackageType": "Zip",
    "Architectures": [
        "arm64"
    ],
    "EphemeralStorage": {
        "Size": 512
    },
    "SnapStart": {
        "ApplyOn": "None",
        "OptimizationStatus": "Off"
    },
    "RuntimeVersionConfig": {
        "RuntimeVersionArn": "arn:aws:lambda:ap-northeast-1::runtime:8eeff65f6809a3ce81507fe733fe09b835899b99481ba22fd75b5a7338290ec1"
    },
    "LoggingConfig": {
        "LogFormat": "Text",
        "LogGroup": "/aws/lambda/demo-local-lambda"
    }
}
```

これらのコマンドにより、S3バケット（`demo-local-bucket`）、Lambda関数（`demo-local-lambda`）が正常に作成されていることを確認できます。Lambda関数の環境変数にはDefectDojoとの連携に必要な設定が含まれています。






























## 動作確認


### Semgrep のスキャンファイルを生成

任意のフォルダで以下を実行して、Semgrepを使用してOWASP Juice Shopのソースコードを静的に解析します。


```bash
# Clone OWASP Juice Shop source code
git clone https://github.com/juice-shop/juice-shop.git

# Run Semgrep and save the results
docker run --rm -v "${PWD}:/src" semgrep/semgrep semgrep \
  --config=auto --json -o /src/semgrep_results.json juice-shop/
```

`semgrep_results.json`が生成されていれば成功です。

```bash
$ ls -l
total 336
drwxr-xr-x  55 bfl  staff    1760 10  5 07:17 juice-shop
-rw-r--r--   1 bfl  staff  168470 10  5 07:18 semgrep_results.json
```




### DefectDojoをローカルで起動

以下の公式のQuick Startを参考にして、ローカルでDefectDojoを起動しておきます。

https://github.com/DefectDojo/django-DefectDojo?tab=readme-ov-file#quick-start-for-compose-v2

事前に`Product`と`Engagement`を作成しておきます。

⭐️DefectDojoのEngagementの画面





```
docker compose logs initializer | grep "Admin password:"

QMHQAacvMAar39xr53iodM

http://0.0.0.0:8080
```








### S3にファイルをアップロード

LocalStack上のS3にSemgrepのスキャン結果をアップロードします。

```bash
# ファイルアップロード
awslocal s3 cp semgrep_results.json s3://demo-local-bucket

# 確認
awslocal s3 ls s3://demo-local-bucket
```


以下、実行例

```bash
$ awslocal s3 cp semgrep_results.json s3://demo-local-bucket
upload: ./semgrep_results.json to s3://demo-local-bucket/semgrep_results.json
$ awslocal s3 ls s3://demo-local-bucket
2025-10-05 10:23:56     168470 semgrep_results.json
```


Lambda関数のログを確認すると、Lambda関数が呼び出されていることと、DefectDojoへのスキャン結果の送信が成功していることがわかります。

```bash
$ awslocal logs tail --follow /aws/lambda/demo-local-lambda
2025-10-05T01:23:59.962000+00:00 2025/10/05/[$LATEST]aa2a63883edf1f4af74b690adf9dca92 START RequestId: 4a2472ca-bc45-4bb2-96cc-6bb4a14c4f21 Version: $LATEST
2025-10-05T01:23:59.962000+00:00 2025/10/05/[$LATEST]aa2a63883edf1f4af74b690adf9dca92 {"minimum_severity":"Info","active":false,"verified":false,"endpoint_to_add":null,"product_name":"demo-app","engagement_name":"demo-engagement","auto_create_context":false,"deduplication_on_engagement":false,"lead":null,"push_to_jira":false,"api_scan_configuration":null,"create_finding_groups_for_all_findings":true,"test_id":10,"engagement_id":1,"product_id":1,"product_type_id":1,"statistics":{"after":{"info":{"active":0,"verified":0,"duplicate":0,"false_p":0,"out_of_scope":0,"is_mitigated":0,"risk_accepted":0,"total":0},"low":{"active":2,"verified":0,"duplicate":0,"false_p":0,"out_of_scope":0,"is_mitigated":0,"risk_accepted":0,"total":2},"medium":{"active":26,"verified":0,"duplicate":0,"false_p":0,"out_of_scope":0,"is_mitigated":0,"risk_accepted":0,"total":26},"high":{"active":12,"verified":0,"duplicate":0,"false_p":0,"out_of_scope":0,"is_mitigated":0,"risk_accepted":0,"total":12},"critical":{"active":0,"verified":0,"duplicate":0,"false_p":0,"out_of_scope":0,"is_mitigated":0,"risk_accepted":0,"total":0},"total":{"active":40,"verified":0,"duplicate":0,"false_p":0,"out_of_scope":0,"is_mitigated":0,"risk_accepted":0,"total":40}}},"pro":["Did you know, Pro has an automated no-code connector for Semgrep JSON Report? Try today for free or email us at hello@defectdojo.com"],"apply_tags_to_findings":false,"apply_tags_to_endpoints":false,"scan_type":"Semgrep JSON Report","close_old_findings":false,"close_old_findings_product_scope":false,"test":10}
2025-10-05T01:23:59.962000+00:00 2025/10/05/[$LATEST]aa2a63883edf1f4af74b690adf9dca92 END RequestId: 4a2472ca-bc45-4bb2-96cc-6bb4a14c4f21
2025-10-05T01:23:59.962000+00:00 2025/10/05/[$LATEST]aa2a63883edf1f4af74b690adf9dca92 REPORT RequestId: 4a2472ca-bc45-4bb2-96cc-6bb4a14c4f21	Duration: 1275.90 ms	Billed Duration: 1276 ms	Memory Size: 256 MB	Max Memory Used: 256 MB
```


DefectDojoの画面を確認するとSemgrepのスキャン結果がインポートされていることが確認できます。


⭐️DefectDojoのエンゲージメントの画面

⭐️DefectDojoのテストの画面







## Tips

リソースを作成後、S3 にファイルをアップロードしても DefectDojo へ結果が送られませんでした。

まず **Lambda の CloudWatch Logs に出力が無い**かを確認しましたがログ出力がなかったので **そもそも Lambda が呼ばれていない／起動に失敗している** 可能性が考えられます。

このような時は`localstack logs` で LocalStack 側の処理状況を確認しましょう。今回のケースでは、`localstack logs` に以下のメッセージが出力されていました。

```bash
2025-10-04T22:53:20.316  WARN --- [et.reactor-3] l.s.l.i.executor_endpoint  : Execution environment startup failed: {"errorMessage": "Unable to import module 'handler': No module named 'requests'", "errorType": "Runtime.ImportModuleError", "requestId": "", "stackTrace": []}
2025-10-04T22:53:20.316  INFO --- [et.reactor-3] localstack.request.http    : POST /_localstack_lambda/c87d42378f2fdd3c75ed10209644e871/status/c87d42378f2fdd3c75ed10209644e871/error => 202
2025-10-04T22:53:20.316  WARN --- [da:$LATEST_0] l.s.l.i.execution_environm : Failed to start execution environment c87d42378f2fdd3c75ed10209644e871: Environment startup failed
2025-10-04T22:53:20.316  WARN --- [da:$LATEST_0] l.s.l.i.execution_environm : Execution environment c87d42378f2fdd3c75ed10209644e871 for function arn:aws:lambda:ap-northeast-1:000000000000:function:demo-local-lambda:$LATEST failed during startup. Check for errors during the startup of your Lambda function.
````

この1行目のエラーメッセージより、Lambda関数の依存関係が正しくパッケージ化されていないことに気づくことが出来ました。





## まとめ

今回試したのは [Free プラン](https://www.localstack.cloud/pricing）で、すべてのAWS サービスが使えるわけではありません。また、LocalStack はあくまでエミュレーションであり、本番 AWS と完全に同一ではない点は常に意識しておく必要があります。

とはいえ、料金を気にせず試せること、そして実際に稼働中の環境へ一切影響を与えずに挙動を確認できる安心感は非常に大きいと感じました。特に今回のように S3 と Lambda を組み合わせる構成は実務でもよく登場するため、今後も検証・再現・トラブルシュートの高速化に積極的に活用していきたいです。
