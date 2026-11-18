"""Knowledge-base topics: laptops, peripherals, printing and phones."""

from datagen.model import HARDWARE, SECOPS, SECURITY, WORKPLACE, K, T

T(
    "laptop-slow",
    "Speed up a slow laptop",
    system="Laptop",
    category=HARDWARE,
    subcategory="Performance",
    kind="troubleshooting",
    summary="Most slow laptops are fixed by a restart, pending updates or freeing disk space; laptops with 8 GB of memory or older than four years may qualify for replacement.",
    symptoms=[
        "Applications take a long time to open.",
        "The fan runs constantly and typing lags.",
        "Calls stutter while other apps are open.",
    ],
    causes=[
        "The laptop has not been restarted for more than a week.",
        "Updates are waiting for a restart.",
        "Less than 15 percent of the disk is free.",
        "Too many apps start automatically.",
        "8 GB of memory is not enough for the applications in use.",
    ],
    steps={
        "windows": [
            "Restart the laptop; choose Restart, not Shut down, so updates finish installing.",
            "Open Settings, Windows Update, install everything offered and restart again.",
            "Press Ctrl + Shift + Esc to open Task Manager and sort Processes by Memory and by CPU. Close what you do not need.",
            "In Task Manager open Startup apps and disable those you do not use daily.",
            "Open Settings, System, Storage, and free space until at least 15 percent of the disk is free.",
            "If Task Manager shows memory above 85 percent with only your normal apps open, raise a ticket; include the laptop asset tag.",
        ],
        "macos": [
            "Restart the Mac from the Apple menu.",
            "Open System Settings, General, Software Update, install what is offered and restart again.",
            "Open Activity Monitor and sort by Memory and by CPU. Quit what you do not need.",
            "Open System Settings, General, Login Items, and remove apps you do not use daily.",
            "Open System Settings, General, Storage, and free space until at least 15 percent of the disk is free.",
            "If Memory Pressure in Activity Monitor stays red with only your normal apps open, raise a ticket; include the laptop asset tag.",
        ],
    },
    notes=[
        "A regional service incident can also make everything feel slow. Check the service status page in HelpHub first.",
        "Laptops are replaced after 48 months. A laptop with 8 GB of memory can be replaced earlier when IT confirms the memory is the cause.",
    ],
    group=WORKPLACE,
    policy="POL-004",
    ticket=K(
        shorts=[
            "Laptop very slow",
            "My laptop is slow",
            "Computer freezing all the time",
            "laptop performance issue",
            "Everything takes forever to open",
        ],
        descs=[
            "My laptop is very slow, what is wrong? It takes minutes to open Outlook.",
            "My {model} freezes several times a day, especially on calls.",
            "Laptop has become painfully slow over the last month. Fan is always on.",
            "Typing lags and Excel hangs on my {os} laptop.",
        ],
        fixes=[
            "Laptop had 41 days of uptime and updates pending. Installed updates and restarted twice; performance normal.",
            "Disk was 97 percent full. Cleared 60 GB with Storage settings; laptop responsive again.",
            "8 GB laptop older than four years with memory above 90 percent under normal load. Raised a replacement request under the device policy.",
        ],
        weight=2.4,
        priority=(0, 5, 65, 30),
    ),
)

