import PySpin
import time
import cv2
import yaml
import logging

from camera_settings_api import *

logging.basicConfig(filename='camera_log.txt', level=logging.INFO,
                     format='%(asctime)s - %(levelname)s - %(message)s')
open('camera_log.txt', 'w').close()

def capture_video_one_second(master_cam, slave_cam, full_config, output_file='output.mkv'):

    processor = PySpin.ImageProcessor()
    processor.SetColorProcessing(PySpin.SPINNAKER_COLOR_PROCESSING_ALGORITHM_HQ_LINEAR)

    SN1 = get_serial_number(master_cam)
    SN2 = get_serial_number(slave_cam)

    # 取得影像的寬度與高度
    frame_width = full_config["camera_settings"]["width"]
    frame_height = full_config["camera_settings"]["height"]
    frame_size = (frame_width, frame_height)

    fps = full_config["acquisition_settings"]["fps"]

    # 設定影片儲存的格式與編碼器 (MP4V 編碼)
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    master_out = cv2.VideoWriter(f"left_{output_file}", fourcc, fps, frame_size)

    slave_out = cv2.VideoWriter(f"right_{output_file}", fourcc, fps, frame_size)

    # 設定錄影時間 (1 秒)
    duration = 1  # 秒數
    start_time = time.time()

    while True:
        logging.info("Reading Frame for %s...", SN1)
        master_image_result = master_cam.GetNextImage(1000)
        if master_image_result.IsIncomplete():
            logging.warning('SN %s: Image incomplete with image status %d', SN1, master_image_result.GetImageStatus())
        else:
            logging.info("Grabbed Frame for %s", SN1)

        logging.info("Reading Frame for %s...", SN2)
        slave_image_result = master_cam.GetNextImage(1000)
        if slave_image_result.IsIncomplete():
            logging.warning('SN %s: Image incomplete with image status %d', SN2, slave_image_result.GetImageStatus())
        else:
            logging.info("Grabbed Frame for %s", SN2)

        master_image_converted = processor.Convert(master_image_result, PySpin.PixelFormat_BayerRG8)
        master_image_data = master_image_converted.GetNDArray()
        master_image_data = cv2.cvtColor(master_image_data, cv2.COLOR_BayerRG2RGB)

        slave_image_converted = processor.Convert(slave_image_result, PySpin.PixelFormat_BayerRG8)
        slave_image_data = slave_image_converted.GetNDArray()
        slave_image_data = cv2.cvtColor(slave_image_data, cv2.COLOR_BayerRG2RGB)

        # 寫入幀到影片檔案
        logging.info("Writing Frame for %s...", SN1)
        master_out.write(master_image_data)

        # 寫入幀到影片檔案
        logging.info("Writing Frame for %s...", SN2)
        slave_out.write(slave_image_data)
        
        master_image_result.Release()
        slave_image_result.Release()

        # 判斷是否超過 1 秒
        if time.time() - start_time > duration:
            break

    master_out.release()
    slave_out.release()

    logging.info("Video of %s and %s saved to left_%s and right_%s", SN1, SN2, output_file, output_file)

if __name__ == "__main__":
    # Load YAML configuration
    yaml_file_path = "camera_config.yaml"
    config = parse_yaml_config(yaml_file_path)

    system = PySpin.System.GetInstance()
    cam_list = system.GetCameras()

    if cam_list.GetSize() == 0:
        print("No cameras detected.")
        system.ReleaseInstance()
    
    SN1 = "21091478"
    SN2 = "21091470"
    
    master_cam = cam_list.GetBySerial(SN1)
    configure_master_camera(master_cam, config)

    slave_cam = cam_list.GetBySerial(SN2)
    configure_slave_camera(slave_cam, config)

    disable_trigger_mode(master_cam)

    capture_video_one_second(master_cam, slave_cam, config)

    logging.info("Stopping master camera acquisition...")
    master_cam.EndAcquisition()

    logging.info("Stopping slave camera acquisition...")
    slave_cam.EndAcquisition()

    logging.info("Releasing master camera...")
    master_cam.DeInit()
    logging.info("Master camera released.")

    logging.info("Releasing slave camera...")
    slave_cam.DeInit()
    logging.info("Slave camera released.")

    logging.info("Clearing camera list...")
    cam_list.Clear()
    logging.info("Camera list cleared.")

    logging.info("Releasing system...")
    system.ReleaseInstance()
    logging.info("System released.")