"""Knowledge-base topics: software, updates and security."""

from datagen.model import GENERAL, PACKAGING, SECOPS, SECURITY, SOFTWARE, K, T

T(
    "apphub-install",
    "Install software from App Hub",
    system="App Hub",
    category=SOFTWARE,
    subcategory="Installation",
    kind="how-to",
    summary="App Hub installs approved software without administrator rights; anything not listed there must be requested.",
    steps={
        "windows": [
            "Open App Hub from the Start menu.",
            "Search for the application and choose Install; free applications install at once.",
            "Applications marked Licence required open a request form instead; see Request licensed software.",
            "Keep the laptop awake and online until the status shows Installed.",
            "If an installation stays at Pending for more than 30 minutes, restart and choose Retry.",
        ],
        "macos": [
            "Open App Hub from Launchpad or the Applications folder.",
            "Search for the application and choose Install; free applications install at once.",
            "Applications marked Licence required open a request form instead; see Request licensed software.",
            "Enter your Mac password only if App Hub itself asks for it; never for an installer downloaded from the web.",
            "If an installation stays at Pending for more than 30 minutes, restart and choose Retry.",
        ],
    },
    group=PACKAGING,
    policy="POL-005",
    ticket=K(
        shorts=[
            "Need software installed",
            "How do I install an application",
            "App Hub install stuck on pending",
            "Please install Zoom",
        ],
        descs=[
            "I need a PDF editor installed on my {os} laptop and I do not have admin rights.",
            "App Hub has been showing pending for an hour for the app I selected.",
            "Can you install the screenshot tool for me? It asks for an administrator password.",
        ],
        fixes=[
            "Application is available in App Hub. User installed it without admin rights.",
            "Installation was waiting for a restart. Restarted and retried; installed.",
        ],
        weight=2.0,
        priority=(0, 2, 55, 43),
    ),
)

T(
    "licensed-software-request",
    "Request licensed software",
    system="HelpHub",
    category=SOFTWARE,
    subcategory="Licence request",
    kind="how-to",
    summary="Licensed software is requested in HelpHub; the approvals needed depend on the annual charge shown in the software catalogue.",
    steps={
        "any": [
            "Look up the application in the software catalogue to see its annual charge and approval rule.",
            "In HelpHub choose Request software, pick the application and give the business reason.",
            "Charges under USD 300 a year need your manager's approval.",
            "Charges of USD 300 a year or more need your manager and your cost-centre owner.",
            "Applications that handle Restricted data also need the data owner.",
            "After the last approval the application appears in App Hub within 60 minutes.",
            "A licence not used for 60 days is reclaimed; you are warned by email 7 days before.",
        ]
    },
    notes=[
        "Software that is not in the catalogue needs a security and legal review, which takes up to 10 business days."
    ],
    group=PACKAGING,
    policy="POL-005",
    ticket=K(
        shorts=[
            "Request Visio licence",
            "Need Tableau",
            "Software licence request",
            "Adobe Acrobat Pro licence",
            "Licence was removed",
        ],
        descs=[
            "I need a Visio licence for process mapping. Who approves it?",
            "Please install Tableau Desktop, my manager has agreed.",
            "My Acrobat Pro licence disappeared, I had it last month.",
        ],
        fixes=[
            "Raised the software request. Manager and cost-centre owner approved; application delivered through App Hub.",
            "Licence had been reclaimed after 60 days without use. User re-requested; manager approved.",
            "No free licence in the pool. Request queued until a licence was reclaimed two days later.",
        ],
        weight=2.0,
        priority=(0, 2, 53, 45),
    ),
)

