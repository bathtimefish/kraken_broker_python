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

        ret = self.save_img(request.payload, request.metadata)
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

    def save_img(self, payload, metadata_json, output_dir="images"):
        """
        受信したRGBバイナリストリームをJPEGファイルとして保存
      
        Args:
            payload (bytes): RGB画像のバイナリデータ
            metadata_json (str): メタデータJSON文字列
            output_dir (str): 保存先ディレクトリ
      
        Returns:
            str: 保存されたファイルのパス
        """
        try:
            # メタデータからwidth/heightを取得
            import json
            metadata = json.loads(metadata_json)
            width = metadata.get('width', 640)
            height = metadata.get('height', 480)
            camera_name = metadata.get('camera_name', 'unknown')

            logger.info(f"Processing image from {camera_name}: {width}x{height}")

            # 出力ディレクトリの作成
            os.makedirs(output_dir, exist_ok=True)

            # Unixtimestampを使用してファイル名生成
            timestamp = int(time.time())
            filename = f"{timestamp}.jpg"
            filepath = os.path.join(output_dir, filename)

            # RGBバイナリデータをnumpy配列に変換
            rgb_array = np.frombuffer(payload, dtype=np.uint8)

            # メタデータの解像度でリシェイプ
            expected_size = width * height * 3
            if len(rgb_array) != expected_size:
                logger.warning(f"Size mismatch: expected {expected_size}, got {len(rgb_array)}")
                # データサイズに合わせて調整
                actual_pixels = len(rgb_array) // 3
                if actual_pixels < width * height:
                    # データが不足している場合
                    logger.error(f"Insufficient data: {actual_pixels} < {width * height}")
                    return None

            # 配列をリシェイプ
            rgb_array = rgb_array[:expected_size]  # 余分なデータをカット
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
