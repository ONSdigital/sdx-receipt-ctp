# sdx-receipt-ctp

[![Build Status](https://travis-ci.org/ONSdigital/sdx-receipt-ctp.svg?branch=develop)](https://travis-ci.org/ONSdigital/sdx-receipt-ctp)

The sdx-receipt-ctp app is a component of the Office for National Statistics (ONS) Survey Data Exchange (SDX) project which sends receipts to CTP.

## Configuration

The main configuration options are listed below:

| Environment Variable            | Default       | Description
|---------------------------------|---------------|--------------
| CTP_RECEIPT_HOST                | _none_        | Host for ctp receipt service
| CTP_RECEIPT_PATH                | _none_        | Path for ctp receipt service
| CTP_RECEIPT_USER                | _none_        | User for ctp receipt service
| CTP_RECEIPT_PASS                | _none_        | Password for ctp receipt service
| RECEIPT_CTP_QUEUE               | `ctp_receipt` | Incoming queue to read from
| RABBIT_EXCHANGE                 | `message`     | RabbitMQ exchange to use
| RECEIPT_SECRET                  | _none_        | Key for decrypting messages from queue. Must be the same as used for ``sdx-collect``
| LOGGING_LEVEL                   | `DEBUG`       | Logging sensitivity