T(
    "install-0x80070005",
    "Software installation fails with error 0x80070005",
    system="App Hub",
    category=SOFTWARE,
    subcategory="Installation",
    kind="troubleshooting",
    summary="Error 0x80070005 means 'Access is denied': the installer tried to change something a standard user account is not allowed to change.",
    symptoms=[
        "An installer stops with 'Error 0x80070005: Access is denied'.",
        "An App Hub installation ends with Failed (0x80070005).",
    ],
    causes=[
        "The installer was downloaded from the web instead of installed from App Hub.",
        "A previous version of the application is still running.",
        "A pending restart is locking system files.",
    ],
    steps={
        "windows": [
            "Do not look for an administrator password; install the application from App Hub instead.",
            "If the App Hub installation fails with the same code, close every window of the application and its tray icon.",
            "Restart the laptop to clear pending updates.",
            "In App Hub open Settings and choose Reset cache, then Install again.",
            "If it still fails, raise a ticket for Software Packaging with the application name and the time of the attempt.",
        ]
    },
    codes=["0x80070005"],
    group=PACKAGING,
    policy="POL-005",
    ticket=K(
        shorts=[
            "Install error 0x80070005",
            "Access is denied when installing",
            "Visio install fails 0x80070005",
        ],
        descs=[
            "I am getting error {code} when installing Visio.",
            "Installer says access is denied. I downloaded it from the vendor site.",
            "App Hub shows failed {code} for the reporting add-in.",
        ],
        fixes=[
            "User had downloaded the installer from the web. Installed the packaged version from App Hub.",
            "Old version was still running in the tray. Closed it, reset the App Hub cache and reinstalled.",
        ],
        weight=1.1,
        priority=(0, 3, 62, 35),
    ),
)

T(
    "windows-update-0x800f0922",
    "Windows Update fails with error 0x800F0922",
    system="Windows",
    category=SOFTWARE,
    subcategory="Updates",
    kind="troubleshooting",
    summary="Error 0x800F0922 means the update could not be completed, most often because the laptop could not reach the update service or is short of disk space.",
    symptoms=[
        "Windows Update shows 'Some update files were not installed. 0x800F0922'.",
        "The same update fails after every restart.",
    ],
    causes=[
        "The laptop is not on the office network or VPN while the update downloads.",
        "Less than 10 GB of free disk space.",
        "A VPN drop during installation.",
    ],
    steps={
        "windows": [
            "Connect to the office network, or start SecureTunnel on a stable connection.",
            "Free disk space until at least 10 GB is available.",
            "Restart, open Settings, Windows Update and choose Retry.",
            "If it fails again, open App Hub and run Repair Windows Update, then restart.",
            "If the update still fails, raise a ticket; a laptop more than 30 days behind is blocked from the VPN.",
        ]
    },
    codes=["0x800F0922"],
    group=PACKAGING,
    policy="POL-004",
    ticket=K(
        shorts=[
            "Windows update error 0x800F0922",
            "Updates keep failing",
            "Update will not install",
        ],
        descs=[
            "Windows Update keeps failing with {code} on my {model}.",
            "The same update has failed five times and now the VPN warns me about compliance.",
        ],
        fixes=[
            "Disk had 3 GB free. Cleared space, ran Repair Windows Update from App Hub and the cumulative update installed."
        ],
        weight=1.2,
        priority=(0, 5, 65, 30),
    ),
)

T(
    "macos-update-stuck",
    "macOS update does not install",
    system="macOS",
    category=SOFTWARE,
    subcategory="Updates",
    kind="troubleshooting",
    summary="macOS updates need the charger connected and about 25 GB free; major new versions appear only after IT has approved them.",
    symptoms=[
        "The update downloads and then nothing happens.",
        "Software Update shows 'An error occurred while installing'.",
    ],
    causes=[
        "Too little free disk space.",
        "The Mac is on battery power.",
        "The version is a major release that IT has not approved yet.",
    ],
    steps={
        "macos": [
            "Connect the charger and free disk space until 25 GB is available.",
            "Restart the Mac, open System Settings, General, Software Update and choose Update Now.",
            "Leave the lid open until the Mac has restarted on its own.",
            "A major new macOS version is offered about 60 days after Apple releases it; before that it is hidden on purpose.",
            "If a security update fails twice, raise a ticket.",
        ]
    },
    group=PACKAGING,
    policy="POL-004",
    ticket=K(
        shorts=["macOS update stuck", "Cannot update my Mac", "Update fails on MacBook"],
        descs=[
            "The macOS update fails every night on my {model}.",
            "Why can I not see the new macOS version that came out last month?",
        ],
        fixes=[
            "Only 9 GB free. Cleared space and the update installed.",
            "Explained that major versions are released after about 60 days of testing.",
        ],
        weight=0.5,
        priority=(0, 2, 58, 40),
    ),
)

