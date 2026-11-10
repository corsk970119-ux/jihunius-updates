#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""소재관리 — 독립 현장 확인판 0.4.1 / Python 3.8+ / 추가 설치 없음.

Windows에서 이 파일을 더블클릭. 지후니우스와 별도 실행/별도 저장.
1~9호기 유효 4자리 작업번호 변경 = 가공/양품 +1 (3999, 9012, 9020, 9999 제외).
9020을 거친 같은 번호 복귀는 +0. 불량 버튼은 양품 -1, 불량 +1.
소재교체 = 기존 가공/불량 기록 저장, 새 소재 1봉 출고, 가공/불량 모두 0부터 시작.
중도교체 = 기존 봉을 중도파기 1봉으로 별도 기록. 파기 봉도 소모 1봉이며 봉당 양품·불량 평균에 포함.
보관 재고: Ø10 Z급, Ø10 B급, Ø12, Ø14. 이미 기계에 넣은 소재는 보관 재고에서 제외.
시작 시 보이는 번호는 기준값이며 최초 소재는 '중간 시작'이다.
가공 수는 관측한 번호 변경 횟수이며, 불량 수는 수동으로 입력한 별도 기록이다.
사이트 카운터(part_count)는 읽거나 기록하지 않으며, 프로그램 번호만으로 수량을 판단한다.
데이터: %LOCALAPPDATA%\\MaterialCounter\\counter.sqlite3 (이 PC 전용).
닫기 시 최소화를 선택하면 계속 수집. 완전 종료/PC 절전 중 수집 안 됨.
연결 단절/재실행 후에는 누락 가능 표시와 함께 새 기준을 잡는다.
호기에서 우클릭하면 마지막 수동 입력을 취소할 수 있다.
개발 점검: --data-dir PATH로 별도 데이터 폴더 지정 가능.
"""

import argparse
import calendar
import csv
import ctypes
from contextlib import contextmanager
from datetime import datetime, timedelta
from http.client import HTTPConnection
from ipaddress import IPv4Address
import json
import os
from pathlib import Path
import queue
import re
import sqlite3
import sys
import threading
import time
from urllib.parse import urlencode
import uuid

VERSION = '0.4.1'
HOST = '192.168.0.245'
INTERVAL = 3.0
TIMEOUT = 4.0
FRESH_SECONDS = 9.0
DISPLAY_STALE_SECONDS = 30.0
GAP_SECONDS = 15.0
EXCLUDED_PROGRAMS = frozenset(('3999', '9012', '9020', '9999'))
MACHINES = tuple(range(1, 10))
MATERIAL_TYPES = {'10Z': 'Ø10 Z급', '10B': 'Ø10 B급', '12': 'Ø12', '14': 'Ø14'}
DEFAULT_MATERIAL_TYPE = '10B'
MOVEMENT_NAMES = {'initial':'최초 재고', 'register':'최초 재고', 'receive':'입고', 'adjust':'실사 조정',
                  'consume':'소재 사용', 'return':'교체 취소', 'cancel':'교체 취소',
                  'reversal':'교체 취소', 'reverse':'교체 취소'}
PALETTE = dict(bg='#060b16', card='#060b16', field='#050a14', text='#eaf0fc',
               muted='#9fb2d6', line='#2e333d', blue='#2a66f2', selected='#1d3f86',
               green='#72d9ad', yellow='#f1c676', red='#ed929c', danger='#b91c1c', danger_active='#991b1b')
STATES = {'RUN': '가공 중', 'WAIT': '대기', 'HOLD': '일시정지',
          'ALARM': '알람', 'STOP': '정지', 'OFF': '전원 꺼짐'}
EVENT_NAMES = {'baseline': '시작 기준', 'program': '번호 변경 +1', 'state': '상태 변경',
               'reference': '사이트 카운터 변경', 'defect': '불량 +1', 'rotate': '소재 교체',
               'rotate_early':'소재 중도교체',
               'switch14':'14파이 전환 · 원소재 보관', 'return_original':'원소재 복귀 · 14파이 보관',
               'switch_undo':'소재 전환 취소', 'mass_pause':'양산품 전환 · 집계 보관', 'mass_resume':'양산품 종료 · 집계 재개',
               'gap': '수집 중단', 'resume': '재연결 기준', 'defect_undo': '불량 입력 취소',
               'rotate_undo': '소재 교체 취소', 'material_type':'소재 종류 지정', 'next_type':'다음 소재 예약',
               'program_skip':'집계 제외 번호', 'count_baseline':'유효 번호 기준', 'program_return':'같은 작업번호 복귀'}


def countable_program(program):
    """Program identity is already normalized by parse_sample (e.g. 0123 -> 123)."""
    return bool(re.fullmatch(r'[1-9][0-9]{3}', program)) and program not in EXCLUDED_PROGRAMS


def material_label(type_id):
    return MATERIAL_TYPES.get(type_id, '미지정')


def average_text(value):
    return '—' if value is None else '{:,.1f}'.format(value)


def date_text(ts, short=False):
    if ts is None:
        return '—'
    return datetime.fromtimestamp(ts).strftime('%m-%d %H:%M:%S' if short else '%Y-%m-%d %H:%M:%S')


def parse_sample(result):
    if not isinstance(result, dict) or result.get('message') != 'success':
        raise ValueError('머신 응답이 정상적이지 않습니다.')
    match = re.fullmatch(r'machine\s*([0-9]+)', str(result.get('machine_name', '')).strip(), re.I)
    if not match or int(match.group(1)) not in MACHINES:
        raise ValueError('1~9호기 이름을 확인할 수 없습니다.')
    value = result.get('program_number')
    if isinstance(value, bool) or not isinstance(value, (str, int)):
        raise ValueError('작업번호가 비어 있습니다.')
    number = str(value).strip()
    if not re.fullmatch(r'[0-9]{1,8}', number) or int(number) == 0:
        raise ValueError('작업번호가 비어 있거나 유효하지 않습니다.')
    state = str(result.get('state', '')).strip().upper()
    if state not in STATES:
        raise ValueError('설비 상태를 확인할 수 없습니다.')
    # Keep the legacy field empty for database/client compatibility. Site counters
    # are neither evidence of production nor a reason to refresh the history.
    return dict(machine=int(match.group(1)), program=str(int(number)), state=state, part_count='')


def request_json(endpoint, fields, host=HOST, port=None):
    allowed = {'monitoring_ajax_setting.php': 'loadIPlist',
               'monitoring_ajax_this_machine.php': 'callUpdateMachineOne'}
    if allowed.get(endpoint) != fields.get('ajax_selector'):
        raise ValueError('허용되지 않은 요청입니다.')
    connection = HTTPConnection(host, port=port, timeout=TIMEOUT)
    try:
        connection.request('POST', '/' + endpoint, body=urlencode(fields).encode('ascii'),
                           headers={'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
                                    'Accept': 'application/json', 'Cache-Control': 'no-cache'})
        response = connection.getresponse()
        if response.status != 200:
            raise ValueError('서버 응답 오류: HTTP {}'.format(response.status))
        raw = response.read(131073)
        if len(raw) > 131072:
            raise ValueError('응답 크기가 올바르지 않습니다.')
        result = json.loads(raw.decode('utf-8-sig'))
        if not isinstance(result, dict):
            raise ValueError('응답 형식이 올바르지 않습니다.')
        return result
    finally:
        connection.close()


class InstanceAlreadyRunning(RuntimeError):
    def __init__(self,path):
        self.path=str(path)
        super().__init__('소재카운터가 이미 실행 중입니다. 기존 창에 다시 연결해주세요.')


class InstanceLock:
    """OS가 해제하는 파일 잠금. 종료된 PID 파일 때문에 실행이 막히지 않는다."""
    def __init__(self, path):
        self.file = open(path, 'a+b')
        try:
            # Windows byte locks are mandatory: even reading the sentinel
            # before acquiring the lock can fail with bare EACCES. Locking
            # beyond EOF is supported, so no sentinel I/O is necessary.
            self.file.seek(0)
            if os.name == 'nt':
                import msvcrt
                msvcrt.locking(self.file.fileno(), msvcrt.LK_NBLCK, 1)
            else:
                import fcntl
                fcntl.flock(self.file.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
        except OSError as exc:
            self.file.close()
            import errno
            if exc.errno in (errno.EACCES,errno.EAGAIN,errno.EDEADLK):
                raise InstanceAlreadyRunning(path) from exc
            raise

    def close(self):
        self.file.close()


class Store:
    """SQLite event history and unused-rod stock; mutations commit as one transaction."""
    def __init__(self, path):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.db = sqlite3.connect(str(self.path), timeout=3)
        self.db.row_factory = sqlite3.Row
        self.live = set()
        self.migration_backup = None
        try:
            version = self.db.execute('PRAGMA user_version').fetchone()[0]
            if version not in (0, 1, 2, 3, 4, 5, 6):
                raise RuntimeError('더 새로운 프로그램으로 만든 데이터입니다. 최신 프로그램을 사용해주세요.')
            self.db.execute('PRAGMA foreign_keys=ON')
            if version < 6:
                old_tables = self.db.execute("SELECT name FROM sqlite_master WHERE type='table' AND name IN ('materials','machines','events')").fetchall()
                if old_tables:
                    backup = Path(str(self.path) + '.pre-v6.bak')
                    if not backup.exists():
                        temporary = Path(str(backup) + '.' + uuid.uuid4().hex + '.tmp')
                        target = None
                        try:
                            target = sqlite3.connect(str(temporary))
                            self.db.backup(target)
                            target.close()
                            target = None
                            os.replace(str(temporary), str(backup))
                        finally:
                            if target is not None:
                                target.close()
                            if temporary.exists():
                                temporary.unlink()
                    self.migration_backup = backup
                self._migrate()
            self.db.execute('PRAGMA journal_mode=WAL')
            self.db.execute('PRAGMA synchronous=FULL')
            with self.transaction():
                self.db.executemany('INSERT OR IGNORE INTO machines(machine) VALUES(?)', [(n,) for n in MACHINES])
                self.db.execute('CREATE INDEX IF NOT EXISTS event_machine_at_idx ON events(machine,at)')
                self.db.execute('CREATE INDEX IF NOT EXISTS material_ended_idx ON materials(ended,id)')
        except Exception:
            self.db.close()
            raise

    def _migrate(self):
        # Avoid executescript: its implicit COMMIT would break migration atomicity.
        statements = [
            '''CREATE TABLE IF NOT EXISTS materials(
              id INTEGER PRIMARY KEY, machine INTEGER NOT NULL, started REAL NOT NULL,
              ended REAL, start_program TEXT NOT NULL, end_program TEXT,
              partial INTEGER NOT NULL DEFAULT 0, gap INTEGER NOT NULL DEFAULT 0, merged_into INTEGER)''',
            '''CREATE TABLE IF NOT EXISTS machines(
              machine INTEGER PRIMARY KEY, program TEXT NOT NULL DEFAULT '', state TEXT NOT NULL DEFAULT '',
              part_count TEXT NOT NULL DEFAULT '', last_seen REAL, active_material INTEGER REFERENCES materials(id))''',
            '''CREATE TABLE IF NOT EXISTS events(
              id INTEGER PRIMARY KEY, machine INTEGER NOT NULL, material_id INTEGER REFERENCES materials(id),
              at REAL NOT NULL, kind TEXT NOT NULL, previous TEXT NOT NULL DEFAULT '',
              program TEXT NOT NULL DEFAULT '', state TEXT NOT NULL DEFAULT '', part_count TEXT NOT NULL DEFAULT '',
              auto_delta INTEGER NOT NULL DEFAULT 0, defect_delta INTEGER NOT NULL DEFAULT 0,
              note TEXT NOT NULL DEFAULT '', next_material INTEGER, undone INTEGER NOT NULL DEFAULT 0)''',
            '''CREATE TABLE IF NOT EXISTS stock(
              type_id TEXT PRIMARY KEY, quantity INTEGER CHECK(quantity IS NULL OR quantity >= 0))''',
            '''CREATE TABLE IF NOT EXISTS stock_movements(
              id INTEGER PRIMARY KEY, at REAL NOT NULL, type_id TEXT NOT NULL REFERENCES stock(type_id),
              kind TEXT NOT NULL CHECK(kind IN ('register','receive','adjust','consume','reverse')),
              delta INTEGER NOT NULL, note TEXT NOT NULL DEFAULT '',
              material_id INTEGER REFERENCES materials(id), event_id INTEGER REFERENCES events(id),
              reverses INTEGER UNIQUE REFERENCES stock_movements(id))''',
            'CREATE INDEX IF NOT EXISTS event_material_idx ON events(material_id,id)',
            'CREATE INDEX IF NOT EXISTS event_machine_idx ON events(machine,id)',
            'CREATE INDEX IF NOT EXISTS event_at_idx ON events(at)',
            'CREATE INDEX IF NOT EXISTS stock_movement_at_idx ON stock_movements(at)',
            'CREATE UNIQUE INDEX IF NOT EXISTS stock_consume_event_idx ON stock_movements(event_id) WHERE kind="consume"'
        ]
        with self.transaction():
            for sql in statements:
                self.db.execute(sql)
            for table, column in (('materials', 'material_type'), ('machines', 'initial_type'), ('machines', 'next_type')):
                columns = {r['name'] for r in self.db.execute('PRAGMA table_info({})'.format(table))}
                if column not in columns:
                    self.db.execute('ALTER TABLE {} ADD COLUMN {} TEXT REFERENCES stock(type_id)'.format(table, column))
            self.db.executemany('INSERT OR IGNORE INTO stock(type_id,quantity) VALUES(?,NULL)', [(key,) for key in MATERIAL_TYPES])
            columns = {r['name'] for r in self.db.execute('PRAGMA table_info(materials)')}
            if 'early_end' not in columns:
                self.db.execute('ALTER TABLE materials ADD COLUMN early_end INTEGER NOT NULL DEFAULT 0 CHECK(early_end IN (0,1))')
            self.db.execute('''CREATE TABLE IF NOT EXISTS parked_materials(
              machine INTEGER PRIMARY KEY REFERENCES machines(machine),
              material_id INTEGER NOT NULL UNIQUE REFERENCES materials(id),
              role TEXT NOT NULL CHECK(role IN ('original','14')),
              next_type TEXT REFERENCES stock(type_id))''')
            self.db.execute('''CREATE TABLE IF NOT EXISTS material_switch_actions(
              event_id INTEGER PRIMARY KEY REFERENCES events(id),
              held_before INTEGER REFERENCES materials(id),role_before TEXT,
              held_next_before TEXT REFERENCES stock(type_id),active_next_before TEXT REFERENCES stock(type_id),
              created_new INTEGER NOT NULL CHECK(created_new IN (0,1)))''')
            columns = {r['name'] for r in self.db.execute('PRAGMA table_info(machines)')}
            if 'mass_mode' not in columns:
                self.db.execute('ALTER TABLE machines ADD COLUMN mass_mode INTEGER NOT NULL DEFAULT 0 CHECK(mass_mode IN (0,1))')
            if 'count_program' not in columns:
                self.db.execute("ALTER TABLE machines ADD COLUMN count_program TEXT NOT NULL DEFAULT ''")
                self.db.execute('UPDATE machines SET count_program=program')
                # Recover a known 9020 entry once on upgrade, without revising
                # recorded totals or scanning history during normal collection.
                for row in self.db.execute("SELECT machine FROM machines WHERE program='9020'").fetchall():
                    last = self.db.execute("""SELECT program,previous FROM events WHERE machine=?
                      AND kind IN ('program','program_skip') ORDER BY id DESC LIMIT 1""", (row['machine'],)).fetchone()
                    if last and last['program']=='9020':
                        self.db.execute('UPDATE machines SET count_program=? WHERE machine=?',
                                        (last['previous'], row['machine']))
            self.db.execute('DROP INDEX IF EXISTS switch_machine_idx')
            self.db.execute("""CREATE INDEX switch_machine_idx ON events(machine,id)
              WHERE kind IN ('switch14','return_original','switch_undo','mass_pause','mass_resume')""")
            self.db.execute("""CREATE INDEX IF NOT EXISTS mass_machine_idx ON events(machine,id)
              WHERE kind IN ('mass_pause','mass_resume')""")
            self.db.execute('PRAGMA user_version=6')

    def reset_records(self, reset_stock=False, at=None):
        """Back up first, then atomically start a new recording period.

        The caller pauses collection and discards samples from the old period.
        Keeping stock preserves the actual remaining quantity; it never reverses
        past consumption. The next observation starts a partial-rod baseline.
        """
        if type(reset_stock) is not bool:
            raise ValueError('재고 초기화 여부가 올바르지 않습니다.')
        at = self._at(at)
        if self.db.in_transaction:
            raise RuntimeError('저장 중인 작업이 끝난 뒤 기록을 초기화해주세요.')

        backup = self.backup_records(at)
        self._reset_data(reset_stock, at)
        self.live.clear()
        return backup

    def backup_records(self, at=None):
        at = self._at(at)
        backup_dir = self.path.parent / 'backups'
        backup_dir.mkdir(parents=True, exist_ok=True)
        backup = backup_dir / ('counter_before_reset_' +
                               datetime.fromtimestamp(at).strftime('%Y%m%d_%H%M%S') +
                               '_' + uuid.uuid4().hex + '.sqlite3')
        temporary = backup.with_suffix('.tmp')
        target = None
        try:
            target = sqlite3.connect(str(temporary))
            self.db.backup(target)
            if target.execute('PRAGMA quick_check').fetchone()[0] != 'ok':
                raise sqlite3.DatabaseError('초기화 전 백업을 검증하지 못했습니다.')
            target.close()
            target = None
            os.replace(str(temporary), str(backup))
        finally:
            if target is not None:
                target.close()
            if temporary.exists():
                temporary.unlink()

        return backup

    def _reset_data(self, reset_stock, at):
        with self.transaction():
            if reset_stock:
                self.db.execute('UPDATE machines SET initial_type=NULL,next_type=NULL')
            else:
                # A machine may have changed material since its initial setting.
                self.db.execute('''UPDATE machines SET initial_type=COALESCE(
                  (SELECT material_type FROM materials WHERE id=machines.active_material),initial_type)''')
            self.db.execute("""UPDATE machines SET program='',count_program='',state='',part_count='',
              last_seen=NULL,active_material=NULL,mass_mode=0""")
            self.db.execute('UPDATE stock_movements SET reverses=NULL')
            self.db.execute('DELETE FROM stock_movements')
            self.db.execute('DELETE FROM parked_materials')
            self.db.execute('DELETE FROM material_switch_actions')
            self.db.execute('DELETE FROM events')
            self.db.execute('DELETE FROM materials')
            if reset_stock:
                self.db.execute('UPDATE stock SET quantity=NULL')
            else:
                for row in self.db.execute('SELECT type_id,quantity FROM stock WHERE quantity IS NOT NULL').fetchall():
                    self._movement(row['type_id'], at, 'register', row['quantity'],
                                   '기록 초기화 후 재고 기준')
    @contextmanager
    def transaction(self):
        nested = self.db.in_transaction
        marker = 'sp_' + uuid.uuid4().hex
        self.db.execute('SAVEPOINT ' + marker if nested else 'BEGIN IMMEDIATE')
        try:
            yield
            self.db.execute('RELEASE SAVEPOINT ' + marker) if nested else self.db.commit()
        except BaseException:
            if nested:
                self.db.execute('ROLLBACK TO SAVEPOINT ' + marker)
                self.db.execute('RELEASE SAVEPOINT ' + marker)
            else:
                self.db.rollback()
            raise

    def close(self):
        self.db.close()

    def _machine(self, machine):
        if type(machine) is not int or machine not in MACHINES:
            raise ValueError('호기가 올바르지 않습니다.')
        return dict(self.db.execute('SELECT * FROM machines WHERE machine=?', (machine,)).fetchone())

    def _type(self, type_id):
        if not isinstance(type_id, str) or type_id not in MATERIAL_TYPES:
            raise ValueError('소재 종류를 선택해주세요.')
        return type_id

    def _quantity(self, quantity, positive=False):
        if type(quantity) is not int or quantity < (1 if positive else 0):
            raise ValueError('수량은 {} 정수로 입력해주세요.'.format('1 이상의' if positive else '0 이상의'))
        return quantity

    def _at(self, at):
        value = time.time() if at is None else at
        if isinstance(value, bool) or not isinstance(value, (int, float)) or not -float('inf') < value < float('inf'):
            raise ValueError('기록 시각이 올바르지 않습니다.')
        return value

    def _event(self, row, at, kind, previous='', auto=0, defects=0, note='', next_material=None):
        return self.db.execute('''INSERT INTO events(machine,material_id,at,kind,previous,program,state,
          part_count,auto_delta,defect_delta,note,next_material) VALUES(?,?,?,?,?,?,?,?,?,?,?,?)''',
          (row['machine'], row['active_material'], at, kind, previous, row['program'], row['state'],
           '', auto, defects, note, next_material)).lastrowid

    def _movement(self, type_id, at, kind, delta, note='', material_id=None, event_id=None, reverses=None):
        return self.db.execute('''INSERT INTO stock_movements(at,type_id,kind,delta,note,material_id,event_id,reverses)
          VALUES(?,?,?,?,?,?,?,?)''', (at, type_id, kind, delta, str(note), material_id, event_id, reverses)).lastrowid

    def inventory(self):
        values = {r['type_id']: r['quantity'] for r in self.db.execute('SELECT * FROM stock')}
        return [dict(type_id=key, label=label, quantity=values.get(key), registered=values.get(key) is not None)
                for key, label in MATERIAL_TYPES.items()]

    def register_stock(self, type_id, qty, at=None):
        type_id, qty, at = self._type(type_id), self._quantity(qty), self._at(at)
        with self.transaction():
            changed = self.db.execute('UPDATE stock SET quantity=? WHERE type_id=? AND quantity IS NULL', (qty, type_id))
            if changed.rowcount != 1:
                raise ValueError('이미 등록된 재고입니다. 입고 또는 실사 조정을 사용해주세요.')
            return self._movement(type_id, at, 'register', qty, '보관 중인 미사용 소재의 최초 재고 등록')

    def receive_stock(self, type_id, qty, at=None, note=''):
        type_id, qty, at = self._type(type_id), self._quantity(qty, positive=True), self._at(at)
        with self.transaction():
            changed = self.db.execute('UPDATE stock SET quantity=quantity+? WHERE type_id=? AND quantity IS NOT NULL', (qty, type_id))
            if changed.rowcount != 1:
                raise ValueError('이 소재의 최초 보관 재고를 먼저 등록해주세요.')
            return self._movement(type_id, at, 'receive', qty, note)

    def adjust_stock(self, type_id, new_qty, reason, at=None):
        type_id, new_qty, at = self._type(type_id), self._quantity(new_qty), self._at(at)
        if not isinstance(reason, str) or not reason.strip():
            raise ValueError('실사 조정 사유를 입력해주세요.')
        with self.transaction():
            old = self.db.execute('SELECT quantity FROM stock WHERE type_id=?', (type_id,)).fetchone()[0]
            if old is None:
                raise ValueError('이 소재의 최초 보관 재고를 먼저 등록해주세요.')
            self.db.execute('UPDATE stock SET quantity=? WHERE type_id=?', (new_qty, type_id))
            return self._movement(type_id, at, 'adjust', new_qty-old, reason.strip())

    def movements(self, limit=200):
        query = '''SELECT s.*,m.machine FROM stock_movements s LEFT JOIN materials m ON m.id=s.material_id ORDER BY s.id DESC'''
        params = []
        if limit is not None:
            query += ' LIMIT ?'
            params.append(limit)
        return [dict(r) for r in self.db.execute(query, params)]

    def assign_material(self, machine, type_id, at=None):
        type_id, at = self._type(type_id), self._at(at)
        with self.transaction():
            row = self._machine(machine)
            self._require_custom_mode(row)
            if row['active_material'] is None:
                old_type = row['initial_type']
            else:
                old_type = self.db.execute('SELECT material_type FROM materials WHERE id=?', (row['active_material'],)).fetchone()[0]
            if old_type is not None:
                if old_type == type_id:
                    return
                raise ValueError('현재 소재 종류는 이미 지정되었습니다. 다음 교체 소재를 선택해주세요.')
            if row['active_material'] is None:
                self.db.execute('UPDATE machines SET initial_type=? WHERE machine=?', (type_id, machine))
            else:
                self.db.execute('UPDATE materials SET material_type=? WHERE id=?', (type_id, row['active_material']))
            self.db.execute('UPDATE machines SET next_type=COALESCE(next_type,?) WHERE machine=?', (type_id, machine))
            self._event(row, at, 'material_type', note='현재 장착 소재: {} · 보관 재고 차감 없음'.format(MATERIAL_TYPES[type_id]))

    def set_next_type(self, machine, type_id, at=None):
        type_id, at = self._type(type_id), self._at(at)
        with self.transaction():
            row = self._machine(machine)
            self._require_custom_mode(row)
            self._validate_parked_replacement(machine,type_id)
            if row['next_type'] == type_id:
                return
            self.db.execute('UPDATE machines SET next_type=? WHERE machine=?', (type_id, machine))
            self._event(row, at, 'next_type', note='다음 교체 소재: {}'.format(MATERIAL_TYPES[type_id]))

    def observe(self, sample, at=None):
        at = self._at(at)
        n = sample['machine']
        old = self._machine(n)
        if old['last_seen'] is not None and at < old['last_seen']:
            self.live.discard(n)
        continuous = n in self.live and old['last_seen'] is not None and 0 <= at-old['last_seen'] <= GAP_SECONDS
        row = dict(old, program=sample['program'], state=sample['state'], part_count='')
        eligible = countable_program(sample['program'])
        same_return = old['program']=='9020' and sample['program']==old['count_program']
        # Keep the visible program and counting reference separate. Only 9020 is
        # transparent; 3999/9012/9999 still delimit legitimate same-number rework.
        count_program = old['count_program'] if sample['program']=='9020' else sample['program']
        changed = True
        with self.transaction():
            if old['mass_mode']:
                # Keep a live baseline for safe resume, without storing every mass job.
                changed = any(old[key] != sample[key] for key in ('program','state'))
            elif old['active_material'] is None:
                row['active_material'] = self.db.execute('''INSERT INTO materials(machine,started,start_program,partial,material_type)
                  VALUES(?,?,?,1,?)''', (n, at, sample['program'], old['initial_type'])).lastrowid
                self._event(row, at, 'baseline', note='첫 관측 번호는 기준값입니다. 이후 집계 대상 4자리로 바뀔 때 +1, 3999·9012·9020·9999 및 9020 이후 같은 번호 복귀는 제외합니다.')
            elif not continuous:
                self.db.execute('UPDATE materials SET gap=1 WHERE id=?', (old['active_material'],))
                self._event(row, at, 'resume', previous=old['program'],
                            note='수집 공백 이후 기준 재설정. 공백 중 가공 횟수는 추정하지 않습니다.')
            elif old['program'] != sample['program']:
                counted = eligible and not same_return
                note = ('9020 이후 같은 작업번호 복귀 · 가공 수 유지.' if same_return else
                        '유효 4자리 번호로 변경 +1 · 9020 외 다른 번호를 거친 동일 작업 재가공도 포함.' if counted else
                        '3999·9012·9020·9999 또는 4자리 이외 번호. 상태와 이력만 갱신합니다.')
                self._event(row, at, 'program' if counted else 'program_skip', previous=old['program'],
                            auto=1 if counted else 0, note=note)
            elif old['state'] != sample['state']:
                self._event(row, at, 'state')
            else:
                changed = False
            self.db.execute('''UPDATE machines SET program=?,state=?,part_count=?,last_seen=?,active_material=?,count_program=?
              WHERE machine=?''', (sample['program'], sample['state'], '', at, row['active_material'], count_program, n))
        self.live.add(n)
        return changed

    def disconnected(self, machine, at=None, reason='연결 중단'):
        at = self._at(at)
        if machine not in self.live:
            return
        row = self._machine(machine)
        with self.transaction():
            if row['active_material'] is not None and not row['mass_mode']:
                self.db.execute('UPDATE materials SET gap=1 WHERE id=?', (row['active_material'],))
                self._event(row, at, 'gap', note=str(reason)[:300])
        self.live.discard(machine)

    def defect(self, machine, at=None):
        at = self._at(at)
        with self.transaction():
            row = self.snapshot(machine)
            if row['active_material'] is None:
                raise ValueError('이 호기의 첫 데이터를 받은 뒤 사용할 수 있습니다.')
            if row['good']<=0:
                raise ValueError('불량으로 바꿀 양품이 없습니다. 가공 수집 후 입력해주세요.')
            self._event(row, at, 'defect', defects=1, note='기존 양품 -1 · 불량 +1 · 전체 가공 횟수는 유지')

    def rotate(self, machine, at=None, early=False, manual=False):
        at = self._at(at)
        if type(early) is not bool:raise ValueError('교체 구분이 올바르지 않습니다.')
        with self.transaction():
            row = self._machine(machine)
            self._require_switch_sample(row, machine, at, manual)
            if row['active_material'] is None:
                raise ValueError('이 호기의 첫 데이터를 받은 뒤 사용할 수 있습니다.')
            current = self.db.execute('SELECT * FROM materials WHERE id=?', (row['active_material'],)).fetchone()
            type_id = row['next_type'] or current['material_type']
            self._type(type_id)
            self._validate_parked_replacement(machine,type_id)
            stock = self.db.execute('SELECT quantity FROM stock WHERE type_id=?', (type_id,)).fetchone()[0]
            if stock is None:
                raise ValueError('{} 최초 보관 재고를 먼저 등록해주세요.'.format(MATERIAL_TYPES[type_id]))
            if stock < 1:
                raise ValueError('{} 보관 재고가 없습니다. 입고 또는 실사 조정을 확인해주세요.'.format(MATERIAL_TYPES[type_id]))
            changed = self.db.execute('UPDATE stock SET quantity=quantity-1 WHERE type_id=? AND quantity>=1', (type_id,))
            if changed.rowcount != 1:
                raise ValueError('보관 재고가 부족합니다.')
            self.db.execute('UPDATE materials SET ended=?,end_program=?,early_end=? WHERE id=?', (at, row['program'], int(early), row['active_material']))
            new = self.db.execute('INSERT INTO materials(machine,started,start_program,material_type) VALUES(?,?,?,?)',
                                  (machine, at, row['program'], type_id)).lastrowid
            label = '중도교체' if early else '소재교체'
            action_id = self._event(row, at, 'rotate_early' if early else 'rotate', next_material=new,
                                    note='{} · {} 보관 재고 1봉 사용{}'.format(label,MATERIAL_TYPES[type_id], ' · 이전 봉 중도파기 1봉, 봉당 양품·불량 평균에 포함' if early else ''))
            self._movement(type_id, at, 'consume', -1, '{}호기 {}'.format(machine,label), new, action_id)
            self.db.execute('UPDATE machines SET active_material=?,next_type=? WHERE machine=?', (new, type_id, machine))
            if manual:self._manual_switch_boundary(row,at)
        return row['active_material']

    def _validate_parked_replacement(self,machine,type_id):
        held=self.db.execute('SELECT role FROM parked_materials WHERE machine=?',(machine,)).fetchone()
        if not held:return
        if held['role']=='original' and type_id!='14':
            raise ValueError('원소재가 보관 중입니다. 원소재로 복귀한 뒤 다음 소재를 선택해주세요.')
        if held['role']=='14' and type_id=='14':
            raise ValueError('보관한 14파이가 있습니다. 14파이 교체 버튼으로 전환한 뒤 새 봉 교체를 진행해주세요.')

    def switch_revision(self,machine):
        return self.db.execute("""SELECT MAX(id) FROM events WHERE machine=?
          AND kind IN ('switch14','return_original','switch_undo','mass_pause','mass_resume')""",(machine,)).fetchone()[0]

    @staticmethod
    def _require_custom_mode(row):
        if row['mass_mode']:
            raise ValueError('양산품 모드입니다. 집계 재개 후 입력해주세요.')

    def _require_switch_sample(self,row,machine,at,manual):
        if type(manual) is not bool:raise ValueError('수동 입력 구분이 올바르지 않습니다.')
        if manual:return
        if machine not in self.live or row['last_seen'] is None or not 0<=at-row['last_seen']<=FRESH_SECONDS:
            raise ValueError('최신 머신 상태를 읽지 못했습니다. 연결 후 다시 눌러주세요.')
        if row['state'] not in ('RUN','WAIT','HOLD','ALARM','STOP'):
            raise ValueError('머신 상태를 확인하지 못했습니다. 연결 상태를 확인해주세요.')

    def _manual_switch_boundary(self,row,at):
        # No telemetry means an explicit operator boundary, never an inferred count.
        # Include the ended rod plus both currently open/parked rods.
        self.db.execute('UPDATE materials SET gap=1 WHERE machine=? AND (id=? OR ended IS NULL)',
                        (row['machine'],row['active_material']))
        self._event(row,at,'gap',note='수동 소재 입력 경계 · 실시간 설비 확인 없이 반영 · 다음 관측은 새 기준으로 시작')
        self.live.discard(row['machine'])

    def toggle_mass_mode(self,machine,at=None,manual=False):
        """Keep both rods and their totals intact; resume from the fresh checkpoint."""
        at=self._at(at)
        with self.transaction():
            row=self._machine(machine)
            self._require_switch_sample(row,machine,at,manual)
            if row['active_material'] is None:
                raise ValueError('이 호기의 첫 데이터를 받은 뒤 사용할 수 있습니다.')
            paused=not row['mass_mode']
            self.db.execute('UPDATE machines SET mass_mode=? WHERE machine=?',(int(paused),machine))
            self._event(row,at,'mass_pause' if paused else 'mass_resume',
                note='현재 소재·양품·불량 보관 · 양산품 집계 제외 · 재고 차감 없음' if paused else
                     '보관한 소재의 집계 재개 · 현재 번호를 기준으로 이후 변경부터 집계 · 재고 차감 없음')
            if manual:self._manual_switch_boundary(row,at)
        return paused

    def switch_14(self,machine,at=None,manual=False):
        """Swap physical rods without ending either; only a new 14 mm rod uses stock."""
        at=self._at(at)
        with self.transaction():
            row=self._machine(machine)
            self._require_switch_sample(row,machine,at,manual)
            current=self.db.execute('SELECT * FROM materials WHERE id=?',(row['active_material'],)).fetchone()
            if current is None or current['material_type'] is None:
                raise ValueError('현재 사용 소재를 지정한 뒤 전환해주세요.')
            if current['ended'] is not None or current['merged_into'] is not None:
                raise ValueError('현재 소재 기록을 확인해주세요.')
            held=self.db.execute('SELECT * FROM parked_materials WHERE machine=?',(machine,)).fetchone()
            returning=bool(held and held['role']=='original')
            if returning and current['material_type']!='14':raise ValueError('임시 소재가 14파이가 아닙니다. 소재 기록을 확인해주세요.')
            if not returning and current['material_type']=='14':raise ValueError('복귀할 원소재가 없습니다. 현재 14파이는 기존 소재교체로 관리해주세요.')
            if held:
                target=self.db.execute('SELECT * FROM materials WHERE id=?',(held['material_id'],)).fetchone()
                if (target is None or target['machine']!=machine or target['ended'] is not None
                        or target['merged_into'] is not None or target['id']==current['id']
                        or (target['material_type']=='14')==returning):
                    raise ValueError('보관 소재 기록을 확인해주세요. 전환하지 않았습니다.')
                new=target['id'];next_type=held['next_type'] or target['material_type']
            else:
                if self.db.execute("UPDATE stock SET quantity=quantity-1 WHERE type_id='14' AND quantity>=1").rowcount!=1:
                    raise ValueError('Ø14 보관 재고가 없습니다. 최초 재고 등록 또는 입고를 확인해주세요.')
                new=self.db.execute('INSERT INTO materials(machine,started,start_program,material_type) VALUES(?,?,?,?)',
                    (machine,at,row['program'],'14')).lastrowid
                next_type='14'
            action=self._event(row,at,'return_original' if returning else 'switch14',next_material=new,
                note='현재 봉 보관 · 기존 봉 누적 집계 재개 · 재고 차감 없음' if held else '원소재 보관 · 새 Ø14 봉 투입 · Ø14 재고 1봉 차감')
            self.db.execute('INSERT INTO material_switch_actions VALUES(?,?,?,?,?,?)',
                (action,held['material_id'] if held else None,held['role'] if held else None,
                 held['next_type'] if held else None,row['next_type'],int(held is None)))
            self.db.execute('DELETE FROM parked_materials WHERE machine=?',(machine,))
            self.db.execute('INSERT INTO parked_materials VALUES(?,?,?,?)',
                (machine,current['id'],'14' if returning else 'original',row['next_type']))
            if held is None:self._movement('14',at,'consume',-1,'{}호기 임시 Ø14 새 봉 투입'.format(machine),new,action)
            self.db.execute('UPDATE machines SET active_material=?,next_type=? WHERE machine=?',(new,next_type,machine))
            if manual:self._manual_switch_boundary(row,at)
        return new

    def _undo_switch(self,row,action,at):
        context=self.db.execute('SELECT * FROM material_switch_actions WHERE event_id=?',(action['id'],)).fetchone()
        held=self.db.execute('SELECT * FROM parked_materials WHERE machine=?',(row['machine'],)).fetchone()
        if not context or not held or held['material_id']!=action['material_id'] or row['active_material']!=action['next_material']:
            raise ValueError('소재 전환 경계가 바뀌어 취소할 수 없습니다.')
        if self.db.execute("""SELECT 1 FROM events WHERE machine=? AND id>? AND
          (auto_delta!=0 OR defect_delta!=0 OR kind IN ('next_type','material_type')) LIMIT 1""",(row['machine'],action['id'])).fetchone():
            raise ValueError('전환 후 가공·입력 기록이 있습니다. 취소 대신 소재 전환 버튼으로 복귀해주세요.')
        consumed=self.db.execute("SELECT * FROM stock_movements WHERE event_id=? AND kind='consume'",(action['id'],)).fetchone()
        if consumed and self.db.execute("SELECT 1 FROM stock_movements WHERE type_id=? AND kind='adjust' AND id>? LIMIT 1",
                (consumed['type_id'],consumed['id'])).fetchone():
            raise ValueError('전환 이후 재고 실사 조정이 있어 취소할 수 없습니다.')
        self.db.execute('DELETE FROM parked_materials WHERE machine=?',(row['machine'],))
        if context['held_before'] is not None:
            self.db.execute('INSERT INTO parked_materials VALUES(?,?,?,?)',
                (row['machine'],context['held_before'],context['role_before'],context['held_next_before']))
        if context['created_new']:
            self.db.execute('UPDATE materials SET merged_into=? WHERE id=?',(action['material_id'],action['next_material']))
        self.db.execute('UPDATE machines SET active_material=?,next_type=? WHERE machine=?',
            (action['material_id'],context['active_next_before'],row['machine']))
        # Undo means the switch was entered by mistake: an unobserved interval
        # may belong to the restored rod, just as with regular replacement undo.
        gap=int(self.db.execute("SELECT 1 FROM events WHERE machine=? AND id>? AND kind IN ('gap','resume') LIMIT 1",
            (row['machine'],action['id'])).fetchone() is not None)
        self.db.execute('UPDATE materials SET gap=MAX(gap,?) WHERE id=?',(gap,action['material_id']))
        event=self._event(dict(row,active_material=action['material_id']),at,'switch_undo',note='소재 전환 #{} 취소'.format(action['id']))
        if consumed:
            self.db.execute('UPDATE stock SET quantity=quantity+1 WHERE type_id=?',(consumed['type_id'],))
            self._movement(consumed['type_id'],at,'reverse',1,'소재 전환 취소',action['next_material'],event,consumed['id'])

    def undo_label(self, machine):
        self._machine(machine)
        row = self.db.execute("""SELECT kind FROM events WHERE machine=?
          AND kind IN ('rotate','rotate_early','defect','switch14','return_original') AND undone=0
          AND id>COALESCE((SELECT MAX(id) FROM events WHERE machine=? AND kind IN ('mass_pause','mass_resume')),0)
          ORDER BY id DESC LIMIT 1""", (machine,machine)).fetchone()
        return {'rotate': '마지막 소재교체 취소', 'rotate_early':'마지막 중도교체 취소', 'defect': '마지막 불량 +1 취소',
                'switch14':'마지막 14파이 전환 취소','return_original':'마지막 원소재 복귀 취소'}.get(row['kind'], '') if row else ''

    def undo(self, machine, at=None):
        at = self._at(at)
        with self.transaction():
            row = self._machine(machine)
            action = self.db.execute("SELECT * FROM events WHERE machine=? AND kind IN ('rotate','rotate_early','defect','switch14','return_original') AND undone=0 ORDER BY id DESC LIMIT 1", (machine,)).fetchone()
            if not action:
                raise ValueError('취소할 수동 입력이 없습니다.')
            if self.db.execute("SELECT 1 FROM events WHERE machine=? AND id>? AND kind IN ('mass_pause','mass_resume') LIMIT 1",(machine,action['id'])).fetchone():
                raise ValueError('양산품 모드 전환 이전의 입력은 취소할 수 없습니다. 현재 소재 기록을 확인해주세요.')
            if action['kind'] in ('switch14','return_original'):
                self._undo_switch(row,action,at)
            elif action['kind'] == 'defect':
                correction = dict(row, active_material=action['material_id'])
                self._event(correction, at, 'defect_undo', defects=-action['defect_delta'], note='입력 #{} 취소'.format(action['id']))
            else:
                current, previous = row['active_material'], action['material_id']
                if current != action['next_material']:
                    raise ValueError('이전 소재 경계가 변경되어 취소할 수 없습니다.')
                consumed = self.db.execute("SELECT * FROM stock_movements WHERE event_id=? AND kind='consume'", (action['id'],)).fetchone()
                if consumed is not None and self.db.execute(
                        "SELECT id FROM stock_movements WHERE type_id=? AND kind='adjust' AND id>? LIMIT 1",
                        (consumed['type_id'], consumed['id'])).fetchone():
                    raise ValueError('이 소재교체 이후 같은 종류의 재고 실사 조정이 있어 취소할 수 없습니다. 재고와 소재 이력을 확인해주세요.')
                gap = self.db.execute('SELECT gap FROM materials WHERE id=?', (current,)).fetchone()[0]
                self.db.execute('UPDATE materials SET ended=NULL,end_program=NULL,early_end=0,gap=MAX(gap,?) WHERE id=?', (gap, previous))
                self.db.execute('UPDATE materials SET merged_into=? WHERE id=?', (previous, current))
                self.db.execute('UPDATE events SET material_id=? WHERE material_id=?', (previous, current))
                self.db.execute('UPDATE machines SET active_material=? WHERE machine=?', (previous, machine))
                undo_id = self._event(dict(row, active_material=previous), at, 'rotate_undo', note='입력 #{} 취소 · 이후 집계 병합'.format(action['id']))
                if consumed is not None:
                    if self.db.execute('SELECT id FROM stock_movements WHERE reverses=?', (consumed['id'],)).fetchone():
                        raise ValueError('이미 재고를 복원한 소재 교체입니다.')
                    self.db.execute('UPDATE stock SET quantity=quantity+1 WHERE type_id=?', (consumed['type_id'],))
                    self._movement(consumed['type_id'], at, 'reverse', 1, '소재 교체 #{} 취소'.format(action['id']),
                                   current, undo_id, consumed['id'])
            self.db.execute('UPDATE events SET undone=1 WHERE id=?', (action['id'],))

    def snapshot(self, machine):
        row = self._machine(machine)
        row.update(auto=0, defects=0, total=0, partial=False, gap=False, started=None, material_type=row['initial_type'])
        if row['active_material'] is not None:
            mat = self.db.execute('SELECT * FROM materials WHERE id=?', (row['active_material'],)).fetchone()
            totals = self.db.execute('SELECT COALESCE(SUM(auto_delta),0),COALESCE(SUM(defect_delta),0) FROM events WHERE material_id=?', (mat['id'],)).fetchone()
            row.update(auto=totals[0], defects=totals[1], total=totals[0], material_type=mat['material_type'],
                       partial=bool(mat['partial']), gap=bool(mat['gap']), started=mat['started'])
        row.update(good=max(0,row['total']-row['defects']),defect_excess=max(0,row['defects']-row['total']))
        held=self.db.execute('''SELECT p.*,m.material_type,m.partial,m.gap,
          COALESCE((SELECT SUM(auto_delta) FROM events WHERE material_id=m.id),0) AS total,
          COALESCE((SELECT SUM(defect_delta) FROM events WHERE material_id=m.id),0) AS defects
          FROM parked_materials p JOIN materials m ON m.id=p.material_id WHERE p.machine=?''',(machine,)).fetchone()
        row['parked']=dict(held,good=max(0,held['total']-held['defects'])) if held else None
        return row

    def history(self, machine=None, limit=500):
        # Limit the material cohort before summing events, so old history does not
        # make the most-recent-500 view increasingly expensive.
        query = 'SELECT * FROM materials WHERE ended IS NOT NULL AND merged_into IS NULL'
        params = []
        if machine is not None:
            self._machine(machine)
            query += ' AND machine=?'
            params.append(machine)
        query += ' ORDER BY ended DESC,id DESC'
        if limit is not None:
            query += ' LIMIT ?'
            params.append(limit)
        query = """SELECT m.*,
          COALESCE((SELECT SUM(auto_delta) FROM events WHERE material_id=m.id),0) AS total,
          COALESCE((SELECT SUM(defect_delta) FROM events WHERE material_id=m.id),0) AS defects
          FROM (""" + query + ') m ORDER BY m.ended DESC,m.id DESC'
        rows = [dict(r) for r in self.db.execute(query, params)]
        for row in rows:
            row.update(auto=row['total'],good=max(0,row['total']-row['defects']),
                       defect_excess=max(0,row['defects']-row['total']))
        return rows

    def events(self, machine=None, limit=200):
        where, params = '', []
        if machine is not None:
            self._machine(machine)
            where = 'WHERE machine=?'
            params.append(machine)
        query = 'SELECT * FROM events {} ORDER BY id DESC'.format(where)
        if limit is not None:
            query += ' LIMIT ?'
            params.append(limit)
        return [dict(r) for r in self.db.execute(query, params)]

    def period_report(self, start_ts, end_ts, machine=None):
        """[start,end): consumption/yields use rods ended in range, including early discard.

        The primary yield cohort contains each ended rod's entire observed lifetime.
        Event-date production/defect entries are separate activity statistics; they
        must not be divided by a different set of rods. Unknown/partial/gap totals
        remain visible, but partial/gap/excess-defect rods are excluded from averages.
        """
        start_ts, end_ts = self._at(start_ts), self._at(end_ts)
        if end_ts <= start_ts:
            raise ValueError('종료 시각은 시작 시각보다 뒤여야 합니다.')
        if machine is not None:
            self._machine(machine)
        fields = ('production','good','defects','defect_excess','consumed_rods','normal_rods',
                  'early_rods','loaded_rods','eligible_rods','excluded_rods',
                  'completed_production','completed_good','completed_defects','completed_defect_excess',
                  'eligible_production','eligible_good','eligible_defects')
        def empty():
            return dict.fromkeys(fields,0)
        total = empty()
        by_type = {key: dict(empty(), type_id=key, label=label) for key, label in MATERIAL_TYPES.items()}
        by_machine = {n: dict(empty(), machine=n) for n in (MACHINES if machine is None else (machine,))}
        daily = {}
        def day_row(day):
            return daily.setdefault(day,dict(empty(),day=day))
        def add(type_id, n, values, day=None):
            if type_id not in by_type:
                by_type[type_id] = dict(empty(), type_id=type_id, label=MATERIAL_TYPES.get(type_id, '미지정'))
            targets = [total,by_type[type_id],by_machine[n]] if day is None else [day_row(day)]
            for item in targets:
                for field,quantity in values.items():
                    item[field] += quantity
        filt = ' AND e.machine=?' if machine is not None else ''
        params = [start_ts,end_ts] + ([machine] if machine is not None else [])
        # Aggregate in SQLite, including one clamp per material (not one global
        # clamp which could hide legacy excess defects on another rod).
        for by_day in (False,True):
            day_sql = "strftime('%Y-%m-%d',e.at,'unixepoch','localtime')" if by_day else 'NULL'
            query = """WITH material_activity AS (
              SELECT e.material_id,e.machine,m.material_type,""" + day_sql + """ AS day,
                SUM(e.auto_delta) AS production,
                SUM(CASE WHEN e.kind='defect' AND e.undone=0 THEN e.defect_delta ELSE 0 END) AS defects
              FROM events e LEFT JOIN materials m ON m.id=e.material_id
              WHERE e.at>=? AND e.at<?""" + filt + """
              GROUP BY e.material_id,e.machine,day
            ) SELECT machine,material_type,day,SUM(production) AS production,SUM(defects) AS defects,
              SUM(MAX(0,production-defects)) AS good,SUM(MAX(0,defects-production)) AS defect_excess
              FROM material_activity GROUP BY machine,material_type,day
              HAVING SUM(production)!=0 OR SUM(defects)!=0"""
            for r in self.db.execute(query,params):
                add(r['material_type'],r['machine'],{k:r[k] for k in ('production','good','defects','defect_excess')},
                    r['day'] if by_day else None)
        filt = ' AND m.machine=?' if machine is not None else ''
        # New stock withdrawal belongs to the new material type; consumed rods
        # below belong to the old material type. Undo removes the original load.
        query = """SELECT s.type_id,m.machine,strftime('%Y-%m-%d',s.at,'unixepoch','localtime') AS day,COUNT(*) AS rods
          FROM stock_movements s JOIN materials m ON m.id=s.material_id
          WHERE s.kind='consume' AND s.at>=? AND s.at<?
          AND NOT EXISTS(SELECT 1 FROM stock_movements reversal WHERE reversal.reverses=s.id)""" + filt + ' GROUP BY s.type_id,m.machine,day'
        for r in self.db.execute(query,params):
            values = dict(loaded_rods=r['rods'])
            add(r['type_id'],r['machine'],values)
            add(r['type_id'],r['machine'],values,r['day'])
        query = """SELECT m.*,strftime('%Y-%m-%d',m.ended,'unixepoch','localtime') AS day,
          COALESCE((SELECT SUM(auto_delta) FROM events WHERE material_id=m.id),0) AS production,
          COALESCE((SELECT SUM(defect_delta) FROM events WHERE material_id=m.id),0) AS defects
          FROM materials m WHERE m.ended>=? AND m.ended<? AND m.merged_into IS NULL""" + filt
        for r in self.db.execute(query,params):
            good = max(0,r['production']-r['defects'])
            excess = max(0,r['defects']-r['production'])
            eligible = not r['partial'] and not r['gap'] and not excess
            values = dict(consumed_rods=1,early_rods=int(bool(r['early_end'])),normal_rods=int(not r['early_end']),
                          completed_production=r['production'],completed_good=good,completed_defects=r['defects'],
                          completed_defect_excess=excess,eligible_rods=int(eligible),excluded_rods=int(not eligible))
            if eligible:
                values.update(eligible_production=r['production'],eligible_good=good,eligible_defects=r['defects'])
            add(r['material_type'],r['machine'],values)
            add(r['material_type'],r['machine'],values,r['day'])
        for item in [total] + list(by_type.values()) + list(by_machine.values()) + list(daily.values()):
            count = item['eligible_rods']
            item['used_rods'] = item['loaded_rods']  # Compatibility: older use meant a new stock withdrawal.
            item['completed_rods'] = item['consumed_rods']
            item['average_per_rod'] = item['eligible_production']/count if count else None
            item['avg_good_per_rod'] = item['eligible_good']/count if count else None
            item['avg_defects_per_rod'] = item['eligible_defects']/count if count else None
            for prefix in ('','completed_','eligible_'):
                quantity = item[prefix+'production']
                item[prefix+'defect_rate'] = 100*item[prefix+'defects']/quantity if quantity else None
        return dict(start=start_ts,end=end_ts,machine=machine,totals=total,
                    by_type=list(by_type.values()),by_machine=list(by_machine.values()),
                    daily=[daily[key] for key in sorted(daily)],
                    basis='소모 봉: 기간 내 사용을 끝낸 봉(정상 소진+중도파기). 양품·불량 합계는 해당 봉의 전체 관측 기록입니다. '
                          '봉당 평균: 중도파기를 포함하고 중간 시작·수집 공백·불량초과 봉은 제외합니다. '
                          '사용 중·보관 중인 봉은 종료 후 반영됩니다. 기간 관측 가공·불량 입력은 발생일/입력일 기준 별도 수치입니다.')

    def validate_export_path(self, path):
        target=Path(path).resolve()
        protected={Path(str(self.path)+suffix).resolve() for suffix in ('','-wal','-shm','-journal')}
        if target in protected:
            raise ValueError('현재 데이터 파일에는 내보낼 수 없습니다. 다른 파일 이름을 선택해주세요.')
        if target.exists():
            for source in protected:
                if source.exists() and os.path.samefile(str(target),str(source)):
                    raise ValueError('현재 데이터 파일에는 내보낼 수 없습니다. 다른 파일 이름을 선택해주세요.')
        return target

    @contextmanager
    def _csv_output(self, path):
        target=self.validate_export_path(path)
        temporary=target.with_name('.'+target.name+'.'+uuid.uuid4().hex+'.tmp')
        try:
            with temporary.open('w',encoding='utf-8-sig',newline='') as handle:
                yield handle
            os.replace(str(temporary),str(target))
        finally:
            if temporary.exists():temporary.unlink()

    def export_materials(self, path):
        with self._csv_output(path) as f:
            w = csv.writer(f)
            w.writerow(['기록번호','호기','소재종류','시작','종료','시작 기준번호','마지막 번호','자동 가공','불량','총가공','중간 시작','수집 공백','교체구분','양품','불량초과'])
            for r in self.history(limit=None):
                w.writerow([r['id'],r['machine'],MATERIAL_TYPES.get(r['material_type'], '미지정'),date_text(r['started']),date_text(r['ended']),
                            r['start_program'],r['end_program'],r['auto'],r['defects'],r['total'],
                            '예' if r['partial'] else '', '누락 가능' if r['gap'] else '', '중도교체' if r['early_end'] else '소재교체',r['good'],r['defect_excess']])

    def export_period(self, path, start, end, machine=None):
        report = self.period_report(start,end,machine)
        with self._csv_output(path) as f:
            w = csv.writer(f)
            w.writerow(['구분','소재종류','호기','날짜','소모봉수','정상소진봉수','중도파기소재','신규투입봉수',
                        '소모 봉 양품 합계','소모 봉 불량 합계','소모 봉 가공 합계','소모 봉 불량률(%)',
                        '평균대상소재','평균제외소재','평균 산정 양품','평균 산정 불량','봉당평균양품','봉당평균불량',
                        '평균 대상 불량률(%)','기간 관측 가공','기간 불량 입력','소모 봉 불량초과',
                        '기간시작(포함)','기간종료(제외)','집계기준'])
            def write(kind,row):
                w.writerow([kind,row.get('label',''),row.get('machine',''),row.get('day',''),
                            row['consumed_rods'],row['normal_rods'],row['early_rods'],row['loaded_rods'],
                            row['completed_good'],row['completed_defects'],row['completed_production'],row['completed_defect_rate'],
                            row['eligible_rods'],row['excluded_rods'],row['eligible_good'],row['eligible_defects'],
                            row['avg_good_per_rod'],row['avg_defects_per_rod'],row['eligible_defect_rate'],
                            row['production'],row['defects'],row['completed_defect_excess'],
                            date_text(start),date_text(end),report['basis']])
            write('전체',report['totals'])
            for group,rows in (('소재별',report['by_type']),('호기별',report['by_machine']),('일별',report['daily'])):
                for row in rows:
                    write(group,row)

    def export_movements(self, path):
        with self._csv_output(path) as f:
            w = csv.writer(f)
            w.writerow(['기록번호','시각','소재코드','소재종류','구분','재고증감','사유','소재기록번호','호기','이벤트번호','취소원장번호'])
            for row in self.movements(limit=None):
                w.writerow([row['id'],date_text(row['at']),row['type_id'],MATERIAL_TYPES.get(row['type_id'], '미지정'),
                            row['kind'],row['delta'],row['note'],row['material_id'],row['machine'],row['event_id'],row['reverses']])

class Collector:
    """호기별 순차 요청. 교체 요청은 같은 작업자에서 새로 읽고 UI에 하나로 전달."""
    def __init__(self, output, request=request_json):
        self.output = output
        self.request = request
        self.stop = threading.Event()
        self.lock = threading.Lock()
        self.workers = {}
        self.routes = {}

    def start(self):
        threading.Thread(target=self._discover, daemon=True).start()

    def close(self):
        with self.lock:
            self.stop.set()
            for worker in self.workers.values():
                worker['stop'].set()
                worker['commands'].put(None)

    def checkpoint(self, machine, token):
        with self.lock:
            ip = self.routes.get(machine)
            worker = self.workers.get(ip)
            if not worker or worker['stop'].is_set():
                raise ValueError('이 호기에 연결되지 않았습니다. 연결 후 다시 눌러주세요.')
            worker['commands'].put(token)

    def _discover(self):
        while not self.stop.is_set():
            delay = 15
            try:
                result = self.request('monitoring_ajax_setting.php', {'ajax_selector':'loadIPlist'})
                addresses = result.get('ip')
                if not isinstance(addresses, list) or len(addresses) > 64:
                    raise ValueError('머신 목록 응답을 확인해주세요.')
                addresses = {str(IPv4Address(value.strip())) for value in addresses if isinstance(value, str)}
                if not addresses:
                    raise ValueError('서버의 머신 목록이 비어 있습니다.')
                with self.lock:
                    if self.stop.is_set():return
                    for ip in list(self.workers):
                        if ip not in addresses:
                            old = self.workers.pop(ip)
                            old['stop'].set()
                            old['commands'].put(None)
                            self.output.put(('removed', ip, old['generation'], None, time.time(), None, '머신 목록에서 사라짐'))
                    for ip in addresses:
                        if ip not in self.workers:
                            worker = {'stop':threading.Event(), 'commands':queue.Queue(), 'generation':uuid.uuid4().hex}
                            self.workers[ip] = worker
                            threading.Thread(target=self._poll, args=(ip, worker), daemon=True).start()
                self.output.put(('server', True, '서버 연결됨'))
                delay = 30
            except Exception as e:
                self.output.put(('server', False, str(e)[:200]))
            self.stop.wait(delay)

    def active(self, ip, generation):
        with self.lock:
            worker = self.workers.get(ip)
            return bool(worker and worker['generation'] == generation and not worker['stop'].is_set())

    def queued_source(self, ip, generation):
        with self.lock:
            worker = self.workers.get(ip)
            return bool(worker and worker['generation'] == generation)

    def _poll(self, ip, worker):
        token = None
        generation = worker['generation']
        while not self.stop.is_set() and not worker['stop'].is_set():
            record, error = None, ''
            requested_at = time.monotonic()
            try:
                result = self.request('monitoring_ajax_this_machine.php', {'ajax_selector':'callUpdateMachineOne','ncgateIP':ip})
                record = parse_sample(result)
                record['_requested_monotonic'] = requested_at
                with self.lock:
                    owner = self.routes.get(record['machine'])
                    if owner and owner != ip and owner in self.workers:
                        raise ValueError('동일 호기를 보고하는 머신 주소가 중복되어 집계를 보류합니다.')
                    for n, source in list(self.routes.items()):
                        if source == ip and n != record['machine']:
                            del self.routes[n]
                    self.routes[record['machine']] = ip
            except Exception as e:
                record, error = None, str(e)[:200]
            with self.lock:
                if self.stop.is_set() or worker['stop'].is_set():
                    return
                self.output.put(('sample', ip, generation, record, time.time(), token, error))
            try:
                token = worker['commands'].get(timeout=INTERVAL)
            except queue.Empty:
                token = None


class DatabaseJobs:
    """One background worker; each job uses an independent consistent DB view."""
    def __init__(self, path):
        self.path = Path(path)
        self.requests = queue.Queue(maxsize=8)
        self.results = queue.Queue()
        self.stop = threading.Event()
        self.thread = threading.Thread(target=self._run, daemon=True)
        self.thread.start()

    def submit(self, token, work, writable=False):
        self.requests.put_nowait((token, work, writable))

    def close(self):
        self.stop.set()
        try:self.requests.put_nowait(None)
        except queue.Full:pass

    def _run(self):
        while not self.stop.is_set():
            job = self.requests.get()
            if job is None:return
            token, work, writable = job
            db = None
            try:
                db = sqlite3.connect(str(self.path) if writable else self.path.resolve().as_uri()+'?mode=ro',
                                     timeout=3, uri=not writable)
                db.row_factory = sqlite3.Row
                db.execute('PRAGMA foreign_keys=ON')
                if writable:db.execute('PRAGMA synchronous=FULL')
                else:
                    db.execute('PRAGMA query_only=ON')
                    db.execute('BEGIN')
                view = Store.__new__(Store)
                view.path, view.db, view.live = self.path, db, set()
                result = work(view)
                self.results.put((token, result, None))
            except Exception as exc:
                self.results.put((token, None, exc))
            finally:
                if db is not None:db.close()


def rounded_image(tk, owner, width, height, radius, fill, border=None, border_width=1, raised=False):
    """Antialiased transparent round rectangle, cached per Tk interpreter (no Pillow)."""
    import base64
    from collections import OrderedDict
    import math
    import struct
    import zlib
    root=owner._root()
    width,height=max(1,int(width)),max(1,int(height))
    radius=max(0.0,min(float(radius),width/2,height/2))
    border_width=max(0.0,min(float(border_width),width/2,height/2)) if border else 0.0
    def rgb(value):return tuple(c//257 for c in owner.winfo_rgb(value))
    color=rgb(fill);edge=rgb(border) if border else color
    key=(width,height,radius,color,edge,border_width,raised)
    cache=getattr(root,'_rounded_image_cache',None)
    if cache is None:
        cache=OrderedDict();root._rounded_image_cache=cache
        root._rounded_image_pixels=0
    if key in cache:
        cache.move_to_end(key)
        return cache[key]
    def coverage(x,y,inset):
        w,h=width-2*inset,height-2*inset
        if w<=0 or h<=0:return 0.0
        r=max(0.0,radius-inset)
        qx=abs(x-width/2)-(w/2-r)
        qy=abs(y-height/2)-(h/2-r)
        distance=math.hypot(max(qx,0),max(qy,0))+min(max(qx,qy),0)-r
        return max(0.0,min(1.0,0.5-distance))
    # Only the corner strips need per-pixel math; the wide center is a repeated
    # pixel run. Large rounded panels stay cheap while dragging window edges.
    def pixel(x,y):
        outer=coverage(x,y,0)
        if not outer:return b'\0\0\0\0'
        if border_width:
            inner=min(outer,coverage(x,y,border_width))
            bevel=tuple(min(255,c+28) for c in edge) if raised and y<height/2 else (tuple(max(0,c-35) for c in edge) if raised else edge)
            pixels=tuple(round((color[i]*inner+bevel[i]*(outer-inner))/outer) for i in range(3))
        else:pixels=color
        return bytes(pixels+(round(255*outer),))
    raw=bytearray()
    edge_size=int(math.ceil(max(radius,border_width)+1))
    strip=min(width//2,edge_size)
    row_cache={}
    for y in range(height):
        # Beveled buttons distinguish top/bottom; panels retain symmetric rows.
        reflected=(min(y,height-1-y,edge_size),raised and y>=height/2)
        if reflected not in row_cache:
            left=[pixel(x+.5,y+.5) for x in range(strip)]
            middle=pixel(width/2,y+.5)*(width-2*strip)
            row_cache[reflected]=b'\0'+b''.join(left)+middle+b''.join(reversed(left))
        raw.extend(row_cache[reflected])
    def chunk(kind,data):return struct.pack('!I',len(data))+kind+data+struct.pack('!I',zlib.crc32(kind+data)&0xffffffff)
    png=b'\x89PNG\r\n\x1a\n'+chunk(b'IHDR',struct.pack('!2I5B',width,height,8,6,0,0,0))+chunk(b'IDAT',zlib.compress(bytes(raw),6))+chunk(b'IEND',b'')
    result=tk.PhotoImage(master=root,data=base64.b64encode(png).decode('ascii'))
    cache[key]=result
    root._rounded_image_pixels+=width*height
    while len(cache)>1 and (len(cache)>128 or root._rounded_image_pixels>8000000):
        old_key,old_image=cache.popitem(last=False)
        root._rounded_image_pixels-=old_key[0]*old_key[1]
    return result


def make_rounded_button(tk, parent, **options):
    """Keep native mouse, keyboard, focus, disabled and invoke semantics."""
    widget_class=getattr(tk,'_MaterialCounterRoundedButton',None)
    if widget_class is None:
        from tkinter import font as tkfont
        class RoundedButton(tk.Button):
            _aliases={'bg':'background','fg':'foreground','bd':'borderwidth'}
            _visual={'background','activebackground','font','text','width','height','padx','pady','state'}
            def __init__(self,parent,**kwargs):
                values={self._aliases.get(k,k):v for k,v in kwargs.items()}
                self._round_values={
                    'background':values.pop('background',PALETTE['card']),
                    'activebackground':values.pop('activebackground',PALETTE['selected']),
                    'padx':values.pop('padx',13),'pady':values.pop('pady',7),
                    'width':values.pop('width',0),'height':values.pop('height',0)}
                self._round_hover=False;self._round_focus=False;self._round_signature=None
                self._round_ready=False
                surface=getattr(parent,'_surface_color',None)
                if surface is None:
                    try:surface=parent.cget('background')
                    except tk.TclError:surface=PALETTE['bg']
                self._round_surface=surface
                values.update(background=surface,activebackground=surface,compound='center',
                              borderwidth=0,highlightthickness=0,relief='flat',overrelief='flat',
                              padx=0,pady=0,width=0,height=0,takefocus=1)
                tk.Button.__init__(self,parent,**values)
                self._round_font=tkfont.Font(root=self,font=tk.Button.cget(self,'font'))
                self._round_ready=True
                self.bind('<Enter>',lambda event:self._round_enter(True),add='+')
                self.bind('<Leave>',lambda event:self._round_enter(False),add='+')
                self.bind('<FocusIn>',lambda event:self._round_focused(True),add='+')
                self.bind('<FocusOut>',lambda event:self._round_focused(False),add='+')
                self.bind('<Return>',self._round_return,add='+')
                self._round_paint()

            def _round_return(self,event):
                self.invoke()
                return 'break'

            def _round_enter(self,inside):
                if self._round_hover!=inside:
                    self._round_hover=inside;self._round_paint()

            def _round_focused(self,focused):
                if self._round_focus!=focused:
                    self._round_focus=focused;self._round_paint()

            def _round_paint(self):
                if not self._round_ready:return
                values=self._round_values
                text=str(tk.Button.cget(self,'text'))
                font_value=tk.Button.cget(self,'font')
                if getattr(self,'_round_font_value',None)!=font_value:
                    self._round_font=tkfont.Font(root=self,font=font_value)
                    self._round_font_value=font_value
                font=self._round_font
                desired_width=int(values['width'] or 0)
                desired_height=int(values['height'] or 0)
                text_width=max((font.measure(line) for line in text.split('\n')),default=0)
                w=(desired_width*font.measure('0') if desired_width else text_width)+2*int(values['padx'])+4
                h=(desired_height or max(1,text.count('\n')+1))*font.metrics('linespace')+2*int(values['pady'])+4
                disabled=tk.Button.cget(self,'state')=='disabled'
                fill=values['activebackground'] if self._round_hover and not disabled else values['background']
                if disabled:
                    front=self.winfo_rgb(fill);back=self.winfo_rgb(self._round_surface)
                    fill='#'+''.join('{:02x}'.format(round((a*.64+b*.36)/257)) for a,b in zip(front,back))
                border='#8db3ff' if self._round_focus and not disabled else PALETTE['line']
                signature=(w,h,fill,border)
                if signature==self._round_signature:return
                self._round_signature=signature
                self._round_image=rounded_image(tk,self,w,h,6,fill,border=border,border_width=1.5,raised=False)
                tk.Button.configure(self,image=self._round_image)

            def configure(self,cnf=None,**kwargs):
                if not getattr(self,'_round_ready',False):return tk.Button.configure(self,cnf,**kwargs)
                if isinstance(cnf,str) and not kwargs:
                    key=self._aliases.get(cnf,cnf)
                    result=tk.Button.configure(self,key)
                    if key in self._round_values:return result[:-1]+(self._round_values[key],)
                    return result
                if cnf is None and not kwargs:
                    result=tk.Button.configure(self)
                    for key,value in self._round_values.items():
                        result[key]=result[key][:-1]+(value,)
                    return result
                settings={}
                if cnf:settings.update(cnf)
                settings.update(kwargs)
                settings={self._aliases.get(k,k):v for k,v in settings.items()}
                visual=False
                for key in list(settings):
                    if key in self._round_values:
                        value=settings.pop(key)
                        if self._round_values[key]!=value:
                            self._round_values[key]=value;visual=True
                for key,value in settings.items():
                    if key in self._visual and str(tk.Button.cget(self,key))!=str(value):visual=True
                result=tk.Button.configure(self,**settings) if settings else None
                if visual:self._round_paint()
                return result
            config=configure

            def cget(self,key):
                key=self._aliases.get(key,key)
                if getattr(self,'_round_ready',False) and key in self._round_values:return self._round_values[key]
                return tk.Button.cget(self,key)
            __getitem__=cget
        widget_class=RoundedButton
        tk._MaterialCounterRoundedButton=widget_class
    return widget_class(parent,**options)


class Application:
    dashboard_actions=True
    temporary14_actions=False
    mass_mode_actions=False
    def __init__(self, root, store, folder, collector_factory=Collector, jobs_factory=DatabaseJobs):
        import tkinter as tk
        from tkinter import ttk, font
        self.tk, self.ttk = tk, ttk
        self.root, self.store, self.folder = root, store, Path(folder)
        self.collector_factory = collector_factory
        self.jobs = jobs_factory(store.path)
        self.job_callbacks = {}
        self.resetting = False
        self.queue = queue.Queue()
        self.collector = collector_factory(self.queue)
        self.pending, self.sources, self.errors = {}, {}, {}
        self.source_errors = {}
        self.last_click = {}
        self.dirty_history = True
        self.dirty_inventory = True
        self.closed = False
        self.failed_storage = False
        self.server_ok = False
        self.server_detail = '서버에 연결하는 중입니다.'
        families = set(font.families(root))
        self.font = next((x for x in ('맑은 고딕','Malgun Gothic','Noto Sans CJK KR','Noto Sans CJK JP') if x in families), 'TkDefaultFont')
        self.root.title('소재관리 · 재고와 생산 기록')
        self.root.configure(bg=PALETTE['bg'])
        self.root.geometry('1060x810')
        self.root.minsize(1000, 790)
        self.root.protocol('WM_DELETE_WINDOW', self.on_close)
        self.root.report_callback_exception = self.callback_error
        self._style()
        self._icon()
        self._build()
        self.refresh()
        if any(not r['registered'] for r in self.store.inventory()):
            self.tell('처음 사용: 소재 재고 탭에서 보관 봉 수 등록 → 각 호기의 소재명을 눌러 사용 소재 지정')
        self.collector.start()
        self._ui_timer = self.root.after(100, self.tick)

    def _style(self):
        style = self.ttk.Style(self.root)
        style.theme_use('clam')
        # N3: 얇은 스크롤바(화살표 없음) — 메인 창과 같은 한 가지 코드(visual_theme)를 씁니다.
        try:
            try:
                from jihunius_scrollbars import install_thin_scrollbars
            except ImportError:
                from visual_theme import install_thin_scrollbars
            install_thin_scrollbars(style)
        except Exception:
            pass
        style.configure('.', font=(self.font, 10), background=PALETTE['bg'], foreground=PALETTE['text'])
        style.configure('TFrame', background=PALETTE['bg'])
        style.configure('TLabel', background=PALETTE['bg'], foreground=PALETTE['text'])
        style.configure('TNotebook', background=PALETTE['bg'], borderwidth=0, bordercolor=PALETTE['bg'], lightcolor=PALETTE['bg'], darkcolor=PALETTE['bg'], padding=0)
        style.layout('TNotebook.Tab', [])
        style.configure('TNotebook.Tab', background=PALETTE['card'], foreground=PALETTE['muted'], padding=(22,10))
        style.map('TNotebook.Tab', background=[('selected', PALETTE['selected'])], foreground=[('selected','white')])
        style.configure('Treeview', background=PALETTE['field'], fieldbackground=PALETTE['field'], foreground=PALETTE['text'], rowheight=30, borderwidth=0, bordercolor=PALETTE['field'], lightcolor=PALETTE['field'], darkcolor=PALETTE['field'], relief='flat')
        style.configure('Treeview.Heading', background=PALETTE['card'], foreground=PALETTE['muted'], padding=(6,8), relief='flat', borderwidth=0)
        style.map('Treeview', background=[('selected',PALETTE['selected'])], foreground=[('selected','white')])
        style.configure('TCombobox', fieldbackground=PALETTE['field'], background=PALETTE['card'], foreground=PALETTE['text'], arrowcolor=PALETTE['text'])
        style.map('TCombobox', fieldbackground=[('readonly',PALETTE['field'])], foreground=[('readonly',PALETTE['text'])])
        self._field_images=[rounded_image(self.tk,self.root,28,28,9,PALETTE['field'],border=color)
                            for color in (PALETTE['line'],'#60a5fa')]
        style.element_create('MaterialRound.field','image',self._field_images[0],('focus',self._field_images[1]),
                             border=10,padding=(9,5),sticky='nsew')
        style.layout('Round.TEntry',[('MaterialRound.field',{'sticky':'nsew','children':[
            ('Entry.padding',{'sticky':'nsew','children':[('Entry.textarea',{'sticky':'nsew'})]})]})])
        style.configure('Round.TEntry',foreground=PALETTE['text'],fieldbackground=PALETTE['field'],
                        background=PALETTE['bg'],insertcolor=PALETTE['text'])
        style.layout('Round.TCombobox',[('MaterialRound.field',{'sticky':'nsew','children':[
            ('Combobox.padding',{'sticky':'nsew','children':[
                ('Combobox.downarrow',{'side':'right','sticky':'ns'}),
                ('Combobox.textarea',{'sticky':'nsew'})]})]})])
        style.configure('Round.TCombobox',foreground=PALETTE['text'],fieldbackground=PALETTE['field'],
                        background=PALETTE['field'],arrowcolor=PALETTE['muted'],arrowsize=12,borderwidth=0)
        self.root.option_add('*TCombobox*Listbox.background', PALETTE['field'])
        self.root.option_add('*TCombobox*Listbox.foreground', PALETTE['text'])

    def _icon(self):
        im = self.tk.PhotoImage(width=32, height=32)
        im.put(PALETTE['bg'], to=(0,0,32,32))
        for x,h in ((5,11),(13,18),(21,25)):
            im.put('#60a5fa', to=(x,30-h,x+6,29))
        self.icon = im
        self.root.iconphoto(True, im)

    def label(self, parent, text='', size=10, color=None, bold=False, bg=None, **kwargs):
        return self.tk.Label(parent, text=text, font=(self.font,size,'bold' if bold else 'normal'),
                             bg=bg or PALETTE['bg'], fg=color or PALETTE['text'], **kwargs)

    def button(self, parent, text, command, primary=False, **kwargs):
        return make_rounded_button(self.tk,parent, text=text, command=command, font=(self.font,10,'bold'),
                              bg=PALETTE['blue'] if primary else PALETTE['card'], fg='white',
                              activebackground=PALETTE['selected'], activeforeground='white',
                              disabledforeground='#77797d', relief='flat', bd=0, padx=13, pady=7,
                              cursor='hand2', **kwargs)

    def rounded_panel(self, parent, fill=None, radius=14, border=None):
        fill=fill or PALETTE['card']
        surface=getattr(parent,'_surface_color',None)
        if surface is None:
            try:surface=parent.cget('background')
            except self.tk.TclError:surface=PALETTE['bg']
        panel=self.tk.Frame(parent,bg=surface,bd=0,highlightthickness=0)
        panel._surface_color=fill
        canvas=self.tk.Canvas(panel,bg=surface,bd=0,highlightthickness=0,takefocus=0)
        canvas.place(x=0,y=0,relwidth=1,relheight=1)
        image_id=canvas.create_image(0,0,anchor='nw')
        panel._rounded_size=None
        def paint(event):
            size=(event.width,event.height)
            if size==panel._rounded_size or min(size)<2:return
            panel._rounded_size=size
            panel._rounded_image=rounded_image(self.tk,panel,size[0],size[1],radius,fill,border=border)
            canvas.itemconfigure(image_id,image=panel._rounded_image)
            canvas.tk.call('lower',canvas._w)
        panel.bind('<Configure>',paint,add='+')
        return panel

    def _build(self):
        top = self.tk.Frame(self.root,bg=PALETTE['bg'])
        top.pack(fill='x',padx=24,pady=(16,8))
        self.label(top,'소재관리',size=20,bold=True).pack(side='left')
        self.label(top,'  재고 · 생산 통계  '+VERSION, color=PALETTE['muted']).pack(side='left',pady=(8,0))
        self.button(top,'사용 안내',self.help).pack(side='right')
        self.button(top,'진단 저장',self.diagnostics).pack(side='right',padx=8)
        self.summary = self.label(self.root,'연결 대기',size=11,color=PALETTE['muted'],anchor='w')
        self.summary.pack(fill='x',padx=26,pady=(0,8))
        self.nav=self.tk.Frame(self.root,bg=PALETTE['bg'])
        self.nav.pack(fill='x',padx=24,pady=(3,8))
        self.nav_buttons={}
        self.tabs = self.ttk.Notebook(self.root)
        self.tabs.pack(fill='both',expand=True,padx=20)
        self.current_tab = self.ttk.Frame(self.tabs)
        self.inventory_tab = self.ttk.Frame(self.tabs)
        self.period_tab = self.ttk.Frame(self.tabs)
        self.history_tab = self.ttk.Frame(self.tabs)
        self.tabs.add(self.current_tab,text='현재 집계')
        self.tabs.add(self.inventory_tab,text='소재 재고')
        self.tabs.add(self.period_tab,text='기간 통계')
        self.tabs.add(self.history_tab,text='소재 기록')
        for page,title in ((self.current_tab,'현재 집계'),(self.inventory_tab,'소재 재고'),(self.period_tab,'기간 통계'),(self.history_tab,'소재 기록')):
            button=self.button(self.nav,title,lambda target=page:self.tabs.select(target),width=10)
            button.pack(side='left',padx=(0,8))
            self.nav_buttons[str(page)]=button
        self.tabs.enable_traversal()
        self.tabs.bind('<<NotebookTabChanged>>',self.tab_changed)
        self.label(self.current_tab,'4자리 번호 변경: 양품 +1 · 3999 / 9012 / 9020 / 9999 제외 · 불량 버튼: 양품 −1 / 불량 +1',
                   color=PALETTE['muted'],anchor='w').pack(fill='x',padx=8,pady=(10,8))
        board = self.tk.Frame(self.current_tab,bg=PALETTE['bg'])
        board.pack(fill='both',expand=True,padx=4)
        from tkinter import font as tkfont
        text_font=tkfont.Font(root=self.root,font=(self.font,10))
        program_width=max(88,text_font.measure('양산품 · 집계 중지')+8)
        widths = (62,78,program_width,64,60,144) + ((108,104) if self.dashboard_actions else ()) + ((166,) if self.temporary14_actions else ()) + ((166,) if self.mass_mode_actions else ())
        heads = ('호기','상태','작업번호','양품','불량','사용 소재') + (('', '') if self.dashboard_actions else ()) + (('임시 소재 전환',) if self.temporary14_actions else ()) + (('양산품 모드',) if self.mass_mode_actions else ())
        for j,(width,heading) in enumerate(zip(widths,heads)):
            board.grid_columnconfigure(j,minsize=width,weight=1 if j==5 else 0)
            self.label(board,heading,color=PALETTE['muted'],bg=PALETTE['bg']).grid(row=0,column=j,sticky='nsew',pady=(0,1),ipady=8)
        self.rows = {}
        for n in MACHINES:
            bg = PALETTE['card'] if n%2 else '#0a1224'
            row_card=self.rounded_panel(board,fill=bg,radius=11)
            row_card.grid(row=n,column=0,columnspan=len(widths),sticky='nsew',pady=(0,4))
            # All headings and machine cells belong to ONE grid. Independent
            # row grids grow differently for paused programs and larger counts.
            # Keep the rounded card underneath as decoration only.
            widgets = {}
            for j,key in enumerate(('machine','state','program','total','defects','material')):
                options = dict(size=18 if key=='total' else 10,bold=key in ('machine','total'),bg=bg)
                widget = self.label(board,'{}호기'.format(n) if key=='machine' else '—',**options)
                widget.grid(row=n,column=j,sticky='nsew',padx=(8,0) if j==0 else 0,pady=(5,9),ipady=1)
                widget.bind('<Button-3>',lambda e,m=n:self.context(e,m))
                if key=='material':
                    widget.configure(cursor='hand2')
                    widget.bind('<Button-1>',lambda e,m=n:self.material_dialog(m))
                widgets[key]=widget
            actions=((6,'rotate','소재교체',self.rotate),(7,'defect','불량 +1',self.defect)) if self.dashboard_actions else ()
            if self.temporary14_actions:actions+=((len(widths)-1-int(self.mass_mode_actions),'switch14','14파이 교체',self.switch_14),)
            if self.mass_mode_actions:actions+=((len(widths)-1,'mass_mode','양산품 교체',self.toggle_mass_mode),)
            for j,key,text,fn in actions:
                box = self.tk.Frame(board,bg=bg)
                box.grid(row=n,column=j,sticky='nsew',padx=(0,7) if j==7 else 0,pady=(2,6))
                button = self.button(box,text,lambda m=n,f=fn:f(m),primary=key=='rotate',width=7)
                if key in ('switch14','mass_mode'):button.configure(width=12,padx=9)
                if key=='defect':button.configure(bg=PALETTE['danger'],activebackground=PALETTE['danger_active'],disabledforeground='#e3a3a3')
                button.pack(expand=True,padx=4,pady=0)
                button.bind('<Button-3>',lambda e,m=n:self.context(e,m))
                widgets[key]=button
            board.grid_rowconfigure(n,weight=1,minsize=47)
            self.rows[n]=widgets
        self.bottom_hint=self.label(self.current_tab,('소재교체: 소모 1봉으로 집계' if self.dashboard_actions else '소재교체·불량 입력: 지후니우스 메인 하단')+'    |    소재명 클릭: 다음 소재    |    우클릭: 취소',
                   color=PALETTE['muted'],anchor='w',size=9)
        self.bottom_hint.pack(side='bottom',before=board,fill='x',padx=8,pady=8)
        self._history_build()
        self._inventory_build()
        self._period_build()
        self.notice = self.label(self.root,'',color=PALETTE['green'],anchor='w')
        self.notice.pack(side='bottom',before=self.tabs,fill='x',padx=24,pady=(8,2))
        self.footer = self.label(self.root,'이 PC에 자동 저장  ·  3초 간격 조회  ·  최소화해도 수집 계속',color=PALETTE['muted'],size=9,anchor='w')
        self.footer.pack(side='bottom',before=self.notice,fill='x',padx=24,pady=(0,10))

    def run_report_job(self, work, on_success, on_error=None, writable=False):
        if self.closed or self.failed_storage or (self.resetting and not writable):return False
        token=uuid.uuid4().hex
        try:self.jobs.submit(token,work,writable)
        except queue.Full:
            self.tell('조회 작업이 밀려 있습니다. 잠시 후 다시 눌러주세요.',error=True)
            return False
        self.job_callbacks[token]=(on_success,on_error)
        return True

    def _finish_jobs(self):
        for _ in range(10):
            try:token,result,error=self.jobs.results.get_nowait()
            except queue.Empty:break
            callbacks=self.job_callbacks.pop(token,None)
            if callbacks is None:continue
            success,failure=callbacks
            if error is not None:
                if failure:failure(error)
                else:self.tell('처리 실패: '+str(error)[:180],error=True)
            else:success(result)

    def reset_dialog(self):
        from tkinter import messagebox
        if self.failed_storage or self.resetting:return
        auto_backup=getattr(self,'backup_before_reset',True)
        if self.pending or self.job_callbacks:
            self.tell('소재교체·조회·내보내기 처리가 끝난 뒤 기록을 삭제해주세요.',error=True)
            return
        dialog=self.tk.Toplevel(self.root)
        dialog.title('기록 삭제 · 새로 수집 시작')
        dialog.configure(bg=PALETTE['bg']);dialog.resizable(False,False)
        dialog.transient(self.root)
        self.label(dialog,'테스트 기록을 삭제하고 새로 시작',size=15,bold=True,anchor='w').pack(fill='x',padx=24,pady=(22,12))
        safety='삭제 전 전체 데이터가 자동 백업되며, 백업에 실패하면 삭제하지 않습니다.' if auto_backup else '자동 백업 없이 삭제하며 프로그램에서 되돌릴 수 없습니다.'
        self.label(dialog,'1~9호기의 가공·불량·소재교체·입출고 이력과 현재 집계를 삭제합니다.\n'+safety,
                   color=PALETTE['muted'],justify='left',anchor='w').pack(fill='x',padx=24,pady=(0,14))
        reset_stock=self.tk.BooleanVar(value=False)
        for value,text in ((False,'현재 재고 유지 · 남은 봉 수와 소재 설정 유지'),(True,'재고도 초기화 · 남은 봉 수와 소재 설정을 다시 등록')):
            self.tk.Radiobutton(dialog,text=text,variable=reset_stock,value=value,bg=PALETTE['card'],fg=PALETTE['text'],
                activebackground=PALETTE['selected'],activeforeground='white',selectcolor=PALETTE['field'],
                font=(self.font,11),anchor='w',padx=12,pady=12).pack(fill='x',padx=24,pady=4)
        self.label(dialog,'현재 재고를 유지하면 과거 테스트에서 차감된 봉을 되돌리지 않습니다.\n실제 잔량이 다르면 소재 재고 탭에서 수정하세요.\n\n삭제 후 첫 번호는 기준으로 잡고, 현재 장착 봉은 중간 시작으로 표시합니다.',
                   color=PALETTE['yellow'],justify='left',anchor='w',size=9).pack(fill='x',padx=24,pady=14)
        status=self.label(dialog,'',color=PALETTE['muted'],anchor='w',wraplength=510,justify='left')
        status.pack(fill='x',padx=24)
        buttons=self.tk.Frame(dialog,bg=PALETTE['bg']);buttons.pack(fill='x',padx=24,pady=(10,22))
        cancel=self.button(buttons,'취소',dialog.destroy);cancel.pack(side='left')
        def apply():
            if self.pending or self.job_callbacks:
                status.configure(text='처리 중인 작업이 있습니다. 완료 후 다시 눌러주세요.');return
            scope='재고·소재 설정까지' if reset_stock.get() else '현재 재고는 유지하고'
            detail='자동 백업 후 새로 수집을 시작합니다.' if auto_backup else '자동 백업 없이 삭제하고 새로 수집을 시작합니다.'
            if not messagebox.askyesno('기록 삭제 확인',scope+' 모든 수집 기록을 삭제할까요?\n'+detail,parent=dialog):return
            apply_button.configure(state='disabled');cancel.configure(state='disabled')
            dialog.protocol('WM_DELETE_WINDOW',lambda:None)
            status.configure(text=('백업 및 기록 삭제 중입니다.' if auto_backup else '기록 삭제 중입니다.')+' 완료될 때까지 기다려주세요.')
            self._begin_reset(reset_stock.get(),dialog,status,apply_button,cancel)
        apply_button=self.button(buttons,'백업 후 기록 삭제' if auto_backup else '기록 삭제',apply)
        apply_button.configure(bg=PALETTE['danger'],activebackground=PALETTE['danger_active'])
        apply_button.pack(side='right')
        dialog.grab_set()

    def _begin_reset(self, reset_stock, dialog=None, status=None, apply_button=None, cancel=None):
        if self.pending or self.job_callbacks or self.resetting or self.failed_storage:return False
        self.collector.close()
        try:
            while True:self.handle(self.queue.get_nowait(),draining=True)
        except queue.Empty:pass
        except sqlite3.Error as exc:
            self.storage_error(exc)
            if dialog:dialog.destroy()
            return False
        self.resetting=True
        self.refresh()
        def restart():
            self.pending.clear();self.sources.clear();self.errors.clear();self.source_errors.clear();self.last_click.clear()
            self.store.live.clear()
            self.queue=queue.Queue()
            self.collector=self.collector_factory(self.queue)
            self.server_ok=False;self.server_detail='새 수집 기준을 확인하고 있습니다.'
            self.dirty_history=True;self.dirty_inventory=True
            self.resetting=False
            self.collector.start()
            self.refresh();self.refresh_history(force=True);self.refresh_inventory()
        def done(backup):
            restart()
            if dialog:dialog.destroy()
            self.refresh_period()
            self.tell('기록 삭제 완료 · '+('재고 미등록으로 초기화' if reset_stock else '현재 재고 유지')+' · 자동 백업: '+backup.name)
        def failed(exc):
            # Resume conservatively: a paused interval is never inferred as production.
            self.resetting=False
            try:
                for n in list(self.store.live):self.store.disconnected(n,time.time(),'기록 초기화 시도 중 수집 일시 중단')
            except sqlite3.Error as db_error:
                if dialog:dialog.destroy()
                self.storage_error(db_error);return
            restart()
            if status:status.configure(text='삭제하지 못했습니다. 기존 기록을 유지합니다.\n'+str(exc)[:180],fg=PALETTE['red'])
            if apply_button:apply_button.configure(state='normal')
            if cancel:cancel.configure(state='normal')
            if dialog:dialog.protocol('WM_DELETE_WINDOW',dialog.destroy)
            self.tell('기록 삭제 실패 · 기존 데이터 유지: '+str(exc)[:120],error=True)
        accepted=self.run_report_job(lambda view:view.reset_records(reset_stock),done,failed,writable=True)
        if not accepted:failed(RuntimeError('초기화 작업을 시작하지 못했습니다. 잠시 후 다시 시도해주세요.'))
        return accepted

    def _history_build(self):
        bar = self.tk.Frame(self.history_tab,bg=PALETTE['bg'])
        bar.pack(fill='x',pady=12)
        self.filter = self.tk.StringVar(value='전체 호기')
        combo = self.ttk.Combobox(bar,style='Round.TCombobox',textvariable=self.filter,values=['전체 호기']+['{}호기'.format(n) for n in MACHINES],state='readonly',width=12)
        combo.pack(side='left',padx=4)
        combo.bind('<<ComboboxSelected>>',lambda e:self.refresh_history(force=True))
        self.reset_button=self.button(bar,'기록 삭제',self.reset_dialog)
        self.reset_button.configure(fg=PALETTE['red'])
        self.reset_button.pack(side='right',padx=4)
        self.button(bar,'CSV 내보내기',self.export).pack(side='right',padx=4)
        self.button(bar,'저장 폴더',self.open_folder).pack(side='right',padx=4)
        self.label(self.history_tab,'교체 완료한 소재  ·  최근 500건 표시 / CSV는 전체 기록',color=PALETTE['muted'],anchor='w').pack(fill='x',padx=4,pady=(0,6))
        columns = ('id','machine','type','start','end','total','good','defect','note')
        headings = ('기록','호기','소재','시작','종료','가공','양품','불량','비고')
        widths = (42,44,90,124,124,55,55,50,130)
        self.history_tree = self._tree(self.history_tab,columns,headings,widths,height=6)
        self.label(self.history_tab,'수집 이력  ·  최근 200건  ·  같은 값의 반복 조회는 쌓지 않습니다.',color=PALETTE['muted'],anchor='w').pack(fill='x',padx=4,pady=(16,6))
        self.event_tree = self._tree(self.history_tab,('at','machine','kind','program'),
                                     ('관측시각','호기','내용','작업번호'),(138,48,190,160),height=4)
        self.event_tree.bind('<Double-1>',self.event_detail)

    def tab_changed(self,event=None):
        selected=self.tabs.select()
        for page,button in self.nav_buttons.items():
            button.configure(bg=PALETTE['blue'] if page==selected else PALETTE['card'],
                             fg='white' if page==selected else PALETTE['muted'])
        if selected==str(self.history_tab):self.refresh_history(force=True)
        elif selected==str(self.inventory_tab):self.refresh_inventory()
        elif selected==str(self.period_tab) and hasattr(self,'report_tree'):self.refresh_period()

    def _inventory_build(self):
        self.label(self.inventory_tab,'보관 중인 미사용 봉을 관리합니다. 이미 기계에 넣은 소재는 최초 재고에서 제외하세요.',
                   color=PALETTE['muted'],anchor='w').pack(fill='x',padx=8,pady=(14,10))
        cards=self.tk.Frame(self.inventory_tab,bg=PALETTE['bg'])
        cards.pack(fill='x',padx=4)
        self.stock_cards={}
        for i,(key,label) in enumerate(MATERIAL_TYPES.items()):
            cards.grid_columnconfigure(i,weight=1,uniform='stock')
            card=self.rounded_panel(cards,border=PALETTE['line'])
            card.grid(row=0,column=i,sticky='nsew',padx=4)
            self.label(card,label,bold=True,size=12,bg=PALETTE['card']).pack(pady=(12,4))
            qty=self.label(card,'미등록',bold=True,size=24,bg=PALETTE['card'])
            qty.pack(pady=(0,8))
            buttons=self.tk.Frame(card,bg=PALETTE['card'])
            buttons.pack(pady=(0,12))
            receive=self.button(buttons,'최초 등록',lambda t=key:self.stock_dialog(t,'receive'),primary=True)
            receive.pack(side='left',padx=3)
            adjust=self.button(buttons,'수정',lambda t=key:self.stock_dialog(t,'adjust'))
            adjust.pack(side='left',padx=3)
            self.stock_cards[key]=(qty,receive,adjust)
        bar=self.tk.Frame(self.inventory_tab,bg=PALETTE['bg'])
        bar.pack(fill='x',padx=8,pady=(18,8))
        self.label(bar,'입고 · 사용 · 재고 수정 이력',bold=True).pack(side='left')
        self.button(bar,'입출고 CSV',self.export_movements).pack(side='right')
        self.button(bar,'전체 데이터 백업',self.backup_data).pack(side='right',padx=8)
        self.label(self.inventory_tab,'소재교체 시 새로 넣는 소재 1봉이 차감됩니다. 취소·수정도 기록에 남습니다.',
                   color=PALETTE['muted'],size=9,anchor='w').pack(fill='x',padx=8,pady=(0,8))
        self.stock_tree=self._tree(self.inventory_tab,('at','type','kind','delta','note'),
                                  ('시각','소재','내용','봉 수 증감','비고'),(145,100,100,90,320),height=9)
        self.inventory_hint=self.label(self.inventory_tab,'최근 200건 표시 · CSV는 전체 이력 · 이 PC의 재고 데이터입니다.',
                   color=PALETTE['muted'],size=9,anchor='w')
        self.inventory_hint.pack(side='bottom',before=self.stock_tree.master,fill='x',padx=8,pady=8)

    def refresh_inventory(self):
        if not hasattr(self,'stock_tree'):return
        for row in self.store.inventory():
            qty,receive,adjust=self.stock_cards[row['type_id']]
            qty.configure(text='미등록' if row['quantity'] is None else '{:,} 봉'.format(row['quantity']),
                          fg=PALETTE['yellow'] if row['quantity'] in (None,0) else PALETTE['text'])
            receive.configure(text='입고 +' if row['registered'] else '최초 등록',state='disabled' if self.failed_storage else 'normal')
            adjust.configure(state='normal' if row['registered'] and not self.failed_storage and not self.resetting else 'disabled')
        old=self.stock_tree.get_children()
        if old:self.stock_tree.delete(*old)
        for row in self.store.movements():
            self.stock_tree.insert('','end',values=(date_text(row['at'],True),material_label(row['type_id']),
              MOVEMENT_NAMES.get(row['kind'],row['kind']),'{:+d}'.format(row['delta']),row['note']))
        self.dirty_inventory=False

    def stock_dialog(self,type_id,mode):
        from tkinter import simpledialog
        if self.failed_storage or self.resetting:return
        if self.pending:
            self.tell('소재교체 처리 결과가 나온 뒤 재고를 입력해주세요.',error=True)
            return
        row=next(r for r in self.store.inventory() if r['type_id']==type_id)
        revision=self.store.db.execute('SELECT MAX(id) FROM stock_movements WHERE type_id=?',(type_id,)).fetchone()[0]
        label=material_label(type_id)
        try:
            if not row['registered']:
                qty=simpledialog.askinteger('최초 재고 등록',label+' 보관 재고는 몇 봉인가요?\n이미 기계에 넣은 소재는 빼고 입력하세요.',minvalue=0,maxvalue=1000000,parent=self.root)
                if qty is None:return
                self.store.register_stock(type_id,qty)
            elif mode=='receive':
                qty=simpledialog.askinteger('소재 입고',label+' 새로 입고된 수량을 입력하세요. (봉)',minvalue=1,maxvalue=1000000,parent=self.root)
                if qty is None:return
                self.store.receive_stock(type_id,qty)
            else:
                qty=simpledialog.askinteger('재고 수정',label+' 실제 보관 재고를 입력하세요. (봉)',initialvalue=row['quantity'],minvalue=0,maxvalue=1000000,parent=self.root)
                if qty is None:return
                reason=simpledialog.askstring('수정 이유','수정 이유를 입력하세요. 예: 초기 입력 정정, 실사 차이',parent=self.root)
                if reason is None:return
                latest=self.store.db.execute('SELECT MAX(id) FROM stock_movements WHERE type_id=?',(type_id,)).fetchone()[0]
                if latest!=revision:
                    raise ValueError('입력 중 재고가 변경되었습니다. 최신 수량을 확인한 뒤 다시 수정해주세요.')
                self.store.adjust_stock(type_id,qty,reason)
            self.dirty_inventory=True
            self.refresh_inventory()
            self.tell(label+' 재고를 저장했습니다.')
        except ValueError as e:self.tell(str(e),error=True)
        except sqlite3.Error as e:self.storage_error(e)

    def material_dialog(self,n):
        from tkinter import messagebox
        if n in self.pending or self.failed_storage or self.resetting:return
        row=self.store.snapshot(n)
        initial=not row.get('material_type')
        dialog=self.tk.Toplevel(self.root)
        dialog.title('{}호기 소재 지정'.format(n))
        dialog.configure(bg=PALETTE['bg']);dialog.resizable(False,False)
        dialog.transient(self.root)
        self.label(dialog,'{}호기 · {}'.format(n,'사용 중인 소재 지정' if initial else '다음에 넣을 소재 선택'),size=13,bold=True).pack(padx=22,pady=(18,10))
        self.label(dialog,('이미 기계에 들어 있는 소재입니다.\n현재 재고는 차감하지 않습니다.' if initial else '현재 기록: '+material_label(row['material_type'])+'\n선택한 소재는 다음 소재교체부터 적용됩니다.'),color=PALETTE['muted']).pack(padx=22,pady=(0,12))
        chosen=self.tk.StringVar(value=material_label(row.get('next_type') or row.get('material_type') or DEFAULT_MATERIAL_TYPE))
        combo=self.ttk.Combobox(dialog,style='Round.TCombobox',textvariable=chosen,values=list(MATERIAL_TYPES.values()),state='readonly',width=22)
        combo.pack(padx=22,pady=6)
        def save():
            key=next(k for k,v in MATERIAL_TYPES.items() if v==chosen.get())
            try:
                if initial:self.store.assign_material(n,key)
                else:self.store.set_next_type(n,key)
                self.dirty_history=True
                self.refresh()
                self.tell('{}호기 {}: {}'.format(n,'현재 소재 지정' if initial else '다음 교체 소재 예약',material_label(key)))
                dialog.destroy()
            except ValueError as e:messagebox.showerror('소재 지정',str(e),parent=dialog)
            except sqlite3.Error as e:
                dialog.destroy();self.storage_error(e)
        self.button(dialog,'적용',save,primary=True).pack(pady=(10,18))
        dialog.grab_set();combo.focus_set()

    def _period_build(self):
        """Compact Jihunius-style dashboard; every primary measure shares one rod cohort."""
        panel=self.tk.Frame(self.period_tab,bg=PALETTE['bg'])
        panel.pack(fill='both',expand=True,padx=8,pady=(10,6))
        panel.grid_columnconfigure(0,weight=1)
        panel.grid_rowconfigure(5,weight=1,minsize=160)
        bar=self.tk.Frame(panel,bg=PALETTE['bg'])
        bar.grid(row=0,column=0,sticky='ew',pady=(0,5))
        self.period_controls=bar
        now=datetime.now()
        self.date_from=self.tk.StringVar(value=now.replace(day=1).strftime('%Y-%m-%d'))
        self.date_to=self.tk.StringVar(value=now.strftime('%Y-%m-%d'))
        for variable in (self.date_from,self.date_to):
            entry=self.ttk.Entry(bar,textvariable=variable,width=11,style='Round.TEntry',font=(self.font,10))
            entry.pack(side='left',ipady=3,padx=(0,5))
            entry.bind('<Return>',lambda e:self.refresh_period())
            if variable is self.date_from:self.label(bar,'~').pack(side='left',padx=(0,5))
        self.period_previous_button=self.button(bar,'<',lambda:self.shift_period_month(-1))
        self.period_previous_button.configure(padx=6)
        self.period_previous_button.pack(side='left',padx=(3,2))
        self.period_month_button=self.button(bar,'월 선택',self.open_period_month)
        self.period_month_button.configure(padx=8,width=11)
        self.period_month_button.pack(side='left')
        self.period_next_button=self.button(bar,'>',lambda:self.shift_period_month(1))
        self.period_next_button.configure(padx=6)
        self.period_next_button.pack(side='left',padx=(2,5))
        for variable in (self.date_from,self.date_to):
            variable.trace_add('write',lambda *args:self._period_month_label())
        self._period_month_label()
        self.period_machine=self.tk.StringVar(value='전체 호기')
        machines=self.ttk.Combobox(bar,style='Round.TCombobox',textvariable=self.period_machine,values=['전체 호기']+['{}호기'.format(n) for n in MACHINES],width=9,state='readonly')
        machines.pack(side='left',padx=4)
        machines.bind('<<ComboboxSelected>>',lambda e:self.refresh_period())
        self.button(bar,'조회',self.refresh_period,primary=True).pack(side='left',padx=3)
        self.button(bar,'오늘',lambda:self.period_preset('today')).pack(side='left',padx=3)
        self.button(bar,'이번 달',lambda:self.period_preset('month')).pack(side='left',padx=3)
        self.button(bar,'CSV 저장',self.export_period).pack(side='right')
        self.period_scope=self.label(panel,'기간 내 사용을 끝낸 소재 기준',color=PALETTE['muted'],size=9,anchor='w')
        self.period_scope.grid(row=1,column=0,sticky='ew',pady=(0,6))
        cards=self.tk.Frame(panel,bg=PALETTE['bg'])
        cards.grid(row=2,column=0,sticky='ew')
        self.period_cards={}
        for i,(key,title,color,detail) in enumerate((
                ('good','봉당 양품',PALETTE['green'],'양품 합계 ÷ 평균 대상 봉'),
                ('defects','봉당 불량',PALETTE['red'],'불량 합계 ÷ 평균 대상 봉'),
                ('consumed','소모 소재',PALETTE['text'],'소재교체로 사용을 끝낸 봉'),
                ('diameter10','Ø10 사용 소재',PALETTE['text'],'Z급 · B급 합산'),
                ('diameter12','Ø12 사용 소재',PALETTE['text'],'기간 내 사용을 끝낸 봉'),
                ('diameter14','Ø14 사용 소재',PALETTE['text'],'기간 내 사용을 끝낸 봉'))):
            column=i%3
            cards.grid_columnconfigure(column,weight=1,uniform='period_cards')
            card=self.rounded_panel(cards,border=PALETTE['line'])
            card.grid(row=i//3,column=column,sticky='nsew',padx=(0 if column==0 else 4,0 if column==2 else 4),pady=(0 if i<3 else 8,0))
            self.label(card,title,bold=True,size=10,bg=PALETTE['card'],anchor='w').pack(fill='x',padx=12,pady=(11,0))
            value=self.label(card,'—',bold=True,size=22,color=color,bg=PALETTE['card'],anchor='w')
            value.pack(fill='x',padx=12)
            note=self.label(card,detail,size=9,color=PALETTE['muted'],bg=PALETTE['card'],anchor='w')
            note.pack(fill='x',padx=12,pady=(0,10))
            self.period_cards[key]=(value,note)
        self.period_summary=self.label(panel,'조회하면 평균 산정 수량과 제외한 봉 수를 확인할 수 있습니다.',anchor='w',size=9,color=PALETTE['muted'])
        self.period_summary.grid(row=3,column=0,sticky='ew',pady=(7,5))
        modebar=self.tk.Frame(panel,bg=PALETTE['bg'])
        modebar.grid(row=4,column=0,sticky='ew',pady=(0,4))
        self.period_group=self.tk.StringVar(value='소재별')
        self.period_group_buttons={}
        for name in ('소재별','호기별','일별'):
            button=self.button(modebar,name,lambda value=name:self._period_set_group(value))
            button.configure(pady=4,padx=14)
            button.pack(side='left',padx=(0,5))
            self.period_group_buttons[name]=button
        self.period_table_caption=self.label(modebar,'소모 봉의 양품·불량 관측 합계',size=9,color=PALETTE['muted'])
        self.period_table_caption.pack(side='right')
        self.report_tree=self._period_table(panel,5,
            ('name','consumed','good','defects','avg_good','avg_defects','eligible','excluded'),
            ('소재 / 호기','소모 봉','양품 합계','불량 합계','봉당 양품','봉당 불량','평균 대상','평균 제외'),
            (125,80,100,95,100,100,85,85))
        self.daily_tree=self._period_table(panel,5,
            ('day','consumed','good','defects','avg_good','avg_defects','eligible'),
            ('종료일','소모 봉','양품 합계','불량 합계','봉당 양품','봉당 불량','평균 대상'),
            (140,85,110,105,110,110,100))
        self.period_observed=self.label(panel,'기간 중 수집 · 조회 대기',size=9,color=PALETTE['muted'],anchor='w')
        self.period_observed.grid(row=6,column=0,sticky='ew',pady=(7,4))
        self.period_hint=self.label(panel,
            '봉당 평균: 이 기간에 사용을 끝낸 봉의 처음부터 끝까지 수량으로 계산합니다. 사용 중·보관 중인 봉은 종료 후 반영됩니다.\n가공량이 적어도 교체한 봉은 1봉으로 포함하며, 중간 시작·수집 공백·불량초과 봉은 평균에서 제외합니다.',
            color=PALETTE['muted'],size=9,anchor='w',justify='left',wraplength=900)
        self.period_hint.grid(row=7,column=0,sticky='ew')
        panel.bind('<Configure>',lambda e:self.period_hint.configure(wraplength=max(400,e.width-10)))
        self._period_report=None
        self._period_request=0
        self._period_set_group('소재별')

    def _period_table(self,parent,row,columns,headings,widths):
        frame=self.rounded_panel(parent,fill=PALETTE['field'],radius=13,border=PALETTE['line'])
        frame.grid(row=row,column=0,sticky='nsew')
        frame.grid_rowconfigure(0,weight=1)
        frame.grid_columnconfigure(0,weight=1)
        self.ttk.Style(self.root).configure('Period.Treeview',rowheight=26)
        tree=self.ttk.Treeview(frame,columns=columns,show='headings',height=3,selectmode='browse',style='Period.Treeview')
        for key,title,width in zip(columns,headings,widths):
            tree.heading(key,text=title)
            tree.column(key,width=width,minwidth=width,anchor='center',stretch=True)
        vertical=self.ttk.Scrollbar(frame,orient='vertical',command=tree.yview)
        horizontal=self.ttk.Scrollbar(frame,orient='horizontal',command=tree.xview)
        tree.configure(yscrollcommand=vertical.set,xscrollcommand=horizontal.set)
        tree.grid(row=0,column=0,sticky='nsew',padx=(8,0),pady=(8,0))
        vertical.grid(row=0,column=1,sticky='ns',padx=(0,8),pady=(8,0))
        horizontal.grid(row=1,column=0,sticky='ew',padx=(8,0),pady=(0,8))
        tree.tag_configure('warning',foreground=PALETTE['yellow'])
        tree.tag_configure('total',background=PALETTE['selected'],foreground='white')
        return tree

    def _period_set_group(self,value):
        self.period_group.set(value)
        for name,button in self.period_group_buttons.items():
            button.configure(bg=PALETTE['selected'] if name==value else PALETTE['card'])
        if value=='일별':
            self.report_tree.master.grid_remove()
            self.daily_tree.master.grid()
            self.period_table_caption.configure(text='소재 사용 종료일별 · 기간 합계와 같은 기준')
        else:
            self.daily_tree.master.grid_remove()
            self.report_tree.master.grid()
            self.period_table_caption.configure(text='소모 봉의 양품·불량 관측 합계')
        if self._period_report is not None:self._render_period_rows(self._period_report)

    def _render_period_rows(self,report):
        old=self.report_tree.get_children()
        if old:self.report_tree.delete(*old)
        group='호기별' if self.period_group.get()=='호기별' else '소재별'
        rows=report['by_type'] if group=='소재별' else report['by_machine']
        for row in [dict(report['totals'],label='전체',_total=True)]+rows:
            name='전체' if row.get('_total') else (row['label'] if group=='소재별' else '{}호기'.format(row['machine']))
            self.report_tree.insert('','end',values=(name,
                '{:,}'.format(row['consumed_rods']),
                '{:,}'.format(row['completed_good']),'{:,}'.format(row['completed_defects']),
                average_text(row['avg_good_per_rod']),average_text(row['avg_defects_per_rod']),
                '{:,}'.format(row['eligible_rods']),'{:,}'.format(row['excluded_rods'])),
                tags=('total',) if row.get('_total') else (('warning',) if row['excluded_rods'] else ()))

    def _render_period(self,report):
        self._period_report=report
        total=report['totals']
        machine=report['machine']
        period='{} ~ {}'.format(datetime.fromtimestamp(report['start']).strftime('%Y-%m-%d'),
                              (datetime.fromtimestamp(report['end'])-timedelta(days=1)).strftime('%Y-%m-%d'))
        self.period_scope.configure(text='{}  ·  {}  ·  기간 내 사용을 끝낸 소재 기준'.format(period,'전체 호기' if machine is None else '{}호기'.format(machine)))
        self.period_cards['good'][0].configure(text=average_text(total['avg_good_per_rod'])+(' 개' if total['avg_good_per_rod'] is not None else ''))
        self.period_cards['defects'][0].configure(text=average_text(total['avg_defects_per_rod'])+(' 개' if total['avg_defects_per_rod'] is not None else ''))
        self.period_cards['consumed'][0].configure(text='{:,} 봉'.format(total['consumed_rods']))
        self.period_cards['consumed'][1].configure(text='소재교체로 사용을 끝낸 봉')
        by_type={row['type_id']:row['consumed_rods'] for row in report['by_type']}
        for diameter,kinds in (('10',('10Z','10B')),('12',('12',)),('14',('14',))):
            value,note=self.period_cards['diameter'+diameter]
            value.configure(text='{:,} 봉'.format(sum(by_type.get(kind,0) for kind in kinds)))
            note.configure(text='Z급 {:,}봉 · B급 {:,}봉'.format(by_type.get('10Z',0),by_type.get('10B',0)) if diameter=='10' else '기간 내 사용을 끝낸 봉')
        self.period_cards['good'][1].configure(text='양품 {:,}개 ÷ {:,}봉'.format(total['eligible_good'],total['eligible_rods']) if total['eligible_rods'] else '평균을 계산할 측정 봉 없음')
        self.period_cards['defects'][1].configure(text='불량 {:,}개 ÷ {:,}봉'.format(total['eligible_defects'],total['eligible_rods']) if total['eligible_rods'] else '평균을 계산할 측정 봉 없음')
        self.period_summary.configure(text='소모 {:,}봉 중 평균 대상 {:,}봉  ·  평균 제외 {:,}봉 (중간 시작 / 수집 공백 / 불량초과)'.format(
            total['consumed_rods'],total['eligible_rods'],total['excluded_rods']),
            fg=PALETTE['yellow'] if total['excluded_rods'] else PALETTE['muted'])
        self._render_period_rows(report)
        old=self.daily_tree.get_children()
        if old:self.daily_tree.delete(*old)
        for row in report['daily']:
            if not row['consumed_rods']:continue
            self.daily_tree.insert('','end',values=(row['day'],'{:,}'.format(row['consumed_rods']),
                '{:,}'.format(row['completed_good']),'{:,}'.format(row['completed_defects']),
                average_text(row['avg_good_per_rod']),average_text(row['avg_defects_per_rod']),'{:,}'.format(row['eligible_rods'])),
                tags=('warning',) if row['excluded_rods'] else ())
        self.period_observed.configure(text='기간 중 수집: 관측 가공 {:,}회 · 불량 입력 {:,}개 · 새 봉 투입 {:,}봉  |  사용 중인 봉도 포함'.format(
            total['production'],total['defects'],total['loaded_rods']))
        if not total['consumed_rods']:
            self.period_summary.configure(text='이 기간에 사용을 끝낸 소재가 없습니다. 소재교체 후 봉당 수량이 표시됩니다.',fg=PALETTE['muted'])
        elif not total['eligible_rods']:
            self.period_summary.configure(text='소모 {:,}봉 모두 측정이 불완전하여 봉당 평균을 계산하지 않았습니다. 양품·불량 관측 합계는 표에 보존됩니다.'.format(total['consumed_rods']),fg=PALETTE['yellow'])

    def _period_month_anchor(self):
        for variable in (self.date_from,self.date_to):
            try:return datetime.strptime(variable.get().strip(),'%Y-%m-%d')
            except ValueError:pass
        return datetime.now()

    def _period_month_label(self):
        text='월 선택'
        try:
            begin=datetime.strptime(self.date_from.get().strip(),'%Y-%m-%d')
            end=datetime.strptime(self.date_to.get().strip(),'%Y-%m-%d')
            if begin.day==1 and (begin.year,begin.month)==(end.year,end.month) and end.day==calendar.monthrange(begin.year,begin.month)[1]:
                text='{}년 {}월'.format(begin.year,begin.month)
        except ValueError:pass
        self.period_month_button.configure(text=text)

    def select_period_month(self,year,month):
        # Keep the inclusive last day in the fields; period_range supplies the
        # next midnight to the existing asynchronous report query.
        if not 1<=year<=9998 or not 1<=month<=12:return
        last=calendar.monthrange(year,month)[1]
        self.date_from.set('{:04d}-{:02d}-01'.format(year,month))
        self.date_to.set('{:04d}-{:02d}-{:02d}'.format(year,month,last))
        self.refresh_period()

    def shift_period_month(self,offset):
        anchor=self._period_month_anchor()
        year,month=divmod(anchor.year*12+anchor.month-1+offset,12)
        self.select_period_month(year,month+1)

    def open_period_month(self):
        existing=getattr(self,'_month_dialog',None)
        if existing is not None and existing.winfo_exists():
            existing.lift();existing.focus_force();return
        anchor=self._period_month_anchor()
        dialog=self.tk.Toplevel(self.root);self._month_dialog=dialog
        dialog.title('월 선택');dialog.configure(bg=PALETTE['bg'])
        dialog.transient(self.root);dialog.resizable(False,False)
        year=self.tk.IntVar(value=min(anchor.year,9998))
        header=self.tk.Frame(dialog,bg=PALETTE['bg']);header.pack(fill='x',padx=16,pady=(14,8))
        def move_year(offset):
            value=year.get()+offset
            if 1<=value<=9998:year.set(value);paint()
        previous=self.button(header,'<',lambda:move_year(-1));previous.pack(side='left')
        caption=self.label(header,bold=True,size=13);caption.pack(side='left',expand=True)
        following=self.button(header,'>',lambda:move_year(1));following.pack(side='right')
        months=self.tk.Frame(dialog,bg=PALETTE['bg']);months.pack(padx=16,pady=(0,14))
        def choose(month):
            value=year.get();dialog.destroy();self.select_period_month(value,month)
        self._month_buttons=[]
        for month in range(1,13):
            button=self.button(months,str(month)+'월',lambda value=month:choose(value))
            button.configure(width=5)
            button.grid(row=(month-1)//4,column=(month-1)%4,padx=3,pady=3)
            self._month_buttons.append(button)
        def paint():
            caption.configure(text=str(year.get())+'년')
            previous.configure(state='normal' if year.get()>1 else 'disabled')
            following.configure(state='normal' if year.get()<9998 else 'disabled')
            for month,button in enumerate(self._month_buttons,1):
                button.configure(bg=PALETTE['blue'] if (year.get(),month)==(anchor.year,anchor.month) else PALETTE['card'])
        paint()
        dialog.bind('<Escape>',lambda event:dialog.destroy())
        dialog.update_idletasks()
        x=self.root.winfo_rootx()+(self.root.winfo_width()-dialog.winfo_reqwidth())//2
        y=self.root.winfo_rooty()+(self.root.winfo_height()-dialog.winfo_reqheight())//2
        dialog.geometry('+{}+{}'.format(x,y))
        dialog.grab_set();self._month_buttons[anchor.month-1].focus_set()

    def period_preset(self,kind):
        now=datetime.now()
        if kind=='month':self.select_period_month(now.year,now.month);return
        self.date_from.set(now.strftime('%Y-%m-%d'))
        self.date_to.set(now.strftime('%Y-%m-%d'))
        self.refresh_period()

    def refresh_period(self):
        if not hasattr(self,'report_tree'):return
        try:begin,end,machine=self.period_range()
        except ValueError as e:self.tell(str(e),error=True);return
        self._period_request+=1
        request=self._period_request
        self._period_report=None
        for value,note in self.period_cards.values():
            value.configure(text='…')
            note.configure(text='계산 중')
        for tree in (self.report_tree,self.daily_tree):
            old=tree.get_children()
            if old:tree.delete(*old)
        self.period_scope.configure(text='통계 조회 중 · 수집은 계속됩니다.')
        self.period_summary.configure(text='소모 소재와 봉당 양품·불량을 계산하고 있습니다.',fg=PALETTE['muted'])
        self.period_observed.configure(text='기간 중 수집 · 계산 중')
        def ready(report):
            if request!=self._period_request or self.closed:return
            try:current_range=self.period_range()
            except ValueError:current_range=None
            if current_range!=(begin,end,machine):
                for value,note in self.period_cards.values():
                    value.configure(text='—');note.configure(text='다시 조회해주세요')
                self.period_scope.configure(text='조회 조건이 변경되었습니다. 조회 버튼을 눌러주세요.')
                self.period_summary.configure(text='변경된 날짜 범위를 확인한 뒤 다시 조회해주세요.',fg=PALETTE['muted'])
                self.period_observed.configure(text='기간 중 수집 · 조회 대기')
                return
            self._render_period(report)
        def failed(error):
            if request!=self._period_request or self.closed:return
            for value,note in self.period_cards.values():
                value.configure(text='—');note.configure(text='다시 조회해주세요')
            self.period_scope.configure(text='통계를 불러오지 못했습니다. 다시 조회해주세요.')
            self.period_summary.configure(text=str(error)[:150],fg=PALETTE['red'])
            self.period_observed.configure(text='기간 중 수집 · 조회 실패')
            self.tell('통계 조회 실패: '+str(error)[:150],error=True)
        if not self.run_report_job(lambda store:store.period_report(begin,end,machine),ready,failed):
            failed('다른 작업을 처리 중입니다. 잠시 후 다시 조회해주세요.')

    def export_period(self):
        from tkinter import filedialog
        try:begin,end,machine=self.period_range()
        except ValueError as e:self.tell(str(e),error=True);return
        path=filedialog.asksaveasfilename(parent=self.root,title='소재 사용·봉당 양품과 불량 통계 저장',defaultextension='.csv',
            initialfile='소재통계_'+self.date_from.get()+'_'+self.date_to.get()+'.csv',filetypes=[('CSV','*.csv')])
        if not path:return
        self.tell('기간 통계를 CSV로 저장하고 있습니다. 수집은 계속됩니다.')
        self.run_report_job(lambda store:store.export_period(path,begin,end,machine),
                            lambda result:self.tell('기간 통계를 CSV로 저장했습니다.'))


    def period_range(self):
        try:
            begin=datetime.strptime(self.date_from.get().strip(),'%Y-%m-%d')
            finish=datetime.strptime(self.date_to.get().strip(),'%Y-%m-%d')
        except ValueError:
            raise ValueError('날짜를 YYYY-MM-DD 형식으로 입력해주세요.')
        if finish<begin:raise ValueError('종료일은 시작일 이후여야 합니다.')
        selection=self.period_machine.get()
        machine=None if selection=='전체 호기' else int(selection[:-2])
        return begin.timestamp(),(finish+timedelta(days=1)).timestamp(),machine




    def export_movements(self):
        from tkinter import filedialog,messagebox
        path=filedialog.asksaveasfilename(parent=self.root,title='전체 입출고 이력 저장',defaultextension='.csv',
            initialfile='소재입출고_'+datetime.now().strftime('%Y%m%d')+'.csv',filetypes=[('CSV','*.csv')])
        if not path:return
        self.run_report_job(lambda view:view.export_movements(path),
                            lambda result:self.tell('전체 입출고 이력을 저장했습니다.'))

    def backup_data(self):
        from tkinter import filedialog,messagebox
        path=filedialog.asksaveasfilename(parent=self.root,title='전체 데이터 백업 저장',defaultextension='.sqlite3',
            initialfile='소재관리_백업_'+datetime.now().strftime('%Y%m%d_%H%M%S')+'.sqlite3',filetypes=[('SQLite 데이터','*.sqlite3')])
        if not path:return
        def work(view):
            destination=view.validate_export_path(path)
            temporary=destination.with_name('.'+destination.name+'.'+uuid.uuid4().hex+'.tmp')
            try:
                target=sqlite3.connect(str(temporary))
                try:
                    view.db.backup(target)
                    if target.execute('PRAGMA quick_check').fetchone()[0]!='ok':
                        raise sqlite3.DatabaseError('백업 파일을 검증하지 못했습니다.')
                finally:target.close()
                os.replace(str(temporary),str(destination))
            finally:
                if temporary.exists():temporary.unlink()
        self.run_report_job(work,lambda result:self.tell('전체 데이터 백업을 저장했습니다.'))

    def _tree(self,parent,columns,headings,widths,height):
        frame=self.rounded_panel(parent,fill=PALETTE['field'],radius=13,border=PALETTE['line'])
        frame.pack(fill='both',expand=True,padx=4)
        tree=self.ttk.Treeview(frame,columns=columns,show='headings',height=height,selectmode='browse')
        for key,text,width in zip(columns,headings,widths):
            tree.heading(key,text=text)
            tree.column(key,width=width,minwidth=40,anchor='center',stretch=True)
        scroll=self.ttk.Scrollbar(frame,orient='vertical',command=tree.yview)
        tree.configure(yscrollcommand=scroll.set)
        tree.pack(side='left',fill='both',expand=True,padx=(8,0),pady=8)
        scroll.pack(side='right',fill='y',padx=(0,8),pady=8)
        return tree

    def _selected_machine(self):
        value=self.filter.get()
        return None if value=='전체 호기' else int(value[:-2])

    def tick(self):
        if self.closed:
            return
        try:
            self._finish_jobs()
            if self.failed_storage or self.resetting:return
            for _ in range(100):
                try:
                    event=self.queue.get_nowait()
                except queue.Empty:
                    break
                self.handle(event)
            now=time.time()
            for n in (list(self.store.live) if self.queue.empty() else []):
                seen=self.store._machine(n)['last_seen']
                if seen is not None and now-seen>GAP_SECONDS:
                    self.store.disconnected(n,now,'새 데이터가 도착하지 않음')
                    self.errors[n]='수집 지연'
                    self.dirty_history=True
            for n,(token,started,early) in list(self.pending.items()):
                if now-started>TIMEOUT*2+INTERVAL+3:
                    del self.pending[n]
                    self.tell('{}호기: 교체 요청 시간이 초과됐습니다. 저장되지 않았습니다.'.format(n),error=True)
            self.refresh()
            if self.tabs.select()==str(self.history_tab):
                self.refresh_history()
            elif self.tabs.select()==str(self.inventory_tab) and self.dirty_inventory:
                self.refresh_inventory()
        except sqlite3.Error as e:
            self.storage_error(e)
        finally:
            if not self.closed:
                self.root.after(200,self.tick)

    def handle(self,event,draining=False):
        if event[0]=='server':
            self.server_ok,self.server_detail=event[1:]
            return
        kind,ip,generation,record,at,token,error=event
        # Collector serializes sample publication and removal under one lock.
        # Consume published samples in FIFO order, even after their worker retires.
        # Reset creates a new queue so previous-session samples cannot enter it.
        old=self.sources.get(ip)
        changed=False
        machine=record['machine'] if record else (old[0] if old else None)
        if kind=='removed' and old and old[1]!=generation:
            return
        if record and old and old[0]!=machine:
            self.store.disconnected(old[0],at,'머신 주소의 호기 번호가 바뀜')
        if record:
            self.sources[ip]=(machine,generation)
            changed=self.store.observe(record,at)
            self.errors.pop(machine,None)
            self.source_errors.pop(ip,None)
        else:
            self.source_errors[ip]=error
            if machine:
                changed=machine in self.store.live
                self.store.disconnected(machine,at,error)
                self.errors[machine]=error
        if token:
            target=next((n for n,v in self.pending.items() if v[0]==token),None)
            if target is not None:
                early=self.pending.pop(target)[2]
                try:
                    if not record or machine!=target:
                        raise ValueError(error or '호기 정보를 확인할 수 없습니다.')
                    self.store.rotate(target,time.time(),early=early)
                    changed=True
                    self.dirty_inventory=True
                    self.tell('{}호기 {}: 기록 저장{} · 가공·불량 0부터 시작 · 새 봉 재고 1봉 차감'.format(target,'중도교체' if early else '소재교체',' / 파기 1봉 집계' if early else ''))
                except ValueError as e:
                    self.tell('{}호기: {}'.format(target,e),error=True)
        self.dirty_history=self.dirty_history or changed

    def refresh(self):
        now=time.time()
        online,total,good,defects=0,0,0,0
        for n,widgets in self.rows.items():
            row=self.store.snapshot(n)
            age=None if row['last_seen'] is None else now-row['last_seen']
            fresh=n in self.store.live and age is not None and 0<=age<=FRESH_SECONDS
            recent=age is not None and 0<=age<=DISPLAY_STALE_SECONDS
            online+=int(recent)
            total+=row['total']; good+=row['good']; defects+=row['defects']
            state=STATES.get(row['state'],'연결 대기') if fresh else ('갱신 대기' if recent else ('연결 끊김' if row['program'] else '연결 대기'))
            color=PALETTE['green'] if fresh and row['state']=='RUN' else (PALETTE['yellow'] if fresh else PALETTE['muted'])
            if fresh and row['state']=='ALARM':color=PALETTE['red']
            widgets['state'].configure(text=state,fg=color)
            excluded=bool(row['program']) and not countable_program(row['program'])
            program_text=('O'+row['program']+('\n집계 제외' if excluded else '')) if row['program'] else '—'
            widgets['program'].configure(text=program_text,fg=PALETTE['yellow'] if fresh and excluded else (PALETTE['text'] if fresh else PALETTE['muted']))
            widgets['total'].configure(text=str(row['good']))
            widgets['defects'].configure(text=str(row['defects']),fg=PALETTE['yellow'] if row['defects'] else PALETTE['muted'])
            flags=[]
            if row['defect_excess']:flags.append('불량초과 {}'.format(row['defect_excess']))
            if row['partial']:flags.append('중간 시작')
            if row['gap']:flags.append('누락 가능')
            caption=material_label(row['material_type']) if row['material_type'] else '소재 지정'
            if row['next_type'] and row['next_type']!=row['material_type']:
                caption+='\n다음 '+material_label(row['next_type'])
            else:
                caption+='\n'+(' · '.join(flags) if flags else (datetime.fromtimestamp(row['started']).strftime('%m/%d %H:%M') if row['started'] else '첫 데이터 대기'))
            widgets['material'].configure(text=caption,fg=PALETTE['yellow'] if row['gap'] else ('#60a5fa' if not row['material_type'] else PALETTE['text']))
            if self.dashboard_actions:
                actions=self.action_availability(n,row,now)
                widgets['rotate'].configure(text='확인 중…' if n in self.pending else '소재교체',state='normal' if actions['rotate'] else 'disabled')
                widgets['defect'].configure(state='normal' if actions['defect'] else 'disabled')
        self.summary.configure(text='최근 응답 {} / 9호기   |   진행 중 양품 {:,}개   |   가공 {:,}회   |   불량 {:,}개'.format(online,good,total,defects))
        if self.failed_storage:
            self.footer.configure(text='저장 오류로 수집 중단 · 저장 공간/권한을 확인한 뒤 프로그램을 다시 실행해주세요.',fg=PALETTE['red'])
        elif online==0:
            detail=next(iter(self.source_errors.values()),self.server_detail)
            self.footer.configure(text='연결 대기 · {} · {}'.format(HOST,detail[:65]),fg=PALETTE['yellow'])
        else:
            self.footer.configure(text='이 PC에 자동 저장  ·  3초 간격 조회  ·  최소화해도 수집 계속',fg=PALETTE['muted'])

    def action_availability(self,n,row=None,now=None):
        row=self.store.snapshot(n) if row is None else row
        now=time.time() if now is None else now
        age=None if row['last_seen'] is None else now-row['last_seen']
        fresh=n in self.store.live and age is not None and 0<=age<=FRESH_SECONDS
        ready=n not in self.pending and not self.failed_storage and not self.resetting and not row.get('mass_mode',False)
        return dict(rotate=bool(ready and fresh),defect=bool(ready and row['good']>0))

    def tell(self,text,error=False):
        self.notice.configure(text=text,fg=PALETTE['red'] if error else PALETTE['green'])

    def _debounce(self,n,kind):
        key=(n,kind)
        now=time.monotonic()
        if now-self.last_click.get(key,-10)<0.65:return False
        self.last_click[key]=now
        return True

    def defect(self,n):
        if n in self.pending or self.failed_storage or self.resetting:return
        try:
            self.store.defect(n)
            self.dirty_history=True
            self.tell('{}호기: 양품 −1 / 불량 +1 · 전체 가공 횟수는 그대로입니다.'.format(n))
            self.refresh()
        except ValueError as e:self.tell(str(e),error=True)
        except sqlite3.Error as e:self.storage_error(e)

    def rotate(self,n,early=False):
        if self.failed_storage or self.resetting or not self._debounce(n,'rotate') or n in self.pending:return
        try:
            row=self.store.snapshot(n)
            if not row['material_type']:
                self.material_dialog(n)
                self.tell('{}호기 소재를 지정한 뒤 소재교체를 눌러주세요.'.format(n))
                return
            if row['state']=='RUN':
                raise ValueError('머신이 멈춘 뒤 소재교체를 눌러주세요.')
            token=uuid.uuid4().hex
            self.pending[n]=(token,time.time(),early)
            self.collector.checkpoint(n,token)
            self.tell('{}호기 최신 상태를 확인하는 중입니다.'.format(n))
            self.refresh()
        except ValueError as e:
            self.pending.pop(n,None)
            self.tell(str(e),error=True)

    def context(self,event,n):
        menu=self.tk.Menu(self.root,tearoff=0,bg=PALETTE['card'],fg=PALETTE['text'])
        menu.add_command(label='소재 지정 / 다음 소재 선택',state='normal' if n not in self.pending and not self.failed_storage and not self.resetting else 'disabled',command=lambda:self.material_dialog(n))
        label=self.store.undo_label(n)
        menu.add_command(label=label or '취소할 수동 입력 없음',state='normal' if label and n not in self.pending and not self.failed_storage and not self.resetting else 'disabled',command=lambda:self.undo(n))
        menu.add_command(label='{}호기 수집 이력 보기'.format(n),command=lambda:self.show_machine(n))
        try:menu.tk_popup(event.x_root,event.y_root)
        finally:menu.grab_release()

    def undo(self,n):
        from tkinter import messagebox
        if n in self.pending or self.failed_storage or self.resetting:return
        label=self.store.undo_label(n)
        if not messagebox.askyesno('입력 취소','{}호기의 {}를 진행할까요?\n자동 수집 이력은 유지됩니다.'.format(n,label),parent=self.root):return
        try:
            self.store.undo(n)
            self.dirty_history=True
            self.dirty_inventory=True
            self.tell('{}호기: {}'.format(n,label))
            self.refresh(); self.refresh_history(force=True); self.refresh_inventory()
        except ValueError as e:self.tell(str(e),error=True)
        except sqlite3.Error as e:self.storage_error(e)

    def show_machine(self,n):
        self.filter.set('{}호기'.format(n))
        self.tabs.select(self.history_tab)
        self.refresh_history(force=True)

    def refresh_history(self,force=False):
        if not self.dirty_history and not force:return
        n=self._selected_machine()
        for tree in (self.history_tree,self.event_tree):
            children=tree.get_children()
            if children:tree.delete(*children)
        for r in self.store.history(n):
            flags=[]
            if r['early_end']:flags.append('중도교체')
            if r['partial']:flags.append('중간 시작')
            if r['gap']:flags.append('누락 가능')
            if r['defect_excess']:flags.append('불량초과 {}'.format(r['defect_excess']))
            self.history_tree.insert('', 'end',values=(r['id'],'{}호기'.format(r['machine']),material_label(r['material_type']),date_text(r['started'],True),date_text(r['ended'],True),r['total'],r['good'],r['defects'],' · '.join(flags) or '전체 구간'))
        self.event_details={}
        for r in self.store.events(n):
            program=('O'+r['previous']+' → ' if r['previous'] else '')+('O'+r['program'] if r['program'] else '—')
            label=EVENT_NAMES.get(r['kind'],r['kind'])+(' (취소됨)' if r['undone'] else '')
            item=self.event_tree.insert('','end',values=(date_text(r['at'],True),'{}호기'.format(r['machine']),label,program))
            self.event_details[item]=r
        self.dirty_history=False

    def event_detail(self,event=None):
        from tkinter import messagebox
        selected=self.event_tree.selection()
        if not selected:return
        r=self.event_details.get(selected[0])
        if not r:return
        messagebox.showinfo('수집 이력','{}\n{}호기 · {}\n작업번호: {} → {}\n상태: {}\n\n{}'.format(date_text(r['at']),r['machine'],EVENT_NAMES.get(r['kind'],r['kind']),r['previous'] or '—',r['program'],r['state'],r['note']),parent=self.root)

    def export(self):
        from tkinter import filedialog, messagebox
        path=filedialog.asksaveasfilename(parent=self.root,title='전체 소재 기록 내보내기',defaultextension='.csv',initialfile='소재기록_'+datetime.now().strftime('%Y%m%d')+'.csv',filetypes=[('CSV','*.csv')])
        if not path:return
        self.run_report_job(lambda view:view.export_materials(path),
                            lambda result:self.tell('전체 소재 기록을 CSV로 저장했습니다.'))

    def diagnostics(self):
        from tkinter import filedialog,messagebox
        path=filedialog.asksaveasfilename(parent=self.root,title='확인용 데이터 저장',defaultextension='.json',initialfile='소재카운터_확인_'+datetime.now().strftime('%Y%m%d_%H%M%S')+'.json',filetypes=[('JSON','*.json')])
        if not path:return
        try:
            payload=dict(version=VERSION,saved_at=date_text(time.time()),host=HOST,
                         count_rule='observed transition into eligible number: machining/good +1; 1000..9999 except 3999/9012/9020/9999; return after 9020 to the same number +0, a different eligible number +1; return after other numbers counts as rework; repeated same polling +0; manual defect: good -1/defect +1, machining unchanged; early-discard rods count as one consumed rod and enter good/defect averages; completed-cohort averages exclude partial/gap/excess-defect rods; site part_count ignored and not recorded in new events',
                         server=self.server_detail,errors=self.errors,source_errors=self.source_errors,
                         machines=[self.store.snapshot(n) for n in MACHINES],
                         materials=self.store.history(),events=self.store.events(limit=1000),
                         inventory=self.store.inventory(),stock_movements=self.store.movements(limit=1000))
            self.store.validate_export_path(path)
            Path(path).write_text(json.dumps(payload,ensure_ascii=False,indent=2),encoding='utf-8')
            self.tell('확인용 데이터를 저장했습니다. 문제가 있으면 이 파일을 보내주세요.')
        except Exception as e:messagebox.showerror('저장 실패',str(e),parent=self.root)

    def open_folder(self):
        from tkinter import messagebox
        try:
            if os.name=='nt':os.startfile(str(self.folder))
            else:messagebox.showinfo('저장 폴더',str(self.folder),parent=self.root)
        except OSError as e:messagebox.showerror('폴더 열기 실패',str(e),parent=self.root)

    def help(self):
        from tkinter import messagebox
        messagebox.showinfo('사용 안내',
          '1. 소재 재고 탭: Ø10 Z급 / Ø10 B급 / Ø12 / Ø14 보관 봉 수를 등록합니다.\n'
          '   이미 기계에 들어 있는 봉은 제외합니다. 추가 입고와 재고 수정도 기록됩니다.\n'
          '2. 현재 집계의 소재명 클릭: 이미 투입된 소재를 지정합니다. 최초 지정은 재고 차감 없음.\n'
          '   지정 후 다시 클릭하면 다음 교체에 넣을 소재를 예약합니다.\n'
          '3. 4자리 작업번호만 비교해 번호 변경마다 가공 +1. 3999·9012·9020·9999는 제외합니다.\n'
          '   1061→3999→1061은 재가공 +1. 1061→9020→1061과 같은 번호 반복 조회는 +0입니다.\n'
          '4. 불량 +1: 이미 집계한 양품 1개를 불량으로 변경합니다. 양품 -1, 불량 +1, 전체 가공은 그대로.\n'
          '   양품은 가공 횟수에서 불량을 뺀 수입니다. 양품이 0이면 불량 추가를 막습니다.\n'
          '5. 소재교체: 정지 상태를 다시 확인한 뒤 기록 저장, 새 가공·불량 0, 투입 재고 1봉 차감.\n'
          '   중도교체: 이전 봉을 중도파기 1봉으로 별도 집계합니다. 해당 봉도 소모 1봉이며 봉당 평균에 포함합니다.\n'
          '   중도교체도 가공·불량은 보존하며 새 봉 1봉을 차감합니다. 사용하던 봉은 미사용 재고로 돌리지 않습니다.\n'
          '6. 호기 우클릭: 마지막 불량/소재교체 취소. 소재교체 취소 시 재고도 복원됩니다.\n'
          '7. 기간 통계: 종료일 기준 소모 봉 수, 봉당 양품·불량을 소재별·호기별·일별로 조회합니다.\n'
          '   평균은 기간 내 종료된 완전측정 봉의 전체 양품·불량 기준. 중도파기 포함, 중간 시작·공백·불량초과 제외.\n'
          '8. 기록 삭제: 현재 재고 유지 또는 재고까지 초기화를 선택합니다. 삭제 전 자동 백업됩니다.\n'
          '   초기화 후 현재 장착 봉은 중간 시작입니다. 새 봉을 넣은 뒤부터 봉당 평균에 반영됩니다.\n'
          '9. CSV 내보내기와 전체 데이터 백업으로 기록을 따로 보관할 수 있습니다.\n\n'
          '첫 관측 번호는 기준값입니다. 첫 소재에는 중간 시작이 표시됩니다.\n'
          '같은 번호의 반복 조회는 세지 않습니다. 번호의 숫자 차이는 사용하지 않습니다.\n'
          '사이트 카운터는 읽거나 기록하지 않습니다. 수량은 프로그램 번호 변화만으로 판단합니다.\n'
          '실제 조회는 3초 간격입니다. 화면은 응답 지연 시 갱신 대기, 30초 초과 시 연결 끊김을 표시합니다.\n'
          '재실행하면 기존 집계를 유지합니다. 종료·연결 끊김 구간은 누락 가능으로 표시하고 새 기준을 잡습니다.\n'
          '실제 완료·양품을 판정하는 기능은 아닙니다. 현장 번호 변화를 확인해주세요.\n\n'
          '기존 기록은 유지되며, 과거 소재 종류를 모르면 미지정으로 남습니다.\n'
          '기존 불량이 가공 수보다 많은 기록은 보존하고 불량초과를 표시합니다. 양품은 0 미만으로 표시하지 않습니다.\n'
          '이 시험판은 한 PC 전용입니다. 다른 PC와 집계를 공유하지 않습니다.\n'
          '최소화하면 계속 수집합니다. 완전 종료·PC 절전 중에는 수집하지 않습니다.\n'
          '진단 저장 파일로 실제 사이트의 프로그램 번호·상태 변화를 확인할 수 있습니다.\n\n'
          '자동 저장 위치:\n'+str(self.folder),parent=self.root)

    def storage_error(self,e):
        from tkinter import messagebox
        if self.failed_storage:return
        self.failed_storage=True
        self.collector.close()
        self.pending.clear()
        if self.dashboard_actions:
            for widgets in self.rows.values():
                widgets['rotate'].configure(state='disabled')
                widgets['defect'].configure(state='disabled')
        for qty,receive,adjust in self.stock_cards.values():
            receive.configure(state='disabled');adjust.configure(state='disabled')
        self.footer.configure(text='저장 오류로 수집 중단 · 저장 공간/권한을 확인한 뒤 다시 실행해주세요.',fg=PALETTE['red'])
        self.tell('저장 실패로 수집을 중단했습니다. 재시작 전 저장 공간과 권한을 확인해주세요.',error=True)
        messagebox.showerror('데이터 저장 오류',str(e)+'\n\n저장되지 않은 집계로 계속 진행하지 않도록 수집을 중단했습니다.',parent=self.root)

    def callback_error(self,kind,value,trace):
        from tkinter import messagebox
        if isinstance(value,sqlite3.Error):
            self.storage_error(value)
            return
        self.tell('오류가 발생했습니다: '+str(value)[:100],error=True)
        messagebox.showerror('소재카운터 오류',str(value),parent=self.root)

    def on_close(self):
        from tkinter import messagebox
        if self.resetting or self.job_callbacks:
            messagebox.showinfo('처리 중','통계 조회·내보내기·초기화가 끝난 뒤 닫아주세요.',parent=self.root)
            return
        if self.pending:
            messagebox.showinfo('소재교체 확인 중','소재교체 요청을 처리 중입니다. 처리 결과가 표시된 뒤 닫아주세요.',parent=self.root)
            return
        answer=messagebox.askyesnocancel('수집 계속하기','창을 최소화하고 수집을 계속할까요?\n\n예: 최소화하고 계속 수집\n아니오: 기록을 유지하고 완전 종료\n취소: 돌아가기',parent=self.root)
        if answer is None:return
        if answer:self.root.iconify();return
        self.shutdown()

    def shutdown(self):
        if self.closed or self.resetting:return
        self.collector.close()
        if not self.failed_storage:
            try:
                while True:self.handle(self.queue.get_nowait(),draining=True)
            except queue.Empty:pass
            except sqlite3.Error as e:
                self.storage_error(e)
                return
        self.closed=True
        self.jobs.close()
        self.store.close()
        self.root.destroy()


def default_folder():
    root=os.environ.get('LOCALAPPDATA')
    return Path(root)/'MaterialCounter' if root else Path.home()/'.local'/'share'/'MaterialCounter'


def main():
    parser=argparse.ArgumentParser(description='소재카운터 독립 현장 확인판')
    parser.add_argument('--data-dir',type=Path,default=None)
    args=parser.parse_args()
    folder=args.data_dir or default_folder()
    import tkinter as tk
    from tkinter import messagebox
    if os.name=='nt':
        try:ctypes.windll.shcore.SetProcessDpiAwareness(1)
        except Exception:pass
        try:ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID('Jihunius.MaterialCounter')
        except Exception:pass
    root=tk.Tk()
    root.withdraw()
    lock=None
    store=None
    try:
        folder.mkdir(parents=True,exist_ok=True)
        lock=InstanceLock(folder/'instance.lock')
        store=Store(folder/'counter.sqlite3')
        application=Application(root,store,folder)
        root.deiconify()
        root.mainloop()
    except Exception as e:
        try:messagebox.showerror('소재카운터 실행 실패',str(e),parent=root)
        except Exception:pass
        raise
    finally:
        if store:
            try:store.close()
            except Exception:pass
        if lock:lock.close()


if __name__=='__main__':
    main()
