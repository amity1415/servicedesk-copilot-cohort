"""Knowledge-base topics: passwords, multi-factor authentication and access."""

from datagen.model import ACCESS, IAM, K, T

T(
    "password-reset",
    "Reset your LarkID password",
    system="LarkID",
    category=ACCESS,
    subcategory="Password",
    kind="how-to",
    summary="Reset a forgotten LarkID password yourself in about two minutes, without calling the service desk.",
    steps={
        "any": [
            "Open https://id.larkhaven.example/reset in any browser, on any network.",
            "Enter your work email address and choose Verify with LarkID Authenticator.",
            "Approve the prompt on your phone and type the two-digit number shown on the screen.",
            "Choose a new password of at least 14 characters that is not one of your last 10 passwords.",
            "Lock and unlock your laptop with the new password so the saved sign-in is updated.",
            "Update the password in the mail app on your phone if it asks for it.",
        ]
    },
    notes=[
        "If you have no working authentication method, the service desk must verify your identity before resetting the password.",
    ],
    policy="POL-003",
    ticket=K(
        shorts=[
            "Forgot my password",
            "Need a password reset",
            "Password not working",
            "cant remember LarkID password",
        ],
        descs=[
            "I forgot my LarkID password and cannot sign in to anything this morning.",
            "My password stopped working after the weekend. I tried three times and do not want to get locked out.",
            "Back from leave and I cannot remember my password. Please reset it.",
        ],
        fixes=[
            "Guided the user through self-service reset at id.larkhaven.example/reset. New password set and laptop sign-in refreshed.",
            "User completed the self-service reset with Authenticator verification. Confirmed sign-in to laptop and Outlook.",
        ],
        weight=3.0,
        priority=(0, 3, 62, 35),
    ),
)

T(
    "account-locked",
    "Unlock a locked LarkID account (error LID-1203)",
    system="LarkID",
    category=ACCESS,
    subcategory="Account lockout",
    kind="troubleshooting",
    summary="LarkID locks an account after 8 failed sign-ins in 15 minutes and unlocks it automatically after 30 minutes.",
    symptoms=[
        "Sign-in shows 'Your account is locked. LID-1203'.",
        "The correct password is rejected on every device at once.",
    ],
    causes=[
        "An old password saved on a phone, tablet or second laptop keeps retrying.",
        "A mapped drive or a mail app is still using the previous password.",
    ],
    steps={
        "any": [
            "Wait 30 minutes for the automatic unlock, or unlock now at https://id.larkhaven.example/unlock using LarkID Authenticator.",
            "Before signing in again, update or remove the old password on every phone, tablet and mail app.",
            "On Windows, open Credential Manager and delete saved entries for larkhaven.example.",
            "On macOS, open Keychain Access and delete saved larkhaven.example passwords.",
            "Sign in once with the current password and check that the lock does not return within 15 minutes.",
        ]
    },
    codes=["LID-1203"],
    notes=[
        "Repeated lockouts with no old devices can indicate a password-guessing attempt; report them to the service desk."
    ],
    policy="POL-003",
    ticket=K(
        shorts=[
            "Account locked out",
            "LID-1203 account is locked",
            "Locked out again",
            "cannot login account locked",
        ],
        descs=[
            "I keep getting 'Your account is locked. {code}' when I sign in on my {os} laptop.",
            "My account locks every hour or so even though I am typing the right password.",
            "Locked out after changing my password yesterday. Phone mail also stopped.",
        ],
        fixes=[
            "Unlocked via self-service. Old password was still saved in the phone mail app; user updated it and the lockouts stopped.",
            "Cleared stale saved credentials on the laptop and removed the old mail profile on the tablet. No further lockouts after 30 minutes.",
        ],
        weight=2.2,
        priority=(0, 8, 67, 25),
    ),
)

