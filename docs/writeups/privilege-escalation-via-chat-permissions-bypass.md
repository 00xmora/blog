---
title: Privilege Escalation via Chat Permissions Bypass
description: A real-world case where UI-level permission controls were not enforced at the API level, allowing message sending and user impersonation.
date: 2024-02-07
tags:
  - privilege-escalation
  - access-control
  - api-security
  - bug-bounty
---

# Privilege Escalation via Chat Permissions Bypass

Sometimes, what seems like a minor UI restriction hides a deeper flaw — one that lets you step into someone else's shoes.

In this case, I discovered a privilege escalation issue in a platform’s internal messaging system that relied too heavily on UI-level permission enforcement. Here's the story.

---

## 🧭 The Discovery

While exploring the messaging functionality of a platform, I noticed that even after a user’s "Inbox" permission was revoked via the UI, API requests to send messages were still succeeding.

> _The frontend was hiding the feature, but the backend wasn't blocking access._

Naturally, I dug deeper.

---

## 🔁 What I Tried

I created two test users and performed a basic exchange of messages between them. Then, I intentionally disabled messaging for one of the users via the platform’s settings.

After intercepting the API request for sending a message and replaying it using a tool like Repeater, the message still went through — even though, from the UI, the user was clearly blocked.

<small>🖼️ *Insert screenshot or video of message being sent after permission removal*</small>

---

## 👤 It Gets Worse: Impersonation

At this point, I asked myself: *What if I try to send a message pretending to be someone else?*

After experimenting with user IDs in the request body, it became clear that the system allowed arbitrary `user_id` values — meaning I could send a message **as another user**, without any ownership of their session.

This effectively allowed **impersonation** inside the internal chat system.

<small>🖼️ *Insert screenshot or video showing message from forged identity*</small>

---

## 🎯 Impact Summary

- Sending messages without "Inbox" permission
- Sending messages **as another user** using only their ID
- Bypassing client-side restrictions entirely
- No backend validation for sender identity

This kind of flaw could be used to impersonate internal users, trick recipients, or trigger automated actions linked to specific users.

---

## 📬 Responsible Disclosure & Response

I responsibly reported the issue through hackerone. The team acknowledged the finding and confirmed that the UI-level permissions were never meant to enforce true access control.

However, the **impersonation aspect** was unexpected, and they treated it seriously.

> _"Our engineering team has released a fix for the user impersonation issue..."_

The issue was resolved after internal investigation and patching.

![Resolved Report](/assets/writeups/1.png)

---

## 💭 Final Thoughts

This was a great example of why **client-side restrictions ≠ security**. Relying solely on frontend visibility or toggles is dangerous if backend validation is missing.

It's always worth looking at the **actual requests** the browser makes — not just what the UI lets you see.

---

Thanks for reading!  
If you have thoughts, ideas, or want to chat, feel free to reach out on [X (Twitter)](https://twitter.com/00xmora).