T(
    "laptop-no-power",
    "Laptop does not turn on or does not charge",
    system="Laptop",
    category=HARDWARE,
    subcategory="Power",
    kind="troubleshooting",
    summary="A laptop that seems dead usually has a drained battery or a charger fault; a 30-second power reset fixes many cases.",
    symptoms=[
        "Nothing happens when you press the power button.",
        "The charging light is off or blinks.",
    ],
    causes=[
        "A fully drained battery.",
        "A faulty charger, cable or dock.",
        "The laptop is in a hung sleep state.",
    ],
    steps={
        "any": [
            "Connect the original charger directly to a wall socket, not through a dock, and wait 15 minutes.",
            "Try a different socket and, if you can, a colleague's charger of the same type.",
            "Hold the power button for 30 seconds, release it, then press it once.",
            "Disconnect docks, USB devices and external screens, then try again.",
            "If there is still no sign of power, raise a ticket or visit a Tech Bar; a loan laptop is issued while yours is repaired.",
        ]
    },
    group=WORKPLACE,
    policy="POL-004",
    ticket=K(
        shorts=[
            "Laptop will not turn on",
            "Laptop not charging",
            "Dead laptop",
            "Battery not charging plugged in",
        ],
        descs=[
            "My laptop will not switch on this morning. No lights at all.",
            "The battery says plugged in, not charging and it is at 4 percent.",
            "Laptop died during a meeting and will not start again.",
        ],
        fixes=[
            "30-second power reset brought the laptop back. Battery had fully drained in sleep.",
            "Charger was faulty. Replaced the charger at the Tech Bar.",
            "No power after reset. Issued a loan laptop and sent the device for repair.",
        ],
        weight=1.1,
        priority=(0, 20, 65, 15),
    ),
)

T(
    "laptop-refresh-request",
    "Request a replacement laptop",
    system="Laptop",
    category=HARDWARE,
    subcategory="Hardware request",
    kind="how-to",
    summary="Laptops are replaced every 48 months; earlier replacement needs a confirmed fault or a role that needs a higher specification.",
    steps={
        "any": [
            "Check the age of your laptop at https://id.larkhaven.example/devices under My devices.",
            "If it is 48 months or older, choose Request replacement in HelpHub; no approval is needed.",
            "If it is younger, raise a ticket describing the problem; IT confirms whether repair or replacement is right.",
            "Roles that need more than the standard specification need the manager's approval and a cost centre.",
            "Back up nothing by hand: files in OneDrive and settings are restored on the new laptop.",
            "Return the old laptop within 5 business days of receiving the new one.",
        ]
    },
    group=WORKPLACE,
    policy="POL-004",
    ticket=K(
        shorts=[
            "Request new laptop",
            "Laptop replacement",
            "Is my laptop due for refresh",
            "Need higher spec laptop",
        ],
        descs=[
            "My laptop is more than four years old. How do I get a new one?",
            "I need a laptop with more memory for data work. My manager supports this.",
        ],
        fixes=[
            "Laptop was 52 months old. Replacement request raised without approval; new laptop shipped.",
            "Laptop was 20 months old with no fault. Explained the policy; manager to approve a higher specification with cost centre.",
        ],
        weight=0.9,
        priority=(0, 0, 40, 60),
    ),
)

T(
    "dock-monitors",
    "Set up a docking station and external screens",
    system="Dock",
    category=HARDWARE,
    subcategory="Peripherals",
    kind="how-to",
    summary="Connect screens to the dock, the dock to the laptop with the single USB-C cable, then arrange the screens in display settings.",
    steps={
        "windows": [
            "Connect the dock to power and both screens to the dock.",
            "Connect the dock's USB-C cable to the laptop port marked with a lightning or D symbol.",
            "Press Windows key + P and choose Extend.",
            "Open Settings, System, Display, drag the screens into the order they sit on your desk and choose the main display.",
            "If a screen stays black, open App Hub and run Driver updates, then restart with the dock connected.",
        ],
        "macos": [
            "Connect the dock to power and the screens to the dock.",
            "Connect the dock's USB-C cable to any port on the Mac.",
            "Open System Settings, Displays, choose Arrange and drag the screens into the order they sit on your desk.",
            "MacBook Air models drive one external screen through a standard dock; a second screen needs a DisplayLink dock from IT.",
            "If a screen stays black, unplug the dock from power for 10 seconds and reconnect.",
        ],
    },
    group=WORKPLACE,
    ticket=K(
        shorts=[
            "External monitor not detected",
            "Dock not working",
            "Second screen black",
            "Monitors not working after update",
        ],
        descs=[
            "My second monitor is not detected through the dock on my {model}.",
            "Since yesterday both screens stay black when I dock the laptop.",
            "Only one external display works on my Mac.",
        ],
        fixes=[
            "Dock firmware and display driver were out of date. Ran Driver updates from App Hub; both screens detected.",
            "MacBook Air supports one external screen on a standard dock. Supplied a DisplayLink dock.",
            "Power-cycled the dock; displays returned.",
        ],
        weight=1.4,
        priority=(0, 5, 62, 33),
    ),
)

