import EasyPySpin
import PySpin
import time
import cv2
import yaml
import logging

logging.basicConfig(filename='camera_log.txt', level=logging.INFO,
                     format='%(asctime)s - %(levelname)s - %(message)s')
open('camera_log.txt', 'w').close()

def parse_yaml_config(yaml_file_path):
    with open(yaml_file_path, 'r') as file:
        return yaml.safe_load(file)

def get_serial_number(cam):
    """Retrieve the serial number of the camera."""
    nodemap = cam.GetTLDeviceNodeMap()
    serial_number_node = PySpin.CStringPtr(nodemap.GetNode('DeviceSerialNumber'))
    if PySpin.IsReadable(serial_number_node):
        return serial_number_node.GetValue()
    return "Unknown"

def configure_camera_general(cam, config):
    serial_number = get_serial_number(cam)
    nodemap = cam.GetNodeMap()
    cam_width = PySpin.CIntegerPtr(nodemap.GetNode('Width'))
    cam_width.SetValue(config['width'])
    logging.info('Width of camera %s is set to %d', serial_number, config['width'])

    cam_height = PySpin.CIntegerPtr(nodemap.GetNode('Height'))
    cam_height.SetValue(config['height'])
    logging.info('Height of camera %s is set to %d', serial_number, config['height'])

    cam_offset_x = PySpin.CIntegerPtr(nodemap.GetNode('OffsetX'))
    cam_offset_x.SetValue(config['offset_x'])
    logging.info('OffsetX of camera %s is set to %d', serial_number, config['offset_x'])

    cam_offset_y = PySpin.CIntegerPtr(nodemap.GetNode('OffsetY'))
    cam_offset_y.SetValue(config['offset_y'])
    logging.info('OffsetY of camera %s is set to %d', serial_number, config['offset_y'])

    pixel_format = PySpin.CEnumerationPtr(nodemap.GetNode('PixelFormat'))
    pixel_format_entry = pixel_format.GetEntryByName(config['pixel_format'])
    pixel_format.SetIntValue(pixel_format_entry.GetValue())
    logging.info('Pixel format of camera %s is set to %s', serial_number, config['pixel_format'])

def configure_acquisition(cam, config):
    serial_number = get_serial_number(cam)
    nodemap = cam.GetNodeMap()
    acquisition_mode = PySpin.CEnumerationPtr(nodemap.GetNode('AcquisitionMode'))
    continuous_mode = PySpin.CEnumEntryPtr(acquisition_mode.GetEntryByName('Continuous'))
    acquisition_mode.SetIntValue(continuous_mode.GetValue())
    logging.info('Acquisition mode of camera %s is set to Continuous', serial_number)

    frame_rate_auto = PySpin.CEnumerationPtr(nodemap.GetNode('AcquisitionFrameRateAuto'))
    frame_rate_auto_off = PySpin.CEnumEntryPtr(frame_rate_auto.GetEntryByName('Off'))
    frame_rate_auto.SetIntValue(frame_rate_auto_off.GetValue())
    logging.info('Frame rate auto of camera %s is set to Off', serial_number)

    frame_rate_enable = PySpin.CBooleanPtr(nodemap.GetNode('AcquisitionFrameRateEnabled'))
    frame_rate_enable.SetValue(True)
    logging.info('Frame rate control of camera %s is enabled', serial_number)

    frame_rate = PySpin.CFloatPtr(nodemap.GetNode('AcquisitionFrameRate'))
    frame_rate.SetValue(config['fps'])
    logging.info('Frame rate of camera %s is set to %s fps', serial_number, config['fps'])

def configure_exposure(cam, config):
    serial_number = get_serial_number(cam)
    nodemap = cam.GetNodeMap()

    compensation_auto = PySpin.CEnumerationPtr(nodemap.GetNode('pgrExposureCompensationAuto'))
    compensation_auto_off = PySpin.CEnumEntryPtr(compensation_auto.GetEntryByName('Once'))
    compensation_auto.SetIntValue(compensation_auto_off.GetValue())
    logging.info('Exposure compensation auto of camera %s is set to Once', serial_number)

    exposure_auto = PySpin.CEnumerationPtr(nodemap.GetNode('ExposureAuto'))
    exposure_auto_off = PySpin.CEnumEntryPtr(exposure_auto.GetEntryByName('Off'))
    exposure_auto.SetIntValue(exposure_auto_off.GetValue())
    logging.info('Exposure auto of camera %s is set to Off', serial_number)

    exposure_time = PySpin.CFloatPtr(nodemap.GetNode('ExposureTime'))
    exposure_time.SetValue(config['exposure_time'])
    logging.info('Exposure time of camera %s is set to %s', serial_number, config['exposure_time'])

