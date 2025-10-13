import logging
import json
import os
import time
import numpy as np
from PIL import Image
from lib import kraken_pb2
from lib.broker import Broker
from adapters.slack import SlackAdapter

logging.basicConfig(format='%(asctime)s %(message)s', level=logging.DEBUG)
logger = logging.getLogger(__name__)

class CameraBroker(Broker):

    def __init__(self):
        self.name = "CameraBroker"
        self.slack = SlackAdapter()

    async def on(self, request: kraken_pb2.KrakenRequest, response: 
kraken_pb2.KrakenResponse) -> kraken_pb2.KrakenResponse|None:
        logger.debug("=== CameraBroker: Processing request ===")
        logger.debug(request.collector_name)
        logger.debug(request.metadata)

        # 注意: request.payloadを使用（response.payloadではなく）
        ret = self.save_img(request.payload)   # save image from camera
        logger.debug(ret)

        response_content_type = "text/plain"
        response_meta = {
            "response_type": "simple",
            "saved_image": ret
        }
        meta_str = json.dumps(response_meta)
        kraken_response = response(
            collector_name=request.collector_name,
            content_type=response_content_type,
            metadata=meta_str,
            payload=bytes([0x00])
        )
        logger.debug("=== CameraBroker: Sending response ===")
        logger.debug(kraken_response)
        return kraken_response
    def save_img(self, payload, output_dir="images"):
        """
        受信したRGBバイナリストリームをJPEGファイルとして保存
        """
        try:
            # 出力ディレクトリの作成
            os.makedirs(output_dir, exist_ok=True)

            # Unixtimestampを使用してファイル名生成
            timestamp = int(time.time())
            filename = f"{timestamp}.jpg"
            filepath = os.path.join(output_dir, filename)

            # RGBバイナリデータをnumpy配列に変換
            rgb_array = np.frombuffer(payload, dtype=np.uint8)

            # 実際のデータサイズから画像サイズを計算
            total_pixels = len(rgb_array) // 3  # RGB = 3チャンネル

            # 一般的なアスペクト比から幅と高さを推定 (16:9 or 4:3)
            # 6220800 bytes ÷ 3 = 2073600 pixels
            # √2073600 ≈ 1440 → 1920x1080 程度と推定

            # より安全な方法: 平方根から正方形に近い形で計算
            side_length = int(np.sqrt(total_pixels))

            # アスペクト比を考慮した調整
            if total_pixels == 2073600:  # 1920x1080の場合
                width, height = 1920, 1080
            elif total_pixels == 921600:  # 640x480の場合  
                width, height = 640, 480
            else:
                # 汎用的な計算
                aspect_ratio = 16/9  # 一般的なアスペクト比
                height = int(np.sqrt(total_pixels / aspect_ratio))
                width = int(total_pixels / height)

            logger.info(f"Calculated dimensions: {width}x{height} = {width*height} pixels")
            logger.info(f"Total pixels available: {total_pixels}")

            # サイズ調整（必要に応じて）
            if width * height != total_pixels:
                logger.warning(f"Pixel mismatch: calculated {width*height}, available {total_pixels}")
                # 最も近い完全なサイズに調整
                actual_size = width * height * 3
                rgb_array = rgb_array[:actual_size]

            # 配列をリシェイプ
            rgb_array = rgb_array.reshape((height, width, 3))

            # PIL Imageオブジェクトを作成
            image = Image.fromarray(rgb_array, 'RGB')

            # JPEGとして保存
            image.save(filepath, 'JPEG', quality=85)

            logger.info(f"Image saved: {filepath} ({width}x{height})")
            return filepath

        except Exception as e:
            logger.error(f"Error saving image: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return None
