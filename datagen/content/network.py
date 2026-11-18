"""Knowledge-base topics: VPN, Wi-Fi and network access."""

from datagen.model import NETOPS, NETWORK, K, T

T(
    "vpn-install",
    "Install and set up SecureTunnel VPN",
    system="SecureTunnel VPN",
    category=NETWORK,
    subcategory="VPN",
    kind="how-to",
    summary="SecureTunnel is the company VPN; install it from App Hub and sign in with LarkID to reach internal systems from outside the office.",
    steps={
        "windows": [
            "Open App Hub from the Start menu and install SecureTunnel.",
            "Start SecureTunnel from the system tray; the gateway vpn.larkhaven.example is filled in already.",
            "Choose Connect and sign in with your LarkID email and password.",
            "Approve the prompt in LarkID Authenticator.",
            "Wait for the device check to finish; the tray icon turns green when you are connected.",
            "Open https://intranet.larkhaven.example to confirm internal sites load.",
        ],
        "macos": [
            "Open App Hub from Launchpad and install SecureTunnel.",
            "When macOS asks, open System Settings, Privacy and Security, and allow the SecureTunnel system extension.",
            "Allow SecureTunnel to add VPN configurations when prompted.",
            "Click the SecureTunnel icon in the menu bar, choose Connect and sign in with LarkID.",
            "Approve the prompt in LarkID Authenticator; the menu bar icon shows a closed lock when connected.",
            "Open https://intranet.larkhaven.example to confirm internal sites load.",
        ],
    },
    notes=[
        "A VPN session ends after 12 hours or after 30 minutes without activity. Reconnect to continue."
    ],
    policy="POL-006",
    ticket=K(
        shorts=[
            "How do I set up VPN",
            "Need VPN installed",
            "VPN setup on new laptop",
            "SecureTunnel not installed",
        ],
        descs=[
            "How do I set up VPN on my {os} laptop? I am working from home tomorrow.",
            "New {model} and SecureTunnel is not installed. I need it for the client site next week.",
            "I installed the VPN but it asks to allow a system extension and I do not know where.",
        ],
        fixes=[
            "Guided installation from App Hub and first sign-in with LarkID. Connection confirmed by opening the intranet.",
            "System extension had not been allowed. Approved it in Privacy and Security; VPN connected.",
        ],
        weight=2.2,
        priority=(0, 4, 60, 36),
    ),
)

T(
    "vpn-error-809",
    "Fix VPN error 809 on Windows",
    system="SecureTunnel VPN",
    category=NETWORK,
    subcategory="VPN",
    kind="troubleshooting",
    summary="Error 809 means the network you are on blocks the ports the VPN needs; it is a problem with the local network, not your account.",
    symptoms=[
        "SecureTunnel shows 'The network connection between your computer and the VPN server could not be established. Error 809'.",
        "The VPN works on one network, such as a phone hotspot, but not on another.",
    ],
    causes=[
        "A home router, hotel or guest network blocks UDP ports 500 and 4500.",
        "The router has IPsec passthrough turned off.",
        "A third-party firewall on the laptop blocks the VPN.",
    ],
    steps={
        "windows": [
            "Connect the laptop to a phone hotspot and try the VPN. If it works, the first network is blocking it.",
            "Restart the home router, then try again.",
            "In the router settings turn on IPsec passthrough, sometimes called VPN passthrough.",
            "In SecureTunnel open Settings, Protocol, and choose TLS fallback, which uses TCP port 443.",
            "Restart the laptop and connect again.",
            "If error 809 appears on every network, raise a ticket for Network Operations and attach the SecureTunnel log bundle.",
        ]
    },
    codes=["809"],
    notes=[
        "Hotels and public Wi-Fi often block VPN ports. TLS fallback is slower but works on almost every network."
    ],
    group=NETOPS,
    policy="POL-006",
    ticket=K(
        shorts=[
            "VPN error 809",
            "VPN fails with error 809",
            "Cannot connect to VPN from home",
            "SecureTunnel 809",
        ],
        descs=[
            "VPN fails with error {code} on my Windows laptop. It worked in the office yesterday.",
            "Getting 'network connection between your computer and the VPN server could not be established' at the hotel.",
            "SecureTunnel will not connect from my home broadband, error {code}. Hotspot works fine.",
        ],
        fixes=[
            "Home router was blocking UDP 500 and 4500. Enabled TLS fallback in SecureTunnel settings; connected on TCP 443.",
            "Confirmed the VPN worked on a hotspot. User enabled IPsec passthrough on the router and the error cleared.",
        ],
        weight=1.6,
        priority=(0, 10, 68, 22),
    ),
)

