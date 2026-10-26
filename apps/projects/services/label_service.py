from django.db import transaction

from ..exceptions import (
    LabelInvalidException,
    LabelNotFoundException,
)

from ..models import IssueLabel, Label


class LabelService:

    @staticmethod
    def list_labels(*, project, search=None):
        labels = Label.objects.filter(project=project)

        if search:
            labels = labels.filter(name__icontains=search.strip())

        return labels.order_by("name")

    @staticmethod
    @transaction.atomic
    def add_label(*, project, issue, name=None, color="#999999", label_id=None):
        if issue.project_id != project.id:
            raise LabelInvalidException("The issue does not belong to this project.")

        if label_id:
            label = Label.objects.filter(project=project, id=label_id).first()

            if label is None:
                raise LabelNotFoundException("Label not found.")
        else:
            name = name.strip()

            label, _ = Label.objects.get_or_create(
                project=project, name=name, defaults={"color": color}
            )

        IssueLabel.objects.get_or_create(issue=issue, label=label)

        return label

    @staticmethod
    @transaction.atomic
    def remove_label(*, project, issue, label_id):
        issue_label = IssueLabel.objects.filter(
            issue=issue, label_id=label_id, label__project=project
        ).first()

        if issue_label is None:
            raise LabelNotFoundException("Label is not assigned to this issue.")

        issue_label.delete()
