### Unreleased
  - Timestamp all logs as UTC
  - Add common library logging configurator
  - Route receipt 404 errors correctly
  - Change `stats_code` to 'status' for SDX logging
  - Add environment variables to README
  - Add codacy badge
  - Import async_consumer from sdx-common
  - Add support for codecov to see unit test coverage
  - Update and pin version of sdx-common to 0.7.0

### 1.1.1 2017-03-22
  - Remove Rabbit URL from logging messages

### 1.1.0 2017-03-15
  - Log version number on startup
  - Add correct content type header to request
  - Align async consumer with Pika docs
  - Change `calling service` log message to add the service being called

### 1.0.1 2017-02-17
  - Fix [#17 - RRM/CTP Typo](https://github.com/ONSdigital/sdx-receipt-ctp/issues/17)

### 1.0.0 2017-02-16
  - Initial release
