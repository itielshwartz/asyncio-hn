#!/usr/bin/env python3.6
# -*- coding: utf-8 -*-

import pytest

from asyncio_hn import ClientHN


@pytest.mark.asyncio
async def test_last_n_posts():
    async with ClientHN() as hn:
        posts = await hn.last_n_items(2)
        assert len(posts) == 2


@pytest.mark.asyncio
async def test_download_posts():
    async with ClientHN() as hn:
        posts = await hn.items((42, 4242, 424242))
        for post in posts:
            validate_post(post, post_id=424242, post_creator="1gor")
            validate_post(post, post_id=4242, post_creator="PindaxDotCom")
            validate_post(post, post_id=42, post_creator="sergei")


def validate_post(post, post_id, post_creator):
    if post.get("id") == post_id:
        assert post_creator == post.get("by")


@pytest.mark.asyncio
async def test_best_and_latest():
    async with ClientHN() as hn:
        stories = await hn.best_stories()
        assert len(stories) == 200
        latest = await hn.new_stories()
        assert len(latest) == 500


@pytest.mark.asyncio
async def test_download_users():
    async with ClientHN() as hn:
        users = await hn.users(["maximabramchuk", "anthonybsd"])
        for user in users:
            if user["id"] == "maximabramchuk":
                assert user["created"] == 1441729807
            if user["id"] == "'anthonybsd'":
                assert user["created"] == 1436886156
