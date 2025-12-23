'''
导入文件
'''

from flask import Blueprint
from flask_restful import Api, fields

from flask_pika import Pika as FPika

api_blueprint = Blueprint('api', __name__, url_prefix='/api')

api = Api(api_blueprint)

fpika = FPika()

from . import plateYieldStaisticsApi
from . import diagnosisDataApi
from . import VisualizationTsneApi
from . import VisualizationTsneApi_V1
from . import VisualizationPCAApi
from . import VisualizationPCAApi_V1
from . import VisualizationISOMAPApi
from . import VisualizationUMAPApi
from . import VisualizationMDSApi
from . import getFlag
from . import newVisualization
from . import VisualizationCorrelation
from . import VisualizationPlatetypes
from . import singelSteel
from . import getMareyDataApi
from . import BoardNumApi
from . import newGetMareyDataApi
from . import diagnosisDataByTimeApi
from . import monitorDataByTimeApi
from . import newVisualizationByBatch
from . import getEventDataApi
from . import GetNumberOfPlatesByTimeApi
from . import GetScatterDataByTimeApi
from . import DiagnosesByUpidsApi
from . import RediagnosesApi
from . import getSpecDataApi
from . import getSpecCountApi
from . import heatingReportApi
from . import rollingReportApi
from . import coolingReportApi
from . import fqcReportApi