T(
    "password-requirements",
    "LarkID password rules",
    system="LarkID",
    category=ACCESS,
    subcategory="Password",
    kind="reference",
    summary="The rules a LarkID password must meet, taken from the Password and MFA Policy version 4.0.",
    steps={
        "any": [
            "Use at least 14 characters; a phrase of four or more words is recommended.",
            "Do not reuse any of your last 10 passwords.",
            "Passwords no longer expire on a schedule; you must change yours only if it may have been exposed.",
            "Never share a password, including with IT staff. The service desk will never ask for it.",
            "Store work passwords only in VaultKey, the approved password manager.",
        ]
    },
    notes=[
        "Version 3.2 of the policy required 12 characters and a change every 90 days. Those rules ended on 1 March 2026."
    ],
    policy="POL-003",
    ticket=K(
        shorts=[
            "Password policy question",
            "How often do I need to change my password",
            "password rules?",
        ],
        descs=[
            "Do we still have to change passwords every 90 days? My colleague says no.",
            "What are the requirements for a new password? The reset page rejected mine.",
        ],
        fixes=[
            "Explained the current rules: 14 characters minimum, no scheduled expiry, last 10 passwords blocked. Shared the KB article."
        ],
        weight=0.4,
        priority=(0, 0, 30, 70),
    ),
)

T(
    "mfa-setup",
    "Set up LarkID Authenticator",
    system="LarkID Authenticator",
    category=ACCESS,
    subcategory="MFA",
    kind="how-to",
    summary="Install LarkID Authenticator on your phone and register it as your sign-in approval method.",
    steps={
        "ios": [
            "Install LarkID Authenticator from the App Store.",
            "On your laptop, open https://id.larkhaven.example/security and choose Add method, then Authenticator app.",
            "In the app, tap Add account and scan the QR code shown on the laptop.",
            "Allow notifications when iOS asks; approvals arrive as notifications.",
            "Approve the test prompt and type the two-digit number to finish.",
        ],
        "android": [
            "Install LarkID Authenticator from Google Play, or from the work profile store on an enrolled phone.",
            "On your laptop, open https://id.larkhaven.example/security and choose Add method, then Authenticator app.",
            "In the app, tap Add account and scan the QR code shown on the laptop.",
            "Turn off battery optimisation for the app so approval prompts are not delayed.",
            "Approve the test prompt and type the two-digit number to finish.",
        ],
    },
    notes=[
        "Text-message codes are not an approved method. A FIDO2 security key can be registered as a second method."
    ],
    policy="POL-003",
    ticket=K(
        shorts=[
            "Set up MFA",
            "Need help with Authenticator setup",
            "How to register authenticator app",
        ],
        descs=[
            "I am new and need to set up the authenticator app on my {os} phone. The QR code will not scan.",
            "Please help me register LarkID Authenticator. I do not get the approval notification.",
        ],
        fixes=[
            "Walked the user through registration at id.larkhaven.example/security. Notifications were disabled; enabled them and the test approval worked.",
        ],
        weight=1.0,
        priority=(0, 4, 60, 36),
    ),
)

T(
    "mfa-code-rejected",
    "Fix rejected approval codes in LarkID Authenticator (error LID-MFA-102)",
    system="LarkID Authenticator",
    category=ACCESS,
    subcategory="MFA",
    kind="troubleshooting",
    summary="Error LID-MFA-102 means the code from the phone does not match the server, almost always because the phone clock is wrong.",
    symptoms=[
        "Sign-in shows 'Verification failed. LID-MFA-102'.",
        "Six-digit codes are rejected although they are typed correctly.",
    ],
    causes=[
        "The phone date, time or time zone is set manually.",
        "The account was re-registered and the old entry is still in the app.",
    ],
    steps={
        "any": [
            "On the phone, set date and time to automatic and confirm the time zone is correct.",
            "Close and reopen LarkID Authenticator, then try a new code.",
            "If there are two Larkhaven entries in the app, delete the older one.",
            "Use a push approval instead of typing a code if the option is offered.",
            "If codes are still rejected, raise a ticket; the Identity and Access team will reset your registration after verifying your identity.",
        ]
    },
    codes=["LID-MFA-102"],
    group=IAM,
    policy="POL-003",
    ticket=K(
        shorts=[
            "MFA code rejected",
            "Authenticator codes not working LID-MFA-102",
            "Verification failed error",
        ],
        descs=[
            "Every code from the authenticator app is rejected with {code}. I am travelling this week.",
            "Verification failed again and again. The codes are right, I checked twice.",
            "Got a new SIM and now the app codes do not work when I sign in to VPN.",
        ],
        fixes=[
            "Phone clock was set manually and was four minutes off. Switched to automatic time; codes accepted.",
            "Duplicate account entry in the app. Removed the stale entry and tested a push approval successfully.",
        ],
        weight=1.4,
        priority=(0, 10, 65, 25),
    ),
)

