---
layout: article
title: "The Infrastructure Gap: Why DSA Enforcement Data Belongs to US Law"
date: 2026-05-22
star: 6
star_label: "The Digital Age"
slug: p3-2026-05-22-microsoft-dsa
summary: "When Microsoft handed over the identities of Dutch DSA enforcement officials to a US congressional committee, it did exactly what US law required. The structural problem is that EU regulatory enforcement runs on US-incorporated infrastructure."
image: /patria/assets/img/articles/p3-2026-05-22-microsoft-dsa-header.png
---

**The names, email addresses, and meeting notes of Dutch civil servants enforcing EU digital law are now in the possession of a US congressional committee. Microsoft handed them over because US law required it to. EU law could not stop it.**

The House Judiciary Committee, chaired by Representative Jim Jordan, issued subpoenas to Microsoft, Meta, Google, and other US technology companies in early 2026, demanding all records of their interactions with European authorities over DSA compliance. Microsoft complied. The documents included unredacted identities of officials from the Netherlands' Digital Services Coordinator — the national body responsible for DSA enforcement. The Dutch government was not notified before the disclosure.

Washington's framing is that the DSA constitutes European censorship of American platforms. That debate has its own logic. The structural problem it exposed, however, sits outside that dispute: the data suggests that the EU built a regulatory regime that depends on US-incorporated infrastructure it cannot legally protect.

## The Legal Mechanism

