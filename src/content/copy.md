# YellowForce site copy (final, 2026-10-25)

Source of truth for every word on the site. Page builders paste from here; do not rewrite copy in the HTML.
If a line does not fit a layout, flag it to the copy lane instead of editing it in place.

## Conventions

- `Label` lines are the small uppercase bracket labels. Write them exactly as given, spaces inside the brackets: `( 24/7 )`. CSS uppercases them.
- `H0` = giant hero type (beats separated by periods; `/` marks the intended line break). `H1`, `H2`, `H3` = normal heading levels.
- Case: Title Case only for the Home hero beats ("Fight AI. / With AI."). Every other heading on the site, inner H1s included, is sentence case ("Your security. / Run by us."), as on the reference.
- `Meta L` / `Meta R` = the two short meta lines to the right of a section H2 (left one is the bracket label, right one the short fact).
- `[copy-email]` = a `<button>` that copies `info@yellow-force.com` and shows the toast (see Global). Never a mailto link, never a form.
- `-> /path/` = link target.
- Apostrophes are written straight (`'`). Builders may convert them to typographic `’` in HTML. No em dashes or spaced en dashes anywhere.
- Inside article bodies: `####` = article H2, `#####` = article H3, `>` = pull quote, `- **Lead.** text` = bold-lead list.
- Year, location, owner: "© 2026 YellowForce" and "San Francisco, CA". Nothing else.

---

## Core claim (Axel, 2026-10-26: every page says this the same way)

- Site wording (use exactly, do not paraphrase): "We run your entire cybersecurity. Our AI and our experts stop every threat, AI swarms included. 24/7."
- Axel, 2026-10-26: the older long claim ("We stop every cyber threat, especially AI swarms. We fight AI with AI, plus our cyber experts. Fully managed, A to Z: ...") is too long, unclear and unpleasant to read. Do not bring it back, on Home or anywhere else.
- Short sentences, one idea each. No long claim sentences stacked with commas and colons.
- Allowed short variants: "Fight AI with AI" (hero, tagline), "Fully managed, A to Z", "every threat", "AI agents and cyber experts", "one team", "24/7".
- Order matters: what we do (run all of it), who does it (our AI and our experts) and what they stop (every threat, AI swarms included), when (24/7).

## Global

### Toast (copy email)
- Success title: Email copied
- Success body: info@yellow-force.com
- Under attack variant, extra line: Put URGENT in the subject. We answer 24/7.
- Fallback (clipboard blocked, address text is selected instead): Press Cmd+C or Ctrl+C to copy
- Button aria-label: Copy email address info@yellow-force.com

### Pill nav
- Logo link aria-label: YellowForce home
- Menu button aria-label: Open menu / Close menu
- Center line: per-page tagline (each page below has its own `Nav tagline`)
- Menu rows (label / meta / target):
  - Home / Fight AI with AI / -> /
  - Services / Six practices / expands:
    - All services -> /services/
    - Deploy and connect -> /services/#deploy
    - Detect 24/7 -> /services/#detect
    - Respond -> /services/#respond
    - Attack -> /services/#attack
    - Harden -> /services/#harden
    - Govern -> /services/#govern
  - Coverage / 10 domains / expands:
    - All coverage -> /coverage/
    - Network -> /coverage/network/
    - Endpoint and devices -> /coverage/endpoint/
    - Cloud -> /coverage/cloud/
    - Identity and access -> /coverage/identity/
    - Email -> /coverage/email/
    - Apps and APIs -> /coverage/applications/
    - Data -> /coverage/data/
    - AI and agents -> /coverage/ai-agents/
    - OT and IoT -> /coverage/ot-iot/
    - Governance and risk -> /coverage/governance/
  - About / San Francisco / -> /about/
  - Insights / Notes from the front / -> /insights/
  - Contact / Always on / -> /contact/
  - Under attack? / We answer 24/7 / [copy-email] with the Under attack toast variant
- Panel CTA button: Talk to us -> /contact/

### CTA band (Home, Services, Coverage, every domain page, About, Insights, every article. Not on Contact, Privacy, Security, 404)
- H0: We'll take it / from here. (sentence case, like every heading except the Home hero)
- Text: Tell us what you run. We go in, connect everything and defend it 24/7, starting today.
- Button 1 (light): Talk to us -> /contact/
- Button 2 (dark): How we work -> /services/

### Footer
- Blurb: YellowForce is a fully managed cybersecurity company. We run your entire security, A to Z. Our AI and our experts stop every threat, AI swarms included. 24/7.
- Email line: info@yellow-force.com [copy-email]
- Big links: Home, Services, Coverage, About, Insights, Contact
- Small links: Privacy -> /privacy/ · Security -> /security/ · security.txt -> /.well-known/security.txt
- Bottom bar left: © 2026 YellowForce
- Bottom bar right: San Francisco, CA
- Optional small line: Fighting AI with AI, 24/7.

---

## Page: Home

- URL: /
- Meta title: YellowForce | Fully managed cybersecurity, 24/7
- Meta description: We run your entire cybersecurity. Our AI and our experts stop every threat, AI swarms included. Fully managed, 24/7.
- Nav tagline: Fight AI with AI

### 01 Hero (inset dark card)
- Label (small, above or below the H0; keep it on mobile, the status card hides there): ( Fully managed cybersecurity · 24/7 )
- H0: Fight AI. / With AI.
- Status card (Axel, 2026-10-26: the whole card is a [copy-email] button with the Under attack toast; no "Status: live", no graphic):
  - Label (with amber live dot): Under attack?
  - Line: Write to us now. We answer 24/7.
  - Small: info@yellow-force.com (+ copy icon)
  - Thumb: real photo, photo/insight-2 (lit hand on a keyboard; brighter than about-strip-1 at thumb size)
  - aria-label: Under attack? Copy email address info@yellow-force.com. We answer 24/7.
  - Hidden on phones (<= 767) like the reference; the menu's "Under attack?" row covers phones.

### 02 Statement (scroll-filled) + marquee
- Statement (Axel, 2026-10-26, exact): We run your entire cybersecurity. Our AI and our experts stop every threat, AI swarms included. 24/7.
- Marquee (text only, no logos; repeat the set for the loop): Network · Endpoint · Cloud · Identity · Email · Apps and APIs · Data · AI agents · OT and IoT · Governance