T(
    "bitlocker-recovery",
    "Laptop asks for a BitLocker recovery key",
    system="Windows",
    category=HARDWARE,
    subcategory="Encryption",
    kind="troubleshooting",
    summary="Windows asks for the 48-digit BitLocker recovery key after certain hardware or firmware changes; you can look the key up yourself.",
    symptoms=["A blue screen at start-up asks you to enter the recovery key for this drive."],
    causes=[
        "A firmware or BIOS update.",
        "The laptop was started with a new dock or USB device attached.",
        "Several wrong PIN attempts.",
    ],
    steps={
        "windows": [
            "On your phone or another computer open https://id.larkhaven.example/devices and sign in.",
            "Choose your laptop under My devices, then Show recovery key.",
            "Check that the Key ID on the laptop screen matches the first eight characters shown in the portal.",
            "Type the 48-digit key on the laptop.",
            "If the laptop asks again at every start, raise a ticket; IT will suspend and resume BitLocker to reset it.",
        ]
    },
    notes=[
        "If you cannot sign in to the portal, the service desk can read the key to you after verifying your identity."
    ],
    group=WORKPLACE,
    policy="POL-004",
    ticket=K(
        shorts=[
            "BitLocker recovery key needed",
            "Laptop asking for recovery key",
            "Blue BitLocker screen on startup",
        ],
        descs=[
            "My laptop shows a blue screen asking for a BitLocker recovery key and I do not have one.",
            "After a BIOS update the laptop wants a 48-digit key every time I start it.",
        ],
        fixes=[
            "User retrieved the key from id.larkhaven.example/devices on their phone. Laptop unlocked.",
            "Identity verified by phone; key provided. Suspended and resumed BitLocker to stop the repeat prompt.",
        ],
        weight=0.9,
        priority=(0, 22, 63, 15),
    ),
)

T(
    "filevault-recovery",
    "Mac does not accept your password at start-up (FileVault)",
    system="macOS",
    category=HARDWARE,
    subcategory="Encryption",
    kind="troubleshooting",
    summary="If the FileVault unlock screen rejects your password, use the recovery key stored in the LarkID portal to unlock the Mac and set the password again.",
    symptoms=[
        "The first login screen after a restart rejects the current password.",
        "A question mark appears after three attempts.",
    ],
    causes=[
        "The LarkID password was changed while the Mac was switched off or away from the network."
    ],
    steps={
        "macos": [
            "Try the previous password; the start-up screen may still expect it.",
            "On your phone open https://id.larkhaven.example/devices, choose the Mac and Show recovery key.",
            "On the Mac click the question mark, choose Restart and show password reset options, and enter the recovery key.",
            "Set the Mac password to match your current LarkID password.",
            "After signing in, connect to the office network or SecureTunnel so the passwords stay in step.",
        ]
    },
    group=WORKPLACE,
    policy="POL-004",
    ticket=K(
        shorts=[
            "Mac will not accept password at startup",
            "FileVault recovery key",
            "Locked out of MacBook after password change",
        ],
        descs=[
            "I changed my password on my phone and now my {model} will not let me in at start-up.",
            "Mac asks for a recovery key after I typed the password wrong a few times.",
        ],
        fixes=[
            "Previous password unlocked the disk. Synchronised the Mac password with LarkID over SecureTunnel."
        ],
        weight=0.4,
        priority=(0, 20, 65, 15),
    ),
)

