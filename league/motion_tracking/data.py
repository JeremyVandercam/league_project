# from roboflow import Roboflow
# from league.motion_tracking.params import LOCAL_DATA_PATH, ROBOFLOW_API_KEY


# def load_data():
#     rf = Roboflow(api_key=ROBOFLOW_API_KEY)
#     project = rf.workspace("jasperan").project("league-of-legends-detection")
#     version = project.version(5)
#     print(LOCAL_DATA_PATH)
#     dataset = version.download(model_format="yolov11", location=LOCAL_DATA_PATH)
#     return dataset


# if __name__ == "__main__":
#     dataset = load_data()