T(
    "browser-cache-extensions",
    "Fix a website that does not load or display properly",
    system="Browser",
    category=SOFTWARE,
    subcategory="Browser",
    kind="troubleshooting",
    summary="Clearing saved site data fixes most web application problems; only extensions from the approved list can be installed.",
    symptoms=[
        "A web application shows a blank page, an endless spinner or an old version.",
        "A site works in a private window but not in a normal one.",
    ],
    causes=[
        "Out-of-date cached files or cookies.",
        "A browser extension interfering with the page.",
    ],
    steps={
        "any": [
            "Open the site in a private or InPrivate window. If it works there, continue below.",
            "Press Ctrl + Shift + Delete (Cmd + Shift + Delete on a Mac), choose Cached images and files and Cookies for the last 7 days, and clear.",
            "Turn off extensions one at a time to find the one that breaks the page.",
            "Try the other supported browser; Chrome and Edge are both supported.",
            "Extensions come only from the approved list in the browser's managed store. Request a new one through HelpHub.",
        ]
    },
    ticket=K(
        shorts=[
            "Website not loading",
            "HelpHub page blank",
            "Web app stuck on loading",
            "Chrome extension blocked",
        ],
        descs=[
            "The expenses site shows a blank page in Chrome but my colleague can open it.",
            "I cannot install a browser extension, it says blocked by your administrator.",
        ],
        fixes=[
            "Cleared cached files and cookies; the site loaded.",
            "Extension is not on the approved list. User raised a request for review.",
        ],
        weight=1.0,
        priority=(0, 2, 58, 40),
    ),
)

T(
    "unapproved-software",
    "You received an 'Unapproved software detected' notice",
    system="EndpointShield",
    category=SOFTWARE,
    subcategory="Compliance",
    kind="how-to",
    summary="The notice means software that is not in the catalogue was found on your laptop; remove it or ask for it to be reviewed within 5 business days.",
    steps={
        "any": [
            "Read the notice for the name of the application.",
            "If you do not need it, uninstall it; the notice closes at the next daily scan.",
            "If you need it for work, reply to the notice with the business reason; a review takes up to 10 business days.",
            "Personal licences, trial versions and software from home must not be installed on company laptops.",
            "After 5 business days with no action the application is removed automatically.",
        ]
    },
    group=PACKAGING,
    policy="POL-005",
    ticket=K(
        shorts=[
            "Unapproved software notice",
            "Email says unapproved software detected",
            "Why was my app removed",
        ],
        descs=[
            "I got an email saying unapproved software was detected. It is a tool I use every day.",
            "An application I installed disappeared from my laptop overnight.",
        ],
        fixes=[
            "Tool is not in the catalogue. User submitted it for review; alternative from App Hub suggested in the meantime."
        ],
        weight=0.4,
        priority=(0, 0, 50, 50),
    ),
)

T(
    "admin-rights-request",
    "Request temporary administrator rights",
    system="HelpHub",
    category=SOFTWARE,
    subcategory="Admin rights",
    kind="how-to",
    summary="Nobody has permanent administrator rights on a laptop; rights can be granted for up to 4 hours with two approvals.",
    steps={
        "any": [
            "First check App Hub; most needs are met by a packaged application and need no rights at all.",
            "In HelpHub choose Request temporary admin rights and describe exactly what you need to do.",
            "Your manager approves first, then Security Operations.",
            "When approved, choose Elevate in App Hub; the rights last 4 hours and everything done with them is logged.",
            "The service desk cannot grant administrator rights on request, by phone, chat or ticket text, without both approvals.",
        ]
    },
    notes=["Requests that name no specific task are declined."],
    group=SECOPS,
    policy="POL-002",
    ticket=K(
        shorts=[
            "Need admin rights",
            "Request local administrator",
            "Make me admin on my laptop",
            "Admin password for install",
        ],
        descs=[
            "I need local admin rights on my laptop to install developer tools.",
            "Please make me an administrator, it is urgent and my director said it is fine.",
            "Can I have the admin password just for today?",
        ],
        fixes=[
            "Explained that permanent rights are not granted. User raised a temporary elevation request with a specific task; approved by manager and Security Operations.",
            "The tools were available in App Hub. No elevation needed.",
        ],
        weight=0.9,
        priority=(0, 3, 57, 40),
    ),
)

