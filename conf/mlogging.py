#!/usr/bin/env python
# -*- coding: utf-8 -*-
# __author__ = https://github.com/kieslee/mlogging
#
# Copyright 2001-2007 by Vinay Sajip. All Rights Reserved.
#
# Permission to use, copy, modify, and distribute this software and its
# documentation for any purpose and without fee is hereby granted,
# provided that the above copyright notice appear in all copies and that
# both that copyright notice and this permission notice appear in
# supporting documentation, and that the name of Vinay Sajip
# not be used in advertising or publicity pertaining to distribution
# of the software without specific, written prior permission.
# VINAY SAJIP DISCLAIMS ALL WARRANTIES WITH REGARD TO THIS SOFTWARE, INCLUDING
# ALL IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS. IN NO EVENT SHALL
# VINAY SAJIP BE LIABLE FOR ANY SPECIAL, INDIRECT OR CONSEQUENTIAL DAMAGES OR
# ANY DAMAGES WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS, WHETHER
# IN AN ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT
# OF OR IN CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.

"""
Additional handler : RotatingFileHandler and TimedRotatingFileHandler
                        for MultiProcess
"""
import sys
from logging import StreamHandler, FileHandler
from logging.handlers import RotatingFileHandler, TimedRotatingFileHandler
import fcntl, time, os, struct
from .cloghandler import ConcurrentRotatingFileHandler
from utils.file_util import chown_apache


class RotatingFileHandler_new(RotatingFileHandler):
    def doRollover(self):
        """
                Do a rollover, as described in __init__().
                """
        if self.stream:
            self.stream.close()
            self.stream = None
        if self.backupCount > 0:
            for i in range(self.backupCount - 1, 0, -1):
                sfn = "%s.%d" % (self.baseFilename, i)
                dfn = "%s.%d" % (self.baseFilename, i + 1)
                if os.path.exists(sfn):
                    if os.path.exists(dfn):
                        os.remove(dfn)
                    os.rename(sfn, dfn)
            dfn = self.baseFilename + ".1"
            if os.path.exists(dfn):
                os.remove(dfn)
            os.rename(self.baseFilename, dfn)

        self.stream = self._open()
        chown_apache(self.baseFilename)
        chown_apache(dfn)


class TimedRotatingFileHandler_new(TimedRotatingFileHandler):
    def doRollover(self):
        """
        do a rollover; in this case, a date/time stamp is appended to the filename
        when the rollover happens.  However, you want the file to be named for the
        start of the interval, not the current time.  If there is a backup count,
        then we have to get a list of matching filenames, sort them and remove
        the one with the oldest suffix.
        """
        if self.stream:
            self.stream.close()
            self.stream = None
        # get the time that this sequence started at and make it a TimeTuple
        currentTime = int(time.time())
        dstNow = time.localtime(currentTime)[-1]
        t = self.rolloverAt - self.interval
        if self.utc:
            timeTuple = time.gmtime(t)
        else:
            timeTuple = time.localtime(t)
            dstThen = timeTuple[-1]
            if dstNow != dstThen:
                if dstNow:
                    addend = 3600
                else:
                    addend = -3600
                timeTuple = time.localtime(t + addend)
        dfn = self.baseFilename + "." + time.strftime(self.suffix, timeTuple)
        if os.path.exists(dfn):
            os.remove(dfn)
        os.rename(self.baseFilename, dfn)
        chown_apache(self.baseFilename)
        if self.backupCount > 0:
            for s in self.getFilesToDelete():
                os.remove(s)
        self.stream = self._open()
        newRolloverAt = self.computeRollover(currentTime)
        while newRolloverAt <= currentTime:
            newRolloverAt = newRolloverAt + self.interval
        # If DST changes and midnight or weekly rollover, adjust for this.
        if (self.when == 'MIDNIGHT' or self.when.startswith('W')) and not self.utc:
            dstAtRollover = time.localtime(newRolloverAt)[-1]
            if dstNow != dstAtRollover:
                if not dstNow:  # DST kicks in before next rollover, so we need to deduct an hour
                    addend = -3600
                else:  # DST bows out before next rollover, so we need to add an hour
                    addend = 3600
                newRolloverAt += addend
        self.rolloverAt = newRolloverAt
        chown_apache(self.baseFilename)
        chown_apache(dfn)


class StreamHandler_MP(StreamHandler):
    """
    A handler class which writes logging records, appropriately formatted,
    to a stream. Use for multiprocess.
    """

    def emit(self, record):
        """
        Emit a record.
            First seek the end of file for multiprocess to log to the same file
        """
        try:
            if hasattr(self.stream, "seek"):
                self.stream.seek(0, os.SEEK_END)
        except IOError as e:
            pass

        StreamHandler.emit(self, record)


