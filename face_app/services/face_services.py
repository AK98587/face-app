from face_app.core.load_model import InsightFaceLoader
from face_app.face.pose import face_angle_state
from face_app.face.liveness import eye_open_close
from face_app.face.quality import brightness_ok, is_blurry, size_ok
from face_app.face.detector import extract_faces_frsom_image
class FaceService:
    def __init__(self):
        self.model = InsightFaceLoader.get_model()
    def process_image(self, img, image_type: str):
        face_records = extract_faces_frsom_image(img, self.model)


        if len(face_records) != 1:
            raise ValueError("Require exactly one face")

        face_record = face_records[0]

        bbox = face_record["bbox"]
        lmk106 = face_record["landmark106"]
        pose = face_record["pose"]
        emb = face_record["emb"]

        # size check
        if not size_ok(bbox)[0]:
            raise ValueError("Face size is too small")

        # blur check
        if is_blurry(img, bbox)[0]:
            raise ValueError("Image is too blurry")

        # brightness check
        if not brightness_ok(img, bbox)[0]:
            raise ValueError("Image brightness is not acceptable")


        # liveness
        self.liveness_check(lmk106, image_type)

        return {
        "bbox": bbox,
        "lmk106": lmk106,
        "pose": pose,
        "emb": emb
    }


    def pose_check(self, pose, image_type: str):

        if image_type != face_angle_state(pose):
            raise ValueError("Face pose does not match the expected image type")
        
    def liveness_check(self, lmk106, image_type: str):
        is_left_open, is_right_open = eye_open_close(lmk106, ear_th=0.2)
        if image_type == "FRONT" or image_type =="LOOK_UP" or image_type =="LOOK_DOWN":
            if not is_left_open and not is_right_open:
                raise ValueError("Eyes are not open")
        
        elif image_type == "LEFT" or image_type == "RIGHT":
            if not is_left_open or not is_right_open:
                raise ValueError("Eyes are not open")

    
            
            
        
        



