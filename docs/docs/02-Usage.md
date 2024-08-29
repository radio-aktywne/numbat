---
slug: /usage
title: Usage
---

## Listing prerecordings

You can list prerecordings using the `/prerecordings/:event` endpoint.
For example, you can use `curl` to list all prerecordings for an event:

```sh
curl \
    --request GET \
    http://localhost:28000/prerecordings/0f339cb0-7ab4-43fe-852d-75708232f76c
```

## Uploading and downloading prerecordings

You can upload and download prerecordings
using the `/prerecordings/:event/:start` endpoint.
To upload a prerecording, you can use
[`curl`](https://curl.se) to send a `PUT` request
streaming the content from a file:

```sh
curl \
    --request PUT \
    --header "Content-Type: audio/ogg" \
    --header "Transfer-Encoding: chunked" \
    --upload-file prerecording.ogg \
    http://localhost:28000/prerecordings/0f339cb0-7ab4-43fe-852d-75708232f76c/2024-01-01T00:00:00
```

To download a prerecording, you can use
[`curl`](https://curl.se) to send a `GET` request
and save the response body to a file:

```sh
curl \
    --request GET \
    --output prerecording.ogg \
    http://localhost:28000/prerecordings/0f339cb0-7ab4-43fe-852d-75708232f76c/2024-01-01T00:00:00
```

## Deleting prerecordings

You can delete prerecordings using the `/prerecordings/:event/:start` endpoint.
For example, you can use `curl` to delete a prerecording:

```sh
curl \
    --request DELETE \
    http://localhost:28000/prerecordings/0f339cb0-7ab4-43fe-852d-75708232f76c/2024-01-01T00:00:00
```

## Ping

You can check the status of the app by sending
either a `GET` or `HEAD` request to the `/ping` endpoint.
The app should respond with a `204 No Content` status code.

For example, you can use `curl` to do that:

```sh
curl \
    --request HEAD \
    --head \
    http://localhost:28000/ping
```
