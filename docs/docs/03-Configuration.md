---
slug: /config
title: Configuration
---

## Environment variables

You can configure the app at runtime using various environment variables:

- `EMILOUNGE__SERVER__HOST` -
  host to run the server on
  (default: `0.0.0.0`)
- `EMILOUNGE__SERVER__PORT` -
  port to run the server on
  (default: `28000`)
- `EMILOUNGE__SERVER__TRUSTED` -
  trusted IP addresses
  (default: `*`)
- `EMILOUNGE__EMISHOWS__HTTP__SCHEME` -
  scheme of the HTTP API of the emishows service
  (default: `http`)
- `EMILOUNGE__EMISHOWS__HTTP__HOST` -
  host of the HTTP API of the emishows service
  (default: `localhost`)
- `EMILOUNGE__EMISHOWS__HTTP__PORT` -
  port of the HTTP API of the emishows service
  (default: `35000`)
- `EMILOUNGE__EMISHOWS__HTTP__PATH` -
  path of the HTTP API of the emishows service
  (default: ``)
- `EMILOUNGE__MEDIALOUNGE__S3__SECURE` -
  whether to use secure connections for the S3 API of the medialounge database
  (default: `false`)
- `EMILOUNGE__MEDIALOUNGE__S3__HOST` -
  host of the S3 API of the medialounge database
  (default: `localhost`)
- `EMILOUNGE__MEDIALOUNGE__S3__PORT` -
  port of the S3 API of the medialounge database
  (default: `29000`)
- `EMILOUNGE__MEDIALOUNGE__S3__USER` -
  user to authenticate with the S3 API of the medialounge database
  (default: `readwrite`)
- `EMILOUNGE__MEDIALOUNGE__S3__PASSWORD` -
  password to authenticate with the S3 API of the medialounge database
  (default: `password`)
- `EMILOUNGE__DEBUG` -
  enable debug mode
  (default: `false`)
