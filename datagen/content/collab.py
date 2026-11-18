"""Knowledge-base topics: email, calendar, Teams and files."""

from datagen.model import EMAIL, MESSAGING, K, T

T(
    "email-on-phone",
    "Set up work email on your phone",
    system="Email",
    category=EMAIL,
    subcategory="Mobile email",
    kind="how-to",
    summary="Work email on a phone needs the phone enrolled in DeviceCare and the Outlook app; the built-in mail app is blocked.",
    steps={
        "ios": [
            "Install DeviceCare from the App Store and sign in with LarkID to enrol the phone.",
            "Accept the management profile in Settings, General, VPN and Device Management.",
            "Install Outlook from the App Store.",
            "Open Outlook, add your work address and sign in with LarkID.",
            "Set a 6-digit passcode if the phone asks; shorter passcodes are not accepted.",
        ],
        "android": [
            "Install DeviceCare from Google Play and sign in with LarkID to create the work profile.",
            "Open the work profile's Play Store, marked with a briefcase, and install Outlook.",
            "Open the work copy of Outlook, add your work address and sign in with LarkID.",
            "Set a 6-digit screen lock if the phone asks; patterns are not accepted.",
        ],
    },
    notes=[
        "Enrolment lets IT remove work data from the phone. It does not show IT your photos, messages or personal apps."
    ],
    group=MESSAGING,
    policy="POL-008",
    ticket=K(
        shorts=["Email on phone", "Cannot add work email to phone", "Outlook mobile setup"],
        descs=[
            "How do I get work email on my {os} phone? The normal mail app refuses my account.",
            "Outlook on my phone says the device must be managed.",
        ],
        fixes=[
            "Phone was not enrolled. Enrolled it in DeviceCare, installed Outlook from the work profile and mail synced."
        ],
        weight=1.3,
        priority=(0, 2, 53, 45),
    ),
)

T(
    "outlook-0x800ccc0e",
    "Outlook cannot connect to the server (error 0x800CCC0E)",
    system="Outlook",
    category=EMAIL,
    subcategory="Outlook",
    kind="troubleshooting",
    summary="Error 0x800CCC0E means Outlook on Windows could not reach the mail server; the mail profile or the network path is at fault.",
    symptoms=[
        "Send and receive fails with 0x800CCC0E.",
        "The status bar shows Disconnected or Trying to connect.",
    ],
    causes=[
        "Work Offline is switched on.",
        "A damaged Outlook profile.",
        "A proxy or security add-in is blocking the connection.",
    ],
    steps={
        "windows": [
            "Open https://outlook.larkhaven.example in a browser. If webmail works, the mailbox is healthy.",
            "In Outlook open the Send / Receive tab and make sure Work Offline is not highlighted.",
            "Close Outlook, hold Ctrl while starting it, and choose Yes to start in safe mode. If it connects, disable add-ins one at a time.",
            "Open Control Panel, Mail, Show Profiles, add a new profile and set it as default.",
            "Start Outlook and let the mailbox synchronise; a large mailbox can take an hour.",
        ]
    },
    codes=["0x800CCC0E"],
    group=MESSAGING,
    ticket=K(
        shorts=[
            "Outlook error 0x800CCC0E",
            "Outlook disconnected",
            "Outlook cannot connect to server",
        ],
        descs=[
            "Outlook shows {code} when I send and receive. Webmail works.",
            "Outlook has been stuck on trying to connect since I came back from lunch.",
            "No new mail in Outlook since yesterday, the bottom bar says disconnected.",
        ],
        fixes=[
            "Work Offline was enabled. Turned it off and mail flowed.",
            "Profile was damaged. Created a new Outlook profile and the mailbox synchronised.",
        ],
        weight=1.5,
        priority=(0, 8, 67, 25),
    ),
)

