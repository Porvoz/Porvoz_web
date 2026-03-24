from django.db import models
from contacts.models import Contact


class Reminder(models.Model):
    STATUS_PENDING = "pending"
    STATUS_CALLED = "called"
    STATUS_FAILED = "failed"

    contact = models.ForeignKey(
        Contact, on_delete=models.CASCADE, db_column="contact_id", related_name="reminders"
    )
    title = models.TextField()
    message = models.TextField()
    scheduled_at = models.DateTimeField()
    status = models.TextField(default="pending")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "reminders"
        ordering = ["scheduled_at"]

    def to_dict(self):
        return {
            "id": self.id,
            "contactId": self.contact_id,
            "contactName": self.contact.name if self.contact_id else None,
            "contactPhone": self.contact.phone if self.contact_id else None,
            "title": self.title,
            "message": self.message,
            "scheduledAt": self.scheduled_at.isoformat() if self.scheduled_at else None,
            "status": self.status,
            "createdAt": self.created_at.isoformat() if self.created_at else None,
        }
