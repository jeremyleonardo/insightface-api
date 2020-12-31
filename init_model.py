import insightface

fa = insightface.app.FaceAnalysis()
fa.prepare(ctx_id = -1, nms=0.4)