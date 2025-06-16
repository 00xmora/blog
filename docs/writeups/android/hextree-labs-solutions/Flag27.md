---
title: Hextree Labs - Flag27Service Messenger Vulnerability (Solution) 
description: A short write-up on exploiting an Android Service vulnerability involving Messenger IPC and state management to retrieve a hidden flag. 
summary: A short write-up on exploiting an Android Service vulnerability involving Messenger IPC and state management to retrieve a hidden flag.
date: 2025-06-14 
tags: Android, CTF, Hextree Labs, Messenger, IPC, Vulnerability, Writeup, Reverse Engineering
read_time: 3 minute read
---

# Hextree Labs – Flag27Service Messenger Vulnerability (Solution)

## Introduction

This write-up covers the solution for the `Flag27Service` challenge from Hextree Labs. This challenge highlights a common Android Inter-Process Communication (IPC) vulnerability when services handle messages via `Messenger` and maintain state. The goal was to extract a hidden flag by interacting with the service in a specific sequence.

## Understanding the Target (`Flag27Service`)

The `Flag27Service` exposes a `Messenger` for IPC. Our analysis of its `IncomingHandler` revealed three key message types:

- **`MSG_ECHO (what = 1)`**: Allows setting an `echo` string within the service.
- **`MSG_GET_PASSWORD (what = 2)`**: Generates a UUID, stores it internally, and replies with it.
- **`MSG_GET_FLAG (what = 3)`**: Requires:
  1. `echo` must be `"give flag"`.
  2. `password` must match the previously generated one.

If both conditions are met, the service launches `Flag27Activity` with the flag.

## The Vulnerability: Stateful Handler and `message.obj` Check

The `IncomingHandler` maintains internal state (`echo`, `password`). The `MSG_GET_PASSWORD` handler includes:

```java
if (message.obj == null) {
    Flag27Service.this.sendReply(message, "Error");
    return;
}
// proceed to generate and send password
````

So if `obj` is `null`, no password is sent. This check is key to bypassing.

## Exploitation Strategy

### Step 1 – Set the `echo` string

Send `MSG_ECHO` with `"give flag"` to prep the state.

### Step 2 – Get the password

Send `MSG_GET_PASSWORD` with a **non-null `obj`** (e.g., an empty `Bundle`) to bypass the null-check.

### Step 3 – Get the flag

Send `MSG_GET_FLAG` with the captured password inside a `Bundle`.

## The Exploit Code (`HextreeActivity.java`)

The following Android activity binds to `Flag27Service` and performs the 3-step exploit:

```java
// Full code omitted for brevity – see original version above for details
// Handles service connection, sending messages, and receiving replies
```

Key logic:

* Set `"give flag"` using `MSG_ECHO`.
* Get password via `MSG_GET_PASSWORD` (with `obj = new Bundle()`).
* Immediately send `MSG_GET_FLAG` with the password.

## Execution and Results

1. **Install** target app: `io.hextree.attacksurface`.
2. **Install** exploit app: `com.example.hexatree`.
3. Launch `HextreeActivity` and tap "Attack".
4. **Logcat shows**:

   * MSG 1 → `echo` set.
   * MSG 2 → password received.
   * MSG 3 → flag request sent.
   * Success response logged.
5. **Flag27Activity appears**, revealing the flag.

## Conclusion

This challenge demonstrates how vulnerable stateful IPC services can be. Validating message structure (like `obj`) and avoiding persistent state in bound services are crucial steps to securing Android components.