T(
    "endpoint-protection-alert",
    "EndpointShield quarantined a file (alert ES-QUAR-21)",
    system="EndpointShield",
    category=SECURITY,
    subcategory="Endpoint protection",
    kind="troubleshooting",
    summary="ES-QUAR-21 means EndpointShield blocked a file it considers malicious and moved it to quarantine; no action is needed unless the file was legitimate.",
    symptoms=["A notification says 'Threat quarantined. ES-QUAR-21' with a file name."],
    causes=[
        "A malicious attachment or download.",
        "Occasionally, a legitimate tool that behaves like malware, such as a script or macro.",
    ],
    steps={
        "any": [
            "Do not try to restore the file yourself.",
            "Note the file name and where it came from: an email, a website or a USB stick.",
            "If it came from an email, report that email with the Report phishing button.",
            "If you believe the file is legitimate work material, raise a ticket for Security Operations with the file name and the alert time.",
            "If alerts repeat or the laptop behaves strangely, follow the article What to do if you suspect malware.",
        ]
    },
    codes=["ES-QUAR-21"],
    group=SECOPS,
    policy="POL-010",
    ticket=K(
        shorts=[
            "EndpointShield threat quarantined",
            "Antivirus alert ES-QUAR-21",
            "Security pop-up about a file",
        ],
        descs=[
            "EndpointShield showed threat quarantined {code} when I opened an invoice attachment.",
            "My macro workbook was quarantined and I need it back for month-end.",
        ],
        fixes=[
            "File was a malicious attachment. Email reported and removed from other mailboxes. No further action on the device.",
            "File reviewed by Security Operations and confirmed safe. Released from quarantine and excluded by hash.",
        ],
        weight=1.0,
        priority=(0, 30, 60, 10),
    ),
)

T(
    "phishing-report",
    "Report a suspicious email",
    system="Email",
    category=SECURITY,
    subcategory="Phishing",
    kind="how-to",
    summary="Use the Report phishing button for any suspicious email; if you clicked a link or typed your password, also call the service desk at once.",
    steps={
        "any": [
            "Do not click links, open attachments or reply.",
            "Select the message and choose Report phishing in the Outlook toolbar; the message moves out of your inbox.",
            "If you already clicked a link or opened an attachment, call the service desk now; this is handled as priority 2.",
            "If you typed your password on the page, change it at https://id.larkhaven.example/reset before doing anything else.",
            "Security Operations replies within 1 hour to say whether the email was malicious.",
        ]
    },
    notes=[
        "Do not forward suspicious emails to colleagues or to the service desk; forwarding spreads the risk."
    ],
    group=SECOPS,
    policy="POL-010",
    ticket=K(
        shorts=[
            "Suspicious email",
            "Phishing email received",
            "I clicked a link in a strange email",
            "Is this email genuine",
        ],
        descs=[
            "I received an email asking me to confirm my password for a mailbox upgrade. It looks odd.",
            "I think I clicked on a phishing link and entered my password. What should I do?",
            "Got a strange invoice email from a supplier I do not know.",
        ],
        fixes=[
            "Email confirmed as phishing and removed from 42 mailboxes. User had not clicked.",
            "User had entered credentials. Password reset, sessions revoked and sign-in logs reviewed; no suspicious activity found.",
        ],
        weight=2.0,
        priority=(1, 35, 50, 14),
    ),
)

T(
    "suspected-malware",
    "What to do if you suspect malware",
    system="Security",
    category=SECURITY,
    subcategory="Malware",
    kind="how-to",
    summary="If a laptop shows signs of malware, take it off the network, leave it switched on and call the service desk.",
    steps={
        "any": [
            "Disconnect from the network: turn off Wi-Fi and unplug the network cable and dock.",
            "Leave the laptop switched on; switching it off destroys evidence.",
            "Call the service desk from a phone; do not use the affected laptop to raise the ticket.",
            "Do not pay, click or type anything that the laptop demands.",
            "Security Operations isolates the laptop and tells you when it is safe to use.",
        ]
    },
    symptoms=[
        "Files renamed or impossible to open.",
        "Pop-ups demanding payment.",
        "The mouse moving or windows opening by themselves.",
    ],
    group=SECOPS,
    policy="POL-010",
    ticket=K(
        shorts=[
            "Possible virus",
            "Laptop behaving strangely pop-ups",
            "Ransom message on screen",
            "Think my laptop is infected",
        ],
        descs=[
            "Strange pop-ups keep appearing and my files have odd names.",
            "My browser keeps redirecting to adverts and the laptop is acting strangely.",
        ],
        fixes=[
            "Laptop isolated by Security Operations. Adware removed and browser reset; device returned to service.",
            "Device isolated and re-imaged. Files restored from OneDrive.",
        ],
        weight=0.8,
        priority=(4, 56, 35, 5),
    ),
)

