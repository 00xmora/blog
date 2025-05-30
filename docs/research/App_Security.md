---
title: app security
description: A detailed bug bounty writeup explaining how I bypassed OTP brute-force protection on PDFfiller using a rate-limiting flaw.
image: /assets/writeups/pdf-otp.png

date: 2025-05-28
tags:

- bug bounty
- 2fa
- rate limiting
- web security
date: 2025-05-30
---

# app security 

- **1- Application Secure Design Foundations**
    
    ### Introduction to Application Security
    
    - Application Security involves protecting applications **from the development phase through to production**.
    - It is broader than just penetration testing, which occurs at the end of the development cycle.
    - Late-stage vulnerability detection is inefficient, often requiring a restart of the development cycle and consuming time and resources.
    - The goal is to **proactively reduce risks** through secure coding, proper design, and integrated security practices throughout the software development lifecycle.
    
    ---
    
    ### Reactive vs. Proactive Approaches
    
    - **Penetration Testing** is reactive — identifies vulnerabilities after development.
    - **Application Security** is proactive — focuses on preventing vulnerabilities early in development.
    
    ---
    
    ### DevSecOps: Integrating Security into DevOps
    
    - DevSecOps brings together development, security, and operations to **embed security into every stage of software development**.
    - Key practices include:
    
    ### Shifting Security Left
    
    - Introduce security as early as possible — during code writing, commit, build, and release.
    
    ### Automation
    
    - Use automation tools to handle repetitive security checks, increasing speed and reducing manual effort.
    
    ### Additional Goals
    
    - Detect vulnerabilities before production.
    - Manage configurations and third-party dependencies securely.
    - Reduce production-stage vulnerabilities.
    - Support rapid releases without compromising security.
    - Enable faster remediation of discovered issues.
    
    ---
    
    ### DevSecOps Workflow by Development Phase
    
    ### Pre-Commit Phase
    
    - Performed before committing code.
    - Use pre-commit hooks to detect secrets or bad patterns.
    - Employ IDE plugins with real-time code scanning.
    - Follow secure coding guidelines.
    
    ### Commit Phase (Integration)
    
    - Occurs when code is committed to the repository.
    - Tools and practices:
        - **SAST** (Static Analysis): Scans code for known vulnerabilities.
        - **SCA** (Software Composition Analysis): Scans dependencies for known risks (e.g., OWASP Dependency-Check, Trivy).
        - **IaC Security**: Reviews infrastructure-as-code for misconfigurations.
        - **Container Security**: Scans Docker images (e.g., Trivy, Anchor, Docker Scan).
    
    ### Acceptance/Test Phase
    
    - Conducted in pre-production environments.
    - Tools and methods:
        - **DAST** (Dynamic Analysis): Scans running applications for runtime vulnerabilities (e.g., Burp Suite, OWASP ZAP).
        - **IAST** (Interactive Analysis): Combines DAST and SAST for deeper accuracy with in-app agents.
    
    ### Production Phase
    
    - Final live environment.
    - Focus on:
        - Regulatory and compliance checks.
        - **RASP** (Runtime Application Self-Protection): Monitors and defends against attacks in real time.
    
    ### Operation Phase
    
    - Ongoing monitoring and response.
    - Practices include:
        - Using **SIEM** tools and centralized logging.
        - Setting retention and monitoring policies.
        - Being ready to detect and respond to post-deployment threats.
    
    ---
    
    ### Secure by Design Principles
    
    ### Least Privilege
    
    - Users and services should have only the access necessary for their role.
    
    ### Defense in Depth
    
    - Use multiple layers of security so that a failure in one layer doesn't compromise the entire system.
    
    ### Secure Defaults / Fail Secure
    
    - Systems should default to a **secure state** and fail in a secure way (e.g., locking access).
    
    ### Open Design
    
    - Use well-established, publicly vetted encryption and security protocols (e.g., AES, RSA, OpenPGP).
    
    ### Minimize Attack Surface
    
    - Reduce entry points by disabling unnecessary services, ports, or features.
    
    ### Validate Input
    
    - Input validation on both client and server side to prevent attacks like SQL Injection.
    - Use parameterized queries instead of dynamic input concatenation.
    
    ---
    
    ### Threat Modeling
    
    - Helps identify, assess, and mitigate potential threats before they manifest.
    
    ### Process
    
    1. Understand the application’s architecture and trust boundaries.
    2. Identify threats based on components and data flows.
    3. Evaluate potential vulnerabilities.
    4. Define mitigations and defenses.
    
    ### STRIDE Framework
    
    - **Spoofing**: Impersonating users — mitigated by MFA, CAPTCHA.
    - **Tampering**: Unauthorized data modification — mitigated by validation.
    - **Repudiation**: Denying actions — mitigated by logging and auditing.
    - **Information Disclosure**: Leaking sensitive data — mitigated by access control and secure API design.
    - **Denial of Service**: Disrupting availability — mitigated by rate limiting, timeouts, and lockouts.
    - **Elevation of Privilege**: Gaining higher permissions — mitigated by strict access controls.
    
    ---
    
    ### Key Roles in Application Security
    
    - **DevSecOps Engineer**: Automates security in CI/CD pipelines and secures cloud environments.
    - **Application Security Engineer**: Performs code reviews and uses SAST/DAST/IAST tools.
    - **Cloud Security Engineer**: Specializes in securing cloud infrastructure and services.
    - **Security Architect**: Designs security architecture and policies across projects.
    
    ---
    
    ### Required Skills
    
    - Proficiency in at least one programming language.
    - Solid grasp of security concepts and common vulnerabilities (e.g., OWASP Top 10).
    - Familiarity with web, mobile, or cloud environments.
    - Experience working with CI/CD pipelines.
    - Code review and secure coding knowledge.
    - Practical experience with security tools.
    - Understanding of and some experience in penetration testing is a valuable bonus.
    
    ---
    