T(
    "vpn-no-internal-sites",
    "VPN is connected but internal sites do not load",
    system="SecureTunnel VPN",
    category=NETWORK,
    subcategory="VPN",
    kind="troubleshooting",
    summary="When the VPN shows connected but intranet pages time out, the laptop is usually still using the home network's DNS servers.",
    symptoms=[
        "SecureTunnel shows connected.",
        "Public websites load but intranet.larkhaven.example does not.",
    ],
    causes=[
        "A stale DNS cache.",
        "A manually configured DNS server on the network adapter.",
        "A browser secure-DNS setting that bypasses the VPN.",
    ],
    steps={
        "windows": [
            "Disconnect and reconnect SecureTunnel.",
            "Open Command Prompt and run: ipconfig /flushdns",
            "Open Settings, Network and internet, your adapter, and set DNS server assignment to Automatic.",
            "In the browser settings turn off Use secure DNS.",
            "Test with https://intranet.larkhaven.example.",
        ],
        "macos": [
            "Disconnect and reconnect SecureTunnel.",
            "Open Terminal and run: sudo dscacheutil -flushcache; sudo killall -HUP mDNSResponder",
            "Open System Settings, Network, your connection, Details, DNS, and remove any servers you added by hand.",
            "In the browser settings turn off Use secure DNS.",
            "Test with https://intranet.larkhaven.example.",
        ],
    },
    group=NETOPS,
    policy="POL-006",
    ticket=K(
        shorts=[
            "VPN connected but intranet not loading",
            "Internal sites time out on VPN",
            "Cannot reach file server over VPN",
        ],
        descs=[
            "VPN says connected but none of the internal sites open. Google works.",
            "On VPN from home on my {model}, the intranet and HelpHub just spin.",
        ],
        fixes=[
            "Manual DNS server set on the Wi-Fi adapter. Set to automatic and flushed the DNS cache; intranet loaded.",
            "Browser secure DNS was bypassing the VPN resolver. Disabled it and internal sites resolved.",
        ],
        weight=1.4,
        priority=(0, 8, 67, 25),
    ),
)

T(
    "vpn-posture-check",
    "SecureTunnel device check failed (error ST-407)",
    system="SecureTunnel VPN",
    category=NETWORK,
    subcategory="VPN",
    kind="troubleshooting",
    summary="ST-407 means the laptop failed the security check that runs before every VPN connection.",
    symptoms=[
        "SecureTunnel shows 'Device does not meet requirements. ST-407' and lists the failed check."
    ],
    causes=[
        "Disk encryption is turned off or still encrypting.",
        "EndpointShield is not running or its definitions are older than 7 days.",
        "Operating system updates are more than 30 days behind.",
    ],
    steps={
        "any": [
            "Read the failed check named under the error message.",
            "For Encryption, confirm BitLocker or FileVault is on and wait for encryption to finish.",
            "For Endpoint protection, open EndpointShield and choose Update now, then restart.",
            "For Updates, install all pending operating system updates and restart.",
            "Connect again; the check runs each time you connect.",
        ]
    },
    codes=["ST-407"],
    notes=[
        "Personal laptops always fail the device check. Use a company laptop or the web portal for email."
    ],
    group=NETOPS,
    policy="POL-006",
    ticket=K(
        shorts=[
            "VPN ST-407 device does not meet requirements",
            "SecureTunnel device check failed",
            "VPN blocked after update",
        ],
        descs=[
            "SecureTunnel refuses to connect with {code}. It says endpoint protection.",
            "VPN says my device does not meet requirements. Nothing changed on my side.",
        ],
        fixes=[
            "EndpointShield definitions were 12 days old. Forced an update and restarted; device check passed.",
            "Laptop was 45 days behind on updates. Installed pending updates and the VPN connected.",
        ],
        weight=1.1,
        priority=(0, 8, 67, 25),
    ),
)