T(
    "usb-storage",
    "Using USB storage devices",
    system="EndpointShield",
    category=SECURITY,
    subcategory="Removable media",
    kind="how-to",
    summary="USB sticks and drives are read-only on company laptops; writing to them needs an approved exception and a company-issued encrypted stick.",
    steps={
        "any": [
            "You can read files from any USB storage device; they are scanned when opened.",
            "Copying files to USB storage is blocked by default.",
            "If you must write to USB for work, raise a HelpHub request for a removable media exception.",
            "Your manager and Security Operations approve; exceptions last at most 90 days.",
            "Use only the encrypted stick IT issues with the exception. Restricted data must never be copied to removable media.",
        ]
    },
    group=SECOPS,
    policy="POL-007",
    ticket=K(
        shorts=["USB stick blocked", "Cannot copy files to USB drive", "Need USB write access"],
        descs=[
            "I cannot copy a presentation to a USB stick for the conference.",
            "My external drive shows as read-only on the work laptop.",
        ],
        fixes=[
            "Explained that USB write is blocked by policy. User will share by SendSafe instead; no exception needed."
        ],
        weight=0.4,
        priority=(0, 3, 57, 40),
    ),
)

T(
    "data-classification-guide",
    "Data classification quick guide",
    system="Policy",
    category=GENERAL,
    subcategory="Policy question",
    kind="reference",
    summary="Every document belongs to one of four classes, and the class decides where it may be stored and with whom it may be shared.",
    steps={
        "any": [
            "Public: approved for anyone, such as published brochures. No restrictions.",
            "Internal: everyday business information. Share freely inside the company; not outside without a reason.",
            "Confidential: contracts, pricing, personal data. Share only with people who need it; outside the company only by SendSafe.",
            "Restricted: financial results before publication, payroll, security details. Named people only; never on removable media or personal devices.",
            "If you are unsure, treat the document as Confidential and ask the data owner.",
        ]
    },
    policy="POL-007",
    ticket=K(
        shorts=[
            "Data classification question",
            "Can I share this file externally",
            "Where can I store confidential files",
        ],
        descs=[
            "Am I allowed to send a customer contract to an outside lawyer by email?",
            "What label should I use for a budget spreadsheet?",
        ],
        fixes=[
            "Advised Confidential classification and SendSafe for the external transfer. Shared the quick guide."
        ],
        weight=0.3,
        priority=(0, 0, 35, 65),
    ),
)

T(
    "travel-with-devices",
    "Travelling abroad with company devices",
    system="Policy",
    category=GENERAL,
    subcategory="Travel",
    kind="how-to",
    summary="Tell IT before travelling to a high-risk country; you may be given a loan laptop and phone for the trip.",
    steps={
        "any": [
            "Check the high-risk country list on the intranet travel page.",
            "For a listed country, raise a HelpHub travel request at least 5 business days before departure.",
            "IT issues a clean loan laptop and phone; your own devices stay at home.",
            "Use only SecureTunnel on hotel, airport and conference Wi-Fi.",
            "Keep devices with you; do not leave them in hotel rooms or checked baggage.",
            "Return loan devices within 2 business days of coming back; they are wiped.",
        ]
    },
    policy="POL-006",
    ticket=K(
        shorts=[
            "Travelling abroad with laptop",
            "Loan laptop for business trip",
            "Can I take my work laptop overseas",
        ],
        descs=[
            "I am travelling to a customer site abroad next month. Do I need to do anything about my laptop?",
            "I need a loan laptop for a trip in two weeks.",
        ],
        fixes=[
            "Destination is on the high-risk list. Travel request raised; loan laptop and phone prepared for collection."
        ],
        weight=0.5,
        priority=(0, 2, 48, 50),
    ),
)
