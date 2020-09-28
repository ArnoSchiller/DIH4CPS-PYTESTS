#!/bin/sh
. /usr/share/phytec-gstreamer-examples/func.sh

init_dev
[ $? -ne 0 ] && exit 1

guess_param

echo ""
echo " configure IPU1_CSI0 (camera_0 port) with media_control"
echo " Note: For use IPU2_CSI1 (camera_1 port) or 2 cameras or other"
echo " resolutions, see the scripts in path ...\\gstreamer_examples\\..."
echo " ==============================================================="

media-ctl -r
media-ctl -l ''$CAM_ENTITY_NUMBER'0->"ipu1_csi0_mux":1[1]'
media-ctl -l "'ipu1_csi0_mux':2->'ipu1_csi0':0[1]"
media-ctl -l "'ipu1_csi0':2->'ipu1_csi0 capture':0[1]"
#           Camera -> IPU1_CSI0_mux -> IPU1-CSI0 -> IPU1-CSI0 capture (/dev/videoX)   

media-ctl -V ''$CAM_ENTITY_NUMBER'0 [fmt:'$CAM_BW_FMT'/'$GRAB_RES' ('$OFFSET_SENSOR')/'$SENSOR_RES_LIVE_DEMO']'
media-ctl -V '"ipu1_csi0_mux":2 [fmt:'$CAM_BW_FMT'/'$GRAB_RES']'
media-ctl -V '"ipu1_csi0":2 [fmt:'$CAM_BW_FMT'/'$GRAB_RES']'

echo ""
echo " configure camera with v4l2_control"
echo " =================================="
echo ""
echo " $V4L2_CTRL_CAM0"
$V4L2_CTRL_CAM0

echo ""
echo " Camera name and v4l2 properties"
echo " ==============================="
echo " The camera $CAMERA is at i2c bus=$CAM_I2C_BUS with i2c adress=0x$CAM_I2C_ADRESS installed"
echo " The camera $CAMERA is now present as <$IPU1_CSI0_DEVICE> device"
echo " The sensor resolution is <$SENSOR_RES_LIVE_DEMO> and the set resolution is <$GRAB_RES>"
echo " The set color format is <raw,format=GRAY8,depth=8> ($CAM_BW_FMT)"
echo ""


