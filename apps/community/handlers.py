#!/usr/bin/env python3
# vim: fileencoding=utf-8 fdm=indent sw=4 ts=4 sts=4 et
import json
from tornado.web import RequestHandler
from playhouse.shortcuts import model_to_dict

from mxforum.handlers import RedisHandler
from apps.utils.decorators import authenticated
from apps.utils.serializers import datetime2json
from apps.community.models import Group
from apps.community.forms import GroupForm


class GroupHandler(RedisHandler):
    async def get(self, *args, **kwargs):
        # 获取小组列表
        r = []
        # extend() is a custom method to do a join query with User
        query = Group.extend()

        # 根据组/社区类别做过滤
        category = self.get_argument("c", None)  # c for category
        if category:
            query = query.filter(Group.category == category)

        # 根据参数进行排序
        order = self.get_argument("o", None)  # o for order
        if order:
            if order == "new":
                query = query.order_by(Group.created_time.desc())
            elif order == "hot":
                query = query.order_by(Group.member_num.desc())
        limit = self.get_argument("limit", None)
        if limit:
            query = query.limit(int(limit))
        groups = await self.application.objects.execute(query)
        for group in groups:
            group_dict = model_to_dict(group)
            group_dict["front_image"] = group.front_image_url
            r.append(group_dict)

        self.finish(json.dumps(r, default=datetime2json))

    @authenticated
    async def post(self, *args, **kwargs):
        r = {}
        # 不能使用JSON Form，前端传递封面文件时必须传递表单
        form = GroupForm(self.request.body_arguments)
        if form.validate():
            # 自实现图片字段（文件）验证，WTForms没有支持
            files_meta = self.request.files.get("front_image", None)
            if files_meta is None:
                self.set_status(400)
                r["front_image"] = "请设置小组图片"
            else:
                # 保存图片, I/O
                filename = ""
                for meta in files_meta:
                    filename = await Group.save_front_image(meta)
                group = await self.application.objects.create(
                    Group,
                    creator=self.current_user,
                    name=form.name.data,
                    category=form.category.data,
                    desc=form.desc.data,
                    notice=form.notice.data,
                    front_image=filename,
                )
                r["id"] = group.id
        else:
            self.set_status(400)
            for field in form.errors:
                r[field] = form.errors[field][0]
        self.finish(r)