T(
    "mfa-new-phone",
    "Move LarkID Authenticator to a new phone",
    system="LarkID Authenticator",
    category=ACCESS,
    subcategory="MFA",
    kind="how-to",
    summary="Register a new phone while you still have the old one, or ask for a verified reset if the old phone is gone.",
    steps={
        "any": [
            "If you still have the old phone, sign in at https://id.larkhaven.example/security and approve with the old phone.",
            "Choose Add method, register the app on the new phone, then remove the old phone from the list.",
            "If the old phone is lost, broken or wiped, raise a HelpHub ticket in the category MFA reset.",
            "The Identity and Access team will verify you by video call with your manager present or with your badge at a Tech Bar.",
            "After verification you receive a temporary access pass valid for 60 minutes to register the new phone.",
        ]
    },
    notes=[
        "A lost phone that held work data must also be reported as a lost device within 2 hours."
    ],
    group=IAM,
    policy="POL-003",
    ticket=K(
        shorts=[
            "New phone need MFA moved",
            "Lost phone cannot approve sign in",
            "Authenticator on new phone",
        ],
        descs=[
            "I replaced my phone at the weekend and the old one is already wiped. I cannot approve any sign-in.",
            "My phone was stolen yesterday. I need the authenticator on my replacement phone.",
            "Upgraded my phone, how do I move the authenticator app across?",
        ],
        fixes=[
            "Identity verified by video call with the line manager. Issued a temporary access pass; user registered the new phone and removed the old one.",
            "User still had the old phone. Guided adding the new device at id.larkhaven.example/security and removing the old one.",
        ],
        weight=1.2,
        priority=(0, 12, 68, 20),
    ),
)

T(
    "sso-app-missing",
    "An application tile is missing from the LarkID portal",
    system="LarkID",
    category=ACCESS,
    subcategory="Single sign-on",
    kind="troubleshooting",
    summary="A missing tile means your account is not in the access group for that application, or the portal has not refreshed yet.",
    symptoms=[
        "A colleague sees a tile that you do not.",
        "A bookmark opens the app and shows 'You do not have access'.",
    ],
    causes=[
        "Access was never requested or was removed in a quarterly access review.",
        "Access was approved less than 60 minutes ago.",
    ],
    steps={
        "any": [
            "Open https://id.larkhaven.example and choose Refresh my apps from the profile menu.",
            "Sign out of the portal and sign in again.",
            "Check HelpHub, My requests, to see whether an access request is still waiting for approval.",
            "If you have never requested the application, follow the article Request access to an application.",
        ]
    },
    policy="POL-002",
    ticket=K(
        shorts=[
            "App missing from LarkID portal",
            "Cannot see application tile",
            "You do not have access message",
        ],
        descs=[
            "The tile for the expense tool has gone from my portal. It was there last week.",
            "My teammate can see the reporting app in LarkID but I cannot. Same team, same role.",
        ],
        fixes=[
            "Access was removed in the quarterly review because the app had not been used for 90 days. User raised a new access request.",
            "Access was approved 20 minutes earlier. Refreshed apps in the portal and the tile appeared.",
        ],
        weight=0.8,
        priority=(0, 3, 60, 37),
    ),
)

T(
    "access-request-app",
    "Request access to an application",
    system="HelpHub",
    category=ACCESS,
    subcategory="Application access",
    kind="how-to",
    summary="Request application access in HelpHub; standard applications need your manager's approval and restricted ones also need the data owner's.",
    steps={
        "any": [
            "Open https://helphub.larkhaven.example and choose Request access.",
            "Search for the application and pick the role you need; choose the lowest role that lets you do your job.",
            "Write the business reason in one or two sentences. Requests without a reason are returned.",
            "Submit. Your line manager is asked to approve; restricted applications are then sent to the data owner.",
            "When approved, access is granted automatically within 60 minutes and the tile appears in the LarkID portal.",
        ]
    },
    notes=[
        "Restricted applications include FinSight, CoreERP and PeopleHub administration.",
        "Nobody can approve their own request, and the service desk cannot approve on a manager's behalf.",
    ],
    group=IAM,
    policy="POL-002",
    ticket=K(
        shorts=[
            "Need access to an application",
            "Access request",
            "Please grant access to CoreERP",
            "Request access for new team member",
        ],
        descs=[
            "I have moved to a new team and need access to the same applications as my colleagues.",
            "Please give me access to CoreERP read-only. My manager already agreed by email.",
            "How do I get access to the project tracker? I cannot find where to request it.",
        ],
        fixes=[
            "Explained that approval must be given in HelpHub, not by email. User submitted the request; manager approved and access was granted.",
            "Raised the access request with the user. Approved by the line manager the same day; tile visible after refresh.",
        ],
        weight=2.0,
        priority=(0, 2, 55, 43),
    ),
)