T(
    "vpn-disconnects",
    "VPN keeps disconnecting",
    system="SecureTunnel VPN",
    category=NETWORK,
    subcategory="VPN",
    kind="troubleshooting",
    summary="Frequent VPN drops are usually caused by weak Wi-Fi or power saving on the network adapter, not by the VPN service.",
    symptoms=[
        "The VPN drops every few minutes.",
        "Calls freeze and SecureTunnel shows Reconnecting.",
    ],
    causes=[
        "Weak or congested Wi-Fi.",
        "The network adapter sleeps to save power.",
        "An out-of-date SecureTunnel client.",
    ],
    steps={
        "windows": [
            "Check the service status page in HelpHub for a VPN incident in your region.",
            "Move closer to the router or use a network cable, then test again.",
            "Open Device Manager, Network adapters, your Wi-Fi adapter, Power Management, and clear Allow the computer to turn off this device.",
            "Update SecureTunnel from App Hub to version 5.3 or later.",
            "If drops continue on a wired connection, raise a ticket with the times of three recent drops.",
        ],
        "macos": [
            "Check the service status page in HelpHub for a VPN incident in your region.",
            "Move closer to the router or use a network cable, then test again.",
            "Open System Settings, Wi-Fi, Details for your network, and turn off Limit IP address tracking.",
            "Update SecureTunnel from App Hub to version 5.3 or later; version 5.2 drops on macOS 26.",
            "If drops continue on a wired connection, raise a ticket with the times of three recent drops.",
        ],
    },
    group=NETOPS,
    policy="POL-006",
    ticket=K(
        shorts=[
            "VPN keeps dropping",
            "SecureTunnel disconnects every few minutes",
            "VPN unstable on calls",
        ],
        descs=[
            "The VPN disconnects every ten minutes or so on my {os} laptop. Very disruptive on calls.",
            "SecureTunnel shows reconnecting again and again since this morning.",
            "VPN drops whenever I am on a Teams call from home.",
        ],
        fixes=[
            "Client was on SecureTunnel 5.2. Updated to 5.3 from App Hub; no drops in the following hour.",
            "Wi-Fi adapter power saving was enabled. Disabled it; connection stable.",
            "Regional VPN gateway incident was in progress. Linked the ticket to the incident; resolved when the gateway recovered.",
        ],
        weight=1.8,
        priority=(1, 12, 65, 22),
    ),
)

T(
    "vpn-auth-failed",
    "SecureTunnel sign-in fails (error ST-401)",
    system="SecureTunnel VPN",
    category=NETWORK,
    subcategory="VPN",
    kind="troubleshooting",
    summary="ST-401 means the VPN reached the gateway but your sign-in was refused.",
    symptoms=["SecureTunnel shows 'Authentication failed. ST-401' after you approve the sign-in."],
    causes=[
        "The password was changed and the old one is saved.",
        "The account is locked.",
        "The account is not in the remote access group.",
    ],
    steps={
        "any": [
            "Sign in at https://id.larkhaven.example to confirm your password works and the account is not locked.",
            "In SecureTunnel choose Settings, Forget saved sign-in, then connect and type the password again.",
            "Contractors and new joiners: check with your manager that remote access was requested for you.",
            "If the portal sign-in works but the VPN still shows ST-401, raise a ticket for Network Operations.",
        ]
    },
    codes=["ST-401"],
    group=NETOPS,
    policy="POL-006",
    ticket=K(
        shorts=["VPN authentication failed ST-401", "Cannot sign in to VPN", "VPN login rejected"],
        descs=[
            "VPN gives authentication failed {code} right after I approve on my phone.",
            "I can sign in to the portal but the VPN rejects me.",
        ],
        fixes=[
            "Contractor account was missing from the remote access group. Access request approved by the manager; VPN sign-in works.",
            "Old password was saved in the client. Cleared the saved sign-in and reconnected.",
        ],
        weight=1.0,
        priority=(0, 8, 67, 25),
    ),
)

