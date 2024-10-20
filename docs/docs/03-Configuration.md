---
slug: /config
title: Configuration
---

## Environment variables

You can configure the service at runtime using various environment variables:

- `NUMBAT__SERVER__HOST` -
  host to run the server on
  (default: `0.0.0.0`)
- `NUMBAT__SERVER__PORT` -
  port to run the server on
  (default: `10600`)
- `NUMBAT__SERVER__TRUSTED` -
  trusted IP addresses
  (default: `*`)
- `NUMBAT__AMBER__S3__SECURE` -
  whether to use secure connections for the S3 API of the amber database
  (default: `false`)
- `NUMBAT__AMBER__S3__HOST` -
  host of the S3 API of the amber database
  (default: `localhost`)
- `NUMBAT__AMBER__S3__PORT` -
  port of the S3 API of the amber database
  (default: `10610`)
- `NUMBAT__AMBER__S3__USER` -
  user to authenticate with the S3 API of the amber database
  (default: `readwrite`)
- `NUMBAT__AMBER__S3__PASSWORD` -
  password to authenticate with the S3 API of the amber database
  (default: `password`)
- `NUMBAT__BEAVER__HTTP__SCHEME` -
  scheme of the HTTP API of the beaver service
  (default: `http`)
- `NUMBAT__BEAVER__HTTP__HOST` -
  host of the HTTP API of the beaver service
  (default: `localhost`)
- `NUMBAT__BEAVER__HTTP__PORT` -
  port of the HTTP API of the beaver service
  (default: `10500`)
- `NUMBAT__BEAVER__HTTP__PATH` -
  path of the HTTP API of the beaver service
  (default: ``)
- `NUMBAT__DEBUG` -
  enable debug mode
  (default: `false`)
