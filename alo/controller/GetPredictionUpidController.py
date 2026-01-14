from ..models import queryPredictionData

class GetPredictionUpidController:
    def __init__(self, upid):
        self.upid = upid

    def run(self):
        basic_data, columns = queryPredictionData.get_upid(self.upid)

        p_label = [2, 2, 2, 2, 2] if not basic_data[0][3] else basic_data[0][3]
        res = {
            'upid': self.upid,
            'status_cooling': basic_data[0][2],
            'platetype': basic_data[0][1],
            'p_label': p_label
        }
        return res