### 03 What we stop. (2x2 cards)
- H2: What we stop.
- Meta L: ( Four threats )
- Meta R: AI made all of them faster
- Card link text (all cards): See how we stop it
- Cards (name / meta line 1 / meta line 2 / one line / target):
  1. AI swarms / Threat 01 / AI and agents / Many AI agents hitting you at once, sharing what they find. We meet them with our own. / -> /insights/ai-swarms/
  2. Hijacked agents / Threat 02 / AI and agents / Your own AI turned against you through prompt injection and poisoned tools. / -> /coverage/ai-agents/
  3. Deepfakes / Threat 03 / Email and identity / Flawless emails, cloned voices, fake executives on video. Caught before anyone acts. / -> /coverage/email/
  4. Ransomware / Threat 04 / Data and devices / Steal, encrypt, extort. We cut it off at the first move and keep your backups out of reach. / -> /coverage/data/

### 04 Coverage table (replaces the live projects table)
- H2: Every domain, covered.
- Meta L: ( 10 / 10 domains )
- Meta R: Watched 24/7
- Row layout: domain (H3) / what it covers / bar (full, all live) with meta "Watched 24/7" and "AI + experts" / what we do (3 words)
- Three rows, like the reference table (2026-10-26, round 3: was five): AI first, identity and email (where the deepfakes land), then one row for the other seven (the marquee above names all ten). On phones a row is just domain | bar. Keep each "covers" line on one line at 1440 (about 30 characters).
- Rows (domain / covers / what we do / target):
  1. AI and agents / Swarms, agents, models / Stop swarms, hijacks / -> /coverage/ai-agents/
  2. Identity and email / Takeovers, phishing, deepfakes / Stop impersonation / -> /coverage/identity/
  3. Seven more domains / Network, cloud, data and more / See all 10 domains / -> /coverage/

### 05 What we do. (numbered slider)
- H2: What we do.
- Meta L: ( Six practices )
- Meta R: One team, A to Z
- Slider arrows aria-label: Previous practice / Next practice
- Cards (number / title / line / target). Each line fits two lines on the card at 1440 so the titles line up:
  - ( 001 ) / Deploy and connect / We go in and connect our tech to every tool you already run. / -> /services/#deploy
  - ( 002 ) / Detect 24/7 / AI agents watch every signal across every domain, day and night. / -> /services/#detect
  - ( 003 ) / Respond / We shut attacks down in real time and run the incident end to end. / -> /services/#respond
  - ( 004 ) / Attack / AI and human red teamers attack you first to find every way in. / -> /services/#attack
  - ( 005 ) / Harden / We fix what we find, then retest until every gap is closed. / -> /services/#harden
  - ( 006 ) / Govern / Policies, risk and compliance, kept current as you change. / -> /services/#govern