- **2- Threat Modeling – Key Concepts & Notes**
    
    ## Threat Modeling – Key Concepts & Notes
    
    ### What is Threat Modeling?
    
    - A **proactive process** to **identify potential threats** in an application/system **before attackers do**.
    - Helps understand:
        - The **exposure** (internet-facing vs. internal).
        - The **critical assets** attackers may target.
    
    ### Who Performs It?
    
    - Can be done:
        - **Internally** within an organization.
        - As a **security service** for clients by third-party providers.
    
    ### Objectives
    
    - Create a **documented threat model** for communication with:
        - Developers
        - Application owners
        - Project managers
    - **Track threats and their mitigations**, showing their status (e.g., mitigated, accepted risk).
    
    ### Why Perform Threat Modeling?
    
    - **Reduces vulnerability fix costs** by detecting issues early.
    - Offers a **holistic view**:
        - Interactions, trust boundaries, components, data flow.
        - Mitigation status of threats.
    - Can be used as **input for security tools** like:
        - SAST (Static Analysis)
        - DAST (Dynamic Analysis)
        - SCA (Software Composition Analysis)
    
    ### When is it Done?
    
    - Typically during the **Design Phase** of the **Secure Development Life Cycle (SDLC)**.
    - Done before coding starts.
    - Involves collaboration between:
        - Application Security Engineers
        - Developers
        - Architects
    
    ### Frameworks for Threat Modeling
    
    - **STRIDE** *(main focus)*
    - **PASTA**
    - **OCTAVE**
    - **VAST**
    
    ### Popular Tools
    
    - **OWASP Threat Canvas** *(example used in the source)*
    - **Threat Dragon**
    - **Microsoft Threat Modeling Tool**
    
    ---
    
    ## Components in a Threat Model
    
    ### Entity (Threat Actor)
    
    - A user or system interacting with the app (e.g., admin, customer).
    - Visual: Orange shape in Threat Canvas.
    
    ### Data Store
    
    - Where data resides (e.g., DB, S3 bucket, FTP).
    - Visual: Unique data store icon.
    
    ### Process
    
    - Any operation or service (e.g., web app, API).
    - Represents core business logic.
    
    ### Trust Boundary
    
    - Marks component location: internal, internet, cloud, etc.
    - Helps define **attack surfaces**.
    
    ### Data Flow Diagram (DFD)
    
    - Final output showing **component relations**.
    - **Arrows** indicate interaction direction (request/response).
    - **One-way** (e.g., sensor ➝ DB) or **Two-way** (e.g., user ↔ app).
    
    ---
    
    ## Example Scenario – Book Store Web App
    
    ### Components:
    
    - **Entity:** Registered User (on the internet)
    - **Process:** Web Application (internet-facing)
    - **Data Stores:**
        - AWS S3 Bucket → User photos (cloud network)
        - Internal Database → Customer data (internal network)
    
    ### Trust Boundaries:
    
    - Internet, Internal Network, Cloud Network
    
    ### Threats Identified:
    
    - Auth/authz flaws (e.g., privilege escalation)
    - Clickjacking
    - XSS
    - DoS
    - Insecure file upload
    - SQL Injection (if using SQL DB)
    - ❌ *Irrelevant threats (e.g., NoSQLi for MySQL) are excluded*
    
    ### Mitigations:
    
    - For each threat, controls are defined:
        - **Status:** Implemented / In Progress / Missing
    
    ### Risk Acceptance:
    
    - Business can **accept certain risks** for strategic reasons.
    
    ### Threat Model Summary (PDF):
    
    - DFD
    - Risk summaries by STRIDE category
    - Mitigation status
    - Risk thresholds
    - Used for stakeholder reporting