T(
    "outlook-password-prompts",
    "Outlook keeps asking for your password",
    system="Outlook",
    category=EMAIL,
    subcategory="Outlook",
    kind="troubleshooting",
    summary="Repeated password prompts in Outlook come from a saved old password or a sign-in session that expired.",
    symptoms=[
        "A password box appears every few minutes.",
        "Typing the correct password makes the box come back.",
    ],
    causes=[
        "The LarkID password was changed recently.",
        "Outlook is signed in with a cached session that has expired.",
    ],
    steps={
        "windows": [
            "Close Outlook and Teams.",
            "Open Credential Manager, Windows Credentials, and remove entries that start with MicrosoftOffice or contain larkhaven.example.",
            "Start Outlook and sign in once with LarkID, approving the prompt on your phone.",
            "If the prompt returns, open File, Office Account, Sign out, then sign in again.",
        ],
        "macos": [
            "Quit Outlook and Teams.",
            "Open Keychain Access, search for Exchange and for larkhaven.example, and delete the matching entries.",
            "Start Outlook and sign in once with LarkID, approving the prompt on your phone.",
            "If the prompt returns, open Outlook, Settings, Accounts, remove the account and add it again.",
        ],
    },
    group=MESSAGING,
    ticket=K(
        shorts=[
            "Outlook keeps asking for password",
            "Password prompt in Outlook will not go away",
            "Outlook needs password loop",
        ],
        descs=[
            "Outlook asks for my password every five minutes on my {os} laptop. I type it and it asks again.",
            "After the password change Outlook will not stop prompting me.",
        ],
        fixes=[
            "Removed stale saved credentials and signed in again with LarkID. No further prompts."
        ],
        weight=1.5,
        priority=(0, 5, 65, 30),
    ),
)

T(
    "mailbox-full",
    "Mailbox is full or nearly full",
    system="Email",
    category=EMAIL,
    subcategory="Mailbox",
    kind="how-to",
    summary="Mailboxes hold 50 GB; at 49 GB you are warned and at 50 GB you can no longer send.",
    steps={
        "any": [
            "In Outlook open File, Tools, Mailbox Cleanup to see which folders are largest.",
            "Sort the largest folder by size and delete or save big attachments to OneDrive.",
            "Empty Deleted Items and Junk Email.",
            "Mail older than 24 months moves to your Online Archive automatically; check it has not been turned off.",
            "If you are still above 45 GB, raise a ticket to have the archive start at 12 months.",
        ]
    },
    group=MESSAGING,
    ticket=K(
        shorts=["Mailbox full", "Cannot send email mailbox over limit", "Mailbox quota warning"],
        descs=[
            "I get a warning that my mailbox is almost full and now I cannot send.",
            "Please increase my mailbox size, I am at the limit.",
        ],
        fixes=[
            "Explained that quota is fixed at 50 GB. Emptied Deleted Items and enabled the 12-month archive policy; usage dropped to 31 GB."
        ],
        weight=0.9,
        priority=(0, 5, 60, 35),
    ),
)

T(
    "calendar-delegate",
    "Share your calendar or give someone delegate access",
    system="Email",
    category=EMAIL,
    subcategory="Calendar",
    kind="how-to",
    summary="You control who sees or manages your calendar; IT does not need to be involved.",
    steps={
        "any": [
            "In Outlook open Calendar, right-click your calendar and choose Sharing Permissions.",
            "Add the person and choose Can view all details, or Can edit.",
            "For someone who sends invitations for you, choose Delegate and decide whether they see private items.",
            "The other person accepts the sharing invitation that arrives by email.",
            "Remove a person from the same screen when they no longer need access.",
        ]
    },
    ticket=K(
        shorts=[
            "Calendar delegate access",
            "Share calendar with assistant",
            "Cannot see manager calendar details",
        ],
        descs=[
            "My assistant needs to manage my calendar and send invitations for me.",
            "I can only see busy and free on my manager's calendar, not the details.",
        ],
        fixes=[
            "Showed the user how to grant delegate access from Sharing Permissions. Delegate confirmed they can create meetings."
        ],
        weight=0.7,
        priority=(0, 2, 45, 53),
    ),
)