T(
    "finsight-access",
    "Get access to FinSight, the finance reporting tool",
    system="FinSight",
    category=ACCESS,
    subcategory="Application access",
    kind="how-to",
    summary="FinSight is a restricted application: access needs your manager and the Finance data owner to approve, and a free named licence.",
    steps={
        "any": [
            "In HelpHub choose Request access and search for FinSight.",
            "Pick a role: Viewer for reports, Analyst to build reports, Admin for the Finance systems team only.",
            "State which cost centres or legal entities you need to see and why.",
            "After your manager approves, the request goes to the Finance data owner, who answers within 2 business days.",
            "If no licence is free, the request waits until one is reclaimed; licences unused for 60 days are reclaimed automatically.",
            "On first sign-in open FinSight from the LarkID portal and accept the confidentiality notice.",
        ]
    },
    notes=[
        "FinSight holds Restricted data. Reports must not be exported to personal devices or personal cloud storage."
    ],
    group=IAM,
    policy="POL-002",
    ticket=K(
        shorts=[
            "Need access to FinSight",
            "Access to finance reporting tool",
            "FinSight request pending",
        ],
        descs=[
            "I need access to the finance reporting tool for month-end. Viewer is enough.",
            "My FinSight request has been pending for three days. Who needs to approve it?",
            "Joined the finance team this week and need FinSight analyst access.",
        ],
        fixes=[
            "Request was waiting for the Finance data owner. Chased approval; licence assigned and access confirmed.",
            "No free FinSight licence. Reclaimed one unused for more than 60 days, then granted Viewer access after both approvals.",
        ],
        weight=0.8,
        priority=(0, 5, 60, 35),
    ),
)

T(
    "shared-folder-access",
    "Request access to a shared folder",
    system="File Shares",
    category=ACCESS,
    subcategory="Shared folder",
    kind="how-to",
    summary="Access to a departmental shared folder is approved by the folder owner, not by IT.",
    steps={
        "any": [
            "Ask a colleague for the exact folder path, for example \\\\files.larkhaven.example\\finance\\budgets.",
            "In HelpHub choose Request access, then Shared folder, and paste the path.",
            "Choose Read or Read and write.",
            "The folder owner receives the request and approves or declines it.",
            "After approval, sign out of your laptop and sign in again so the new permission applies.",
        ]
    },
    policy="POL-002",
    ticket=K(
        shorts=[
            "Access denied to shared folder",
            "Need access to team drive",
            "Cannot open folder on files server",
        ],
        descs=[
            "I get access denied when opening the budgets folder on the shared drive.",
            "Please add me to the marketing shared folder, I need to upload files today.",
        ],
        fixes=[
            "User was not in the folder group. Raised a shared folder request; owner approved and access worked after sign-out and sign-in.",
        ],
        weight=1.5,
        priority=(0, 3, 57, 40),
    ),
)

T(
    "shared-mailbox-request",
    "Request a shared mailbox or access to one",
    system="Email",
    category=ACCESS,
    subcategory="Shared mailbox",
    kind="how-to",
    summary="A shared mailbox has an owner who approves members; new mailboxes take up to 2 business days.",
    steps={
        "any": [
            "For access to an existing mailbox, choose Request access, then Shared mailbox, in HelpHub and enter its address.",
            "The mailbox owner approves the request; the mailbox then appears in Outlook automatically within 60 minutes.",
            "For a new mailbox, choose New shared mailbox and give the address you want, the owner and the first members.",
            "Addresses must describe a function, for example invoices-emea@larkhaven.example, not a person.",
        ]
    },
    policy="POL-002",
    ticket=K(
        shorts=[
            "Shared mailbox access",
            "New shared mailbox request",
            "Cannot see team mailbox in Outlook",
        ],
        descs=[
            "Please add me to the customer-returns shared mailbox.",
            "We need a new shared mailbox for the events team with five members.",
        ],
        fixes=[
            "Owner approved the membership request. Mailbox appeared in Outlook after a restart."
        ],
        weight=0.7,
        priority=(0, 2, 50, 48),
    ),
)

