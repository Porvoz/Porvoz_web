from django.db import models


class Contact(models.Model):
    name = models.TextField()
    phone = models.TextField()
    notes = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "contacts"
        ordering = ["created_at"]

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "phone": self.phone,
            "notes": self.notes,
            "createdAt": self.created_at.isoformat() if self.created_at else None,
        }