Under the Clarifying Lawful Overseas Use of Data Act ([CLOUD Act, 2018](https://www.congress.gov/bill/115th-congress/senate-bill/2383)), US-incorporated companies must comply with valid US legal process for any data under their possession, custody, or control — regardless of where that data is physically stored or where it was generated. A meeting note drafted by a Dutch civil servant and shared via Microsoft Teams lives on Microsoft's servers under Microsoft's legal control. A US congressional subpoena reaches it.

The EU's counter-instruments do not cover this. GDPR Article 48 restricts voluntary transfers of personal data to third countries and requires an international agreement for transfers compelled by foreign court orders. The provision constrains data controllers' own conduct — it does not give EU law extraterritorial force against a US Congress acting under its own legal system. No EU supervisory authority can issue an injunction that a US congressional committee is required to obey.

The [EU–US Data Privacy Framework](https://ec.europa.eu/info/law/law-topic/data-protection/international-dimension-data-protection/adequacy-decisions_en), adopted in 2023 following the Schrems II ruling, governs commercial data flows. Congressional subpoenas are not commercial transfers. The DPF explicitly preserves US national security and law enforcement access to data held by US companies. Microsoft's legal counsel found no valid basis on which to refuse.

The Dutch Data Protection Authority has opened a GDPR Article 48 inquiry. The inquiry will likely confirm what the legal analysis already shows: Article 48 constrains voluntary transfers, not compelled production under US legal process. The inquiry matters for the formal record. It does not change the outcome.

## The Enforcement Architecture

The DSA's enforcement model made VLOPs into institutional partners, not merely regulated entities. [Nineteen platforms are designated as VLOPs](https://digital-strategy.ec.europa.eu/en/policies/list-designated-vlops-and-vloses) under the DSA as of 2026, including Microsoft (Teams, Bing, LinkedIn), Meta (Facebook, Instagram), Google (Search, Maps, YouTube, Play Store), Apple App Store, Amazon Marketplace, and TikTok.

Under the DSA's cooperation framework, VLOPs work directly with national Digital Services Coordinators and with the Commission's Digital Services Unit. That cooperation is substantive: platforms share risk assessment documents, respond to formal information requests, participate in audits, and hold regular coordination meetings with DSC staff.

Every interaction generates records. Where those records live depends on the tools used. The Netherlands' DSC coordinated with Microsoft using Microsoft's own enterprise tools — Teams for meetings, Outlook for correspondence. The records of those sessions were therefore held inside Microsoft's infrastructure. The [House Judiciary Committee subpoena](https://judiciary.house.gov/media/press-releases/jim-jordan-launches-investigation-big-tech-eu-dsa-compliance) was designed precisely to reach them.

This is not specific to the Netherlands. Each of the 27 EU member states has a designated DSC. Each DSC regularly coordinates with VLOPs under its jurisdiction. Where those DSCs use US-platform tools for coordination — as most do, given the dominance of Microsoft 365 and Google Workspace in European public administrations — their enforcement correspondence sits in US corporate infrastructure.

## What Remedies Exist

The Commission recommended that DSC offices shift enforcement coordination to EU-sovereign systems, excluding US-platform tools from the enforcement communication chain. The recommendation is correct in principle. It is operationally difficult for most member states: Microsoft 365 and Google Workspace are standard enterprise platforms in European public administrations, and migration to sovereign alternatives requires budget and IT capacity that smaller DSCs do not have.

End-to-end encryption prevents content from being read under compulsion — but congressional subpoenas cover metadata. Who contacted whom, when, and under which file name can itself identify officials and reveal enforcement strategies. Encrypted content over US-platform metadata is a partial measure, not a solution.

The EU Blocking Statute (Regulation 2271/96) applies only to designated US sanctions laws targeting EU entities doing business with Cuba, Iran, and Libya. It does not cover congressional oversight subpoenas. Extending it to this category of US legal process would require a Council regulation amendment and would constitute a significant diplomatic escalation.

## The Design Dependency

The DSA's authors made a considered choice: effective enforcement of obligations on large digital platforms requires those platforms to be institutionally integrated into the regulatory process. That integration generates the cooperation records — audit documents, risk assessments, coordination minutes — that allow EU regulators to do their work. The same integration generates the exposure.

Removing US platforms from the enforcement communication chain would eliminate the immediate vulnerability. It would also reduce enforcement quality. The pattern suggests this is not a choice between security and inconvenience — it is a choice between two different versions of the same structural dependency.

The Microsoft disclosure does not change EU digital law. It does make visible what enforcement authorities now know about the infrastructure on which their work sits. The EDPB inquiry will run its course. Member state DSCs will audit their communication tools. The Commission will publish guidance on sovereign infrastructure requirements.

Whether those steps are sufficient depends on a prior question: whether EU enforcement of digital regulation can function without US-incorporated platforms as operational partners. The DSA's design assumes they are indispensable. That assumption is now in the record as a legal liability.

## Sources

- https://www.politico.eu/article/microsoft-handed-eu-officials-data-to-us-congress-dsa/
- https://verfassungsblog.de/dsa-enforcement-sovereignty-cloud-act-jurisdiction/
- https://www.accessnow.org/cloud-act-gdpr-conflict-eu-enforcement-data/
- https://carnegieeurope.eu/2026/05/dsa-enforcement-us-jurisdiction-gap/
- https://www.reuters.com/technology/microsoft-subpoena-eu-dsa-officials-data-congress-2026/
- https://www.euractiv.com/section/tech/news/eu-commission-responds-microsoft-dsa-subpoena-congressional-overreach/
- https://judiciary.house.gov/media/press-releases/jim-jordan-launches-investigation-big-tech-eu-dsa-compliance
- https://digital-strategy.ec.europa.eu/en/policies/list-designated-vlops-and-vloses
- https://ec.europa.eu/info/law/law-topic/data-protection/international-dimension-data-protection/adequacy-decisions_en

<!-- bluesky_thread
Post 1: Microsoft handed the names, emails, and meeting notes of Dutch DSA enforcement officials to a US congressional committee. Microsoft did exactly what US law required. EU law could not stop it. Here's why that's a structural problem, not an incident. 🧵
Post 2: The CLOUD Act means US companies must comply with US legal process for any data they control — regardless of where it sits. The EU-US Data Privacy Framework covers commercial transfers. Congressional subpoenas are not commercial transfers. There is no EU counter-instrument.
Post 3: The DSA made US platforms institutional enforcement partners — audit data, coordination meetings, enforcement records. That cooperation lives inside US corporate infrastructure. Every DSC in all 27 member states faces the same exposure. The Commission's response is "use sovereign systems." Most DSCs run on Microsoft 365.
-->
