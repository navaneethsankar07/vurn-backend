FAQ_ITEMS = [
    {
        "id": "archive-project",
        "question": "How do I archive a project?",
        "answer": """
<p>Archiving a project lets you remove it from active work while
preserving it for future reference.</p>

<h3>To archive a project</h3>
<ol>
    <li>Open the organization containing the project.</li>
    <li>Navigate to the project you want to archive.</li>
    <li>Open the project's settings.</li>
    <li>Choose the archive action and confirm if prompted.</li>
</ol>

<p>You may need appropriate project permissions to archive it.
Archived projects may no longer appear alongside active projects,
depending on the current view and filters.</p>
""",
    },
    {
        "id": "ai-credits",
        "question": "How do AI Credits work?",
        "answer": """
<p>AI Credits represent the usage allowance for AI operations
covered by your Vurn workspace's credit policy.</p>

<ul>
    <li>Credit consumption depends on the AI feature and its
    configured usage rules.</li>
    <li>Check the AI feature or credit information displayed in
    Vurn to understand your available balance.</li>
    <li>Review AI-generated results before using or publishing them.</li>
</ul>

<p>Credit limits, replenishment rules, and operation costs depend
on the policy implemented for your workspace. Refer to the
in-product information for the current details.</p>
""",
    },
    {
        "id": "connect-github",
        "question": "How do I connect GitHub?",
        "answer": """
<p>You can connect a GitHub repository through the relevant
project's integration or repository settings.</p>

<ol>
    <li>Open the project you want to connect.</li>
    <li>Navigate to its GitHub or repository integration settings.</li>
    <li>Follow the available authorization flow.</li>
    <li>Select the intended repository if prompted.</li>
    <li>Verify that the repository is connected to the correct project.</li>
</ol>

<p>You must have the necessary GitHub repository access and
Vurn permissions. If the connection fails, check the authorization
status and the repository you selected.</p>
""",
    },
    {
        "id": "multiple-repositories",
        "question": "Can multiple projects connect different repositories?",
        "answer": """
<p>Yes, projects can be associated with different repositories
when the available GitHub integration supports those connections.</p>

<ul>
    <li>Open each project and configure its repository connection.</li>
    <li>Select the repository intended for that project.</li>
    <li>Verify each connection independently.</li>
</ul>

<p>Make sure you have access to every repository and avoid
accidentally connecting a project to the wrong codebase.</p>
""",
    },
    {
        "id": "delete-organization",
        "question": "Who can delete an organization?",
        "answer": """
<p>Organization deletion should be restricted to users who have
the required organization-level authority under Vurn's permission
rules.</p>

<p>If you cannot find the delete action, or it is unavailable,
check your organization role and permissions or contact the
organization owner.</p>

<p>Before deleting an organization, review the confirmation
details carefully. Deletion may affect the organization's projects,
members, and related resources according to Vurn's deletion rules.</p>
""",
    },
    {
        "id": "restore-project",
        "question": "How do I restore an archived project?",
        "answer": """
<p>If Vurn supports restoring archived projects in your current
workspace, you can restore a project from its archived-project
view or the relevant project settings.</p>

<ol>
    <li>Open the organization that contains the project.</li>
    <li>Locate the archived projects using the filter options.</li>
    <li>Open the project you want to restore.</li>
    <li>Find the restore or unarchive action in the project settings.</li>
    <li>Confirm the action if prompted.</li>
</ol>

<p>You may need appropriate permissions to restore a project.
If you cannot find the project or restoration option, contact
your organization administrator.</p>
""",
    },
]
