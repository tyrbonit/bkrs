# -*- coding: utf-8 -*-
from scheduler import Scheduler
import sys, time
from gluon.serializers import json
from bkrswizard import sozdanie_bazy

scheduler = Scheduler(db, max_empty_runs=50, heartbeat=1, )