T(
    "recover-deleted",
    "Recover a deleted email or file",
    system="Email",
    category=EMAIL,
    subcategory="Recovery",
    kind="how-to",
    summary="Deleted email can be recovered for 30 days and deleted OneDrive files for 93 days, without a ticket.",
    steps={
        "any": [
            "Email: open Deleted Items and move the message back to your inbox.",
            "If it is not there, choose Recover items recently removed from this folder at the top of Deleted Items.",
            "Files: open OneDrive in a browser, choose Recycle bin, select the file and choose Restore.",
            "For an earlier version of a file, right-click it in OneDrive and choose Version history.",
            "After these periods the item cannot be recovered by IT either.",
        ]
    },
    group=MESSAGING,
    ticket=K(
        shorts=[
            "Recover deleted email",
            "Deleted file by mistake",
            "Need to restore a folder I deleted",
        ],
        descs=[
            "I deleted an important email thread last week and emptied the bin. Can it be recovered?",
            "I overwrote a spreadsheet in OneDrive and need yesterday's version.",
        ],
        fixes=[
            "Recovered the messages from Recover items recently removed. Within the 30-day window.",
            "Restored the previous version from OneDrive version history.",
        ],
        weight=0.9,
        priority=(0, 5, 55, 40),
    ),
)

T(
    "teams-signin-caa70004",
    "Teams sign-in fails with error caa70004",
    system="Microsoft Teams",
    category=EMAIL,
    subcategory="Teams",
    kind="troubleshooting",
    summary="Error caa70004 appears when Teams on Windows cannot complete sign-in, usually because of a damaged cache.",
    symptoms=[
        "Teams shows 'We're sorry, we've run into an issue' with error code caa70004.",
        "Teams in the browser works.",
    ],
    causes=[
        "A damaged Teams cache.",
        "The laptop date or time is wrong.",
        "Another work account is signed in to Windows.",
    ],
    steps={
        "windows": [
            "Check that Teams works at https://teams.microsoft.com in a browser.",
            "Right-click the Teams icon in the system tray and choose Quit.",
            "Open Settings, Apps, Installed apps, Microsoft Teams, Advanced options, and choose Reset.",
            "Check the date, time and time zone are set automatically.",
            "Start Teams and sign in with LarkID.",
        ]
    },
    codes=["caa70004"],
    group=MESSAGING,
    ticket=K(
        shorts=["Teams error caa70004", "Cannot sign in to Teams", "Teams stuck on sign in"],
        descs=[
            "Teams will not sign in, it shows error code {code}. The web version is fine.",
            "Teams desktop app stuck on we've run into an issue since the update.",
        ],
        fixes=["Reset the Teams app from Installed apps and signed in again with LarkID. Working."],
        weight=1.2,
        priority=(0, 8, 67, 25),
    ),
)

T(
    "teams-camera-mic",
    "Camera or microphone does not work in Teams",
    system="Microsoft Teams",
    category=EMAIL,
    subcategory="Teams",
    kind="troubleshooting",
    summary="Teams needs permission from the operating system to use the camera and microphone, and the right device must be selected.",
    symptoms=[
        "Others cannot hear or see you.",
        "Teams shows a crossed-out camera or 'No microphone found'.",
    ],
    causes=[
        "Privacy settings block the camera or microphone.",
        "Teams is using the wrong device, such as a dock with no microphone.",
        "Another app is using the camera.",
    ],
    steps={
        "windows": [
            "In Teams open Settings, Devices, and choose the right speaker, microphone and camera; make a test call.",
            "Open Windows Settings, Privacy and security, Camera, and turn on Let desktop apps access your camera. Do the same for Microphone.",
            "Close other apps that use the camera, such as Zoom or the Camera app.",
            "Unplug and reconnect a USB headset or dock.",
            "Slide open the privacy shutter above the screen if the picture is black.",
        ],
        "macos": [
            "In Teams open Settings, Devices, and choose the right speaker, microphone and camera; make a test call.",
            "Open System Settings, Privacy and Security, Camera, and turn on Microsoft Teams. Do the same for Microphone.",
            "Quit and reopen Teams; macOS applies the permission only after a restart of the app.",
            "Close other apps that use the camera.",
        ],
    },
    group=MESSAGING,
    ticket=K(
        shorts=[
            "Teams microphone not working",
            "Camera not working in Teams",
            "Nobody can hear me in meetings",
        ],
        descs=[
            "Nobody can hear me in Teams meetings on my {os} laptop. The headset works for music.",
            "My camera shows a black screen in Teams.",
            "Teams says no microphone found since I got the new dock.",
        ],
        fixes=[
            "Teams was using the dock audio device. Selected the headset in Devices; test call passed.",
            "Camera permission was off in privacy settings. Enabled it and restarted Teams.",
        ],
        weight=1.7,
        priority=(0, 8, 67, 25),
    ),
)

