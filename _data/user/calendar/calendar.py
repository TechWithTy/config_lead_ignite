from config._data.user.blogs.plan import BlogPlan, BlogStatus, BlogUrgency
from config._data.user.blogs.posted import PostedBlog
from pydantic import BaseModel, Field
from typing import List, Union, Optional
from datetime import datetime

class CalendarEntry(BaseModel):
    """
    A calendar entry can be a BlogPlan or a PostedBlog, with optional calendar metadata.
    """
    entry: Union[BlogPlan, PostedBlog]
    scheduled_date: Optional[str] = Field(None, description="Scheduled date (ISO 8601)")
    completed_date: Optional[str] = Field(None, description="Completion/publish date (ISO 8601)")
    priority: Optional[int] = Field(None, description="Priority/ranking for scheduling")
    notes: Optional[str] = Field(None, description="Calendar-specific notes")

class BlogCalendar(BaseModel):
    """
    Dynamic calendar of blog plans and posted blogs.
    """
    entries: List[CalendarEntry] = Field(default_factory=list, description="Calendar entries (BlogPlan or PostedBlog)")
    created_at: str = Field(default_factory=lambda: datetime.utcnow().isoformat(), description="Calendar creation timestamp")
    updated_at: Optional[str] = Field(None, description="Last updated timestamp")
    owner: Optional[str] = Field(None, description="Owner/user of the calendar")
    description: Optional[str] = Field(None, description="Description or title for this calendar")

    def add_entry(self, entry: Union[BlogPlan, PostedBlog], **kwargs):
        self.entries.append(CalendarEntry(entry=entry, **kwargs))
        self.updated_at = datetime.utcnow().isoformat()

    def get_plans(self) -> List[BlogPlan]:
        return [e.entry for e in self.entries if isinstance(e.entry, BlogPlan)]

    def get_posted(self) -> List[PostedBlog]:
        return [e.entry for e in self.entries if isinstance(e.entry, PostedBlog)]

    def get_by_status(self, status: BlogStatus) -> List[BlogPlan]:
        return [e.entry for e in self.entries if isinstance(e.entry, BlogPlan) and e.entry.status == status]

    def get_by_urgency(self, urgency: BlogUrgency) -> List[BlogPlan]:
        return [e.entry for e in self.entries if isinstance(e.entry, BlogPlan) and e.entry.urgency == urgency]

    def get_by_date(self, date: str) -> List[CalendarEntry]:
        """Return all entries scheduled for a given date (ISO 8601)."""
        return [e for e in self.entries if e.scheduled_date == date]

    def analytics(self) -> dict:
        """Return basic analytics: counts of planned, posted, etc."""
        return {
            "total_entries": len(self.entries),
            "planned": len(self.get_plans()),
            "posted": len(self.get_posted()),
        }
