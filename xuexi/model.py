#!/usr/bin/env python
# -*- coding:utf-8 -*-
'''
@project: AutoXue
@file: model.py
@author: kessil
@contact: https://github.com/kessil/AutoXue/
@time: 2019-08-22(星期四) 13:26
@Copyright © 2019. All rights reserved.
'''

from pathlib import Path
import re
import json
from sqlalchemy import Column,Integer, String, Text, Boolean, create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from .mconfig import cfg
from .mloggger import logger as log

# 创建对象的基类:
Base = declarative_base()

class Model():
    def __init__(self):
        # 初始化数据库连接:
        database_uri = cfg.get('database_server', 'uri')
        engine = create_engine(database_uri)
        # 创建DBSession类型:
        Session = sessionmaker(bind=engine)

        Base.metadata.create_all(engine)
        self.session = Session()

    def query(self, id=None, content=None, catagory='挑战题 单选题 多选题 填空题'):
        '''数据库检索记录'''
        catagory = catagory.split(' ')
        if id and isinstance(id, int):
            return self.session.query(Bank).filter_by(id=id).first()
        if content and isinstance(content, str):
            content = re.sub(r'\s+', '%', content)
            return self.session.query(Bank).filter(Bank.catagory.in_(catagory)).filter(Bank.content.like(content)).first()
        return self.session.query(Bank).filter(Bank.catagory.in_(catagory)).all()

    def add(self, item):
        '''数据库添加纪录'''
        result = self.query(content=item.content, catagory=item.catagory)
        if result:
            log.info(f'数据库已存在此纪录，无需添加纪录！')
        else:
            self.session.add(item)
            self.session.commit()
            log.info(f'数据库添加记录成功！<{item.catagory} - {item.id:>4}> {item.answer}')

    def update(self, item):
        self.session.add(item)
        self.session.commit()
        log.info(f'数据库更新记录成功！')

    def load(self, path):
        if '.json' != path.suffix:
            raise ValueError(f'upload file should be JSON file')
        else:
            with path.open(mode='r', encoding='utf-8') as fp:
                data = json.load(fp)
            for d in data:
                temp = Bank.from_dict(d)
                # if not temp.options and not temp.note:
                #     continue
                if '填空题' == temp.catagory and len(temp.answer.split()) != int(temp.options):
                    continue
                if '挑战题' == temp.catagory and '' == temp.answer:
                    continue
                self.add(temp)
            else:
                log.info(f'数据库更新完毕')
                

    def dump(self):
        pathdir = Path(cfg.get('database_server', 'export'))
        pathdir.mkdir(parents=True, exist_ok=True)
        daily = self.query(catagory='填空题 单选题 多选题')
        challenge = self.query(catagory='挑战题')
        md_doc = pathdir / 'data-doc.md'
        with md_doc.open(mode='w', encoding='utf-8') as fp:
            fp.write(f'# 学习强国 挑战答题 题库 {len(challenge):>4} 题\n')
            for item in challenge:
                if not item.answer:
                    continue
                content = re.sub(r'\s\s+', '\_\_\_\_',re.sub(r'[\(（]出题单位.*', '', item.content))
                options = "\n\n".join([f'+ **{x}**' if i==ord(item.answer)-65 else f'+ {x}' for i, x in enumerate(item.options.split('|'))])
                fp.write(f'{item.id}. {content}  *{item.answer}*\n\n{options}\n\n')
            else:
                log.debug(f'数据库导出 {md_doc}')

        md_grid = pathdir / 'data-grid.md'
        with md_grid.open(mode='w', encoding='utf-8') as fp:
            fp.write(f'# 学习强国 挑战答题 题库 {len(challenge):>4} 题\n')
            fp.write(f'|序号|答案|题干|选项A|选项B|选项C|选项D|\n')
            fp.write(f'|:--:|:--:|--------|----|----|----|----|\n')
            for item in challenge:
                if not item.answer:
                    continue
                content = re.sub(r'\s\s+', '\_\_\_\_',re.sub(r'[\(（]出题单位.*', '', item.content))
                options = " | ".join([f'**{x}**' if i==ord(item.answer)-65 else f'{x}' for i, x in enumerate(item.options.split('|'))])
                fp.write(f'| {item.id} | {item.answer} | {content} | {options} |\n')
            else:
                log.debug(f'数据库导出 {md_grid}')

        json_daily = pathdir / 'data-daily.json'
        with json_daily.open(mode='w', encoding='utf-8') as fp:
            json.dump([d.to_dict() for d in daily], fp, indent=4, ensure_ascii=False)
        log.debug(f'数据库导出 {json_daily}')

        json_challenge = pathdir / 'data-challenge.json'
        with json_challenge.open(mode='w', encoding='utf-8') as fp:
            json.dump([c.to_dict() for c in challenge], fp, indent=4, ensure_ascii=False)
        log.debug(f'数据库导出 {json_challenge}')



# 定义Bank对象:
class Bank(Base):
    # 表的名字:
    __tablename__ = 'banks'

    '''表的结构:
        id | catagory | content | options | answer | note
        序号 | 题型 | 题干 | 选项 | 答案 | 注释
    '''
    id = Column(Integer,primary_key=True)
    catagory = Column(String(128)) # radio check blank challenge
    content = Column(Text, default='content')
    # options的处理，每个item用 | 分隔开，若item本身包含 | ，则replace为下划线(_)，一般不不存在 | 。
    options = Column(Text, nullable=True)
    answer = Column(String(256), nullable=True)
    note = Column(Text, nullable=True)

    def __init__(self, catagory:str, content:str, options:list, answer:str=None, note:str=None):
        self.catagory = catagory # 挑战答题-挑战题, 每日答题-单选题、多选题、填空题
        self.content = content or 'default content'
        if not options:
            self.options = ''
        elif isinstance(options, int):
            self.options = str(options)
        elif isinstance(options, list):
            self.options = "|".join([str(x) for x in options]) or ''
        else:
            pass
        self.answer = answer.upper() or ''
        self.note = note or ''

    def __repr__(self):
        return f'<Bank {self.content}>'

    def __str__(self):
        return f'{self.catagory} {self.content} {self.options} {self.answer} {self.note}'

    def to_dict(self):
        dict_bank = {
            "id": self.id,
            "catagory": self.catagory,
            "content": self.content,
            "options": self.options,
            "answer": self.answer,
            "note": self.note
        }
        return dict_bank

    @classmethod
    def from_dict(cls, item):
        return cls( catagory=item['catagory'],
                    content=item['content'],
                    options=item['options'].split('|'),
                    answer=item['answer'],
                    note=item['note'])

db = Model()

if __name__ == "__main__":
    db = Model()
    # db.load(Path('./xuexi/sources/exports/data-challenge.json'))
    # db.load(Path('./xuexi/sources/exports/data-daily.json'))
    db.dump()