T(
    "windows-hello-pin",
    "Reset a Windows Hello PIN that stopped working (error 0x80090016)",
    system="Windows",
    category=ACCESS,
    subcategory="Windows Hello",
    kind="troubleshooting",
    summary="Error 0x80090016 means the PIN store on the laptop is damaged; removing and recreating the PIN fixes it.",
    symptoms=[
        "Windows shows 'Something went wrong and your PIN isn't available. 0x80090016'.",
        "Fingerprint and face sign-in stop at the same time.",
    ],
    causes=[
        "The laptop was restored, re-imaged or had its security chip reset.",
        "The password was changed on another device.",
    ],
    steps={
        "windows": [
            "On the sign-in screen choose Sign-in options and sign in with your LarkID password instead.",
            "Open Settings, Accounts, Sign-in options, PIN (Windows Hello) and choose Remove.",
            "Restart the laptop while connected to the office network or SecureTunnel.",
            "Return to Sign-in options, choose Set up under PIN and approve the LarkID prompt.",
            "Add fingerprint or face recognition again if you use them.",
        ]
    },
    codes=["0x80090016"],
    ticket=K(
        shorts=[
            "PIN not available 0x80090016",
            "Windows Hello PIN stopped working",
            "Cannot sign in with PIN",
        ],
        descs=[
            "My laptop says something went wrong and your PIN isn't available, error {code}.",
            "PIN and fingerprint both stopped working after I changed my password.",
        ],
        fixes=[
            "Signed in with password, removed and recreated the Windows Hello PIN. Fingerprint re-enrolled."
        ],
        weight=0.6,
        priority=(0, 4, 66, 30),
    ),
)

T(
    "keychain-prompts",
    "Stop repeated keychain password prompts on macOS",
    system="macOS",
    category=ACCESS,
    subcategory="Keychain",
    kind="troubleshooting",
    summary="After a password change the Mac keychain still uses the old password, so apps keep asking for the login keychain password.",
    symptoms=[
        "Messages such as 'accountsd wants to use the login keychain' appear repeatedly.",
        "Outlook and Teams ask for a password after every restart.",
    ],
    causes=["The LarkID password was changed on another device or in the browser."],
    steps={
        "macos": [
            "When prompted, try your previous password once; if it works, choose Update Keychain Password.",
            "If you do not remember the old password, open Keychain Access, choose Settings and Reset Default Keychains.",
            "Restart the Mac and sign in with your current LarkID password.",
            "Sign in to Outlook, Teams and OneDrive again when they ask.",
        ]
    },
    notes=[
        "Resetting the default keychain removes saved Wi-Fi and website passwords; VaultKey entries are not affected."
    ],
    ticket=K(
        shorts=[
            "Mac keeps asking for keychain password",
            "login keychain prompt keeps popping up",
            "accountsd wants to use login keychain",
        ],
        descs=[
            "Since I changed my password my Mac asks for the login keychain password every few minutes.",
            "Constant keychain pop-ups on my {model}. Cancelling does not help.",
        ],
        fixes=[
            "Old password no longer known. Reset the default keychain, restarted and re-signed in to Outlook and Teams. Prompts stopped."
        ],
        weight=0.6,
        priority=(0, 2, 60, 38),
    ),
)

T(
    "password-manager-setup",
    "Set up VaultKey, the approved password manager",
    system="VaultKey",
    category=ACCESS,
    subcategory="Password manager",
    kind="how-to",
    summary="VaultKey stores work passwords and is the only approved password manager.",
    steps={
        "any": [
            "Install VaultKey from App Hub on your laptop.",
            "Open it and choose Sign in with LarkID; there is no separate master password.",
            "Add the browser extension when prompted and pin it to the toolbar.",
            "Import passwords saved in the browser, then turn off the browser's own password saving.",
            "Share team passwords through a VaultKey shared vault, never by email or chat.",
        ]
    },
    policy="POL-003",
    ticket=K(
        shorts=[
            "VaultKey setup",
            "Password manager not filling passwords",
            "How do I share a password with my team",
        ],
        descs=[
            "VaultKey extension is installed but it does not fill in passwords on any site.",
            "What is the approved way to share the team account password?",
        ],
        fixes=[
            "Extension was not signed in. Signed in with LarkID and enabled autofill. Created a shared vault for the team account."
        ],
        weight=0.4,
        priority=(0, 0, 40, 60),
    ),
)
