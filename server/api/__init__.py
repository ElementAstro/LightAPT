from .ascom.worker import ASCOMWebsocketWorker as ascom_worker
from .indi.ws import INDIWebsocketWorker as indi_worker
from .astap.solver import solve as astap_solve
from .astrometry.solver import solve as astrometry_solve
from .phd2.phd2client import PHD2ClientWorker as phd2_worker