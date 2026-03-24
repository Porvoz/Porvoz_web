from django.db import models
from contacts.models import Contact


class CallRecord(models.Model):
    reminder = models.ForeignKey(
        "reminders.Reminder",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        db_column="reminder_id",
        related_name="call_records",
    )
    contact = models.ForeignKey(
        Contact,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        db_column="contact_id",
        related_name="call_records",
    )
    call_sid = models.TextField(null=True, blank=True)
    status = models.TextField(default="initiated")
    duration = models.IntegerField(null=True, blank=True)
    transcript = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "call_records"
        ordering = ["-created_at"]

    def to_dict(self):
        return {
            "id": self.id,
            "reminderId": self.reminder_id,
            "contactId": self.contact_id,
            "contactName": self.contact.name if self.contact_id else None,
            "callSid": self.call_sid,
            "status": self.status,
            "duration": self.duration,
            "transcript": self.transcript,
            "createdAt": self.created_at.isoformat() if self.created_at else None,
        }
