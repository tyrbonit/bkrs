# -*- coding: utf-8 -*-
from bkrswizard import Master

@auth.requires_login()
def index():
    bkrsmaster = Master()
    return bkrsmaster.execute()
