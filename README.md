# sdx-receipt-ctp

[![Build Status](https://travis-ci.org/ONSdigital/sdx-receipt-ctp.svg?branch=develop)](https://travis-ci.org/ONSdigital/sdx-receipt-ctp) [![Codacy Badge](https://api.codacy.com/project/badge/Grade/5cfc9ead5af24a7983e4dd203bd81710)](https://www.codacy.com/app/ons-sdc/sdx-receipt-ctp?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=ONSdigital/sdx-receipt-ctp&amp;utm_campaign=Badge_Grade) [![codecov](https://codecov.io/gh/ONSdigital/sdx-receipt-ctp/branch/develop/graph/badge.svg)](https://codecov.io/gh/ONSdigital/sdx-receipt-ctp)

The sdx-receipt-ctp app is a component of the Office for National Statistics (ONS) Survey Data Exchange (SDX) project which sends receipts to CTP.

## Installation

To install, use:

```bash
make build
```

To install using local sdx-common repo (requires SDX_HOME environment variable), use:

```bash
make dev
```

To run the test suite, use:

```bash
make test
```

## Configuration

The main configuration options are listed below:

| Environment Variable            | Default                 | Description
|---------------------------------|-------------------------|--------------
| RECEIPT_HOST                    | `http://localhost:8191` | Host for ctp receipt service
| RECEIPT_PATH                    | `questionnairereceipts` | Path for ctp receipt service
| RECEIPT_USER                    | _xxxx_                  | User for ctp receipt service
| RECEIPT_PASS                    | _xxxx_                  | Password for ctp receipt service
| RABBIT_QUEUE                    | `ctp_receipt`           | Incoming queue to read from
| RABBIT_QUARANTINE_QUEUE         | `ctp_receipt_quarantine`| Quarantine queue
| RABBIT_EXCHANGE                 | `message`               | RabbitMQ exchange to use
| SDX_RECEIPT_CTP_SECRET          | _none_                  | Key for decrypting messages from queue. Must be the same as used for ``sdx-collect``
| LOGGING_LEVEL                   | `DEBUG`                 | Logging sensitivity
