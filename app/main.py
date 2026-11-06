from fastapi import FastAPI, HTTPException, Query, status
from datetime import UTC, datetime
from itertools import count
from pydantic import BaseModel, Field

app = FastAPI(title="Second brain API")


class NoteCreate(BaseModel):
	title: str = Field(min_length=1, max_length=200)
	content: str = ""
	tags: list[str] = Field(default_factory=list)


class NoteUpdate(BaseModel):
	title: str | None = Field(default=None, min_length=1, max_length=200)
	content: str | None = None
	tags: list[str] | None = None
	updated_at: datetime


class NoteRead(BaseModel):
	id: int
	title: str
	content: str
	tags: list[str]
	created_at: datetime


_notes: dict[int, NoteRead] = {}
_ids = count(start=1)
def _get_note_or_404(note_id: int) -> NoteRead:
	note = _notes.get(note_id)
	if note is None:
		raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Note for found")
	return note

@app.post("/notes", status_code=status.HTTP_201_CREATED)
def create_node(payload: NoteCreate) -> NoteRead:
	note = NoteRead(id=next(_ids), created_at=datetime.now(UTC), **payload.model_dump())
	_notes[note.id] = note
	return note

@app.get("/notes")
def list_notes(
	tag: str | None = None,
	limit: int | None = Query(default=20, ge=1, le=100),
	offset: int | None = Query(default=0, ge=0)
) -> list[NoteRead]:
	notes = list(_notes.values())
	if tag is not None:
		notes = [n for n in notes if tag in n.tags]
	return notes[offset: offset + limit]

@app.get("/query/{text}")
def query(text: str) -> NoteRead:
	notes = list(_notes)

	note = [n for n in notes if text in tag for tag in n.tags]
	return note

@app.patch("/notes/{note_id}")
def update_note(note_id: int, payload: NoteUpdate) -> NoteRead:
	note = _get_note_or_404(note_id)
	updated = note.model_copy(update=payload.model_dump(exclude_unset=True))
	updated.updated_at = datetime.now(UTC)
	_notes[note_id] = updated
	return updated

@app.delete("/notes/{note_id}", status_code=status.HTTP_204_NO_CONTENT)
def note_delete(note_id: int) -> None:
	_get_note_or_404(note_id)
	del _notes[note_id]


@app.get("/health")
def health() -> dict[str, str]:
	return {"status": "ok"}


@app.get("/version")
def verion() -> dict[str, str]:
	return {"version": "0.1.0"}

