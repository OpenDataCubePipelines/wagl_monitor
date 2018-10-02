import json

from flask import current_app

from sqlalchemy import (
    Column, Integer, String, JSON, DateTime, ForeignKey,
    UniqueConstraint, ForeignKeyConstraint, MetaData,
    Index
)
from sqlalchemy import create_engine, event, DDL
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy.schema import CreateSchema, DropSchema

from sqlalchemy.ext.declarative import declarative_base

CACHE_TIME = 300
SCHEMA_NAME = 'monitor'

Base = declarative_base(MetaData(schema=SCHEMA_NAME))
Session = sessionmaker()


class WaglBatch(Base):
    __tablename__ = 'wagl_batch'
    __table_args__ = (
        UniqueConstraint('group_id', 'submit_time', name='uix_batch'),  # Required for uniqueness
        UniqueConstraint('id', 'group_id', name='uix_waglfieldmatch'),  # Required for relationship
    )

    id = Column(Integer, primary_key=True)
    group_id = Column(String)
    submit_time = Column(DateTime)
    user = Column(String)
    summary = Column(JSON)

    items = relationship("WaglBatchItem", backref='batch', lazy=True)

    def to_dict(self):
        return {
            'id': self.id,
            'group_id': self.group_id,
            'submit_time': self.submit_time,
            'user': self.user,
            'summary': None
        }


class WaglBatchItem(Base):
    __tablename__ = 'wagl_batchitem'
    # A complex foreign key is used to expose both batch_id and batch_group_id
    __table_args__ = (
        ForeignKeyConstraint(
            ['batch_id', 'batch_group_id'],
            ['wagl_batch.id', 'wagl_batch.group_id'],
            onupdate='CASCADE', ondelete='CASCADE'
        ),
        Index('idx_waglbatchitem__batch_id', 'batch_id', 'processing_status'),
    )

    id = Column(Integer, primary_key=True)
    granule = Column(String)
    level1 = Column(String)
    processing_status = Column(String)
    failed_task = Column(String)
    batch_id = Column(Integer)
    batch_group_id = Column(String)
    job_group_id = Column(String)
    exception = Column(String)
    error_log = Column(String)
    error_ts = Column(DateTime)

    def to_dict(self):
        return {
            'id': self.id,
            'granule': self.granule,
            'level1': self.level1,
            'processing_status': self.processing_status,
            'failed_task': self.failed_task,
            'batch_group_id': self.batch_group_id,
            'job_group_id': self.job_group_id,
            'exception': self.exception,
            'error_log': self.error_log,
            'error_ts': self.error_ts
        }


def get_engine(database_uri=None):
    database_uri = database_uri or current_app.config['DATABASE_URI']
    engine = create_engine(database_uri)
    Session.configure(bind=engine)
    return engine


def create_db(database_uri=None):
    """ Creates the schema in the database """
    create_fnc = CreateSchema(SCHEMA_NAME)
    engine = get_engine(database_uri)

    event.listen(Base.metadata, 'before_create', create_fnc)
    Base.metadata.create_all(engine)
    event.remove(Base.metadata, 'before_create', create_fnc)

    return engine


def drop_db(database_uri=None):
    """ Convenience method for dropping the related tables in the database """
    drop_fnc = DropSchema(SCHEMA_NAME)
    engine = get_engine(database_uri)

    event.listen(Base.metadata, 'after_drop', drop_fnc)
    Base.metadata.drop_all(engine)
    event.remove(Base.metadata, 'after_drop', drop_fnc)