def configure_gain(cam, config):
    serial_number = get_serial_number(cam)
    nodemap = cam.GetNodeMap()
    gain_auto = PySpin.CEnumerationPtr(nodemap.GetNode('GainAuto'))
    gain_auto_once = PySpin.CEnumEntryPtr(gain_auto.GetEntryByName(config['gain_auto']))
    gain_auto.SetIntValue(gain_auto_once.GetValue())
    logging.info('Gain auto of camera %s is set to %s', serial_number, config['gain_auto'])

    gain = PySpin.CFloatPtr(nodemap.GetNode('Gain'))
    gain.SetValue(config['gain_value'])
    logging.info('Gain of camera %s is set to %s', serial_number, config['gain_value'])

def configure_white_balance(cam, config):
    serial_number = get_serial_number(cam)
    nodemap = cam.GetNodeMap()
    node_balance_white_auto = PySpin.CEnumerationPtr(nodemap.GetNode('BalanceWhiteAuto'))
    node_balance_white_auto_value = PySpin.CEnumEntryPtr(node_balance_white_auto.GetEntryByName(config['white_balance_auto']))
    node_balance_white_auto.SetIntValue(node_balance_white_auto_value.GetValue())
    logging.info('White balance of camera %s is set to %s', serial_number, config['white_balance_auto'])

    if config['white_balance_auto'] == "Off":
        node_balance_ratio_selector = PySpin.CEnumerationPtr(nodemap.GetNode('BalanceRatioSelector'))
        node_balance_ratio_selector_blue = PySpin.CEnumEntryPtr(node_balance_ratio_selector.GetEntryByName('Blue'))
        node_balance_ratio_selector.SetIntValue(node_balance_ratio_selector_blue.GetValue())

        node_balance_ratio = PySpin.CFloatPtr(nodemap.GetNode('BalanceRatio'))
        node_balance_ratio.SetValue(config['white_balance_blue_ratio'])
        logging.info('White balance blue ratio of camera %s is set to %f.', serial_number, config['white_balance_blue_ratio'])

        node_balance_ratio_selector_red = PySpin.CEnumEntryPtr(node_balance_ratio_selector.GetEntryByName('Red'))
        node_balance_ratio_selector.SetIntValue(node_balance_ratio_selector_red.GetValue())
        node_balance_ratio.SetValue(config['white_balance_red_ratio'])
        logging.info('White balance red ratio of camera %s is set to %f.', serial_number, config['white_balance_red_ratio'])

def configure_gpio_primary(cam, config):
    serial_number = get_serial_number(cam)
    nodemap = cam.GetNodeMap()
    trigger_mode = PySpin.CEnumerationPtr(nodemap.GetNode('TriggerMode'))
    trigger_mode_on = PySpin.CEnumEntryPtr(trigger_mode.GetEntryByName(config['trigger_mode']))
    trigger_mode.SetIntValue(trigger_mode_on.GetValue())
    logging.info('Trigger mode of primary camera %s is set to %s', serial_number, config['trigger_mode'])

    line_selector = PySpin.CEnumerationPtr(nodemap.GetNode('LineSelector'))
    line_selector_entry = PySpin.CEnumEntryPtr(line_selector.GetEntryByName(config['line_selector']))
    line_selector.SetIntValue(line_selector_entry.GetValue())
    logging.info('Line selector of primary camera %s is set to %s', serial_number, config['line_selector'])

    line_mode = PySpin.CEnumerationPtr(nodemap.GetNode('LineMode'))
    line_mode_entry = PySpin.CEnumEntryPtr(line_mode.GetEntryByName(config['line_mode']))
    line_mode.SetIntValue(line_mode_entry.GetValue())
    logging.info('Line mode of primary camera %s is set to %s', serial_number, config['line_mode'])

    line_source = PySpin.CEnumerationPtr(nodemap.GetNode('LineSource'))
    line_source_entry = PySpin.CEnumEntryPtr(line_source.GetEntryByName(config['line_source']))
    line_source.SetIntValue(line_source_entry.GetValue())
    logging.info('Line source of primary camera %s is set to %s', serial_number, config['line_source'])