T(
    "screen-share-black-macos",
    "Screen sharing shows a black screen on macOS",
    system="Microsoft Teams",
    category=EMAIL,
    subcategory="Teams",
    kind="troubleshooting",
    summary="On a Mac, meeting apps can share the screen only after they are allowed under Screen Recording in System Settings.",
    symptoms=[
        "Participants see a black or frozen window when you share.",
        "Only the desktop background is shared, without windows.",
    ],
    causes=["Screen recording permission was never granted or was reset by a macOS update."],
    steps={
        "macos": [
            "Open System Settings, Privacy and Security, Screen and System Audio Recording.",
            "Turn on Microsoft Teams, and your browser if you join meetings in the browser.",
            "Choose Quit and Reopen when macOS offers it.",
            "Start a test meeting and share a single window first.",
        ]
    },
    group=MESSAGING,
    ticket=K(
        shorts=[
            "Screen share black on Mac",
            "Cannot share screen in Teams on macOS",
            "Participants see black screen when I present",
        ],
        descs=[
            "When I share my screen on my {model} everyone sees black.",
            "Screen sharing stopped working after the macOS update.",
        ],
        fixes=[
            "Screen recording permission for Teams was off after the macOS update. Enabled it and restarted Teams."
        ],
        weight=0.7,
        priority=(0, 8, 67, 25),
    ),
)

T(
    "onedrive-sync",
    "OneDrive is not syncing",
    system="OneDrive",
    category=EMAIL,
    subcategory="OneDrive",
    kind="troubleshooting",
    summary="OneDrive stops syncing when it cannot sign in, when a file name is not allowed, or when the disk is full.",
    symptoms=[
        "The cloud icon shows a red cross or arrows that never finish.",
        "On Windows, 'There was a problem connecting to OneDrive' with error 0x8004de40.",
    ],
    causes=[
        "An expired sign-in.",
        "File names with characters such as * : < > ? or a path longer than 400 characters.",
        "Less than 1 GB of free disk space.",
    ],
    steps={
        "windows": [
            "Select the OneDrive cloud icon and read the message it shows.",
            "For error 0x8004de40, check the internet connection, then sign out of OneDrive from Settings, Account, and sign in again.",
            "Rename files the sync client lists as not allowed.",
            "Free up disk space until at least 1 GB is available.",
            "Press Windows key + R and run: %localappdata%\\Microsoft\\OneDrive\\onedrive.exe /reset",
            "Start OneDrive again from the Start menu and allow up to an hour for a full re-check.",
        ],
        "macos": [
            "Click the OneDrive cloud icon in the menu bar and read the message it shows.",
            "Choose Pause syncing, wait a minute and choose Resume syncing.",
            "Rename files the sync client lists as not allowed.",
            "Free up disk space until at least 1 GB is available.",
            "Quit OneDrive and reopen it from Applications; sign in with LarkID if asked.",
        ],
    },
    codes=["0x8004de40"],
    group=MESSAGING,
    ticket=K(
        shorts=["OneDrive not syncing", "OneDrive error 0x8004de40", "Files stuck on sync pending"],
        descs=[
            "OneDrive has been stuck on processing changes for two days on my {os} laptop.",
            "There was a problem connecting to OneDrive, error code {code}.",
            "My files are not showing up for my colleagues, sync seems stuck.",
        ],
        fixes=[
            "A folder contained file names with colons. Renamed them and sync completed.",
            "Reset the OneDrive client and signed in again; all files re-checked and in sync.",
        ],
        weight=1.5,
        priority=(0, 5, 65, 30),
    ),
)

T(
    "meeting-room",
    "Book a meeting room and use the room screen",
    system="Meeting rooms",
    category=EMAIL,
    subcategory="Meeting rooms",
    kind="how-to",
    summary="Rooms are booked from Outlook and released automatically if nobody checks in within 10 minutes.",
    steps={
        "any": [
            "In a new Outlook meeting choose Room Finder and pick a room in your building.",
            "Add a Teams link if anyone joins remotely; room screens join with one touch.",
            "At the start, tap Check in on the panel outside the room ({room_panel}).",
            "To present, tap Share on the table console, or join the meeting from your laptop and share there.",
            "If the screen is blank, check the console is awake and the input is set to Room PC.",
            "For a broken screen, camera or panel, raise a ticket with the room name. Support hours are {support_hours}.",
        ]
    },
    notes=["Applies to offices in {region_name}."],
    by_region=True,
    group=MESSAGING,
    ticket=K(
        shorts=[
            "Meeting room screen not working",
            "Room display blank",
            "Cannot join Teams from meeting room",
        ],
        descs=[
            "The screen in the large meeting room in {office} is blank and we have a client call in 15 minutes.",
            "Room panel shows the room as free but it is booked.",
        ],
        fixes=[
            "Display input was set to HDMI 2. Switched to Room PC and the console woke.",
            "Room console was frozen. Restarted it remotely; one-touch join working.",
        ],
        weight=0.9,
        priority=(0, 18, 60, 22),
    ),
)