T(
    "office-wifi",
    "Connect to LarkNet, the office Wi-Fi",
    system="LarkNet Wi-Fi",
    category=NETWORK,
    subcategory="Wi-Fi",
    kind="how-to",
    summary="Company laptops join LarkNet automatically with a certificate; you never type a Wi-Fi password.",
    steps={
        "windows": [
            "Select the network icon in the taskbar and choose LarkNet.",
            "If Windows asks for a user name and password, cancel; the certificate is missing.",
            "Connect a network cable or use the LarkGuest network with VPN, then open App Hub and run Repair network certificate.",
            "Restart and select LarkNet again; it connects without prompting.",
        ],
        "macos": [
            "Click the Wi-Fi icon in the menu bar and choose LarkNet.",
            "If macOS asks for a user name and password, cancel; the certificate is missing.",
            "Connect a network cable or use the LarkGuest network with VPN, then open App Hub and run Repair network certificate.",
            "Restart and choose LarkNet again; approve the certificate prompt once with your Mac password.",
        ],
    },
    notes=["Phones and personal devices cannot join LarkNet. Use the guest network instead."],
    group=NETOPS,
    ticket=K(
        shorts=[
            "Cannot connect to office wifi",
            "LarkNet asks for username and password",
            "Wi-Fi not connecting in office",
        ],
        descs=[
            "My laptop will not join LarkNet in the {office} office. It asks for a user name.",
            "Wi-Fi keeps failing to connect at my desk, the cable works.",
        ],
        fixes=[
            "Network certificate was missing after a rebuild. Ran Repair network certificate from App Hub over cable; LarkNet connected."
        ],
        weight=1.5,
        priority=(0, 8, 67, 25),
    ),
)

T(
    "wifi-cert-expired",
    "LarkNet stops connecting because the Wi-Fi certificate expired",
    system="LarkNet Wi-Fi",
    category=NETWORK,
    subcategory="Wi-Fi",
    kind="troubleshooting",
    summary="The LarkNet certificate renews itself every 12 months; a laptop that was off the network at renewal time cannot join until it is repaired.",
    symptoms=[
        "LarkNet shows 'Cannot connect to this network' or 'Authentication failed'.",
        "The laptop worked on LarkNet until recently and other people nearby are connected.",
    ],
    causes=[
        "The laptop was away from the office or VPN for more than 30 days around the renewal date."
    ],
    steps={
        "windows": [
            "Connect by cable, or join the guest network and start SecureTunnel.",
            "Open App Hub and run Repair network certificate.",
            "Open Settings, Network and internet, Wi-Fi, Manage known networks, and forget LarkNet.",
            "Restart and select LarkNet again.",
        ],
        "macos": [
            "Connect by cable, or join the guest network and start SecureTunnel.",
            "Open App Hub and run Repair network certificate.",
            "Open System Settings, Wi-Fi, Details next to LarkNet, and choose Forget This Network.",
            "Restart and choose LarkNet again; approve the certificate prompt once.",
        ],
    },
    group=NETOPS,
    ticket=K(
        shorts=[
            "Wifi authentication failed after holiday",
            "LarkNet cannot connect to this network",
            "Wi-Fi certificate problem",
        ],
        descs=[
            "Back from six weeks of leave and my laptop no longer connects to the office Wi-Fi.",
            "LarkNet says cannot connect to this network on my {model}. Everyone around me is fine.",
        ],
        fixes=[
            "Certificate had expired while the laptop was offline. Repaired it from App Hub over cable and forgot the saved network; reconnected."
        ],
        weight=0.8,
        priority=(0, 6, 68, 26),
    ),
)

