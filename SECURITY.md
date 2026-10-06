# Security

MarkItDown can process complex document formats. Treat uploaded documents as untrusted input.

This GUI intentionally passes uploaded bytes to MarkItDown through `convert_stream()` and does not expose arbitrary URL conversion. That avoids giving users a general-purpose server-side URL fetch primitive.

## Deployment guidance

- Put authentication in front of the app before exposing it to the public internet.
- Keep `MAX_FILE_SIZE_MB` conservative for your server size.
- Run the container with CPU and memory limits.
- Do not mount sensitive host directories into the container.
- Leave third-party plugins disabled unless you trust every installed plugin.
- Keep MarkItDown and its parser dependencies up to date.

Uploaded files are kept in application memory for conversion and are not intentionally persisted by this project. Platform logs, reverse proxies, container layers, or infrastructure outside this application may have their own retention behavior.