T(
    "out-of-office-signature",
    "Set an out-of-office reply and the standard email signature",
    system="Outlook",
    category=EMAIL,
    subcategory="Outlook",
    kind="how-to",
    summary="Set automatic replies before leave and use the standard signature generated from your HR record.",
    steps={
        "any": [
            "In Outlook choose File, Automatic Replies, and set the dates of your absence.",
            "Write one reply for colleagues and one for people outside the company; do not include personal phone numbers.",
            "For the signature, open https://intranet.larkhaven.example/signature and choose Copy signature.",
            "In Outlook open Settings, Signatures, paste it and set it for new messages.",
            "If your title or office is wrong in the signature, ask HR to correct your PeopleHub record; IT cannot edit it.",
        ]
    },
    ticket=K(
        shorts=[
            "Out of office setup",
            "Email signature wrong job title",
            "How to set automatic replies",
        ],
        descs=[
            "My signature shows my old job title. Can you fix it?",
            "I am on leave from Friday and need help setting the out of office message.",
        ],
        fixes=[
            "Job title comes from PeopleHub. Directed the user to HR to correct the record; signature regenerated afterwards."
        ],
        weight=0.5,
        priority=(0, 0, 35, 65),
    ),
)

T(
    "distribution-list",
    "Create or change an email distribution list",
    system="Email",
    category=EMAIL,
    subcategory="Distribution list",
    kind="how-to",
    summary="Distribution lists are managed by their owners; IT creates new lists on request within 2 business days.",
    steps={
        "any": [
            "To join or leave a list, ask its owner. The owner is shown on the list's contact card in Outlook.",
            "Owners add and remove members at https://id.larkhaven.example/groups.",
            "For a new list, raise a HelpHub request with the name, two owners and the purpose.",
            "List addresses start with dl-, for example dl-sales-emea@larkhaven.example.",
            "Lists with no owner for 30 days are disabled.",
        ]
    },
    group=MESSAGING,
    ticket=K(
        shorts=[
            "New distribution list",
            "Add me to distribution list",
            "Not receiving team emails",
        ],
        descs=[
            "Please create a distribution list for the new regional sales team.",
            "I am not getting the emails sent to my team's list.",
        ],
        fixes=[
            "User was not a member of the list. Owner added them at id.larkhaven.example/groups."
        ],
        weight=0.6,
        priority=(0, 0, 45, 55),
    ),
)

T(
    "large-file-transfer",
    "Send a file that is too large for email",
    system="SendSafe",
    category=EMAIL,
    subcategory="File transfer",
    kind="how-to",
    summary="Email attachments are limited to 25 MB; use a OneDrive link for colleagues and SendSafe for people outside the company.",
    steps={
        "any": [
            "For colleagues, upload the file to OneDrive, choose Share and send the link.",
            "For external recipients, open https://sendsafe.larkhaven.example and sign in with LarkID.",
            "Upload up to 20 GB, enter the recipient's email address and set an expiry of at most 14 days.",
            "The recipient gets a link and a one-time code by separate emails.",
            "Files classified Restricted must not be sent through SendSafe without the data owner's written approval.",
        ]
    },
    policy="POL-007",
    ticket=K(
        shorts=[
            "File too large to email",
            "How to send large file to customer",
            "Attachment size limit",
        ],
        descs=[
            "I need to send a 2 GB video to an agency and email rejects it.",
            "What is the approved way to share big files with a customer?",
        ],
        fixes=["Introduced SendSafe for external transfer. File sent with a 7-day expiry."],
        weight=0.6,
        priority=(0, 2, 48, 50),
    ),
)
