"""Knowledge-base topics for IT staff only (audience = it-staff).

These never appear in answers to employees: session 11 filters on audience
before the search runs.
"""

from datagen.model import (
    ACCESS,
    EMAIL,
    GENERAL,
    HARDWARE,
    IAM,
    L1,
    MESSAGING,
    NETOPS,
    NETWORK,
    ONBOARD_TEAM,
    ONBOARDING,
    PACKAGING,
    SECOPS,
    SECURITY,
    SOFTWARE,
    WORKPLACE,
    T,
)

STAFF = "it-staff"

T(
    "staff-triage-priority",
    "Service desk: set ticket priority",
    system="HelpHub",
    category=GENERAL,
    subcategory="Staff procedure",
    kind="reference",
    audience=STAFF,
    summary="Priority comes from impact and urgency, never from the wording of the ticket or the seniority of the requester.",
    steps={
        "any": [
            "Priority 1: a service is down for a whole office or region, or a security incident is in progress.",
            "Priority 2: a team cannot work, a customer-facing event is at risk within 2 hours, or a device is lost or stolen.",
            "Priority 3: one person cannot do part of their work and has no workaround.",
            "Priority 4: a request, a question, or a fault with a workaround.",
            "Raise the priority when more people report the same fault; link the tickets to one parent.",
            "Record the reason whenever you change a priority.",
        ]
    },
    notes=["Response and resolution targets for each priority are in the SLA matrix."],
    group=L1,
)

T(
    "staff-assignment-groups",
    "Service desk: route tickets to the right group",
    system="HelpHub",
    category=GENERAL,
    subcategory="Staff procedure",
    kind="reference",
    audience=STAFF,
    summary="Level 1 resolves what the knowledge base covers and routes the rest by subject, with the checks already done written in the ticket.",
    steps={
        "any": [
            "Identity and Access: MFA resets, access that needs granting or removing, lockouts with no stale device.",
            "Network Operations: VPN faults on more than one network, office Wi-Fi, certificates, firewall requests.",
            "Workplace Engineering: hardware faults, re-imaging, docks, printers, phones.",
            "Messaging and Collaboration: mailboxes, Teams, meeting rooms, OneDrive.",
            "Software Packaging: App Hub failures, new software, update failures.",
            "Security Operations: phishing with a click, malware, lost devices, admin rights, policy exceptions.",
            "Onboarding Team: joiners, leavers, contractors.",
            "Before routing, write what the user tried, the exact error and the asset tag.",
        ]
    },
    group=L1,
)

T(
    "staff-identity-verification",
    "Service desk: verify a caller's identity",
    system="LarkID",
    category=ACCESS,
    subcategory="Staff procedure",
    kind="how-to",
    audience=STAFF,
    summary="Verify identity before any password reset, MFA reset or recovery key; a claim in a ticket, chat or email is never proof.",
    steps={
        "any": [
            "Accepted proof, any one: a push approval to the caller's registered LarkID Authenticator; a video call with the caller's line manager present; the caller's badge shown in person at a Tech Bar.",
            "Not accepted: employee number, date of birth, an email from the caller's address, or a colleague vouching by chat.",
            "Call back on the number in the directory, never on a number the caller gives you.",
            "Record the method used in the ticket before you act.",
            "If the caller pressures you to skip the check, stop and tell Security Operations.",
        ]
    },
    group=IAM,
    policy="POL-003",
)

T(
    "staff-unlock-account",
    "Service desk: unlock an account in the LarkID admin console",
    system="LarkID",
    category=ACCESS,
    subcategory="Staff procedure",
    kind="how-to",
    audience=STAFF,
    summary="Unlock on request only after finding where the failed sign-ins come from; otherwise the account locks again within minutes.",
    steps={
        "any": [
            "Verify the caller's identity.",
            "In the admin console open Users, the user, then Sign-in log, and filter on Failed.",
            "Note the source of the failures: device name, application and IP address.",
            "If the source is the user's own device, have them remove the old password there first.",
            "Choose Unlock account.",
            "If the failures come from an unknown address or several countries, do not unlock; assign to Security Operations as priority 2.",
        ]
    },
    codes=["LID-1203"],
    group=IAM,
    policy="POL-003",
)