def configure_gpio_secondary(cam, config):
    serial_number = get_serial_number(cam)
    nodemap = cam.GetNodeMap()
    trigger_selector = PySpin.CEnumerationPtr(nodemap.GetNode('TriggerSelector'))
    trigger_selector_entry = PySpin.CEnumEntryPtr(trigger_selector.GetEntryByName(config['trigger_selector']))
    trigger_selector.SetIntValue(trigger_selector_entry.GetValue())
    logging.info('Trigger selector of secondary camera %s is set to %s', serial_number, config['trigger_selector'])

    trigger_mode = PySpin.CEnumerationPtr(nodemap.GetNode('TriggerMode'))
    trigger_mode_on = PySpin.CEnumEntryPtr(trigger_mode.GetEntryByName(config['trigger_mode']))
    trigger_mode.SetIntValue(trigger_mode_on.GetValue())
    logging.info('Trigger mode of secondary camera %s is set to %s', serial_number, config['trigger_mode'])

    trigger_source = PySpin.CEnumerationPtr(nodemap.GetNode('TriggerSource'))
    trigger_source_entry = PySpin.CEnumEntryPtr(trigger_source.GetEntryByName(config['trigger_source']))
    trigger_source.SetIntValue(trigger_source_entry.GetValue())
    logging.info('Trigger source of secondary camera %s is set to %s', serial_number, config['trigger_source'])

    trigger_overlap = PySpin.CEnumerationPtr(nodemap.GetNode('TriggerOverlap'))
    trigger_overlap_entry = PySpin.CEnumEntryPtr(trigger_overlap.GetEntryByName(config['trigger_overlap']))
    trigger_overlap.SetIntValue(trigger_overlap_entry.GetValue())
    logging.info('Trigger overlap of secondary camera %s is set to %s', serial_number, config['trigger_overlap'])

    line_selector = PySpin.CEnumerationPtr(nodemap.GetNode('LineSelector'))
    line_selector_entry = PySpin.CEnumEntryPtr(line_selector.GetEntryByName(config['trigger_source']))
    line_selector.SetIntValue(line_selector_entry.GetValue())
    logging.info('Line selector of secondary camera %s is set to %s', serial_number, config['trigger_source'])

def enable_trigger_mode(cam):
    serial_number = get_serial_number(cam)
    nodemap = cam.GetNodeMap()
    trigger_mode = PySpin.CEnumerationPtr(nodemap.GetNode('TriggerMode'))
    trigger_mode_on = PySpin.CEnumEntryPtr(trigger_mode.GetEntryByName('On'))
    trigger_mode.SetIntValue(trigger_mode_on.GetValue())
    logging.info('Trigger mode of camera %s is enabled', serial_number)

def disable_trigger_mode(cam):
    serial_number = get_serial_number(cam)
    nodemap = cam.GetNodeMap()
    trigger_mode = PySpin.CEnumerationPtr(nodemap.GetNode('TriggerMode'))
    trigger_mode_off = PySpin.CEnumEntryPtr(trigger_mode.GetEntryByName('Off'))
    trigger_mode.SetIntValue(trigger_mode_off.GetValue())
    logging.info('Trigger mode of camera %s is disabled', serial_number)

def load_user_set(cam, user_set_name="Default"):
    """
    Load a specified user set from the camera.

    Args:
        cam (PySpin.CameraPtr): The camera object.
        user_set_name (str): The name of the user set to load (e.g., "Default").
    """
    serial_number = get_serial_number(cam)
    nodemap = cam.GetNodeMap()

    # Select the User Set
    user_set_selector = PySpin.CEnumerationPtr(nodemap.GetNode('UserSetSelector'))
    if not PySpin.IsReadable(user_set_selector) or not PySpin.IsWritable(user_set_selector):
        logging.warning('User Set Selector of camera %s is not accessible', serial_number)
        return

    user_set_entry = user_set_selector.GetEntryByName(user_set_name)
    if not PySpin.IsReadable(user_set_entry):
        logging.warning('User Set %s of camera %s is not available', user_set_name, serial_number)
        return

    user_set_selector.SetIntValue(user_set_entry.GetValue())
    logging.info('User Set %s of camera %s selected', user_set_name, serial_number)

    # Load the User Set
    user_set_load = PySpin.CCommandPtr(nodemap.GetNode('UserSetLoad'))
    if not PySpin.IsWritable(user_set_load):
        logging.warning('User Set Load of camera %s is not executable', serial_number)
        return

    user_set_load.Execute()
    logging.info('User Set %s of camera %s loaded', user_set_name, serial_number)

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
    master_cam.Init()
    load_user_set(master_cam, user_set_name="Default")

    slave_cam = cam_list.GetBySerial(SN2)
    slave_cam.Init()
    load_user_set(slave_cam, user_set_name="Default")

    try:
        # Configure master camera
        configure_camera_general(master_cam, config["camera_settings"])
        configure_acquisition(master_cam, config["acquisition_settings"])
        configure_exposure(master_cam, config["exposure_settings"])
        configure_gain(master_cam, config["gain_settings"])
        configure_white_balance(master_cam, config["white_balance_settings"])
        configure_gpio_primary(master_cam, config["gpio_primary"])

        configure_camera_general(slave_cam, config["camera_settings"])
        configure_acquisition(slave_cam, config["acquisition_settings"])
        configure_exposure(slave_cam, config["exposure_settings"])
        configure_gain(slave_cam, config["gain_settings"])
        configure_white_balance(slave_cam, config["white_balance_settings"])
        configure_gpio_secondary(slave_cam, config["gpio_secondary"])

        logging.info("Starting master camera acquisition...")
        master_cam.BeginAcquisition()

        logging.info("Starting slave camera acquisition...")
        slave_cam.BeginAcquisition()

        disable_trigger_mode(master_cam)

        capture_video_one_second(master_cam, slave_cam, config)

    finally:
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