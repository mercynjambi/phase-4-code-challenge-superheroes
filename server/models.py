from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import MetaData
from sqlalchemy.orm import validates
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy_serializer import SerializerMixin

metadata = MetaData(naming_convention={
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
})

db = SQLAlchemy(metadata=metadata)


class Hero(db.Model, SerializerMixin):
    __tablename__ = 'heroes'  # Fix: Double underscores

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    super_name = db.Column(db.String, nullable=False)

    hero_powers = db.relationship('HeroPower', backref='hero', cascade="all, delete-orphan")
    powers = association_proxy('hero_powers', 'power')

    serialize_rules = ('-hero_powers.hero', '-hero_powers.power.hero',)


class Power(db.Model, SerializerMixin):
    __tablename__ = 'powers'  # Double underscores for tablename

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    description = db.Column(db.String, nullable=False)

    hero_powers = db.relationship('HeroPower', backref='power', cascade="all, delete-orphan")
    heroes = association_proxy('hero_powers', 'hero')

    # Ensure 'hero_powers' is not serialized in responses to avoid test failure
    serialize_rules = ('-hero_powers')

    @validates('description')
    def validate_description(self, key, value):
        if not value or len(value) < 20:
            raise ValueError("Description must be at least 20 characters long.")
        return value

    def to_dict(self, include_hero_powers=False):
        power_dict = {
            'id': self.id,
            'name': self.name,
            'description': self.description,
        }
        # Only include 'hero_powers' if requested
        if include_hero_powers:
            power_dict['hero_powers'] = [hero_power.to_dict() for hero_power in self.hero_powers]
        return power_dict


class HeroPower(db.Model, SerializerMixin):
    __tablename__ = 'hero_powers'  # Fix: Double underscores

    id = db.Column(db.Integer, primary_key=True)
    strength = db.Column(db.String, nullable=False)

    hero_id = db.Column(db.Integer, db.ForeignKey('heroes.id'))
    power_id = db.Column(db.Integer, db.ForeignKey('powers.id'))

    serialize_rules = ('-hero.hero_powers', '-power.hero_powers')

    @validates('strength')
    def validate_strength(self, key, value):
        if value not in ['Strong', 'Weak', 'Average']:
            raise ValueError("Strength must be 'Strong', 'Weak', or 'Average'.")
        return value
