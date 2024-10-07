# from flask_sqlalchemy import SQLAlchemy
# from sqlalchemy import MetaData
# from sqlalchemy.orm import validates
# from sqlalchemy.ext.associationproxy import association_proxy
# from sqlalchemy_serializer import SerializerMixin

# metadata = MetaData(naming_convention={
#     "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
# })

# db = SQLAlchemy(metadata=metadata)


# class Hero(db.Model, SerializerMixin):
#     __tablename__ = 'heroes'

#     id = db.Column(db.Integer, primary_key=True)
#     name = db.Column(db.String)
#     super_name = db.Column(db.String)

#     # add relationship

#     # add serialization rules

#     def __repr__(self):
#         return f'<Hero {self.id}>'


# class Power(db.Model, SerializerMixin):
#     __tablename__ = 'powers'

#     id = db.Column(db.Integer, primary_key=True)
#     name = db.Column(db.String)
#     description = db.Column(db.String)

#     # add relationship

#     # add serialization rules

#     # add validation

#     def __repr__(self):
#         return f'<Power {self.id}>'


# class HeroPower(db.Model, SerializerMixin):
#     __tablename__ = 'hero_powers'

#     id = db.Column(db.Integer, primary_key=True)
#     strength = db.Column(db.String, nullable=False)

#     # add relationships

#     # add serialization rules

#     # add validation

#     def __repr__(self):
#         return f'<HeroPower {self.id}>'


from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import MetaData
from sqlalchemy.orm import validates
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy_serializer import SerializerMixin

custom_metadata = MetaData(
    naming_convention={
        "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    }
)

database = SQLAlchemy(metadata=custom_metadata)


class Character(database.Model, SerializerMixin):
    __tablename__ = "characters"

    id = database.Column(database.Integer, primary_key=True)
    real_name = database.Column(database.String)
    alias = database.Column(database.String)

    abilities_link = database.relationship(
        "CharacterAbility", back_populates="character", cascade="all, delete-orphan"
    )
    abilities = association_proxy(
        "abilities_link", "ability", creator=lambda ability_instance: CharacterAbility(ability=ability_instance)
    )

    serialize_rules = ("-abilities_link.character",)

    def __repr__(self):
        return f"<Character {self.id}>"


class Ability(database.Model, SerializerMixin):
    __tablename__ = "abilities"

    id = database.Column(database.Integer, primary_key=True)
    title = database.Column(database.String)
    details = database.Column(database.String, nullable=False)

    abilities_link = database.relationship(
        "CharacterAbility", back_populates="ability", cascade="all, delete-orphan"
    )
    characters = association_proxy(
        "abilities_link", "character", creator=lambda character_instance: CharacterAbility(character=character_instance)
    )

    serialize_rules = ("-abilities_link.ability",)

    @validates("details")
    def check_details(self, key, value):
        if not value:
            raise ValueError("Details cannot be empty")
        if len(value) >= 20:
            return value
        else:
            raise ValueError("Details must be at least 20 characters long")

    def __repr__(self):
        return f"<Ability {self.id}>"


class CharacterAbility(database.Model, SerializerMixin):
    __tablename__ = "character_abilities"

    id = database.Column(database.Integer, primary_key=True)
    power_level = database.Column(database.String, nullable=False)

    # Foreign keys for the relationships 
    character_id = database.Column(database.Integer, database.ForeignKey("characters.id"))
    ability_id = database.Column(database.Integer, database.ForeignKey("abilities.id"))
    
    character = database.relationship("Character", back_populates="abilities_link")
    ability = database.relationship("Ability", back_populates="abilities_link")

    serialize_rules = (
        "-character.abilities_link",
        "-ability.abilities_link",
    )

    @validates("power_level")
    def check_power_level(self, key, value):
        if value not in ["High", "Medium", "Low"]:
            raise ValueError(
                "Power level must be one of the following: 'High', 'Medium', 'Low'"
            )
        return value

    def __repr__(self):
        return f"<CharacterAbility {self.id}>"