### 06 Reel
- Label: ( The reel )
- H2: Defense at / machine speed.
- Island pill: dot + "YellowForce reel" + live San Francisco time (SF 12:00:00) + play/pause
- Picture (live canvas, no video): a filmic long exposure graded like the generated images. Deep navy edges (#030B1C) rising to at most #0B2350 behind the light, a diagonal river of soft amber trails, a warm amber bloom with a white core, grain. No blue-white light, no crisp lines, no comet heads.
- Play/pause aria-label: Play reel / Pause reel

### 07 Why YellowForce. (dark quote card + 5 cards, in the client quotes slot)
- H2: Why YellowForce.
- Meta L: ( Five reasons )
- Meta R: One team, every domain
- Dark card (first slide):
  - Big figure: 24/7
  - Line next to it: AI agents on every signal. Experts on every call. Day and night, in every domain.
  - Bottom: AI and experts / on watch now (two lines), next to a row of 4 overlapping round chips in place of faces: three close crops of our amber light imagery (gen/about-2 burst, gen/threat-swarm vortex, gen/status trail) and a paper chip with the mark
- Cards (text / label 1 / label 2). Alternate top and bottom like the original layout:
  1. You don't get software to manage. You get a team that runs your security from A to Z. / ( 01 ) / Fully managed
  2. Attackers use AI to move at machine speed. Our agents match it. Our experts make the call. / ( 02 ) / AI + experts
  3. Attacks don't keep office hours. We watch, answer and respond 24/7, weekends included. / ( 03 ) / Always on
  4. Network to cloud, inbox to AI agents. One team covers it all, so nothing falls between vendors. / ( 04 ) / Every domain
  5. We plug into the tools and workflows you already have. Nothing to rip out, nothing to relearn. / ( 05 ) / On top of your stack

### 08 FAQ
- H2: Before you let us in.
- Six questions (the reference has five; "Who does the work?" and "What does it cost?" were cut, the statement and the reasons cards answer the first).
- Q/A:
  1. Q: Is this software?
     A: No. We're a team, not a tool. We bring our own AI, run your security for you and answer 24/7.
  2. Q: What do you cover?
     A: All of it. Network, devices, cloud, identity, email, apps, data, AI agents, OT and compliance, with one team.
  3. Q: Do we have to replace our tools?
     A: No. We connect to what you already run and work on top of your workflows, your chat and your tickets.
  4. Q: How fast can you start?
     A: Right away. We go in, connect your systems and start defending from day one.
  5. Q: Where does our data stay?
     A: In your environment wherever possible. We take only the access the job needs and log every action we take.
  6. Q: We're under attack right now.
     A: Write to us now. Copy our email, put URGENT in the subject and send. We answer 24/7, nights and weekends included.
     Button: Copy email [copy-email, Under attack toast]

### 09 Insights teaser
- H2: Notes from the front.
- Meta L: ( Insights )
- Meta R: Threats and how we fight them
- Big cards (2): ai-swarms, fight-ai-with-ai (category / date / title from the Insights section below)
- Index rows (all 3): category / title / date / arrow
- Link under the list: All notes -> /insights/

### 10 CTA band
- Global CTA band.

### 11 Footer
- Global footer.

---

## Page: Services

- URL: /services/
- Meta title: Services | YellowForce fully managed cybersecurity
- Meta description: Deploy, detect, respond, attack, harden, govern. Six practices, one team, run for you 24/7 on top of the tools you already own.
- Nav tagline: We run it all

### 01 Hero
- Label: ( Services )
- H1: Your security. / Run by us.
- Intro (optional line under H1): We don't sell you a tool. We run your cybersecurity for you, from A to Z, 24/7.

### 02 Practice cards (right under the H1, no hero image, like the work index; 2 columns, square cards with frosted label, each -> its row anchor below)
- Card link text: See the practice
- Cards (number / title / meta):
  - 001 / Deploy and connect / Day one
  - 002 / Detect 24/7 / Always on
  - 003 / Respond / Real time
  - 004 / Attack / Continuous
  - 005 / Harden / Fixed and retested
  - 006 / Govern / Kept current

### 03 Problem (below the cards, before the practice rows)
- H2: Too many tools. / Nobody in charge.
- Text: Most companies buy a tool for every problem. A firewall here, an endpoint agent there, an email filter, a cloud scanner, an AI add-on. Each one sends alerts. Nobody owns all of them, and attackers walk through the gaps in between. We take the whole thing over. One team, every domain, every alert, 24/7.

### 04 Practice rows (anchors: #deploy #detect #respond #attack #harden #govern; two per row on desktop, one per row on phones; 3 items each, kept short so the page stays close to the work index length)
- ( 001 ) Deploy and connect. (#deploy)
  - Line: We go in, put our technology inside your environment and connect every tool you already run.
  - Includes:
    - Our AI agents deployed inside your environment
    - Every existing tool and log source connected
    - Your chat, tickets and workflows wired in
- ( 002 ) Detect 24/7. (#detect)
  - Line: AI agents watch every signal across every domain, day and night, and our experts confirm what matters.
  - Includes:
    - Every alert triaged by AI, instantly
    - Swarm and agent traffic spotted as it starts
    - Experts hunting across all ten domains, 24/7
- ( 003 ) Respond. (#respond)
  - Line: We contain and shut down attacks in real time, then run the incident end to end.
  - Includes:
    - Devices isolated, sessions killed, accounts locked in real time
    - Full investigation and root cause
    - Clean recovery and restore
- ( 004 ) Attack. (#attack)
  - Line: We attack you first, with AI and human red teamers, to find every way in before anyone else does.
  - Includes:
    - Continuous AI red teaming of apps, APIs and cloud
    - Phishing and deepfake drills on your people
    - Swarm-style attacks against your defenses
- ( 005 ) Harden. (#harden)
  - Line: We fix what we find. Patch, reconfigure and retest until the hole is closed.
  - Includes:
    - Patches and config changes done for you
    - Accounts, keys and permissions cleaned up
    - Every fix retested against the real attack
- ( 006 ) Govern. (#govern)
  - Line: Policies, risk and compliance, kept current as your company changes.
  - Includes:
    - Security policies written and maintained
    - Audit evidence ready when you need it
    - Customer security questionnaires answered

### 05 How we work. (styled like the progress table)
- H2: How we work.
- Meta L: ( Four steps )
- Meta R: Instant, then continuous
- Rows (step / title / text / bar label / end label; the bar label is only "Step 0N", no "of 04"):
  - 01 / Deploy. / We go inside your company and place our technology in your environment. Nothing to rip out. / Step 01 / Day one
  - 02 / Connect. / We plug into every system you run: cloud, devices, identity, email, code, logs and chat. Your workflows stay. / Step 02 / Day one
  - 03 / Defend. / Our AI agents and experts watch, hunt and respond across every domain. Attacks get shut down as they start. / Step 03 / 24/7
  - 04 / Improve. / We attack, fix and retest without stopping, so your defense gets harder to break every day. / Step 04 / Continuous

### 06 On top of your stack.
- H2: On top of your stack.
- Meta L: ( Integrations )
- Meta R: Keep the tools you have
- Text: We don't replace your tools. We connect to them, act through them and make them work as one.
- Tiles (category / what it covers):
  - Cloud / Accounts, workloads, storage, serverless
  - Identity / Single sign-on, directories, access
  - Devices / Laptops, servers, phones, endpoint tools
  - Network / Firewalls, VPNs, DNS, proxies
  - Email and docs / Mail, office suites, shared drives
  - Code and delivery / Repos, pipelines, packages, secrets
  - Logs and alerts / SIEM, log stores, monitoring
  - Tickets and chat / Issue trackers, team chat, on-call
  - AI tools and agents / Assistants, internal agents, model APIs, MCP servers
  - OT and IoT / Sensors, cameras, controllers, building systems
- Closing line: Running something else? If it has an API or writes logs, we can connect it. [copy-email] "Tell us what you run"

### 07 CTA band + footer
- No FAQ on this page (2026-10-26, page length): Home carries the FAQ, incl. "Is this software?".
- Global.

---

## Page: Coverage (index)

- URL: /coverage/
- Meta title: Coverage | Every cyber domain, defended 24/7 | YellowForce
- Meta description: Network, endpoint, cloud, identity, email, apps, data, AI agents, OT and governance. All ten cyber domains, one team, 24/7.
- Nav tagline: Nothing left open

### 01 Hero
- Label: ( Coverage )
- H1: Every domain. / Every hour.

### 02 Intro
- Text: Attackers don't pick one door, and AI lets them try all of them at once. So we cover all ten domains of cybersecurity with one team, 24/7.

### 03 Domain cards (10, each -> its page)
- Card link text: See the domain
- Card titles are the short one-line names (same as the domain bar). The long name stays on the domain page (hero chip, principle meta, meta title).
- Cards (number / title / line):
  - 01 / Network / Every connection watched, every intruder cut off.
  - 02 / Endpoint / Laptops, servers and phones, isolated the moment they turn.
  - 03 / Cloud / Misconfigurations fixed, leaked keys revoked, every change watched.
  - 04 / Identity / Account takeovers stopped, sessions killed, access kept tight.
  - 05 / Email / Phishing, invoice fraud and deepfakes, caught before anyone acts.
  - 06 / Apps and APIs / Attacked by us first, fixed, then watched 24/7.
  - 07 / Data / Ransomware stopped, leaks blocked, backups kept safe.
  - 08 / AI agents / Swarms stopped, and your own agents kept on a leash.
  - 09 / OT and IoT / Sensors, cameras and control systems, found and protected.
  - 10 / Governance / Policies, risk and compliance, run and kept current.

### 04 CTA band + footer
- Global.

---

## Domain pages (shared parts)

Same skeleton for all ten, in this order: Hero (label, H1, intro) / The threat. (H2, text, gallery) / What we do. (dark section: H2, sub-line, 4 rows with a short tile) / Principle (quote block) / Related (2 cards) / CTA band / Footer.

- "What we do." sub-line (same on every domain page): Four jobs, run by our AI agents and experts, 24/7.
- Principle block meta: ( Our principle ) / the domain name
- Related heading: Related domains.
- Related card link text: See the domain
- Related card titles: the short names from the Coverage cards. Pairs are set so every domain is linked from exactly two pages.

---

## Domain: Network

- URL: /coverage/network/
- Meta title: Network security | YellowForce
- Meta description: We watch every connection on your network 24/7, spot scanning and lateral movement as it starts, and cut off intruders in real time.
- Nav tagline: Every packet, watched

### Hero
- Label: Coverage 01 · Network security · 24/7
- H1: Network.
- Intro: Your network is the road every attack travels. We watch every connection on it, 24/7, and cut off anything that doesn't belong.

### The threat.
- Text: Attackers scan for exposed services, weak VPNs and unpatched edge devices, then slip in and move sideways until they reach something valuable. Once inside, they hide in normal traffic: remote access tools, encrypted tunnels, DNS. AI makes every step faster. Agents scan for a new flaw soon after it goes public, test thousands of entry points in parallel and shape their traffic to look like your own users. Ransomware crews and swarms run the same playbook. The time between a flaw going public and someone trying it on you keeps getting shorter.

### What we do.
| Label | Text | Tile |
|---|---|---|
| Watch | Every connection in and out, mapped and monitored around the clock. | 24/7 |
| Detect | AI spots scanning, lateral movement and hidden tunnels as they start. | Real time |
| Respond | We block hostile traffic and cut off compromised segments in real time. | Instant |
| Harden | We close exposed services, patch edge devices and segment what matters. | Retested |

### Principle
- Quote: If it touches your network, we see it.

### Related
- Endpoint -> /coverage/endpoint/
- OT and IoT -> /coverage/ot-iot/

---

## Domain: Endpoint

- URL: /coverage/endpoint/
- Meta title: Endpoint and device security | YellowForce
- Meta description: Every laptop, server and phone watched 24/7. AI catches new malware by behavior and we isolate infected devices in real time.
- Nav tagline: Every device, guarded

### Hero
- Label: Coverage 02 · Endpoint and device security · 24/7
- H1: Endpoints.
- Intro: Every laptop, server and phone is a way in. We watch all of them, day and night, and isolate any device that turns.

### The threat.
- Text: Most attacks still land on a device: a malicious attachment, a fake software update, a stolen session cookie, a vulnerable driver used to switch off security tools. From there, attackers grab credentials and spread. AI writes new malware variants faster than signatures can follow, tailors lures to each employee and helps attackers live off the land with your own admin tools, so nothing looks foreign. Infostealers quietly lift passwords and session tokens from browsers. Then ransomware hits every machine it can reach at once.

### What we do.
| Label | Text | Tile |
|---|---|---|
| Watch | Every laptop, server and phone, monitored around the clock. | 24/7 |
| Detect | AI judges what a program does, so brand new malware gets caught too. | Every device |
| Respond | We isolate an infected device in real time, then clean it up. | Instant |
| Harden | Patches, encryption and safe settings rolled out and kept current. | Always current |

### Principle
- Quote: Every device is a door. We guard all of them.

### Related
- Network -> /coverage/network/
- Data -> /coverage/data/

---

## Domain: Cloud

- URL: /coverage/cloud/
- Meta title: Cloud security | YellowForce
- Meta description: Your cloud changes every hour. We watch it 24/7, fix misconfigurations, revoke leaked keys and shut down rogue resources in real time.
- Nav tagline: Every change, checked

### Hero
- Label: Coverage 03 · Cloud security · 24/7
- H1: Cloud.
- Intro: Your cloud changes every hour, and every change can open a door. We watch it 24/7 and close what attackers would use.

### The threat.
- Text: Cloud breaches rarely need clever exploits. A storage bucket left public, an access key pushed to a code repo, an admin role nobody needs, a test environment nobody remembers. Attackers find these with automated scans and use them fast. AI agents now read leaked code and config files at scale, pull out secrets and chain small misconfigurations into a full account takeover. Once inside, attackers create hidden users, spin up machines to mine crypto on your bill or quietly copy your data out.

### What we do.
| Label | Text | Tile |
|---|---|---|
| Watch | Every account, workload and permission, monitored 24/7. | 24/7 |
| Detect | AI catches risky changes, leaked keys and strange access as they happen. | Real time |
| Respond | We revoke keys, lock roles and shut down rogue resources in real time. | Instant |
| Harden | We fix misconfigurations, trim permissions and keep your setup clean as it changes. | Retested |

### Principle
- Quote: Nothing in your cloud goes unwatched.

### Related
- Identity -> /coverage/identity/
- Apps and APIs -> /coverage/applications/

---

## Domain: Identity

- URL: /coverage/identity/
- Meta title: Identity and access security | YellowForce
- Meta description: Attackers don't break in, they sign in. We guard every account, session and permission 24/7 and stop account takeovers in real time.
- Nav tagline: Every sign-in, watched

### Hero
- Label: Coverage 04 · Identity and access · 24/7
- H1: Identity.
- Intro: Attackers don't break in anymore. They sign in. We guard every account, every session and every access right, 24/7.

### The threat.
- Text: Stolen passwords, phished one-time codes, push attacks that spam approval requests until someone taps yes, help desk calls that talk an agent into a reset. Once an attacker holds a valid account, every tool trusts them. AI makes this cheap. It runs password spraying across thousands of accounts, writes convincing reset requests and clones a manager's voice for a call to IT. Session tokens stolen from browsers skip multi-factor checks entirely. And service accounts or API keys with too much power are the quietest way in.

### What we do.
| Label | Text | Tile |
|---|---|---|
| Watch | Every sign-in, session and permission change, tracked 24/7. | 24/7 |
| Detect | AI spots impossible travel, token theft and odd access patterns as they happen. | Real time |
| Respond | We kill sessions, lock accounts and reset access in real time. | Instant |
| Harden | Phishing-resistant multi-factor, least privilege and clean admin rights. | Retested |

### Principle
- Quote: Every account is a key. We know where all of them are.

### Related
- Cloud -> /coverage/cloud/
- Email -> /coverage/email/

---

## Domain: Email

- URL: /coverage/email/
- Meta title: Email security: phishing, BEC and deepfakes | YellowForce
- Meta description: AI-written phishing, invoice fraud and deepfake executives. We scan every inbox 24/7 and pull malicious emails everywhere at once.
- Nav tagline: That's not your CEO

### Hero
- Label: Coverage 05 · Email security · 24/7
- H1: Email.
- Intro: Email is still where most attacks start. Now the sender can be an AI that writes like your CEO and talks like your CFO.

### The threat.
- Text: Phishing used to be easy to spot. Not anymore. AI writes flawless messages in any language, studies your people through their public profiles and replies in real time like a human would. Business email compromise hijacks a real vendor thread and swaps the bank details on an invoice. Deepfake voice and video calls impersonate executives to rush a payment or a password reset. QR codes, shared document links and fake sign-in pages carry the attack past basic filters. One click or one wire transfer is enough.

### What we do.
| Label | Text | Tile |
|---|---|---|
| Watch | Every inbox, link and attachment, scanned around the clock. | 24/7 |
| Detect | AI reads intent, so payment fraud and impersonation get flagged even without a bad link. | Real time |
| Respond | We pull a malicious email from every inbox at once and lock any account it hit. | Instant |
| Harden | SPF, DKIM and DMARC set right, safer payment checks and drills on real lures. | Retested |

### Principle
- Quote: If it sounds like your boss and asks for money, we check twice.

### Related
- Identity -> /coverage/identity/
- AI agents -> /coverage/ai-agents/

---

## Domain: Applications

- URL: /coverage/applications/
- Meta title: Application and API security | YellowForce
- Meta description: We attack your apps and APIs first with AI and human red teamers, fix what we find, retest it and watch them 24/7.
- Nav tagline: Attacked by us first

### Hero
- Label: Coverage 06 · Application and API security · 24/7
- H1: Apps and APIs.
- Intro: Your apps and APIs face the internet all day. We attack them first, fix what we find and watch them 24/7.

### The threat.
- Text: Every public app and API is a door attackers can test as often as they like. Broken access controls let one user read another user's data. Injection flaws, exposed admin panels, forgotten test endpoints and vulnerable open-source packages do the rest. AI agents now crawl your app, read your JavaScript, map every endpoint and try thousands of variations without getting tired. They chain small bugs into a real breach, faster than a yearly test can keep up with. Supply chain attacks hide in the packages your code trusts.

### What we do.
| Label | Text | Tile |
|---|---|---|
| Watch | Every app, API and dependency mapped and monitored 24/7. | 24/7 |
| Detect | AI catches abuse, scraping and exploit attempts as they hit. | Real time |
| Respond | We block attacks at the edge and ship emergency fixes right away. | Instant |
| Harden | Continuous AI and human testing, fixes in your code and a retest for every finding. | Retested |

### Principle
- Quote: We attack your apps before anyone else does.

### Related
- Cloud -> /coverage/cloud/
- AI agents -> /coverage/ai-agents/

---

## Domain: Data

- URL: /coverage/data/
- Meta title: Data protection and ransomware defense | YellowForce
- Meta description: Ransomware, extortion and quiet data leaks. We track your sensitive data 24/7, stop mass encryption as it starts and protect your backups.
- Nav tagline: Yours stays yours

### Hero
- Label: Coverage 07 · Data protection · 24/7
- H1: Data.
- Intro: Data is what attackers want. We know where yours lives, who touches it and how to get it back.

### The threat.
- Text: Ransomware crews now steal first and encrypt second, then threaten to publish. Some skip encryption entirely and go straight to extortion. They hunt for your backups and delete them before you notice. Data also leaks the quiet way: files shared with anyone who has the link, exports to personal accounts, sensitive documents pasted into AI tools. AI helps attackers sort stolen data fast to find what hurts most, then write ransom notes and leak threats aimed at your customers and regulators.

### What we do.
| Label | Text | Tile |
|---|---|---|
| Watch | Sensitive data mapped, with every access and transfer tracked 24/7. | 24/7 |
| Detect | AI spots mass encryption, bulk downloads and unusual exports as they start. | Real time |
| Respond | We stop the process, cut off the attacker and protect your backups in real time. | Instant |
| Harden | Isolated, tested backups, tested restores and tighter sharing rules. | Retested |

### Principle
- Quote: If they can't take it or lock it, they have nothing.

### Related
- Governance -> /coverage/governance/
- Email -> /coverage/email/

---

## Domain: AI agents

- URL: /coverage/ai-agents/
- Meta title: AI and agent security: swarms, hijacked agents | YellowForce
- Meta description: We stop AI swarms and protect your own AI agents from prompt injection, poisoned tools and abuse. AI against AI, 24/7.
- Nav tagline: Swarms meet their match

### Hero
- Label: Coverage 08 · AI and agent security · 24/7
- H1: AI agents.
- Intro: AI is now the attacker and the target. We stop AI swarms and keep your own AI agents from being turned against you.

### The threat.
- Text: Two problems at once. Outside, attackers run swarms: many AI agents working together, each scanning, phishing or exploiting in parallel and sharing what they learn. They move at machine speed and never sleep. Inside, your own AI is a new attack surface. Prompt injection hides instructions in an email, a web page or a document, so your assistant leaks data or takes actions it shouldn't. Poisoned tools and plugins, agents with too much power, leaked model keys and AI apps your staff started using on their own all open new doors.

### What we do.
| Label | Text | Tile |
|---|---|---|
| Watch | Every AI tool, agent and model key in your company, found and monitored 24/7. | 24/7 |
| Detect | Our AI picks out swarm patterns and hijacked agent behavior as they start. | Real time |
| Respond | We cut off swarm traffic, revoke agent access and stop rogue actions in real time. | Instant |
| Harden | Prompt injection testing, tight agent permissions and guardrails on every tool. | Retested |

### Principle
- Quote: Fight AI with AI. Then keep yours on a leash.

### Related
- Apps and APIs -> /coverage/applications/
- Governance -> /coverage/governance/

---

## Domain: OT and IoT

- URL: /coverage/ot-iot/
- Meta title: OT and IoT security | YellowForce
- Meta description: Cameras, sensors, badge readers and control systems. We find every connected device, watch it 24/7 and keep attackers off it.
- Nav tagline: If it's plugged in

### Hero
- Label: Coverage 09 · OT and IoT security · 24/7
- H1: OT and IoT.
- Intro: Cameras, sensors, badge readers and control systems run your physical world. We watch them 24/7 and keep attackers off them.

### The threat.
- Text: Connected devices are often old, rarely patched and shipped with default passwords. Many sit on the same network as everyone's laptops. Attackers use them as a quiet foothold, pull them into botnets or pivot through them to reach the control systems that run production lines, buildings and utilities. An attack here can stop a plant, open a door or damage equipment, on top of leaking data. AI helps attackers find exposed devices across the internet and work out unfamiliar control protocols faster than before.

### What we do.
| Label | Text | Tile |
|---|---|---|
| Watch | Every connected device found, identified and monitored around the clock. | 24/7 |
| Detect | AI learns what normal looks like for each device and flags anything off. | Real time |
| Respond | We isolate compromised devices and protect the systems that keep you running. | Instant |
| Harden | Default passwords gone, firmware updated and devices segmented from the rest. | Retested |

### Principle
- Quote: If it's plugged in, it's covered.

### Related
- Network -> /coverage/network/
- Endpoint -> /coverage/endpoint/

---

## Domain: Governance

- URL: /coverage/governance/
- Meta title: Governance, risk and compliance | YellowForce
- Meta description: Policies, risk, vendors, audits and AI use rules, written and kept current as you change, so security holds and customers get proof.
- Nav tagline: Rules that hold

### Hero
- Label: Coverage 10 · Governance, risk and compliance · 24/7
- H1: Governance.
- Intro: Security only holds if the rules behind it hold. We write, run and update yours as your company changes.

### The threat.
- Text: The risk here is quiet. Policies nobody follows, access nobody ever reviewed, vendors with more access than anyone remembers, an audit that turns up gaps right before a big deal closes. New AI rules and security questionnaires keep coming, and customers expect proof. AI also adds risks of its own: which tools your staff use, what data goes into them and who is accountable when an agent acts. Without someone in charge, all of this drifts until it shows up as a breach, a fine or a lost customer.

### What we do.
| Label | Text | Tile |
|---|---|---|
| Watch | Controls, vendors and access reviewed continuously, not once a year. | Continuous |
| Detect | AI flags drift from your policies and frameworks as it happens. | Real time |
| Respond | Audit requests and customer questionnaires answered fast, with evidence. | Fast |
| Harden | Policies, risk register and AI use rules written and kept current. | Always current |

### Principle
- Quote: Compliance is the floor. Security is the job.

### Related
- Data -> /coverage/data/
- OT and IoT -> /coverage/ot-iot/

---

## Page: About

- URL: /about/
- Meta title: About | YellowForce
- Meta description: YellowForce goes inside your company and runs your cybersecurity from A to Z, with AI agents and cyber experts on watch 24/7. San Francisco.
- Nav tagline: Who's on watch?

### 01 Hero
- Label: ( The company )
- H1: We go in. / We stay on.

### 02 Our approach. (+ 3 vertical images)
- H2: Our approach.
- Text: We don't sell you a tool and leave. We go inside your company, put our AI agents and cyber experts in your environment and connect to every system you already run. We work on top of your workflows, in your chat and your tickets, and run your security from A to Z, 24/7. Attackers now fight with AI. So do we, with people in charge of it.

### 03 Values (sticky stack, 4 rows)
- ( Value 01 ) Go in, not around.
  - Text: We don't watch from the outside or send you a report and disappear. We work inside your environment, learn how your company really runs and defend it from there. You get agents and experts who know your systems as well as your own team does.
- ( Value 02 ) Match their speed.
  - Text: Attackers use AI to move at machine speed, so waiting for a person to read every alert is already too slow. Our agents triage, hunt and contain instantly. Our experts make the calls that need judgment. Agents bring the speed, experts bring the judgment, both on all the time.
- ( Value 03 ) Cover every door.
  - Text: Breaches happen in the gaps between tools and vendors. So we take every domain, from your network to your AI agents, and own the result. No finger pointing, no handoffs, no alert that belongs to nobody. If it can be attacked, it's ours to defend.
- ( Value 04 ) Never off duty.
  - Text: Attacks don't keep office hours. Neither do we. We're on 24/7, every day of the year, and when you write to us, a person answers. Nights, weekends, holidays: same team, same speed, same attention to your company.

### 04 Company snapshot. (replaces numbers)
- H2: Company snapshot.
- Button: Talk to us -> /contact/
- Line: Fully managed cybersecurity / San Francisco, CA
- Giant figure: 24/7
- Unit (small, under or next to the figure): Always on
- Cells (label / value):
  - Scope / A to Z
  - Coverage / 10 domains
  - Team / AI + experts
  - Based in / San Francisco

### 05 Careers (replaces the awards table)
- H2: Join the fight.
- Meta L: ( Careers )
- Meta R: San Francisco, CA
- Line: We're hiring people who want to fight AI with AI.
- Sub-line: Tell us what you've broken, built or defended. One email is enough.
- Button: Copy email [copy-email]
- Table head: Discipline / What you'd do / No.
- Rows:
  - Offensive security / Red team with AI, find every way in / 01
  - Detection and response / Hunt, contain and run incidents / 02
  - AI security / Swarms, agents, prompt injection, model abuse / 03
  - Security engineering / Cloud, identity and the automation behind it / 04

### 06 CTA band + footer
- Global.

---

## Page: Insights (index)

- URL: /insights/
- Meta title: Insights | Notes on AI threats and defense | YellowForce
- Meta description: Notes on AI swarms, fighting AI with AI and why one team should cover every cyber domain. Plain words, no hype.
- Nav tagline: Know your enemy

### 01 Header
- Label: ( Insights )
- H1: Notes from / the front.

### 02 Featured (2 big cards)
- ai-swarms
- fight-ai-with-ai

### 03 Index
- H2: All notes.
- Meta L: ( 03 notes )
- Meta R: Threats, approach, coverage
- Rows (all 3, newest first): category / title / date / arrow
- Filter pills (only if the layout needs them): All notes · Threats · Approach · Coverage

### 04 CTA band + footer
- Global.

### Article chrome (all 3 articles)
- Back link: All notes -> /insights/
- Author rail: label "Written by" / name "YellowForce" / role "Research" (logo mark instead of a portrait)
- More section H2: Keep reading.
- More section: the other 2 articles as cards
- Nav tagline (all articles): Worth five minutes

---

## Article: ai-swarms

- URL: /insights/ai-swarms/
- Meta title: What an AI swarm attack looks like | YellowForce
- Meta description: Many AI agents, one target, all at once. How AI swarm attacks work, why they break slow defenses and how we stop them.
- Category: Threats
- Date: Oct 25, 2026
- Read time: 4 min read
- Card summary: Many agents, one target, all at once. Here is how a swarm works and how we stop it.
- H1: What an AI swarm attack looks like.

### Body

An AI swarm is a group of AI agents attacking one target at the same time. Each agent has a job. They share what they find, and a coordinating agent decides what to try next. Think of it less like one burglar picking a lock and more like a crew checking every door and window of a building at once, calling out the moment one opens.

#### How a swarm works.

None of the parts are exotic. Capable models, agent frameworks, tool use and cheap compute are all available to anyone. Put together, they let one operator run work that used to need a whole team. A typical swarm splits the job like this:

- **Recon.** Agents collect everything public about you: domains, cloud services, job posts that name your tools, staff profiles, code in public repos.
- **Access.** Other agents try the doors in parallel: password spraying, phishing written for each employee, every exposed sign-in page and API.
- **Exploitation.** When one door opens, the finding is shared. Exploit agents chain it with what recon found to go deeper.
- **Persistence and theft.** Agents set up hidden access, look for valuable data and move it out, changing tactics when something gets blocked.

Public reports from AI companies already describe attackers using AI agents to run large parts of an intrusion with little human help. As the cost of each attempt drops toward zero, smaller companies become worth attacking too.

#### Why it breaks the old model.

Most defenses were built for human attackers. A person runs a scan, reads the results, picks a target and keeps going for as long as they can stay awake. Detection rules are tuned to that rhythm, and so are the teams reading the alerts.

A swarm doesn't look like that. It creates many small, quiet events across many systems at the same time: a few failed sign-ins on one account, an odd API call, a phishing email to finance, a scan from a cloud server. On its own, each event looks harmless. Spread across separate tools and read by an analyst working through a queue, they never get connected.

Swarms also adapt. Block one address and traffic comes from another. Catch one technique and the coordinator switches to the next. They don't get tired, and they don't stop at 6 p.m.

> A swarm wins by being everywhere at once. Your defense has to be everywhere at once too.

#### How we stop it.

We fight it the only way that works at that speed: with our own AI, and with experts in charge of it.

- **One picture.** Signals from every domain land in one place: identity, email, devices, network, cloud, apps. Scattered events become one attack you can see.
- **Machine-speed triage.** Our AI agents read every signal the moment it arrives. There is no queue for a swarm to hide in.
- **Real-time response.** We lock accounts, block sources, isolate devices, pull emails and revoke keys across all your tools at once.
- **Experts on the call.** Our people make the decisions that need judgment and hunt for what is new.
- **Attack first.** We run swarm-style attacks against you ourselves, so we find the open doors before anyone else does.

##### What you can do today.

Turn on phishing-resistant multi-factor for admins and finance. List every service you expose to the internet. Remove the accounts and keys nobody uses. And decide now who you call when it starts. If the answer is nobody, write to us.

---

## Article: fight-ai-with-ai

- URL: /insights/fight-ai-with-ai/
- Meta title: Why you have to fight AI with AI | YellowForce
- Meta description: Attackers adopted AI fast. Why people alone can't keep up, why AI alone isn't enough, and how our agents and experts split the work.
- Category: Approach
- Date: Oct 25, 2026
- Read time: 4 min read
- Card summary: Attackers already use AI. Here is why defense needs AI too, and why it still needs people in charge.
- H1: Why you have to fight AI with AI.

### Body

Security is now a speed contest. Attackers adopted AI the way they adopt anything that works: quietly and fast. A phishing email that took an afternoon to write now takes seconds. A scan that needed a skilled operator now runs on its own. If your defense still depends on a person reading alerts one at a time, you're bringing a queue to a race.

#### What changed on the other side.

- **Scale.** One attacker with agents can run hundreds of tailored campaigns at once.
- **Quality.** Lures are well written, in any language, and personal. Voices and faces can be cloned.
- **Speed.** New flaws get tested against exposed systems soon after they go public.
- **Adaptation.** When something gets blocked, agents retry with a different approach.
- **Cost.** Each attempt costs almost nothing, so attackers go after more targets, including smaller ones.

#### Why people alone can't keep up.

This isn't about skill. Good analysts are very good at what they do. It's about volume and time. Every new tool, cloud account and AI assistant adds signals. Every attacker using agents adds noise. A person can only look at so many alerts in an hour, and nobody is sharp at 4 a.m. on their fifth night shift in a row. When attacks move in minutes and queues move in hours, the attacker is done before anyone looks.

The result is familiar to anyone who has worked in security: the important alert was in there the whole time, buried under everything else, read too late or not at all.

#### Why AI alone isn't the answer either.

The opposite mistake is just as risky. AI without judgment makes confident mistakes. It can be fooled, including by prompt injection planted in the very data it reads. It doesn't know your business: that the huge transfer is payroll, or that the admin sign-in from abroad is your CTO at a conference. An automated system that blocks the wrong thing at the wrong moment can hurt you as much as an attacker. And when something big happens, someone has to own the decision.

> Agents bring the speed. Experts bring the judgment. You need both, all the time.

#### How we split the work.

Fighting AI with AI doesn't mean handing your security to a model. It means putting each job in the right hands.

- **Our AI agents** watch every signal across every domain, triage it instantly, connect related events, contain clear threats in real time and keep attacking you so we find the gaps first.
- **Our experts** make the high-impact calls, hunt for what's new, tune the agents to how your company really works, run incidents and keep your leadership informed.
- **Together** they learn from every attack, so the next one gets caught earlier.

That's what we mean by fight AI with AI. You don't buy a tool and spend your nights tuning it. You get a team of agents and people that runs your security from A to Z, 24/7.

---

## Article: one-team-every-domain

- URL: /insights/one-team-every-domain/
- Meta title: One team for every cyber domain | YellowForce
- Meta description: One attack can cross email, identity, cloud, data and devices in a morning. Why split vendors leave gaps, and what one team changes.
- Category: Coverage
- Date: Oct 25, 2026
- Read time: 4 min read
- Card summary: Attacks cross domains in one go. Defense that stops at the edge of one tool leaves the gaps attackers need.
- H1: One team for every domain.

### Body

Most companies don't have a tool problem. They have an ownership problem. They run an endpoint agent, an email filter, a firewall, a cloud scanner, maybe a monitoring contract, a yearly penetration test and a compliance consultant. Each one does its job. Nobody owns the whole thing.

#### Attacks don't follow your org chart.

Here is a simple, made-up example of how one attack can move:

1. A phishing email lands in a finance inbox. (Email)
2. The fake sign-in page behind it steals a session token. (Identity)
3. The attacker uses that session to open your cloud console. (Cloud)
4. They create a new access key and copy files out of storage. (Data)
5. They drop ransomware on a server to cover their tracks. (Endpoint)

Five domains. Possibly five tools and three vendors. Each one sees a piece. The email filter saw a message that looked fine. The identity provider saw a valid session. The cloud saw an admin doing admin things. Only when you put the pieces side by side does it look like an attack, and by then the data is gone.

The gaps between tools and vendors are where attackers live. AI makes this worse, because agents move across those gaps faster than any handoff between teams. A ticket that waits for the right vendor to pick it up is time the attacker gets for free.

> An attack can cross five domains in one morning. Your defense can't stop at the edge of one tool.

#### What one team changes.

- **One picture.** Every signal, from every domain, lands with the same team and the same AI agents.
- **One owner.** When something happens, nobody asks whose problem it is. It's ours.
- **One response.** We act across every system at once: kill the session, revoke the key, isolate the server, pull the email from every inbox.
- **One loop.** What we learn attacking you shapes what we watch and what we harden.

#### The ten domains.

When we say every domain, we mean it: network, endpoints and devices, cloud, identity and access, email, applications and APIs, data, AI and agents, OT and IoT, and governance, risk and compliance. Each has its own attacks and its own specialists. But a phishing email is an email problem only until it becomes an identity problem, then a cloud problem, then a data problem. Attackers treat all ten as one surface. So do we.

#### Why fully managed.

Doing this yourself means hiring specialists across ten areas and staffing them around the clock, then getting them to work as one. Most companies can't, and they shouldn't have to. It also means one relationship instead of a pile of contracts, and one place to go when a customer, an insurer or your board asks how you're protected. You keep the tools you have. We go in, connect them and run the whole thing for you, 24/7, from A to Z.

---

## Page: Contact

- URL: /contact/
- Meta title: Contact | YellowForce, 24/7
- Meta description: Email info@yellow-force.com. We answer 24/7. Under attack? Write now with URGENT in the subject and we'll get on it.
- Nav tagline: Someone's always up

### 01 Hero
- Label: ( Contact )
- H1: Tell us / what you run.
- Direct strip (2 cells):
  - Cell 1 label: Email / value: info@yellow-force.com [copy-email]
  - Cell 2 label: Hours / value: 24/7, every day

### 02 Write to us. (image + big email, replaces the form)
- H2: Write to us.
- Text: One email is all it takes. Tell us what you run and what worries you most.
- Big email button: info@yellow-force.com [copy-email]
- Hint under the button: Click to copy
- What happens next (label): ( What happens next )
- Bullets:
  1. We reply fast, day or night. A real expert, not a bot.
  2. We get on a call and look at what you run, the same day if you want.
  3. We go in, connect and start defending. Coverage from day one.

### 03 Under attack?
- Label: ( Urgent )
- H2: Under attack?
- Text: Write to us now. Put URGENT in the subject. We answer 24/7, nights and weekends included.
- Button: Copy email [copy-email, Under attack toast]
- While you wait (label): ( While you wait )
- Steps:
  - Don't wipe or reinstall anything. Evidence matters.
  - Disconnect affected machines from the network, but leave them powered on.
  - Change exposed passwords from a clean device.
  - Write down what you saw, when, and on which systems.

### 04 Footer
- Global footer. No CTA band.

---

## Page: Privacy

- URL: /privacy/
- Meta title: Privacy | YellowForce
- Meta description: How yellow-force.com handles your data: no cookies, no analytics, no forms. Just the emails you send us and basic hosting logs.
- Nav tagline: We keep almost nothing

### Hero
- Label: ( Legal )
- H1: Privacy.
- Effective date line: Effective October 25, 2026

### Body

#### The short version.

This site has no cookies, no analytics, no ads, no forms and no accounts. Fonts and scripts load from our own site, so your browser doesn't contact anyone else when you visit. We only get personal information when you email us.

#### Who we are.

This policy covers yellow-force.com, run by YellowForce, San Francisco, California. Questions about it go to info@yellow-force.com.

#### What we collect.

- **Emails you send us.** Your email address, your name if you include it, your message and anything you attach.
- **Hosting logs.** This site is hosted on GitHub Pages. GitHub, which runs that service, may log technical data such as your IP address for security purposes. GitHub handles that data under its own privacy statement.
- **Copy buttons.** The buttons that copy our email address write to your clipboard. They don't read your clipboard and don't send anything anywhere.

We don't collect anything else from this site.

#### How we use it.

We use what you send us to reply, to provide services you ask for, to keep normal business records, to protect our systems and to meet legal obligations. We don't sell or share your personal information, and we don't use it for advertising.

#### Who else sees it.

Our email runs on Google Workspace and this site runs on GitHub Pages, so those providers process data on our behalf. We may also disclose information if the law requires it, or to a successor if YellowForce is ever merged or acquired. Nobody else.

#### How long we keep it.

We keep emails as long as we need them for the conversation and our business records, then delete them. Ask us and we'll delete yours sooner, unless the law requires us to keep it.

#### Your rights.

You can ask us what we hold about you, and ask us to correct it, delete it or stop using it. Email info@yellow-force.com. Depending on where you live, for example California, the EU or the UK, the law gives you these rights. We honor them for everyone, and we won't treat you differently for using them.

#### Do Not Track.

We don't track visitors across sites, so Do Not Track signals don't change anything here.

#### Children.

This site isn't meant for children under 13, and we don't knowingly collect their information.

#### Where your data goes.

We're based in the United States, and the information you send us is processed in the United States.

#### Changes.

If we change this policy, we'll update it here and change the effective date at the top.

---

## Page: Security

- URL: /security/
- Meta title: Security and responsible disclosure | YellowForce
- Meta description: Found a vulnerability in yellow-force.com? Here's how to report it to us, what's in scope and the safe harbor we give researchers.
- Nav tagline: Ethical hackers welcome

### Hero
- Label: ( Responsible disclosure )
- H1: Found a / way in?
- Intro: We fight attackers for a living, so we take reports about our own security seriously. If you found a vulnerability in yellow-force.com, thank you. Here's how to tell us.

### Body

#### In scope.

- The yellow-force.com website and its pages.

#### Out of scope.

- Services run by others, such as our hosting and email providers. Please report those to them directly.
- Systems of the companies we defend. Never test them under this policy.
- Denial of service, spam, social engineering of our people and physical attacks.
- Automated scanner output without a working proof of impact.
- Missing security headers, email settings (SPF, DKIM, DMARC) or best-practice notes without a demonstrated impact.

#### How to report.

Email info@yellow-force.com with "Security report" in the subject. Please include:

- What you found and where.
- Steps to reproduce it.
- What an attacker could do with it.
- Your name or handle, if you'd like credit.

#### What we ask.

- Act in good faith and stay inside this policy.
- Stop as soon as you've confirmed the issue, and tell us.
- Don't access, change or delete data that isn't yours.
- Don't degrade the site for anyone else, and keep automated testing light.
- Keep the details private until we've fixed it, and give us reasonable time to do so.

#### What we promise.

- We acknowledge reports quickly and keep you updated until it's fixed.
- If you follow this policy, we consider your research authorized. We won't take legal action against you or ask anyone else to.
- If someone else takes action against you for research done under this policy, we'll make clear that you acted with our permission.
- We'll credit you publicly once it's fixed, if you want.

#### Rewards.

We don't pay bounties. We do say thank you, and we mean it.

#### Machine-readable.

Our contact details are also published at /.well-known/security.txt.

---

## Page: 404

- URL: /404.html
- Meta title: Page not found | YellowForce
- Meta description: This page doesn't exist. Everything we defend is still where it should be.
- Nav tagline: Wrong door

### Hero (inset dark card)
- Label: ( Error / 404 )
- H1: Nothing here / to defend.
- Text: This page doesn't exist, moved, or never did. Everything we protect is still exactly where it should be.
- Button 1 (light): Back to home -> /
- Button 2 (ghost): See coverage -> /coverage/
