from backend.db import SessionLocal, Message

class SessionManager:
    def __init__(self, session_id: str):
        self.session_id = session_id
        self.system_prompt = (
            "You are a helpful, conversational AI assistant. "
            "Keep your answers concise and natural for a voice conversation. "
            "Do not use markdown formatting like asterisks or code blocks."
        )

    def add_message(self, role: str, content: str):
        db = SessionLocal()
        try:
            msg = Message(session_id=self.session_id, role=role, content=content)
            db.add(msg)
            db.commit()
        finally:
            db.close()

    def get_history(self):
        db = SessionLocal()
        try:
            messages = db.query(Message).filter(Message.session_id == self.session_id).order_by(Message.timestamp).all()
            history = [{"role": "system", "content": self.system_prompt}]
            for msg in messages:
                history.append({"role": msg.role, "content": msg.content})
            return history
        finally:
            db.close()

    def clear_history(self):
        db = SessionLocal()
        try:
            db.query(Message).filter(Message.session_id == self.session_id).delete()
            db.commit()
        finally:
            db.close()
