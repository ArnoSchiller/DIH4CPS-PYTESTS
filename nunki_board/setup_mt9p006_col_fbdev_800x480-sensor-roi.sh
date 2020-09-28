#!/bin/sh
. `dirname $0`/../func.sh

init_dev
[ $? -ne 0 ] && exit 1

guess_param

echo 0 > /sys/class/graphics/fbcon/cursor_blink

GRAB_RES="800x480"
FRAME_SIZE=",width=800,height=480"
OFFSET_SENSOR="912,786"

echo "starting gstreamer with $CAM_COL_FORMAT Source ..."
echo "read $FRAME_SIZE (ROI in center of pic) convert bayer2rgb and write to framebuffer $GRAB_RES"
echo "================================================================================================"
echo ""
echo "configure IPU1_CSI0 (camera_0 port) with media_control"
echo "======================================================"

media-ctl -r
media-ctl -l ''$CAM_ENTITY_NUMBER'0->"ipu1_csi0_mux":1[1]'
media-ctl -l "'ipu1_csi0_mux':2->'ipu1_csi0':0[1]"
media-ctl -l "'ipu1_csi0':2->'ipu1_csi0 capture':0[1]"
#           Camera -> IPU1_CSI0_mux -> IPU1-CSI0 -> IPU1-CSI0 capture (/dev/videoX)

media-ctl -V ''$CAM_ENTITY_NUMBER'0 [fmt:'$CAM_COL_FMT'/'$GRAB_RES' ('$OFFSET_SENSOR')/'$GRAB_RES']'
media-ctl -V '"ipu1_csi0_mux":2 [fmt:'$CAM_COL_FMT'/'$GRAB_RES']'
media-ctl -V '"ipu1_csi0":2 [fmt:'$CAM_COL_FMT'/'$GRAB_RES']'

echo ""
echo " configure camera with v4l2_control"
echo " =================================="

v4l2-ctl -d $IPU1_CSI0_DEVICE -c exposure=480
v4l2-ctl -d $IPU1_CSI0_DEVICE -c gain=32