T(
    "lost-stolen-device",
    "Report a lost or stolen laptop or phone",
    system="Security",
    category=SECURITY,
    subcategory="Lost device",
    kind="how-to",
    summary="Report a lost or stolen device within 2 hours, at any time of day, so IT can lock it before data is exposed.",
    steps={
        "any": [
            "Call the service desk straight away; lost devices are handled 24 hours a day as priority 2.",
            "Say when and where you last had the device and whether it was switched on and unlocked.",
            "IT locks the device remotely. Wiping a device needs the approval of the IT duty manager.",
            "Change your LarkID password at https://id.larkhaven.example/reset.",
            "For theft, report it to the police and add the report number to the ticket within 5 business days.",
            "If the device is found, do not use it; return it to IT for checking.",
        ]
    },
    notes=[
        "A lost phone that had LarkID Authenticator also needs the article Move LarkID Authenticator to a new phone."
    ],
    group=SECOPS,
    policy="POL-010",
    ticket=K(
        shorts=[
            "Lost laptop",
            "Phone stolen",
            "Laptop left in taxi",
            "Stolen bag with work laptop",
        ],
        descs=[
            "My work laptop was in a bag that was stolen from my car last night.",
            "I left my company phone on the train this morning and cannot find it.",
            "Lost my laptop at the airport. It was switched off.",
        ],
        fixes=[
            "Device locked remotely within 20 minutes of the report. Password reset; police report number added. Replacement issued.",
            "Phone located by the user the next day. Work profile had been removed remotely; re-enrolled after inspection.",
        ],
        weight=0.6,
        priority=(2, 75, 23, 0),
    ),
)

T(
    "printer-setup",
    "Print in the office with FollowMe printing",
    system="FollowMe Printing",
    category=HARDWARE,
    subcategory="Printing",
    kind="how-to",
    summary="All office printers share one queue, {printer_queue}; send the job, then release it at any printer with your badge.",
    steps={
        "any": [
            "Open App Hub and run Add office printers; the queue {printer_queue} is installed.",
            "Print to {printer_queue} from any application.",
            "At any printer, tap your badge on the reader and choose Print all or select jobs.",
            "Jobs not released within 24 hours are deleted.",
            "To scan, tap your badge, choose Scan to my email, and the scan arrives as a PDF.",
            "For paper jams or toner, use the QR code on the printer; for anything else raise a ticket. Support hours are {support_hours}.",
        ]
    },
    notes=["Applies to offices in {region_name}. Home printers are not supported."],
    by_region=True,
    group=WORKPLACE,
    ticket=K(
        shorts=[
            "Cannot print",
            "Printer not showing on laptop",
            "Print job not released",
            "Badge not working at printer",
        ],
        descs=[
            "I cannot find any printer on my new laptop in the {office} office.",
            "I sent a document to print and nothing comes out when I badge in.",
            "The printer does not recognise my badge.",
        ],
        fixes=[
            "Queue was not installed. Ran Add office printers from App Hub; test page released by badge.",
            "Badge was not linked to the user. Linked it at the printer with LarkID sign-in.",
        ],
        weight=1.3,
        priority=(0, 3, 57, 40),
    ),
)

T(
    "printer-0x00000709",
    "Printing fails with error 0x00000709 on Windows",
    system="FollowMe Printing",
    category=HARDWARE,
    subcategory="Printing",
    kind="troubleshooting",
    summary="Error 0x00000709 means Windows cannot set or reach the default printer; removing and re-adding the queue clears it.",
    symptoms=[
        "'Operation could not be completed (error 0x00000709). Double check the printer name and make sure that the printer is connected to the network.'"
    ],
    causes=[
        "Windows is managing the default printer and chose one that no longer exists.",
        "The print queue was renamed after an office move.",
    ],
    steps={
        "windows": [
            "Open Settings, Bluetooth and devices, Printers and scanners.",
            "Turn off Let Windows manage my default printer.",
            "Remove any FollowMe queue listed.",
            "Open App Hub and run Add office printers.",
            "Back in Printers and scanners, select the FollowMe queue and choose Set as default.",
        ]
    },
    codes=["0x00000709"],
    group=WORKPLACE,
    ticket=K(
        shorts=[
            "Printer error 0x00000709",
            "Cannot set default printer",
            "Operation could not be completed printing",
        ],
        descs=[
            "Printing gives operation could not be completed, error {code}.",
            "Since I moved desks I cannot print, Windows says double check the printer name.",
        ],
        fixes=[
            "Removed the stale queue, disabled Windows default printer management and re-added FollowMe from App Hub."
        ],
        weight=0.7,
        priority=(0, 3, 62, 35),
    ),
)

