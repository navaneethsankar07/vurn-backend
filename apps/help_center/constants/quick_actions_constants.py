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
<p>Vurn brings project planning, issue tracking, sprint management,
and team collaboration into one engineering workspace.</p>

<h2>1. Organize work into projects</h2>
<p>A project groups related work within an organization.</p>
<ul>
    <li>Use a clear project name and a recognizable project key.</li>
    <li>Write a description explaining the project's purpose.</li>
    <li>Assign a project owner and project lead.</li>
    <li>Add members who need to collaborate on the project.</li>
</ul>

<h2>2. Understand issues</h2>
<p>Issues represent trackable work items.</p>
<ul>
    <li><strong>Title and description:</strong> Explain what needs
    to be done and why.</li>
    <li><strong>Status:</strong> Shows the issue's current position
    in the project workflow.</li>
    <li><strong>Priority:</strong> Indicates the relative urgency
    or importance of the work.</li>
    <li><strong>Assignee:</strong> Identifies the person responsible
    for moving the issue forward.</li>
    <li><strong>Labels:</strong> Help categorize related work.</li>
    <li><strong>Due date and estimates:</strong> Help communicate
    deadlines and expected effort.</li>
</ul>

<h2>3. Use the project board</h2>
<p>The board presents issues according to their workflow status.</p>
<ul>
    <li>Review issues in each status column.</li>
    <li>Move work through the workflow as progress changes.</li>
    <li>Keep issue statuses accurate.</li>
    <li>Review blocked or overdue work regularly.</li>
</ul>

<h2>4. Manage workflows</h2>
<p>Workflow statuses describe the stages through which work moves.
Use the project's configured workflow to keep status transitions
consistent across the team.</p>
<ul>
    <li>Understand what each status means.</li>
    <li>Use the appropriate transition when updating an issue.</li>
    <li>Follow the project's workflow rules and permissions.</li>
</ul>

<h2>5. Plan sprints</h2>
<p>Sprints help teams plan a time-bounded set of work.</p>
<ul>
    <li>Define a clear sprint goal.</li>
    <li>Choose start and end dates.</li>
    <li>Select issues that fit the sprint's objective.</li>
    <li>Review progress and incomplete work before completion.</li>
</ul>

<h2>6. Collaborate on issues</h2>
<p>Use issue discussions, assignments, labels, and available
attachments to keep context close to the work.</p>
<ul>
    <li>Write comments that provide useful context.</li>
    <li>Keep issue descriptions updated when requirements change.</li>
    <li>Communicate blockers as soon as they appear.</li>
</ul>

<h2>7. Archive and maintain projects</h2>
<p>Archive a project when it is no longer actively used but should
remain available for reference. Follow your organization's
permissions and retention practices when archiving or deleting
project resources.</p>
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
}