- **3- Top 10 OWASP CI/CD & DevSecOps Risks!**
    
    ### **DevSecOps Overview**
    
    **Definition and Purpose**
    
    - DevSecOps extends DevOps by integrating development, security, and operations.
    - It addresses the security gaps introduced by rapid DevOps practices.
    - The goal is to build software that is both secure and fast.
    - Emphasizes the balance between speed, security, and quality.
    
    **Why DevSecOps is Important**
    
    - Traditional security processes are too slow and reactive.
    - DevSecOps allows security to shift left—integrating early in the SDLC.
    - Prevents incidents like the July 2024 Cloudflare outage caused by an insecure, unmonitored patch.
    - Ensures compliance with modern standards required by entities like Visa and Mastercard.
    
    ---
    
    ### **Core DevSecOps Principles**
    
    **Security as Code**
    
    - Integrates security checks directly into code and pipeline stages.
    - Involves code scanning, policy as code, and infrastructure as code checks.
    
    **Automation and Scalability**
    
    - Automation ensures faster delivery with consistent security checks.
    - Scalability handles growing codebases and deployment complexity.
    
    **Continuous Security**
    
    - Ongoing security monitoring and vulnerability management.
    - Automated and manual security testing.
    - Security-focused code reviews.
    
    ---
    
    ### **DevSecOps Tools**
    
    **SAST (Static Application Security Testing)**
    
    - Scans code for vulnerabilities without executing it.
    - Detects issues like XSS and SQL injection but may generate false positives.
    
    **DAST (Dynamic Application Security Testing)**
    
    - Tests the running application for vulnerabilities.
    - Tools like Burp Suite simulate attacks on APIs and web interfaces.
    
    **SCA (Software Composition Analysis)**
    
    - Scans third-party libraries for known vulnerabilities.
    - Tools: Snyk, Black Duck, Trivy, OWASP Dependency-Check.
    
    **Mobile Security Tools**
    
    - Used for static and dynamic analysis of mobile apps.
    - Examples: MobSF, NowSecure.
    
    **IAST (Interactive Application Security Testing)**
    
    - Combines techniques from SAST and DAST.
    
    **IaC and Container Scanning**
    
    - Tools like TFSec and Checkov analyze infrastructure code.
    - Container image scanning is used to detect vulnerabilities before deployment.
    
    ---
    
    ### **CI/CD Pipeline Explained**
    
    **Continuous Integration (CI)**
    
    - Developers’ code is compiled into build files (e.g., WAR, JAR).
    
    **Continuous Deployment/Delivery (CD)**
    
    - These build files are deployed onto servers for users.
    
    **DevSecOps Pipeline Phases**
    
    1. Planning: Threat modeling, defining requirements, creating user stories.
    2. Development: Secure coding, code reviews, and static analysis.
    3. Build: Code is transformed into executable build files.
    4. Release: Final, signed versions are prepared for deployment.
    5. Deployment: Code is deployed onto live servers.
    6. Monitoring: Application is monitored for attacks and performance issues.
    
    ---
    
    ### **OWASP Top 10 CI/CD Risks**
    
    1. **Insufficient Flow Control Mechanisms**
        - Lack of process enforcement for promotions, approvals, or rollbacks.
    2. **Insufficient Identity and Access Management**
        - Overprivileged accounts and missing MFA or RBAC policies.
    3. **Insecure System Configuration**
        - Use of default settings, exposed ports, or unprotected CI servers.
    4. **Insecure Third-Party Dependencies**
        - Usage of vulnerable packages. Requires SBOM and regular scanning.
    5. **Poisoned Pipeline Execution**
        - Malicious scripts or compromised CI agents can corrupt builds.
    6. **Insufficient Pipeline Access Control**
        - Pipelines must be restricted to limit their ability to affect hosts or access secrets.
    7. **Improper Credential Management**
        - Secrets stored in plain text, lack of rotation, and shared accounts.
    8. **Insufficient Logging and Monitoring**
        - Lack of monitoring tools and alerts for pipeline anomalies or intrusions.
    9. **Insufficient Supply Chain Integrity**
        - Missing validation checks like hashes to ensure build integrity across stages.
    10. **Insecure Integration of External Tools**
        - Plugins or tools used in the pipeline must be verified and trusted.
    
    ---
    
    ### **Notable Incidents**
    
    - **Cloudflare (2024)**: Insecure patch caused widespread failures, costing billions.
    - **SolarWinds Attack**: Malicious code injected into a trusted software update.
    - **Codecov Breach**: Breach of a security tool’s own pipeline, impacting users.
    
    ---
    
    ### **Upcoming Course Topics**
    
    - Deeper coverage of threat modeling.
    - Hands-on with DevSecOps tools.
    - Application review and secure code review techniques.