T(
    "bluetooth-headset",
    "Pair a Bluetooth headset",
    system="Peripherals",
    category=HARDWARE,
    subcategory="Peripherals",
    kind="how-to",
    summary="Put the headset in pairing mode, add it in Bluetooth settings, then select it in Teams.",
    steps={
        "windows": [
            "Hold the headset power button until the light flashes blue and red.",
            "Open Settings, Bluetooth and devices, Add device, Bluetooth, and choose the headset.",
            "In Teams open Settings, Devices and select the headset for speaker and microphone.",
            "If the sound is poor, plug in the USB adapter that came with the headset and select that instead.",
        ],
        "macos": [
            "Hold the headset power button until the light flashes blue and red.",
            "Open System Settings, Bluetooth, and choose Connect next to the headset.",
            "In Teams open Settings, Devices and select the headset for speaker and microphone.",
            "If the sound is poor, plug in the USB adapter that came with the headset and select that instead.",
        ],
    },
    ticket=K(
        shorts=[
            "Bluetooth headset will not connect",
            "Headset not pairing",
            "Headset audio cutting out",
        ],
        descs=[
            "My headset does not show up in Bluetooth on my {os} laptop.",
            "Headset connects but the sound cuts out in every call.",
        ],
        fixes=[
            "Headset was still paired to the user's phone. Unpaired it there and paired with the laptop. Using the USB adapter for calls."
        ],
        weight=0.8,
        priority=(0, 2, 55, 43),
    ),
)

T(
    "blue-screen",
    "Windows laptop restarts with a blue screen",
    system="Windows",
    category=HARDWARE,
    subcategory="Crashes",
    kind="troubleshooting",
    summary="A single blue screen is usually harmless; a repeating one needs IT, and the stop code on the screen tells them where to look.",
    symptoms=[
        "A blue screen with a sad face and a stop code such as CRITICAL_PROCESS_DIED or DRIVER_IRQL_NOT_LESS_OR_EQUAL."
    ],
    causes=[
        "A faulty or outdated driver, often for a dock or graphics.",
        "Failing memory or disk.",
        "An interrupted update.",
    ],
    steps={
        "windows": [
            "Write down or photograph the stop code before the laptop restarts.",
            "After the restart, open Settings, Windows Update and install everything offered.",
            "Open App Hub and run Driver updates.",
            "Disconnect the dock for a day to see whether the crashes stop.",
            "If it happens again within a week, raise a ticket with the stop code, the time and what you were doing.",
        ]
    },
    codes=["CRITICAL_PROCESS_DIED", "DRIVER_IRQL_NOT_LESS_OR_EQUAL"],
    group=WORKPLACE,
    ticket=K(
        shorts=[
            "Blue screen",
            "Laptop crashes with blue screen",
            "BSOD CRITICAL_PROCESS_DIED",
            "Computer restarts by itself",
        ],
        descs=[
            "My laptop blue screens two or three times a day with {code}.",
            "The laptop suddenly restarted with a blue screen in the middle of a presentation.",
        ],
        fixes=[
            "Dock driver was outdated. Driver updates installed; no crash in the following week.",
            "Memory diagnostics failed. Laptop replaced under warranty.",
        ],
        weight=0.8,
        priority=(0, 15, 65, 20),
    ),
)

