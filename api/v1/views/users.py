import hashlib
from models.base_model import BaseModel, Base
from sqlalchemy import Column, String
from sqlalchemy.orm import relationship

class User(BaseModel, Base):
    """Representation of a user"""
    if models.storage_t == 'db':
        __tablename__ = 'users'
        email = Column(String(128), nullable=False)
        password = Column(String(128), nullable=False)
        first_name = Column(String(128), nullable=True)
        last_name = Column(String(128), nullable=True)
        places = relationship("Place", cascade="all,delete", backref="user")
        reviews = relationship("Review", cascade="all,delete", backref="user")
    else:
        email = ""
        password = ""
        first_name = ""
        last_name = ""

    def __init__(self, *args, **kwargs):
        """Initializes user"""
        super().__init__(*args, **kwargs)

    def update_password(self, new_password):
        """
        Update the user's password and hash it using MD5.
        """
        self.password = hashlib.md5(new_password.encode()).hexdigest()

    def to_dict(self, save_to_disk=False):
        """
        Returns a dictionary representation of the User instance.
        If save_to_disk is True, include the password key.
        """
        user_dict = super().to_dict()
        if not save_to_disk:
            user_dict.pop('password', None)  # Remove password key
        return user_dict
