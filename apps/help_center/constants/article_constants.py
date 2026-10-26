POPULAR_ARTICLES = {
    "creating-your-first-organization": {
        "slug": "creating-your-first-organization",
        "title": "Creating your first organization",
        "category": "Getting Started",
        "description": "Set up your organization and prepare your workspace for collaboration.",
        "read_time_minutes": 4,
        "content": """
<h1>Creating your first organization</h1>
<p>An organization is a shared workspace where your team can manage
projects, collaborate, and organize engineering work in Vurn.</p>

<h2>Before you begin</h2>
<ul>
    <li>Sign in to your Vurn account.</li>
    <li>Decide on a recognizable organization name and URL slug.</li>
    <li>Identify the teammates who should have access.</li>
</ul>

<h2>1. Open Organizations</h2>
<p>Open the Organizations section from the sidebar. Look for the
option to create an organization.</p>

<h2>2. Enter organization details</h2>
<ul>
    <li><strong>Name:</strong> Choose a name that identifies your team.</li>
    <li><strong>Slug:</strong> Choose a short, readable identifier
    if the creation form asks for one.</li>
    <li><strong>Description:</strong> Explain the organization's
    purpose if this field is available.</li>
</ul>

<h2>3. Create the organization</h2>
<p>Submit the form and wait for confirmation. You should then be
able to open the organization workspace.</p>

<h2>4. Configure your workspace</h2>
<ul>
    <li>Review organization preferences and permissions.</li>
    <li>Invite teammates who need access.</li>
    <li>Create a project for your first body of work.</li>
</ul>

<h2>Tips</h2>
<ul>
    <li>Use a consistent naming convention for organizations.</li>
    <li>Give members only the permissions they need.</li>
    <li>Review invitations and membership periodically.</li>
</ul>
""",
    },
    
"inviting-team-members": {
    "slug": "inviting-team-members",
    "title": "Inviting team members",
    "category": "Organizations",
    "description": "Invite teammates using a shareable link, email invitations, or in-app invitations.",
    "read_time_minutes": 5,
    "content": """
<h1>Inviting team members</h1>
<p>Vurn provides multiple ways to invite people to your organization.
You can copy and share an invitation link, send an invitation by
email, or let users accept invitations from within Vurn when they
are logged in.</p>

<h2>Before you begin</h2>
<ul>
    <li>Open the organization where you want to add a member.</li>
    <li>Make sure you have permission to invite members.</li>
    <li>Review your organization's invitation settings and available
    membership roles.</li>
</ul>

<h2>1. Open the invitation interface</h2>
<p>Navigate to your organization and open its member management
or invitation section. Choose the option to invite members.</p>

<h2>2. Choose an invitation method</h2>

<h3>Option A: Copy and share an invitation link</h3>
<ol>
    <li>Choose the option to copy an invitation link.</li>
    <li>Copy the generated link.</li>
    <li>Share it with the intended person through your preferred
    communication channel.</li>
    <li>Ask the recipient to open the link and follow the instructions
    to accept the invitation.</li>
</ol>
<p>This option is convenient when you want to share an invitation
through a messaging application or another communication channel
instead of sending an email directly from Vurn.</p>

<h3>Option B: Send an invitation through email</h3>
<ol>
    <li>Choose the email invitation option.</li>
    <li>Enter the recipient's email address.</li>
    <li>Select a role or job role if the invitation form provides
    those options.</li>
    <li>Review the invitation details and submit the invitation.</li>
    <li>The recipient can use the invitation received by email to
    continue the acceptance process.</li>
</ol>
<p>Check the recipient's email address carefully before sending.
If the invitation does not arrive, ask the recipient to check their
spam or junk folder and verify that the address is correct.</p>

<h3>Option C: Accept an invitation inside Vurn</h3>
<p>Users who are already logged in to Vurn can review invitations
available to their account from the platform's Invitations section.</p>
<ol>
    <li>Sign in to the appropriate Vurn account.</li>
    <li>Open the Invitations section from the sidebar.</li>
    <li>Review the pending organization invitations displayed there.</li>
    <li>Choose the relevant invitation and review its details.</li>
    <li>Accept the invitation to join the organization.</li>
</ol>
<p>This option is useful when the recipient already has a Vurn
account and wants to manage invitations without searching through
their email messages.</p>

<h2>3. Understand invitation acceptance</h2>
<p>Sharing a link or sending an email does not necessarily mean the
recipient has joined the organization. The recipient must complete
the required acceptance process.</p>
<ul>
    <li>A user without a Vurn account may need to register or sign in
    before accepting an invitation.</li>
    <li>A logged-in user can review available invitations in the
    Invitations section.</li>
    <li>Access to the organization is subject to the invitation's
    validity and the platform's acceptance rules.</li>
</ul>

<h2>4. Manage pending invitations</h2>
<ul>
    <li>Review pending invitations in the organization's invitation
    management interface.</li>
    <li>Check invitation status to determine whether it has been
    accepted or is still pending.</li>
    <li>Use the available resend or cancellation actions when needed.</li>
    <li>If an invitation has expired, follow the available process
    to issue a new invitation.</li>
</ul>

<h2>Understanding roles and permissions</h2>
<p>Organization roles and configured permissions determine which
actions a member can perform. Project access may also depend on
project ownership, project membership, and project-specific rules.</p>
<p>Review the selected role before sending an invitation so the
recipient receives the intended level of access.</p>

<h2>Troubleshooting</h2>
<ul>
    <li><strong>Cannot invite a member:</strong> Check your organization
    role, invitation permissions, and organization settings.</li>
    <li><strong>Invitation email not received:</strong> Verify the
    recipient's email address and ask them to check spam or junk.</li>
    <li><strong>Invitation missing in Vurn:</strong> Confirm that the
    user is signed in to the account associated with the invitation.</li>
    <li><strong>Invitation cannot be accepted:</strong> Check its
    status and validity, and follow the available renewal process
    if it has expired.</li>
    <li><strong>Wrong account:</strong> Sign in to the account that
    should receive the invitation and check its Invitations section.</li>
</ul>

<h2>Security recommendations</h2>
<ul>
    <li>Share invitation links only with their intended recipients.</li>
    <li>Review invitation details before accepting an invitation.</li>
    <li>Choose appropriate membership roles and permissions.</li>
    <li>Cancel unwanted pending invitations when the option is available.</li>
</ul>
""",
},
    "creating-projects": {
        "slug": "creating-projects",
        "title": "Creating projects",
        "category": "Projects",
        "description": "Create a project and organize its initial settings and team.",
        "read_time_minutes": 4,
        "content": """
<h1>Creating projects</h1>
<p>Projects help your team organize related issues, workflows,
sprints, and engineering activities.</p>

<h2>1. Select an organization</h2>
<p>Open the organization in which the project should live. You
must have permission to create projects in that organization.</p>

<h2>2. Start project creation</h2>
<p>Open the projects section and choose the create-project action.</p>

<h2>3. Configure project details</h2>
<ul>
    <li><strong>Name:</strong> Use a clear, descriptive project name.</li>
    <li><strong>Key:</strong> Choose a short identifier for issue keys,
    such as APP or WEB.</li>
    <li><strong>Description:</strong> Explain the project's goals
    and scope.</li>
    <li><strong>Dates:</strong> Set dates if the project requires
    a defined timeline.</li>
</ul>

<h2>4. Create and configure the project</h2>
<p>Submit the form. After creation, review the workflow, project
lead, membership, and other settings available to you.</p>

<h2>5. Add and organize work</h2>
<ul>
    <li>Create issues for tasks, features, and bugs.</li>
    <li>Assign work to the appropriate teammates.</li>
    <li>Configure workflow statuses where permitted.</li>
    <li>Create sprints if your team plans work in iterations.</li>
</ul>

<h2>Good practices</h2>
<ul>
    <li>Use a project key that is easy to recognize.</li>
    <li>Keep the project scope and description up to date.</li>
    <li>Grant project access deliberately.</li>
    <li>Archive projects that are no longer active when appropriate.</li>
</ul>
""",
    },
    "managing-issues": {
        "slug": "managing-issues",
        "title": "Managing issues",
        "category": "Issues",
        "description": "Create, assign, prioritize, and track issues through your workflow.",
        "read_time_minutes": 5,
        "content": """
<h1>Managing issues</h1>
<p>Issues represent individual units of work that your team needs
to track, discuss, and complete.</p>

<h2>1. Create an issue</h2>
<ul>
    <li>Open the relevant project.</li>
    <li>Choose the create-issue action.</li>
    <li>Enter a clear title and useful description.</li>
    <li>Select the issue type and priority when available.</li>
    <li>Assign the issue if you already know who should handle it.</li>
</ul>

<h2>2. Understand issue fields</h2>
<ul>
    <li><strong>Identifier:</strong> A project key and issue number
    used to reference the issue.</li>
    <li><strong>Status:</strong> The current stage of the work.</li>
    <li><strong>Priority:</strong> The relative urgency of the issue.</li>
    <li><strong>Assignee:</strong> The person responsible for the work.</li>
    <li><strong>Reporter:</strong> The person who reported the issue.</li>
    <li><strong>Labels:</strong> Categories used to group related work.</li>
    <li><strong>Due date:</strong> A target date when applicable.</li>
</ul>

<h2>3. Update issue status</h2>
<p>Move issues through the project's configured workflow as work
progresses. Follow any status-transition rules enforced by the
project.</p>

<h2>4. Assign and prioritize work</h2>
<ul>
    <li>Choose an assignee who can take responsibility for the issue.</li>
    <li>Set priority according to impact and urgency.</li>
    <li>Use estimates and due dates where they help planning.</li>
    <li>Keep ownership clear when work changes hands.</li>
</ul>

<h2>5. Use sprints</h2>
<p>When sprint planning is available, add appropriate issues to
the relevant sprint and monitor progress against the sprint goal.</p>

<h2>6. Collaborate</h2>
<ul>
    <li>Use comments to share decisions and progress.</li>
    <li>Update descriptions when requirements change.</li>
    <li>Record blockers and link related work where supported.</li>
</ul>

<h2>7. Keep issues useful</h2>
<p>Close completed work using the appropriate workflow status.
Before closing or removing an issue, check its related tasks and
follow your team's conventions.</p>
""",
    },
    "planning-sprints": {
        "slug": "planning-sprints",
        "title": "Planning sprints",
        "category": "Planning",
        "description": "Plan time-boxed work and track progress toward a sprint goal.",
        "read_time_minutes": 5,
        "content": """
<h1>Planning sprints</h1>
<p>A sprint is a time-bounded period in which a team works toward
a defined goal.</p>

<h2>1. Define the sprint goal</h2>
<p>Write a short statement describing the outcome the team wants
to achieve. A clear goal helps the team decide which work belongs
in the sprint.</p>

<h2>2. Create a sprint</h2>
<ul>
    <li>Open the appropriate project and its sprint interface.</li>
    <li>Choose the create-sprint action.</li>
    <li>Enter a sprint name and goal.</li>
    <li>Set the start and end dates.</li>
</ul>

<h2>3. Select issues</h2>
<ul>
    <li>Review the available backlog.</li>
    <li>Select work that contributes to the sprint goal.</li>
    <li>Consider estimates, dependencies, and team capacity.</li>
    <li>Leave room for uncertainty rather than overcommitting.</li>
</ul>

<h2>4. Start the sprint</h2>
<p>Review the selected issues and dates before starting. Once the
sprint begins, keep issue statuses and ownership up to date.</p>

<h2>5. Track progress</h2>
<ul>
    <li>Review remaining work regularly.</li>
    <li>Identify blocked issues early.</li>
    <li>Discuss scope changes with the team.</li>
    <li>Keep the sprint goal visible when making decisions.</li>
</ul>

<h2>6. Complete the sprint</h2>
<p>Review completed and incomplete work before completing the
sprint. Follow Vurn's available completion flow to decide how
unfinished issues should be handled.</p>

<h2>Good practices</h2>
<ul>
    <li>Prefer a clear sprint goal over an arbitrary list of tasks.</li>
    <li>Keep the sprint scope realistic.</li>
    <li>Review outcomes and carry useful lessons into the next sprint.</li>
</ul>
""",
    },
    "using-the-kanban-board": {
        "slug": "using-the-kanban-board",
        "title": "Using the Kanban board",
        "category": "Projects",
        "description": "Understand board columns and visualize work as it progresses.",
        "read_time_minutes": 4,
        "content": """
<h1>Using the Kanban board</h1>
<p>A Kanban board visualizes work as it moves through a workflow.
Each issue appears in a column representing its current status.</p>

<h2>1. Open the project board</h2>
<p>Navigate to the project and open its board view.</p>

<h2>2. Understand columns</h2>
<p>Columns represent the workflow statuses configured for the
project. Their names and ordering may differ between projects.</p>
<ul>
    <li>Review each column to understand the current state of work.</li>
    <li>Look for blocked, overdue, or unassigned issues.</li>
    <li>Use the issue details to understand the next action.</li>
</ul>

<h2>3. Move issues through the workflow</h2>
<p>When work progresses, update the issue status using the
available board interaction or issue details. Some transitions
may be restricted by project workflow rules.</p>

<h2>4. Keep the board accurate</h2>
<ul>
    <li>Update statuses promptly.</li>
    <li>Assign ownership for active work.</li>
    <li>Record blockers and dependencies.</li>
    <li>Review issues that remain in one status for too long.</li>
</ul>

<h2>5. Use the board with sprints</h2>
<p>If your project uses sprints, use the board alongside sprint
planning to understand the state of the selected work.</p>

<h2>Good practices</h2>
<ul>
    <li>Focus on completing existing work before starting too much
    new work.</li>
    <li>Keep issue titles and descriptions meaningful.</li>
    <li>Review workflow columns with your team so their meanings
    remain consistent.</li>
</ul>
""",
    },
    "connecting-github-repositories": {
        "slug": "connecting-github-repositories",
        "title": "Connecting GitHub repositories",
        "category": "Integrations",
        "description": "Connect a repository and troubleshoot integration access.",
        "read_time_minutes": 4,
        "content": """
<h1>Connecting GitHub repositories</h1>
<p>Connecting a GitHub repository can link source-code activity
with the work tracked in a Vurn project.</p>

<h2>1. Check access</h2>
<ul>
    <li>Sign in to the GitHub account that can access the repository.</li>
    <li>Confirm that the repository belongs to the intended account
    or organization.</li>
    <li>Make sure you can authorize the requested integration.</li>
</ul>

<h2>2. Open project integration settings</h2>
<p>Open the project and locate the repository or GitHub integration
settings. Follow the connection flow available in your version
of Vurn.</p>

<h2>3. Authorize and select the repository</h2>
<ul>
    <li>Review the permissions requested by the integration.</li>
    <li>Complete the supported GitHub authorization flow.</li>
    <li>Select the intended repository if repository selection is
    available.</li>
    <li>Confirm that the correct repository is linked to the project.</li>
</ul>

<h2>4. Work with linked development activity</h2>
<p>Where supported, reference issue identifiers in commit messages
and pull requests to help connect code changes with project work.</p>

<h2>5. Troubleshoot problems</h2>
<ul>
    <li>Verify that the GitHub account has repository access.</li>
    <li>Check whether authorization has expired or been revoked.</li>
    <li>Confirm that the correct repository was selected.</li>
    <li>Review the error shown by Vurn before retrying.</li>
</ul>

<h2>Security guidance</h2>
<p>Never paste access tokens or secrets into commits, issues, or
comments. Grant only the integration permissions required for
your workflow.</p>
""",
    },
    "understanding-ai-credits": {
        "slug": "understanding-ai-credits",
        "title": "Understanding AI Credits",
        "category": "AI Features",
        "description": "Learn how to interpret AI credit usage and availability.",
        "read_time_minutes": 3,
        "content": """
<h1>Understanding AI Credits</h1>
<p>If AI credits are enabled in your Vurn workspace, they represent
a usage allowance for the AI operations covered by your workspace's
credit policy.</p>

<h2>1. Check credit availability</h2>
<p>Open the relevant AI feature or credit information interface,
if available, to review your current allowance and usage.</p>

<h2>2. Understand usage</h2>
<p>Credit consumption can depend on the AI operation and the
configured billing or usage policy. Consult the information shown
by Vurn rather than assuming every operation has the same cost.</p>

<h2>3. Manage usage responsibly</h2>
<ul>
    <li>Use AI features for tasks where they provide meaningful value.</li>
    <li>Review generated content before accepting or publishing it.</li>
    <li>Avoid repeatedly submitting the same request without
    understanding the previous result.</li>
</ul>

<h2>4. If credits are unavailable</h2>
<ul>
    <li>Check the usage information shown by the application.</li>
    <li>Verify whether the feature is enabled for your workspace.</li>
    <li>Contact your workspace administrator if you need clarification
    about the credit policy.</li>
</ul>

<h2>Important</h2>
<p>Credit limits, replenishment schedules, and per-operation costs
depend on the policy implemented for your Vurn workspace. Use the
current in-product information as the source of truth.</p>
""",
    },
    "generating-release-notes": {
        "slug": "generating-release-notes",
        "title": "Generating Release Notes",
        "category": "AI Features",
        "description": "Prepare and review release notes from relevant engineering changes.",
        "read_time_minutes": 4,
        "content": """
<h1>Generating Release Notes</h1>
<p>Release notes communicate the changes included in a release.
When AI-assisted release-note generation is available, it can
help prepare a first draft from the relevant engineering context.</p>

<h2>1. Prepare release information</h2>
<ul>
    <li>Identify the release or set of changes to document.</li>
    <li>Review the relevant issues and completed work.</li>
    <li>Gather any additional context required by your release process.</li>
</ul>

<h2>2. Generate a draft</h2>
<p>Open the available release-note generation workflow and provide
the requested release context. Review the input before submitting
the generation request.</p>

<h2>3. Review the generated content</h2>
<ul>
    <li>Verify that the listed changes belong to the intended release.</li>
    <li>Check that important changes have not been omitted.</li>
    <li>Remove duplicate or misleading entries.</li>
    <li>Use language appropriate for the intended audience.</li>
    <li>Verify technical claims against the actual changes.</li>
</ul>

<h2>4. Finalize the release notes</h2>
<p>Edit the draft to reflect the final scope of the release. Follow
your team's review and publishing process before distributing it.</p>

<h2>Good practices</h2>
<ul>
    <li>Separate user-facing changes from internal technical changes
    when appropriate.</li>
    <li>Call out breaking changes and migration requirements.</li>
    <li>Never assume AI-generated notes are complete without review.</li>
</ul>
""",
    },
    "working-with-project-documentation": {
        "slug": "working-with-project-documentation",
        "title": "Working with project documentation",
        "category": "Documentation",
        "description": "Keep project knowledge organized and useful for your team.",
        "read_time_minutes": 4,
        "content": """
<h1>Working with project documentation</h1>
<p>Project documentation keeps important context, decisions,
instructions, and technical knowledge accessible to the team.</p>

<h2>1. Find the documentation area</h2>
<p>Open the relevant project and navigate to its documentation
or knowledge-base section, if enabled and available to you.</p>

<h2>2. Organize information</h2>
<ul>
    <li>Use descriptive titles for documents.</li>
    <li>Group related information by purpose or topic.</li>
    <li>Write a short introduction explaining what each document covers.</li>
    <li>Link related issues and project resources where supported.</li>
</ul>

<h2>3. Write useful documentation</h2>
<ul>
    <li>Explain the problem, decision, or process being documented.</li>
    <li>Use headings to divide longer documents into sections.</li>
    <li>Include examples where they clarify the explanation.</li>
    <li>Identify assumptions and prerequisites.</li>
</ul>

<h2>4. Maintain documentation</h2>
<ul>
    <li>Update documents when implementation or requirements change.</li>
    <li>Remove outdated instructions or clearly mark them as historical.</li>
    <li>Review links and examples periodically.</li>
    <li>Make ownership clear for important technical documents.</li>
</ul>

<h2>5. Respect permissions</h2>
<p>Access to project documentation may depend on project membership,
organization permissions, and the configured documentation access
rules. Follow your team's information-sharing policies.</p>

<h2>Good practices</h2>
<p>Prefer concise, accurate documentation that answers a real
question. A smaller set of well-maintained documents is more useful
than a large collection of outdated or duplicated information.</p>
""",
    },
}