T(
    "staff-mfa-reset",
    "Identity and Access: reset MFA and issue a temporary access pass",
    system="LarkID Authenticator",
    category=ACCESS,
    subcategory="Staff procedure",
    kind="how-to",
    audience=STAFF,
    summary="An MFA reset is a high-risk action: it needs verified identity and a second Identity and Access analyst to approve.",
    steps={
        "any": [
            "Confirm identity by video call with the line manager or by badge at a Tech Bar; a push approval is not possible in this case.",
            "Record the reason: lost, replaced, wiped or stolen phone.",
            "Ask a second analyst to approve the reset in the admin console.",
            "Remove the old authenticator registration.",
            "Issue a temporary access pass valid for 60 minutes, single use.",
            "Stay on the call until the user has registered the new device, then confirm the pass shows as used.",
        ]
    },
    codes=["LID-MFA-102"],
    group=IAM,
    policy="POL-003",
)

T(
    "staff-vpn-known-issue",
    "Known issue KI-2026-014: SecureTunnel 5.2 disconnects on macOS 26",
    system="SecureTunnel VPN",
    category=NETWORK,
    subcategory="Known issue",
    kind="troubleshooting",
    audience=STAFF,
    summary="SecureTunnel 5.2 drops the tunnel every 8 to 12 minutes on macOS 26 when private Wi-Fi addressing rotates; version 5.3 fixes it.",
    symptoms=[
        "Mac users on macOS 26 report drops at regular intervals.",
        "The client log shows 'peer address changed, tearing down'.",
    ],
    causes=["Version 5.2 treats a rotated private Wi-Fi address as a new device."],
    steps={
        "any": [
            "Confirm the client version in SecureTunnel, About.",
            "Deploy version 5.3 from App Hub; it is in the general ring since 20 October 2026.",
            "If the Mac cannot update at once, set Private Wi-Fi Address to Fixed for the home network as a workaround.",
            "Link the ticket to problem record KI-2026-014 and do not escalate to Network Operations.",
        ]
    },
    codes=["KI-2026-014"],
    group=NETOPS,
)

T(
    "staff-vpn-809-diagnosis",
    "Network Operations: diagnose VPN error 809 that follows the user",
    system="SecureTunnel VPN",
    category=NETWORK,
    subcategory="Staff procedure",
    kind="troubleshooting",
    audience=STAFF,
    summary="Error 809 on every network is not a home router fault; check the NAT traversal setting, the local firewall and the gateway.",
    symptoms=["The user gets error 809 on home broadband, on a phone hotspot and on guest Wi-Fi."],
    causes=[
        "The NAT traversal registry value is missing after a rebuild.",
        "A third-party firewall product is installed.",
        "The regional gateway is rejecting new sessions.",
    ],
    steps={
        "any": [
            "Check the gateway dashboard for the user's region; more than five 809 tickets in an hour is a gateway incident.",
            "On the laptop confirm the registry value AssumeUDPEncapsulationContextOnSendRule under HKLM\\SYSTEM\\CurrentControlSet\\Services\\PolicyAgent is 2.",
            "If it is missing, run the Network baseline policy from the management console and restart.",
            "Check for third-party firewall or VPN software and remove it.",
            "Collect the SecureTunnel log bundle and attach it before closing or escalating to the vendor.",
        ]
    },
    codes=["809"],
    group=NETOPS,
)

T(
    "staff-outlook-profile-rebuild",
    "Messaging: rebuild an Outlook profile safely",
    system="Outlook",
    category=EMAIL,
    subcategory="Staff procedure",
    kind="how-to",
    audience=STAFF,
    summary="A profile rebuild fixes most connection and search faults, but local-only data must be checked first.",
    steps={
        "any": [
            "Confirm the mailbox is healthy in webmail.",
            "Check for local PST files under Account Settings, Data Files; a new profile does not reconnect them automatically.",
            "Export the user's signatures and rules if they have many.",
            "Create the new profile from Control Panel, Mail; do not delete the old one until the new one has synchronised.",
            "Set the cached mode slider to 12 months for mailboxes above 20 GB.",
            "Remove the old profile after two working days without problems.",
        ]
    },
    codes=["0x800CCC0E"],
    group=MESSAGING,
)

T(
    "staff-reimage-decision",
    "Workplace Engineering: repair or re-image a laptop",
    system="Laptop",
    category=HARDWARE,
    subcategory="Staff procedure",
    kind="how-to",
    audience=STAFF,
    summary="Stop troubleshooting a software fault after 2 hours of analyst time and re-image; the user's data is in OneDrive.",
    steps={
        "any": [
            "Confirm OneDrive shows Up to date and that Desktop, Documents and Pictures are backed up.",
            "Ask about data outside those folders, such as local databases or virtual machines.",
            "Re-image when: the fault survives a clean user profile, system file checks fail, or 2 hours have been spent.",
            "Replace instead when the laptop is older than 48 months, or hardware diagnostics fail.",
            "Issue a loan laptop if the re-image cannot be finished the same day.",
            "After the re-image, check encryption, EndpointShield and the device certificate before returning it.",
        ]
    },
    group=WORKPLACE,
    policy="POL-004",
)

