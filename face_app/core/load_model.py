from insightface.app import FaceAnalysis

class InsightFaceLoader:
    _model = None

    @classmethod
    def get_model(cls):
        if cls._model is None:
            cls._model = FaceAnalysis(
                name="buffalo_l",
                providers=["CPUExecutionProvider"]
            )
            cls._model.prepare(ctx_id=0, det_size=(640, 640))
        return cls._model
