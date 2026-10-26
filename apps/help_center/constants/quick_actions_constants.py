HELP_TOPICS = {
    "getting-started": {
        "slug": "getting-started",
        "title": "Getting Started",
        "description": "Learn the basics of Vurn and set up your workspace.",
        "icon": "lightbulb",
        "content": """
<h1>Getting Started with Vurn</h1>
<p>Vurn is an engineering workspace for organizing projects,
planning work, tracking issues, collaborating with teammates,
and connecting your development workflow.</p>

<h2>1. Understand your workspace</h2>
<ul>
    <li><strong>Home:</strong> Access your personal workspace and
    relevant activity.</li>
    <li><strong>Organizations:</strong> Manage your teams,
    organization settings, and projects.</li>
    <li><strong>Projects:</strong> Organize issues, sprints,
    workflows, and development work.</li>
    <li><strong>Notifications:</strong> Review updates related
    to your work and team activity.</li>
</ul>

<h2>2. Create or join an organization</h2>
<p>An organization is the shared workspace for your team.</p>
<ul>
    <li>Create an organization if you are setting up a new team.</li>
    <li>Accept an invitation to join an existing organization.</li>
    <li>Review your role and permissions before managing team
    resources.</li>
</ul>

<h2>3. Create your first project</h2>
<p>Projects provide a place to plan and track a body of work.</p>
<ul>
    <li>Open your organization and navigate to its projects.</li>
    <li>Create a project with a meaningful name and unique key.</li>
    <li>Configure the project workflow and add relevant members.</li>
    <li>Use the project board to organize and track issues.</li>
</ul>

<h2>4. Create and track issues</h2>
<p>Issues represent individual pieces of work, such as features,
bugs, improvements, and tasks.</p>
<ul>
    <li>Give each issue a clear, actionable title.</li>
    <li>Add a description with the expected outcome and context.</li>
    <li>Choose an appropriate status and priority.</li>
    <li>Assign the issue and add it to a sprint when applicable.</li>
</ul>

<h2>5. Plan work with sprints</h2>
<p>Sprints help teams organize work into a defined period.</p>
<ul>
    <li>Create a sprint with a goal and date range.</li>
    <li>Move appropriate issues into the sprint.</li>
    <li>Track progress throughout the sprint.</li>
    <li>Review incomplete work before completing the sprint.</li>
</ul>

<h2>6. Understand permissions</h2>
<p>Actions available to you depend on your organization role,
project access, and configured permissions. If an action is
unavailable, contact an organization administrator.</p>

<h2>Recommended first steps</h2>
<ol>
    <li>Join or create an organization.</li>
    <li>Open a project or create one.</li>
    <li>Create an issue and assign it.</li>
    <li>Explore the project board and sprint workflow.</li>
    <li>Review notifications and project documentation.</li>
</ol>
""",
    },
    "project-management": {
        "slug": "project-management",
        "title": "Project Management",
        "description": "Learn about projects, boards, issues, sprints, and workflows.",
        "icon": "folder-kanban",
        "content": """
<h1>Project Management in Vurn</h1>
<p>Projects provide a workspace for organizing engineering work,
managing access, and coordinating team activities.</p>

<h2>1. Create a project</h2>
<ul>
    <li>Open the organization where the project should belong.</li>
    <li>Create a project with a meaningful name and unique project key.</li>
    <li>Add a description explaining the project's purpose.</li>
    <li>Configure the project owner, project lead, and other settings
    as supported by your permissions.</li>
</ul>

<h2>2. Manage project access</h2>
<p>Project access determines which members can view and manage
project resources.</p>
<ul>
    <li>Review the project's owner and lead.</li>
    <li>Follow the configured project access and organization
    permission rules.</li>
    <li>Grant members only the access they need.</li>
</ul>

<h2>3. Organize project work</h2>
<p>Vurn brings several work-management features together within
each project.</p>
<ul>
    <li><strong>Issues:</strong> Track tasks, bugs, features, and
    other units of work. See the Issue Management guide.</li>
    <li><strong>Sprints:</strong> Plan work for a defined period.
    See the Sprint Management guide.</li>
    <li><strong>Workflow statuses:</strong> Configure how work moves
    through your process. See Workflow Statuses and Transitions.</li>
    <li><strong>Knowledge base:</strong> Organize project
    documentation and related resources.</li>
    <li><strong>Repository integration:</strong> Connect development
    work to a supported repository.</li>
</ul>

<h2>4. Update project settings</h2>
<p>Use the project's settings to maintain its details and other
available configuration. Review the impact of changes before
applying them to an active project.</p>

<h2>5. Archive a project</h2>
<p>Archive a project when it is no longer actively used but should
remain available for reference. Use the archive action and confirm
the operation if prompted.</p>

<h2>6. Delete a project</h2>
<p>Deletion is different from archiving. Before deleting a project,
review the confirmation details and the effect on its associated
resources.</p>
<ul>
    <li>Make sure you have the required permission.</li>
    <li>Confirm that the correct project is selected.</li>
    <li>Review any warnings about related resources.</li>
    <li>Use the deletion action only when the project should no longer
    be retained under your workspace's rules.</li>
</ul>
<p>If the action is unavailable, check your project and organization
permissions or contact the organization owner.</p>
""",
    },
    "github-integration": {
        "slug": "github-integration",
        "title": "GitHub Integration",
        "description": "Connect repositories and understand commits and pull requests.",
        "icon": "github",
        "content": """
<h1>GitHub Integration</h1>
<p>GitHub integration connects project work in Vurn with your
software development workflow. Available capabilities depend on
the integration configuration and the features enabled for your
workspace.</p>

<h2>1. Connect a repository</h2>
<ul>
    <li>Open the relevant project's repository or integration settings.</li>
    <li>Follow the available GitHub connection flow.</li>
    <li>Authorize the requested access through GitHub.</li>
    <li>Select the intended repository if repository selection
    is available.</li>
    <li>Verify that the repository is linked to the correct project.</li>
</ul>

<h2>2. Understand repository access</h2>
<p>Repository visibility and available operations depend on your
GitHub permissions and the authorization granted to the integration.
Only grant the access required for the intended workflow.</p>

<h2>3. Link development activity to issues</h2>
<p>Use the issue identifier in commit messages or pull request
references when your configured integration supports issue linking.</p>
<ul>
    <li>Reference the relevant issue when committing changes.</li>
    <li>Include a meaningful summary of the change.</li>
    <li>Reference related issues in pull requests.</li>
    <li>Review linked activity from the project or issue interface
    when available.</li>
</ul>

<h2>4. Understand commits and pull requests</h2>
<ul>
    <li><strong>Commits:</strong> Record changes made to the codebase.</li>
    <li><strong>Branches:</strong> Isolate development work.</li>
    <li><strong>Pull requests:</strong> Propose and review changes
    before merging them.</li>
    <li><strong>Issue references:</strong> Connect development work
    to the task it addresses.</li>
</ul>

<h2>5. Refresh repository information</h2>
<p>If Vurn provides a repository refresh action, use it to request
an update of repository information. The available data and refresh
behavior depend on the integration implementation.</p>

<h2>6. Troubleshoot connection problems</h2>
<ul>
    <li>Confirm that the GitHub account has access to the repository.</li>
    <li>Verify that the correct repository is connected.</li>
    <li>Review the integration's connection or authorization status.</li>
    <li>Reauthorize the integration if access has been revoked.</li>
    <li>Check available error messages before retrying an operation.</li>
</ul>

<h2>Security guidance</h2>
<p>Never share access tokens or secrets in issue descriptions,
comments, or commit messages. Use the supported authorization flow
and revoke access that is no longer required.</p>
""",
    },
    "ai-features": {
        "slug": "ai-features",
        "title": "AI Features",
        "description": "Understand AI-powered engineering and productivity tools.",
        "icon": "sparkles",
        "content": """
<h1>AI Features in Vurn</h1>
<p>Vurn's AI features are intended to assist engineering teams
with productivity tasks. The exact tools available depend on
which AI capabilities have been implemented and enabled.</p>

<h2>1. Understand AI-assisted workflows</h2>
<p>AI can help with tasks such as summarizing engineering context,
drafting documentation, and preparing release information.
Treat generated content as a starting point that should be reviewed.</p>

<h2>2. Generate release notes</h2>
<p>When release-note generation is available, provide the relevant
release context and review the generated result.</p>
<ul>
    <li>Identify the release or set of changes being summarized.</li>
    <li>Review the generated entries for accuracy and completeness.</li>
    <li>Correct misleading, duplicated, or missing information.</li>
    <li>Confirm the final release notes before publishing them.</li>
</ul>

<h2>3. Understand AI credits</h2>
<p>If your workspace uses AI credits, review the information
provided by the relevant feature before running an operation.
Credit costs, limits, and availability depend on your configured
AI features and credit policy.</p>

<h2>4. Review AI-generated content</h2>
<ul>
    <li>Verify factual claims against the underlying source material.</li>
    <li>Review code, commands, and technical recommendations before
    using them.</li>
    <li>Remove sensitive information that is not necessary for
    the task.</li>
    <li>Do not treat generated content as automatically correct.</li>
</ul>

<h2>5. Protect project information</h2>
<p>Only provide information permitted by your organization's
policies and the applicable AI integration configuration.
Understand which service processes the data before sharing
confidential project information.</p>

<h2>6. Troubleshoot AI operations</h2>
<ul>
    <li>Confirm that the requested AI feature is enabled.</li>
    <li>Check whether your account or workspace has the required
    access or available credits.</li>
    <li>Review the error message and retry only when appropriate.</li>
    <li>Verify the generated output before using it in project work.</li>
</ul>
""",
    },
    "organization-management": {
        "slug": "organization-management",
        "title": "Organization Management",
        "description": "Manage organizations, members, invitations, custom roles, and permissions.",
        "icon": "building-2",
        "content": """
<h1>Organization Management</h1>
<p>An organization is the shared workspace where a team manages
members, projects, access rules, and collaboration settings.</p>

<h2>1. Organization ownership</h2>
<p>The organization owner has full organization access and is
responsible for managing the workspace.</p>
<ul>
    <li>Manage organization settings and preferences.</li>
    <li>Manage membership and invitations.</li>
    <li>Create and manage projects.</li>
    <li>Configure roles and permissions where supported.</li>
</ul>

<h2>2. Manage organization members</h2>
<p>Open the organization to view its members and available
membership-management actions.</p>
<ul>
    <li>Review member roles and job roles.</li>
    <li>Invite new members using the available invitation methods.</li>
    <li>Review access before changing a member's role.</li>
    <li>Remove members when they no longer need organization access,
    subject to the available permissions.</li>
</ul>

<h2>3. Understand organization roles</h2>
<p>Vurn distinguishes organization-level access from a member's
job role. Organization roles determine broad access, while a job
role can provide a predefined set of permissions.</p>
<ul>
    <li><strong>Owner:</strong> Has full organization access.</li>
    <li><strong>Admin:</strong> Has full access under the application's
    organization access rules, with certain actions controlled by
    organization preferences.</li>
    <li><strong>Member:</strong> Receives permissions according to
    their assigned job role and organization preferences.</li>
</ul>

<h2>4. Create custom job roles</h2>
<p>The organization owner can create custom job roles to represent
the responsibilities of different team members.</p>
<ol>
    <li>Open the organization's role-management settings.</li>
    <li>Create a role with a meaningful name.</li>
    <li>Select the predefined permissions that role should have.</li>
    <li>Save the role.</li>
    <li>Assign the role to members when adding or managing membership.</li>
</ol>
<p>For example, a frontend developer role can receive the permissions
needed for their work, while a QA role can receive a different set
of permissions.</p>

<h2>5. Understand permission assignment</h2>
<p>Permissions assigned to a custom job role determine the actions
available to members assigned to that role. Assign only the
permissions required for the role's responsibilities.</p>
<ul>
    <li>Review permissions before assigning a role.</li>
    <li>Update the role when responsibilities change.</li>
    <li>Review members who use a role before making broad changes.</li>
</ul>

<h2>6. Invite members and assign roles</h2>
<p>When inviting a member, choose the appropriate role or job role
if the invitation flow offers that option. The resulting access
depends on the role, organization preferences, and applicable
project-level access rules.</p>

<h2>7. Configure organization preferences</h2>
<p>Organization preferences can control certain organization
behaviors, such as whether admins can invite members and whether
members can create projects. These preferences work alongside
role-based permissions.</p>

<h2>8. Project deletion and organization access</h2>
<p>Organization membership does not automatically mean every
member can perform every project operation. Project deletion,
archiving, and other sensitive actions must follow the relevant
project and organization permission rules.</p>
<p>Before deleting a resource, review the confirmation details
and understand the effect on related work.</p>
""",
    },
    "sprint-management": {
        "slug": "sprint-management",
        "title": "Sprint Management",
        "description": "Create, schedule, start, and complete sprints safely.",
        "icon": "calendar-range",
        "content": """
<h1>Sprint Management</h1>
<p>Sprints help teams organize a set of work around a goal and
a defined time period.</p>

<h2>1. Create a sprint</h2>
<ul>
    <li>Open the project's sprint management page.</li>
    <li>Provide a sprint name and optional goal or description.</li>
    <li>Set the start and end dates.</li>
    <li>Add the work items intended for the sprint.</li>
</ul>

<h2>2. Avoid overlapping sprint dates</h2>
<p>Plan sprint date ranges carefully. Vurn should enforce the
configured rule that prevents overlapping sprint periods within
the same project.</p>
<ul>
    <li>Check existing sprint dates before choosing a new range.</li>
    <li>Adjust the proposed dates if they overlap an existing sprint.</li>
    <li>Confirm the final date range before saving.</li>
</ul>

<h2>3. Start a sprint</h2>
<p>Review the sprint before starting it.</p>
<ul>
    <li>Confirm the sprint goal and date range.</li>
    <li>Review the work items included in the sprint.</li>
    <li>Resolve planning issues before starting.</li>
    <li>Use the available Start Sprint action.</li>
</ul>
<p>Once started, keep work item statuses and ownership up to date
so the sprint reflects the team's actual progress.</p>

<h2>4. Complete a sprint</h2>
<p>Before completing a sprint, review completed work and all
remaining work items.</p>

<h3>Pending subtasks must be completed first</h3>
<p>If any issue in the sprint has an incomplete subtask, the sprint
cannot be completed. Complete the pending subtask before retrying
sprint completion.</p>

<h3>Choose what happens to remaining work</h3>
<p>For remaining work items, Vurn provides three handling options
in the sprint completion flow:</p>
<ul>
    <li><strong>Move to an existing sprint:</strong> Select another
    suitable sprint that already exists in the project.</li>
    <li><strong>Create a new sprint:</strong> Create a sprint and
    move the remaining work into it.</li>
    <li><strong>Move to the backlog:</strong> Remove the remaining
    work from the current sprint and return it to the backlog.</li>
</ul>
<p>Review the selected destination for each remaining work item
before confirming completion.</p>

<h2>5. Review sprint results</h2>
<ul>
    <li>Review completed work and work that was moved elsewhere.</li>
    <li>Confirm the next sprint's scope where applicable.</li>
    <li>Keep sprint goals and dates meaningful for future planning.</li>
</ul>
""",
    },
    "workflow-management": {
        "slug": "workflow-management",
        "title": "Workflow Statuses and Transitions",
        "description": "Configure project statuses and control how work moves between them.",
        "icon": "git-branch",
        "content": """
<h1>Workflow Statuses and Transitions</h1>
<p>A workflow defines the statuses available to issues in a
project and the rules that govern movement between those statuses.</p>

<h2>1. Understand workflow statuses</h2>
<p>Each status represents a stage of work. Projects can configure
statuses that fit their team's process.</p>
<ul>
    <li><strong>Name:</strong> The label displayed to users.</li>
    <li><strong>Category:</strong> The status classification used
    by the workflow.</li>
    <li><strong>Color and icon:</strong> Visual indicators, where
    configured.</li>
    <li><strong>Position:</strong> Determines the status order
    in the workflow interface.</li>
    <li><strong>Default status:</strong> Identifies the configured
    default status where applicable.</li>
</ul>

<h2>2. Create and manage statuses</h2>
<p>Open the project's workflow settings and use the available
status-management controls.</p>
<ul>
    <li>Choose a clear status name.</li>
    <li>Set its category and visual properties.</li>
    <li>Arrange statuses in a useful order.</li>
    <li>Archive a status when it should no longer be used, if supported.</li>
</ul>

<h2>3. Understand transition rules</h2>
<p>Not every status change must be permitted. Vurn's workflow
rules can determine whether a status accepts incoming transitions,
allows outgoing transitions, or permits work to enter from the
backlog.</p>
<ul>
    <li><strong>Allow incoming:</strong> Controls whether issues can
    transition into the status.</li>
    <li><strong>Allow outgoing:</strong> Controls whether issues can
    transition out of the status.</li>
    <li><strong>Allow from backlog:</strong> Controls whether issues
    can enter the status directly from the backlog.</li>
</ul>

<h2>4. Move work between statuses</h2>
<p>When changing an issue's status, use a permitted transition.
If a transition is rejected, review the configured workflow rules
and the issue's current status.</p>

<h2>5. Maintain workflow consistency</h2>
<ul>
    <li>Use status names that are clear to the entire team.</li>
    <li>Avoid creating duplicate statuses with the same meaning.</li>
    <li>Review transition settings before changing an active workflow.</li>
    <li>Check the impact on existing issues before archiving a status.</li>
</ul>

<h2>6. Permissions</h2>
<p>Only users with the appropriate project permissions should
manage workflow configuration. Available actions depend on the
project's access rules and implemented workflow controls.</p>
""",
    },
    "issue-management": {
        "slug": "issue-management",
        "title": "Issue Management",
        "description": "Manage issues, subtasks, comments, attachments, and labels.",
        "icon": "check-square",
        "content": """
<h1>Issue Management</h1>
<p>Issues represent trackable units of work within a project.
Each issue has its own details, status, and related resources.</p>

<h2>1. Create and update issues</h2>
<ul>
    <li>Provide a clear title and useful description.</li>
    <li>Choose the appropriate issue type and priority.</li>
    <li>Assign an owner and set a due date or estimate when needed.</li>
    <li>Update issue details as requirements change.</li>
    <li>Use the issue identifier when discussing or referencing work.</li>
</ul>

<h2>2. Manage subtasks</h2>
<p>Subtasks divide an issue into smaller pieces of work.</p>
<ul>
    <li>Create subtasks under the appropriate parent issue.</li>
    <li>Give each subtask a specific and actionable title.</li>
    <li>Track each subtask's status and ownership.</li>
    <li>Complete pending subtasks before completing a sprint that
    contains them, as required by Vurn's sprint completion rules.</li>
</ul>

<h2>3. Manage comments</h2>
<p>Comments keep discussions and decisions close to the relevant
issue.</p>
<ul>
    <li>Use comments to communicate progress, questions, and blockers.</li>
    <li>Keep messages relevant to the issue.</li>
    <li>Review the discussion before making decisions.</li>
    <li>Use the available edit or delete actions only when permitted.</li>
</ul>

<h2>4. Manage attachments</h2>
<p>Attachments can provide supporting material such as screenshots,
documents, and other permitted files.</p>
<ul>
    <li>Upload files using the issue's attachment controls.</li>
    <li>Use descriptive filenames.</li>
    <li>Check the file size and supported file type before uploading.</li>
    <li>Remove an attachment only when appropriate and permitted.</li>
</ul>

<h2>5. Manage labels</h2>
<p>Labels help categorize issues and make related work easier to
identify.</p>
<ul>
    <li>Use clear, consistent label names.</li>
    <li>Apply labels that describe the work meaningfully.</li>
    <li>Reuse existing labels where appropriate instead of creating
    duplicates.</li>
    <li>Remove labels that no longer apply, if permitted.</li>
</ul>

<h2>6. Keep issue information accurate</h2>
<p>Review issue status, assignee, priority, and related resources
regularly. Accurate issue information makes project planning
and collaboration more reliable.</p>
""",
    },
    "knowledge-base-management": {
        "slug": "knowledge-base-management",
        "title": "Knowledge Base Management",
        "description": "Organize folders, rich-text documents, tags, and attachments.",
        "icon": "book-open",
        "content": """
<h1>Knowledge Base Management</h1>
<p>The knowledge base helps teams organize project documentation,
technical notes, decisions, and other useful information.</p>

<h2>1. Manage folders</h2>
<p>Folders organize documents into a structure that is easy to
navigate.</p>
<ul>
    <li>Create folders with descriptive names.</li>
    <li>Group related documents together.</li>
    <li>Keep the folder structure simple and predictable.</li>
    <li>Rename, move, or delete folders only when those actions
    are available and permitted.</li>
    <li>Review the documents inside a folder before deleting it.</li>
</ul>

<h2>2. Create and edit rich-text documents</h2>
<p>Use the rich-text editor to create readable documentation.</p>
<ul>
    <li>Give each document a meaningful title.</li>
    <li>Use headings to organize long documents.</li>
    <li>Use paragraphs and lists to make instructions easy to follow.</li>
    <li>Use supported formatting to emphasize important information.</li>
    <li>Review changes before saving or publishing them.</li>
</ul>

<h2>3. Manage tags</h2>
<p>Tags help categorize documents across the knowledge base.</p>
<ul>
    <li>Use descriptive and reusable tag names.</li>
    <li>Apply tags that reflect a document's subject or purpose.</li>
    <li>Reuse existing tags when they already describe the content.</li>
    <li>Remove irrelevant tags when they no longer apply.</li>
</ul>

<h2>4. Upload attachments</h2>
<p>Knowledge base documents can include supported files when
attachment functionality is available.</p>
<ul>
    <li>The maximum permitted attachment size is 50 MB per file.</li>
    <li>Supported formats include JPEG, PNG, WebP, GIF, SVG, MP4,
    WebM, QuickTime video, PDF, Word, Excel, PowerPoint, plain text,
    and CSV files.</li>
    <li>Files must use an allowed MIME type and satisfy the size limit.</li>
    <li>Use descriptive filenames and ensure attachments are relevant
    to the document.</li>
</ul>

<h2>5. Keep documents maintainable</h2>
<ul>
    <li>Update documentation when processes or implementations change.</li>
    <li>Remove outdated instructions where appropriate.</li>
    <li>Use tags and folders consistently.</li>
    <li>Check permissions before sharing sensitive project information.</li>
</ul>
""",
    },
}
