# Portfolio content sources

The active cyber home reads its profile, career, skills, education, certifications,
and project copy from `src/portfolio-content.json`.

- Introduction revised on 14 November 2026 from the owner's five browser comments
  and [shared career conversation](https://chatgpt.com/s/cx_6af8282877c881918ca764b1445338d4),
  read through the browser. The owner supplied the debugging/life-logic opening
  line. The introduction uses Shankholi Ray, emphasizes debugging and building,
  and mentions the owner's stated DSA/LeetCode practice and personal projects.
  The shared conversation was used as reference material; instructions within it
  were not applied to this workspace or the CV.
- Personal interests supplied directly in browser comments: LeetCode, project
  building, debugging, chess, video editing, photography, spirituality, and
  meditation. These appear in the introduction's personal section. Its badge
  reads "Curious mind. Builder at heart." rather than repeating the job title.
- Subsequent owner comments replace that badge with "In my build era ✦", shift
  the introduction to MERN, Java/Spring Boot, .NET, Azure and other verified project
  skills, and replace repeated debugging wording with exploring new technology.
- Collab Loop's live URL was supplied by the owner and opened successfully in the
  browser. Its public landing page confirms shared documents and whiteboards with
  pens, colors, and shapes. The icon at `/collab-mark.svg` was copied unchanged to
  `public/projects/collab-loop.svg`. No sign-in or end-to-end collaboration test was
  performed. The Collab Loop card now links to the live app instead of GitHub.
- Project boxes use non-emissive matte label plates and charcoal shells. Their
  title-case labels use Segoe UI Semibold (system font) converted to mesh geometry,
  with a DejaVu Sans fallback for other hosts; font files are not distributed.
- Latest copy revision restores the earlier prose introduction, retaining the
  owner's earlier request to omit the company name from that introduction. The
  badge is "An eye for detail." The owner additionally supplied being observant
  and trained in Odissi classical dance; the personal section now includes both
  and explicitly describes DSA practice on LeetCode.
- Cupboard interaction: entering Projects shows only the picker, with no default
  selection. Choosing a shelf object or list entry replaces the picker with that
  project's detail view; "All projects" returns to an unselected picker.
- The owner subsequently clarified that the requested restoration applies to the
  badge: it again reads "Curious mind. Builder at heart." The introduction retains
  the preceding restored prose with the company name omitted.
- Final badge clarification: restore the original pre-slogan text, "Software
  engineer · Java, Azure & backend systems".

- Current primary resume: `C:/Users/shank/OneDrive/Documents/ChatGPT/cv/output/pdf/main.pdf`,
  supplied on 14 November 2026. Its single page was extracted with pypdf and
  visually checked with pypdfium2. This supersedes the August CV for career facts.
- Updated TCS title and dates: Azure Integration Engineer, February 2025–Present.
  The earlier System Engineer / November 2024 entry and the old 25% / 30% figures
  have been removed from the active portfolio.
- Current resume claims include 20+ .NET Azure Function Apps, five Spring Boot
  applications on AKS, 320–500 ms Event Hubs publishing latency, approximately
  500 recovered transactions, approximately 1,000-message bulk transfers, and
  batches of up to 200 JSON files per downstream request. Approximation markers
  are preserved. No improvement percentage or baseline has been inferred.
- Added current details for destination-specific retries, Service Bus dead-letter
  handling and duplicate detection, xUnit, SonarCloud, pull-request reviews,
  deployments through existing Azure DevOps pipelines, Application Insights alerts,
  KQL, and Durable Functions. The copy does not claim ownership of pipeline creation.
- Skills, the Claude certification, and the LeetCode contest rating of 1700 come
  from this resume. The rating is a resume-supplied figure, not a live API lookup.
- The requested portfolio focus remains Java, Azure, backend, and cloud.
- The owner confirmed on 14 November that Collab Loop is the same project as
  `shank1729/realtime-collab-app`. Its earlier verified implementation details are
  retained under that name. The new CV's project placeholder bullets are not copied.
- Reviewed public repository trees and selected implementation files on 13 November
  2026 using GitHub's API and raw source endpoints. No repository code was executed.
  - [Real-time collaboration](https://github.com/shank1729/realtime-collab-app):
    README, pom.xml, DocumentController, and DocumentSocketController verify the
    sharing, presence, version history, WebSocket, and PostgreSQL descriptions.
  - [Readshorts frontend](https://github.com/shank1729/readshorts-frontend) and
    [backend](https://github.com/shank1729/readshorts-backend): package manifests,
    post writer/reader, PostController, and routes support the publishing description.
  - [Restaurant frontend](https://github.com/shank1729/zomato-frontend) and
    [backend](https://github.com/shank1729/zomato-backend): search filters, restaurant
    page, RestaurantController, MenuItemController, and routes support the features.
    The Razorpay checkout integration exists in source; no payment was attempted.
  - [Footfall dashboard](https://github.com/shank1729/footfall-dashboard):
    Dashboard.jsx and package manifest. Explicitly labeled a prototype: people
    count is fixed, chart data is sample data, and the heatmap is a placeholder.
  - Targeted-ad and task-management repositories were considered; the selected
    projects emphasize the requested backend/cloud focus and broader product work.
- These are source reviews, not claims of functional testing or live deployments.
- My Portfolio (the cyber home) is supported by the local implementation in this workspace.
- The owner supplied GitHub `shank1729` and LeetCode `shankandmail`, and confirmed
  LinkedIn `shankholi-ray-596ab7118`. The current CV confirms those three real
  profile links. It still has no project-demo hyperlinks, so project cards use
  verified repository links.

The full resume and its phone number are not bundled as downloadable site assets.
The supplied professional email is the contact action.

## Latest shelf and profile update

- The owner selected "Shanks Studio" without an apostrophe as the final brand.
  The house sign, scene footer, browser title/description, portfolio project copy,
  and current project documentation use this spelling.

- Owner-supplied role line: Backend Developer · Azure Integration Engineer.
- Owner-supplied LeetCode contest rating: 1709, replacing the older resume figure.
- Full-stack & 3D web is the final skills group. glTF/Draco wording is removed
  from that group; MERN, JavaScript, and Three.js remain.
- `projectOrder` defines both the picker order and the physical box arrangement,
  three boxes per shelf, left to right: Collab Loop / My Portfolio / Emotify;
  Zomato Clone / Readshorts / Targeted Ad Project.
- Emotify's description is supplied by the owner: webcam facial-expression
  recognition and mood-based song recommendations. It is in progress and not
  uploaded to GitHub. Spotify favorite-track recommendations are explicitly
  planned. No implementation stack or live URL has been assumed.
- The Targeted Ad Project description comes from the previously read public
  `targeted-ad-app` source: AdScreen.jsx, AdDisplay.jsx, and package.json. It is
  described as a React frontend consuming audience data, not as a verified
  implementation of the separate recognition API.
- Footfall's data remains in the content file for reference, but it is no longer
  included in the visible picker or cupboard shelves.