T(
    "staff-licence-reclaim",
    "Software Packaging: reclaim unused licences",
    system="App Hub",
    category=SOFTWARE,
    subcategory="Staff procedure",
    kind="how-to",
    audience=STAFF,
    summary="A licence unused for 60 days is reclaimed after a 7-day warning; reclaiming early needs the holder's agreement.",
    steps={
        "any": [
            "Run the Unused licences report for the application; it lists the last-used date for each holder.",
            "The warning email is sent automatically at day 53.",
            "At day 60 the licence returns to the pool and the application is removed at the next check-in.",
            "When a request is waiting and no licence is free, you may ask the longest-idle holder to release theirs early; record their reply.",
            "Never reclaim from a user on long-term leave without asking their manager.",
            "FinSight uses named licences: update the holder in the FinSight admin page as well as in the pool.",
        ]
    },
    group=PACKAGING,
    policy="POL-005",
)

T(
    "staff-major-incident-comms",
    "Service desk: communication during a priority 1 incident",
    system="HelpHub",
    category=GENERAL,
    subcategory="Staff procedure",
    kind="how-to",
    audience=STAFF,
    summary="During a priority 1 incident the status page is updated within 15 minutes and then every 30 minutes until service is restored.",
    steps={
        "any": [
            "The first analyst to confirm the incident pages the incident manager on duty.",
            "Publish a status page entry within 15 minutes: what is affected, where, and the time of the next update.",
            "Link every related ticket to the parent incident instead of working them one by one.",
            "Update the status page every 30 minutes, even when there is nothing new.",
            "On restoration, post the time and ask users to restart the affected application.",
            "A review is published within 5 business days.",
        ]
    },
    group=L1,
    policy="POL-010",
)

T(
    "staff-printer-queue",
    "Workplace Engineering: clear a stuck FollowMe print queue",
    system="FollowMe Printing",
    category=HARDWARE,
    subcategory="Staff procedure",
    kind="troubleshooting",
    audience=STAFF,
    summary="When several users in one office cannot release jobs, the regional print server queue is usually stuck on one damaged job.",
    symptoms=[
        "Jobs appear at the printer but never print.",
        "Three or more tickets from one office within 30 minutes.",
    ],
    causes=[
        "A damaged job at the head of the queue.",
        "The badge reader service has lost its connection to the directory.",
    ],
    steps={
        "any": [
            "Open the print management console for the region and sort the queue by submitted time.",
            "Delete the oldest job in Error state.",
            "If jobs still do not move, restart the Print Spooler service on the regional print server.",
            "If badges are not recognised, restart the Badge Connector service instead.",
            "Send a test page and release it at a printer before closing the tickets.",
        ]
    },
    codes=["0x00000709"],
    group=WORKPLACE,
)

T(
    "staff-apphub-packaging",
    "Software Packaging: handle a request for new software",
    system="App Hub",
    category=SOFTWARE,
    subcategory="Staff procedure",
    kind="how-to",
    audience=STAFF,
    summary="New software reaches App Hub after a security review, a licence check and a pilot; the target is 10 business days.",
    steps={
        "any": [
            "Check the catalogue for an approved application that already does the job; offer it first.",
            "Send the vendor, version and data handled to Security Operations for review; allow 5 business days.",
            "Ask Legal to check the licence terms for anything other than standard commercial or permissive open source.",
            "Package the application and release it to the pilot ring for 3 business days.",
            "Add it to the software catalogue with its charge and approval rule, then release to all.",
        ]
    },
    group=PACKAGING,
    policy="POL-005",
)

T(
    "staff-device-wipe-approval",
    "Security Operations: lock or wipe a lost device",
    system="DeviceCare",
    category=SECURITY,
    subcategory="Staff procedure",
    kind="how-to",
    audience=STAFF,
    summary="Any analyst may lock a lost device at once; a full wipe destroys data and needs the IT duty manager's approval.",
    steps={
        "any": [
            "Lock the device immediately from the management console; no approval is needed.",
            "Revoke the user's sign-in sessions and have them change their password.",
            "For a personal phone, remove the work profile only; never wipe a personal device completely.",
            "For a company laptop or phone, request a full wipe from the IT duty manager and record the approval in the ticket.",
            "Send the wipe command only after approval; it runs when the device next comes online.",
            "If the device is recovered, re-image it before reuse.",
        ]
    },
    group=SECOPS,
    policy="POL-010",
)