- **4-Threat Modeling with STRIDE & OWASP Threat Dragon**
    
    ### Threat Modeling with STRIDE & OWASP Threat Dragon
    
    ### Overview
    
    - Threat modeling is a key component of application security.
    - STRIDE is the most widely used framework for threat modeling.
    - OWASP Threat Dragon is a free, open-source tool that supports STRIDE.
    
    ---
    
    ### STRIDE Model Principles
    
    STRIDE is an acronym made up of six threat categories:
    
    **1. Spoofing**
    
    Occurs when an attacker impersonates another user.
    
    Examples: stealing credentials, brute-forcing logins, token theft.
    
    **2. Tampering**
    
    Involves unauthorized modifications to data.
    
    Examples: intercepting and altering HTTP requests, file modifications.
    
    **3. Repudiation**
    
    A situation where a user denies performing an action.
    
    Mitigated using logging and auditing mechanisms to maintain traceability.
    
    **4. Information Disclosure**
    
    Unauthorized access to or exposure of sensitive data.
    
    Examples: leaking passwords, user data, or institutional records.
    
    **5. Denial of Service (DoS)**
    
    Disruption of service availability.
    
    Examples: DoS/DDoS attacks, resource exhaustion, crashing applications.
    
    **6. Elevation of Privilege**
    
    An attacker gains higher permissions than allowed.
    
    Examples: privilege escalation, bypassing access controls, gaining admin rights.
    
    ---
    
    ### OWASP Threat Dragon
    
    **Tool Overview**
    
    - Free and open-source
    - Developed by OWASP
    - Uses Data Flow Diagrams (DFD)
    - Supports STRIDE for threat identification and mitigation planning
    
    **How It Works**
    
    - Create models using DFD components:
        - Process
        - Data Store
        - Actor
    - Define trust boundaries and data flows between components
    - Use STRIDE to automatically suggest relevant threats
    
    **Steps to Use Threat Dragon**
    
    1. Go to [threatdragon.com](https://threatdragon.com/)
    2. Login using GitHub or Local Session
    3. Choose to:
        - View example model
        - Continue an existing model
        - Create a new model
    
    **Creating a New Model**
    
    - Name the model (e.g., "Our New Web Application")
    - Optionally add owners, reviewers, and system contacts
    - Select STRIDE as the threat modeling framework
    - Add components:
        - Web Server (Process)
        - Web App Server (Process)
        - Database (Data Store)
        - Normal User / Admin (Actor)
    - Connect components with Data Flows
    - Define Trust Boundaries (e.g., internet ↔ DMZ)
    
    **Adding Threats**
    
    - Title the threat (e.g., "Impersonation of user via credentials theft")
    - Describe how it could occur (e.g., brute-force attacks)
    - Add mitigations:
        - Enable MFA
        - Use strong password policies
        - Apply rate-limiting
    - Set threat priority (e.g., High)
    - Optionally assign scores
    
    **Example Threats**
    
    - *Data Tampering in Transit*
        
        Potential Attacks: MITM
        
        Mitigations: Enable TLS/SSL, certificate management, use checksums
        
    
    **Finalizing the Model**
    
    - Save model as a JSON file
    - Generate a PDF report with:
        - DFD diagram
        - Listed assets
        - Threats and their statuses
        - Suggested mitigations
    
    ---
    
    Let me know if you want this exported as a Notion-ready Markdown file or formatted for a PDF handout.
    
- **5- Secure Source Code Control, GitHub, GitLab, Version Control**
    
    ### DevSecOps Pipeline and Automation Overview
    
    - The DevSecOps pipeline integrates **security practices into the DevOps lifecycle**, focusing on automation and version control.
    - The lesson builds on foundational application security concepts and references the **TryHackMe room "Intro to Pipeline Automation"**.
    - By the end, you should understand:
        - What a DevSecOps pipeline is
        - The role of automation in security
        - The meaning and importance of version control
        - How Git and security tools function in CI/CD environments
    
    ---
    
    ### Core Components of a DevSecOps Pipeline
    
    1. **Source Code Storage / Version Control**
    2. **Dependency Management** *(to be covered in the next lesson)*
    3. **Testing**, including security testing
    4. **Continuous Integration**
    5. **Deployment Environments**
    
    ---
    
    ### The Need for Version Control
    
    - In solo development, code may be stored locally.
    - In team environments, centralized **code repositories** are necessary.
    - These repositories must be **secure and collaborative**, prompting questions like:
        - How to manage **access control** and permissions?
        - How to **track code changes** from multiple developers?
        - How to **integrate** code with development tools (IDEs)?
        - How to handle **versioning** and distinguish between feature updates?
        - Where to **host the repository**—locally or in the cloud?
    
    ---
    
    ### What is Version Control?
    
    - Version control allows:
        - Maintaining **multiple versions** of code
        - Branching for **new feature development**
        - **Rolling back** to previous code versions
        - **Tracking contributions** across team members
    - It gives complete **visibility and history** of the codebase
    
    ---
    
    ### Types of Version Control Systems
    
    - **Git**: A **distributed** version control system. Each user has a full local copy of the codebase.
    - **SVN (Subversion)**: A **centralized** version control system. All developers rely on a single central repository.
    
    ---
    
    ### Git Hosting Platforms
    
    - **GitHub**: The largest **online Git repository provider**, supporting both public and private repos.
    - **GitLab**: A self-hosted solution for organizations that prefer to store Git repositories **internally**.
    
    ---
    
    ### Security Concerns in Version Control
    
    - **Authentication**: A compromised developer account can lead to **unauthorized access to the full codebase**.
    - **Access Control and Privilege Management**:
        - Proper permission settings are crucial
        - Failure may result in critical risks like unauthorized **code deletion**
    - **Git Forensics and Git Leaks**:
        - Secrets (like credentials) committed to a Git repo may persist in the **version history**, even if deleted later.
        - Tools like **Gitleaks** can scan Git history to detect and extract sensitive data.
    
    ---
    
    ### TryHackMe – “Intro to Pipeline Automation” Highlights
    
    - Practical exploration of pipeline concepts.
    - Key takeaways from the lab:
        - **GitHub** is identified as the largest online Git provider.
        - **GitLab** can be used to **host a Git server internally**.
        - **Gitleaks** is used to **scan repositories for sensitive information** like secrets or credentials.