T(
    "kernel-panic",
    "Mac restarts with 'Your computer restarted because of a problem'",
    system="macOS",
    category=HARDWARE,
    subcategory="Crashes",
    kind="troubleshooting",
    summary="This message is a kernel panic; one is harmless, repeated ones point to an accessory, an old system extension or failing hardware.",
    symptoms=[
        "The Mac restarts unexpectedly and shows 'Your computer restarted because of a problem' after login."
    ],
    causes=[
        "A dock, adapter or other accessory.",
        "Outdated software that installs a system extension.",
        "Failing hardware.",
    ],
    steps={
        "macos": [
            "Choose Report when the message appears so the details are saved.",
            "Disconnect every accessory and use the Mac on its own for a day.",
            "Open System Settings, General, Software Update and install what is offered.",
            "Update SecureTunnel and EndpointShield from App Hub.",
            "If it happens again within a week, raise a ticket and say whether accessories were connected.",
        ]
    },
    group=WORKPLACE,
    ticket=K(
        shorts=[
            "Mac keeps restarting",
            "Your computer restarted because of a problem",
            "MacBook kernel panic",
        ],
        descs=[
            "My {model} restarts by itself and says it restarted because of a problem.",
            "Mac crashed three times this week when connected to the dock.",
        ],
        fixes=["Crashes stopped with the third-party hub disconnected. Supplied a supported dock."],
        weight=0.3,
        priority=(0, 12, 66, 22),
    ),
)

T(
    "disk-full",
    "Free up disk space",
    system="Laptop",
    category=HARDWARE,
    subcategory="Storage",
    kind="how-to",
    summary="Keep at least 15 percent of the disk free; OneDrive can keep files online only so they stop using local space.",
    steps={
        "windows": [
            "Open Settings, System, Storage, to see what is using space.",
            "Turn on Storage Sense and choose Run Storage Sense now.",
            "Right-click the OneDrive folder in File Explorer and choose Free up space.",
            "Empty the Recycle Bin and the Downloads folder.",
            "Uninstall applications you no longer use from Settings, Apps.",
        ],
        "macos": [
            "Open System Settings, General, Storage, to see what is using space.",
            "Choose Empty Trash automatically and review Large Files under Documents.",
            "In Finder right-click the OneDrive folder and choose Free Up Space.",
            "Empty the Downloads folder.",
            "Delete applications you no longer use from the Applications folder.",
        ],
    },
    ticket=K(
        shorts=[
            "Disk full",
            "Low disk space warning",
            "No space left on laptop",
            "Cannot save files disk full",
        ],
        descs=[
            "I get a low disk space warning every day and cannot install updates.",
            "My {model} says the disk is full but I have hardly any files.",
        ],
        fixes=[
            "OneDrive was keeping 80 GB locally. Used Free up space and enabled Storage Sense; 45 percent free."
        ],
        weight=0.9,
        priority=(0, 3, 60, 37),
    ),
)

T(
    "mdm-enrol-phone",
    "Enrol a phone in DeviceCare",
    system="DeviceCare",
    category=HARDWARE,
    subcategory="Mobile",
    kind="how-to",
    summary="A phone must be enrolled in DeviceCare before it can open work email, Teams or files; personal phones are allowed.",
    steps={
        "ios": [
            "Check the phone runs one of the two latest major iOS versions.",
            "Install DeviceCare from the App Store and sign in with LarkID.",
            "Follow the prompts to install the management profile, then return to DeviceCare.",
            "Set a 6-digit passcode when asked.",
            "Wait for the green Compliant tick, then install Outlook and Teams.",
        ],
        "android": [
            "Check the phone runs one of the two latest major Android versions and is not rooted.",
            "Install DeviceCare from Google Play and sign in with LarkID.",
            "Accept the creation of a work profile; work apps appear with a briefcase badge.",
            "Set a 6-digit screen lock when asked.",
            "Wait for the green Compliant tick, then install Outlook and Teams from the work Play Store.",
        ],
    },
    notes=[
        "IT can remove the work profile and its data. IT cannot see personal apps, photos, messages or location.",
        "Remove the enrolment yourself in DeviceCare before you sell or give away the phone.",
    ],
    group=WORKPLACE,
    policy="POL-008",
    ticket=K(
        shorts=[
            "Phone not compliant",
            "DeviceCare enrolment failed",
            "Cannot enrol personal phone",
        ],
        descs=[
            "DeviceCare says my {os} phone is not compliant and email stopped working.",
            "Enrolment fails at the profile step on my new phone.",
        ],
        fixes=[
            "Phone was two major versions behind. Updated the operating system; device compliant.",
            "Passcode was four digits. Changed to six; compliance check passed.",
        ],
        weight=0.7,
        priority=(0, 2, 58, 40),
    ),
)