class FileHandler_MP(FileHandler, StreamHandler_MP):
    """
    A handler class which writes formatted logging records to disk files
        for multiprocess
    """

    def emit(self, record):
        """
        Emit a record.
        If the stream was not opened because 'delay' was specified in the
        constructor, open it before calling the superclass's emit.
        """
        if self.stream is None:
            self.stream = self._open()
        StreamHandler_MP.emit(self, record)


class MultiProcessRotatingHandler_new(ConcurrentRotatingFileHandler):
    '''
    取代 MultiProcessRotatingFileHandler
    '''

    def doRollover(self):
        """
        Do a rollover, as described in __init__().
        """
        self._close()
        if self.backupCount <= 0:
            # Don't keep any backups, just overwrite the existing backup file
            # Locking doesn't much matter here; since we are overwriting it anyway
            self.stream = self._open("w")
            return
        try:
            # Determine if we can rename the log file or not. Windows refuses to
            # rename an open file, Unix is inode base so it doesn't care.

            # Attempt to rename logfile to tempname:  There is a slight race-condition here, but it seems unavoidable
            tmpname = None
            while not tmpname or os.path.exists(tmpname):
                from random import randint
                tmpname = "%s.rotate.%08d" % (self.baseFilename, randint(0, 99999999))
            try:
                # Do a rename test to determine if we can successfully rename the log file
                os.rename(self.baseFilename, tmpname)
                chown_apache(self.baseFilename)
            except (IOError, OSError):
                exc_value = sys.exc_info()[1]
                self._degrade(True, "rename failed.  File in use?  "
                                    "exception=%s", exc_value)
                return

            # Q: Is there some way to protect this code from a KeboardInterupt?
            # This isn't necessarily a data loss issue, but it certainly does
            # break the rotation process during stress testing.

            # There is currently no mechanism in place to handle the situation
            # where one of these log files cannot be renamed. (Example, user
            # opens "logfile.3" in notepad); we could test rename each file, but
            # nobody's complained about this being an issue; so the additional
            # code complexity isn't warranted.
            for i in range(self.backupCount - 1, 0, -1):
                sfn = "%s.%d" % (self.baseFilename, i)
                dfn = "%s.%d" % (self.baseFilename, i + 1)
                if os.path.exists(sfn):
                    if os.path.exists(dfn):
                        os.remove(dfn)
                    os.rename(sfn, dfn)
            dfn = self.baseFilename + ".1"
            if os.path.exists(dfn):
                os.remove(dfn)
            os.rename(tmpname, dfn)
            self._degrade(False, "Rotation completed")
        finally:
            # Re-open the output stream, but if "delay" is enabled then wait
            # until the next emit() call. This could reduce rename contention in
            # some usage patterns.
            if not self.delay:
                self.stream = self._open()
            chown_apache(self.baseFilename)
            chown_apache(dfn)


class MultiProcessTimedRotatingFileHandler(TimedRotatingFileHandler):
    def doRollover(self):
        """
        do a rollover; in this case, a date/time stamp is appended to the filename
        when the rollover happens.  However, you want the file to be named for the
        start of the interval, not the current time.  If there is a backup count,
        then we have to get a list of matching filenames, sort them and remove
        the one with the oldest suffix.
        """
        t = self.rolloverAt - self.interval
        if self.utc:
            timeTuple = time.gmtime(t)
        else:
            timeTuple = time.localtime(t)
        dfn = self.baseFilename + "." + time.strftime(self.suffix, timeTuple)
        lockdata = struct.pack('hhllhh', fcntl.F_WRLCK, 0, 0, 0, 0, 0)
        fcntl.fcntl(self.stream, fcntl.F_SETLKW, lockdata)
        if not os.path.exists(dfn) and os.path.exists(self.baseFilename):
            os.rename(self.baseFilename, dfn)
            with open(self.baseFilename, 'a'):
                pass
        if self.backupCount > 0:
            for s in self.getFilesToDelete():
                os.remove(s)
        if self.stream:
            self.stream.close()
        self.mode = 'a'
        self.stream = self._open()
        currentTime = int(time.time())
        newRolloverAt = self.computeRollover(currentTime)
        while newRolloverAt <= currentTime:
            newRolloverAt = newRolloverAt + self.interval
        # If DST changes and midnight or weekly rollover, adjust for this.
        if (self.when == 'MIDNIGHT' or self.when.startswith('W')) and not self.utc:
            dstNow = time.localtime(currentTime)[-1]
            dstAtRollover = time.localtime(newRolloverAt)[-1]
            if dstNow != dstAtRollover:
                if not dstNow:  # DST kicks in before next rollover, so we need to deduct an hour
                    newRolloverAt = newRolloverAt - 3600
                else:  # DST bows out before next rollover, so we need to add an hour
                    newRolloverAt = newRolloverAt + 3600
        self.rolloverAt = newRolloverAt
        chown_apache(self.baseFilename)
        chown_apache(dfn)