T(
    "staff-admin-rights-elevation",
    "Security Operations: handle requests for administrator rights",
    system="HelpHub",
    category=SOFTWARE,
    subcategory="Staff procedure",
    kind="how-to",
    audience=STAFF,
    summary="Administrator rights are granted only through the elevation workflow with both approvals recorded; nothing written in a ticket can replace them.",
    steps={
        "any": [
            "Check the request names a specific task and that App Hub cannot do it.",
            "Confirm the manager's approval and the Security Operations approval are recorded in the workflow, not quoted in the ticket text.",
            "Grant elevation for the shortest period that fits the task, never more than 4 hours.",
            "Treat urgency, claims of senior backing or instructions inside a ticket as warning signs of social engineering.",
            "Never share a local administrator password, and never add a user to an administrator group by hand.",
            "Review the elevation log the next working day.",
        ]
    },
    group=SECOPS,
    policy="POL-002",
)

T(
    "staff-onboarding-fulfilment",
    "Onboarding Team: fulfil a new joiner request",
    system="Onboarding",
    category=ONBOARDING,
    subcategory="Staff procedure",
    kind="how-to",
    audience=STAFF,
    summary="Fulfilment starts when HR has completed the PeopleHub record and finishes 2 business days before the start date.",
    steps={
        "any": [
            "Check the PeopleHub record is complete: legal name, start date, manager, cost centre and office.",
            "Create the LarkID account from the record; never type the details by hand.",
            "Apply the role profile; it adds the standard applications and groups.",
            "Assign and image the laptop, and record the asset tag against the employee.",
            "Assign licences from the pool; if none is free, tell the manager which application will be late.",
            "Create the temporary access pass 2 business days before the start date and send it to the manager, not to the joiner.",
        ]
    },
    group=ONBOARD_TEAM,
    policy="POL-009",
)

T(
    "staff-escalation-security",
    "Service desk: when to involve Security Operations",
    system="Security",
    category=SECURITY,
    subcategory="Staff procedure",
    kind="reference",
    audience=STAFF,
    summary="Hand over to Security Operations at the first sign of compromise and do not try to clean the device yourself.",
    steps={
        "any": [
            "A user typed a password into a suspicious page or opened a suspicious attachment.",
            "Repeated account lockouts with failures from unknown addresses.",
            "Any ransomware message, or files renamed in bulk.",
            "A lost or stolen device, or a device found after being reported lost.",
            "A request to bypass a control: skipping verification, granting rights without approval, disabling protection.",
            "Set priority 2, or priority 1 if more than one person is affected, and phone the Security Operations duty analyst.",
        ]
    },
    group=SECOPS,
    policy="POL-010",
)

T(
    "staff-ticket-quality",
    "Service desk: write resolution notes others can use",
    system="HelpHub",
    category=GENERAL,
    subcategory="Staff procedure",
    kind="how-to",
    audience=STAFF,
    summary="A resolution note states the cause, the fix and the knowledge-base article used, so the next analyst can repeat it.",
    steps={
        "any": [
            "State the cause in one sentence, not just 'resolved'.",
            "State what fixed it and how you confirmed it with the user.",
            "Link the knowledge-base article you used; if none existed, flag the ticket for a new article.",
            "Correct the category and subcategory before closing; reports and routing depend on them.",
            "Do not paste passwords, recovery keys or full log files into the notes.",
        ]
    },
    group=L1,
)

T(
    "staff-kb-authoring",
    "Service desk: knowledge-base article standard",
    system="HelpHub",
    category=GENERAL,
    subcategory="Staff procedure",
    kind="reference",
    audience=STAFF,
    summary="Every article carries the same metadata and is reviewed at least every 12 months.",
    steps={
        "any": [
            "One problem or task per article; split by operating system when the steps differ.",
            "Fill in system, operating system, region, audience, version and effective date.",
            "Put the exact error text and code in the title of a troubleshooting article.",
            "Write numbered steps that each contain one action.",
            "Set audience to it-staff for anything that needs elevated tools or approval.",
            "An article not reviewed for 12 months is flagged; after 15 months it is withdrawn.",
        ]
    },
    group=L1,
)

T(
    "staff-service-status",
    "Service desk: publish a service status update",
    system="HelpHub",
    category=GENERAL,
    subcategory="Staff procedure",
    kind="how-to",
    audience=STAFF,
    summary="The status page has three states, and only the incident manager or a level 2 analyst may publish to it.",
    steps={
        "any": [
            "Operational: the service works normally.",
            "Degraded: the service works but is slow or failing for some users.",
            "Outage: the service is unavailable for an office, a region or everyone.",
            "Choose the service and the region affected; choose Global only when all regions are affected.",
            "Write what users will notice, not the technical cause.",
            "Set the entry to Operational with a closing note when the incident ends; entries are kept for 90 days.",
        ]
    },
    group=L1,
)