T(
    "guest-wifi",
    "Give a visitor access to guest Wi-Fi",
    system="Guest Wi-Fi",
    category=NETWORK,
    subcategory="Wi-Fi",
    kind="how-to",
    summary="Visitors use the guest network {guest_ssid}; a Larkhaven employee must sponsor each visitor.",
    steps={
        "any": [
            "Ask the visitor to join the network {guest_ssid} and open any web page.",
            "On the sign-in page the visitor enters their name and your work email address as sponsor.",
            "You receive an email; choose Approve. Access lasts until midnight local time.",
            "For visits longer than one day, request a multi-day guest pass in HelpHub at least one business day ahead.",
            "Guest Wi-Fi gives internet access only. Visitors cannot reach printers or internal systems.",
        ]
    },
    notes=[
        "Applies to offices in {region_name}. Reception can sponsor visitors for all-hands events."
    ],
    by_region=True,
    group=NETOPS,
    ticket=K(
        shorts=[
            "Guest wifi for visitor",
            "Visitor cannot get on wifi",
            "Need guest wifi pass for client workshop",
        ],
        descs=[
            "I have clients visiting the {office} office tomorrow for three days and they need Wi-Fi.",
            "My visitor joined the guest network but never gets past the sign-in page.",
        ],
        fixes=[
            "Sponsor approval email had gone to the junk folder. Sponsor approved and the visitor was online.",
            "Issued a three-day guest pass through HelpHub for the workshop attendees.",
        ],
        weight=0.7,
        priority=(0, 4, 52, 44),
    ),
)

T(
    "home-wifi-tips",
    "Improve a slow home connection for remote work",
    system="Home network",
    category=NETWORK,
    subcategory="Home network",
    kind="how-to",
    summary="Most slow remote sessions are caused by the home network; these checks fix the common cases before you raise a ticket.",
    steps={
        "any": [
            "Run a speed test without the VPN. Calls need at least 5 Mbps download and 2 Mbps upload.",
            "Move within one room of the router, or connect with a network cable.",
            "Use the 5 GHz band if your router offers two networks.",
            "Pause large downloads, backups and streaming on other devices during calls.",
            "Restart the router if it has been running for weeks.",
            "If the speed test is good without the VPN and poor with it, raise a ticket with both results.",
        ]
    },
    policy="POL-006",
    ticket=K(
        shorts=[
            "Slow internet at home",
            "Connection very slow when working remotely",
            "Video calls keep freezing at home",
        ],
        descs=[
            "Everything is slow when I work from home. Calls freeze and files take ages to open.",
            "My connection is fine in the office but terrible at home on VPN.",
        ],
        fixes=[
            "Speed test showed 2 Mbps on the far side of the house. User moved to the 5 GHz band near the router; calls stable."
        ],
        weight=0.9,
        priority=(0, 3, 57, 40),
    ),
)

T(
    "browser-cert-warning",
    "Certificate warning NET::ERR_CERT_AUTHORITY_INVALID on internal sites",
    system="Browser",
    category=NETWORK,
    subcategory="Certificates",
    kind="troubleshooting",
    summary="Internal sites use certificates issued by Larkhaven; the warning appears when the company root certificate is missing from the device.",
    symptoms=[
        "Chrome or Edge shows 'Your connection is not private' with NET::ERR_CERT_AUTHORITY_INVALID on an internal address."
    ],
    causes=[
        "The laptop is not managed or missed a certificate update.",
        "The date on the laptop is wrong.",
        "You are on a personal device.",
    ],
    steps={
        "any": [
            "Check that the address ends in larkhaven.example. If it does not, close the page and report it as phishing.",
            "Check the laptop date and time are correct.",
            "Open App Hub and run Repair network certificate, then restart the browser.",
            "Do not choose Proceed anyway on a page that asks for your password.",
            "If the warning remains on a company laptop, raise a ticket with the full address.",
        ]
    },
    codes=["NET::ERR_CERT_AUTHORITY_INVALID"],
    group=NETOPS,
    ticket=K(
        shorts=[
            "Your connection is not private on intranet",
            "Certificate error on internal site",
            "NET::ERR_CERT_AUTHORITY_INVALID",
        ],
        descs=[
            "Chrome says your connection is not private when I open the intranet. {code}.",
            "Getting a certificate warning on HelpHub since this morning.",
        ],
        fixes=[
            "Company root certificate was missing. Ran Repair network certificate from App Hub; warning gone after browser restart."
        ],
        weight=0.6,
        priority=(0, 5, 65, 30),
    ),
)
