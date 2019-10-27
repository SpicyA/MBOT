from pytz import timezone
import pytz
import datetime

def get_date_in_PT_TZ():
	utc_date = datetime.datetime.now(tz=pytz.utc)
	date_PT = utc_date.astimezone(timezone('US/Pacific'))
	return date_PT

def unix_epoch_to_PT(ux_epoch):
	utc_date = datetime.datetime.fromtimestamp(ux_epoch, tz=pytz.utc)
	date_PT = utc_date.astimezone(timezone('US/Pacific'))
	return date_PT



