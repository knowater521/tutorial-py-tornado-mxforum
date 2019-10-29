#!/usr/bin/env python3
# vim: fileencoding=utf-8 fdm=indent sw=4 ts=4 sts=4 et
import os
from time import time
from datetime import datetime
import uuid
from peewee import CharField, TextField, ForeignKeyField, IntegerField, DateTimeField
import aiofiles
from mxforum.models import BaseModel
from mxforum.settings import settings
from apps.user.models import User


class Group(BaseModel):
    class Meta:
        table_name = "groups"

    creator = ForeignKeyField(User, verbose_name="创建人")
    name = CharField(max_length=100, null=True, verbose_name="名称")
    category = CharField(max_length=20, verbose_name="分类", null=True)
    front_image = CharField(max_length=200, null=True, verbose_name="封面图")
    desc = TextField(verbose_name="简介")
    notice = TextField(verbose_name="公告")

    # group info
    member_num = IntegerField(default=1, verbose_name="成员数")
    post_num = IntegerField(default=0, verbose_name="帖子数")

    @staticmethod
    def __hash_filename(filename):
        """Generate a random name for uploaded file"""
        # 由于 werkzeug.secure_filename 不支持中文，所以没必要使用
        _, _, extension = filename.rpartition(".")
        return "%s.%s" % (uuid.uuid4().hex, extension)

    @staticmethod
    async def save_front_image(uploaded_file):
        filename = __class__.__hash_filename(uploaded_file["filename"])
        file_path = os.path.join(settings["media_root"], filename)
        async with aiofiles.open(file_path, "wb") as f:
            await f.write(uploaded_file["body"])
        return filename

    @property
    def front_image_url(self):
        return "{}/media/{}".format(settings["site_url"], self.front_image)

    @classmethod
    def extend(cls):
        return cls.select(cls, User.id, User.nickname).join(User)


JOIN_STATUS = (("agreed", "已接受"), ("refused", "被拒绝"))


class GroupMember(BaseModel):
    class Meta:
        table_name = "group_members"

    user = ForeignKeyField(User, verbose_name="社区成员")
    group = ForeignKeyField(Group, verbose_name="社区")
    status = CharField(
        choices=JOIN_STATUS, max_length=10, null=True, verbose_name="成员状态"
    )
    apply_reason = CharField(max_length=200, verbose_name="申请加入理由")
    reply = CharField(max_length=200, verbose_name="申请处理答复")
    reply_time = DateTimeField(default=datetime.utcnow, verbose_name="申请处理时间")
