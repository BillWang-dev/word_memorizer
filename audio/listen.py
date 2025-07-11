#!/usr/bin/env python3
"""
Ultra-Simplified Audio Listen Engine for Word & Sentence Memorizer
音频引擎 - 仅实现核心的TTS播放功能
"""

import asyncio
import io
import threading
import time
import logging
from typing import Callable

# 第三方库导入
import pygame  # 用于音频播放的游戏开发库
import edge_tts  # 微软Edge浏览器的文本转语音服务

# 配置日志记录
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TTSEngine:
    """文本转语音引擎，使用edge-tts"""

    def __init__(self):
        # 使用一个常见的英文语音作为默认值
        # AriaNeural是微软的高质量神经网络语音
        self.default_voice = 'en-US-AriaNeural'

    async def text_to_audio_async(self, text: str) -> bytes:
        """
        异步将文本转换为音频数据
        
        Args:
            text: 需要转换的文本内容
            
        Returns:
            bytes: 音频数据的字节流
        """
        # 创建edge-tts的通信对象，指定文本和语音
        communicate = edge_tts.Communicate(text=text, voice=self.default_voice)
        audio_data = b""  # 初始化空的字节数据
        
        # 异步流式获取音频数据
        async for chunk in communicate.stream():
            # 只处理音频类型的数据块
            if chunk["type"] == "audio":
                audio_data += chunk["data"]  # 累加音频数据
        
        return audio_data

    def text_to_audio(self, text: str) -> bytes:
        """
        同步将文本转换为音频数据
        
        Args:
            text: 需要转换的文本内容
            
        Returns:
            bytes: 音频数据的字节流
        """
        try:
            # 尝试获取当前的事件循环
            loop = asyncio.get_event_loop()
        except RuntimeError:
            # 如果没有事件循环，创建一个新的
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        
        # 运行异步函数直到完成
        return loop.run_until_complete(self.text_to_audio_async(text))


class AudioPlayer:
    """简化的音频播放器"""

    def __init__(self):
        # 初始化pygame的音频混音器
        pygame.mixer.init()
        
        # 播放状态标志
        self.is_playing = False
        
        # 设置一个固定的默认音量 (0.0 到 1.0之间)
        pygame.mixer.music.set_volume(0.7)

    def play_audio_data(self, audio_data: bytes, callback: Callable = None) -> bool:
        """
        直接播放音频数据
        
        Args:
            audio_data: 音频数据的字节流
            callback: 播放完成后的回调函数
            
        Returns:
            bool: 播放是否成功启动
        """
        try:
            # 停止当前正在播放的音频
            self.stop_audio()
            
            # 将字节数据转换为类文件对象
            audio_stream = io.BytesIO(audio_data)
            
            # 加载音频流到pygame音乐播放器
            pygame.mixer.music.load(audio_stream)
            
            # 开始播放音频
            pygame.mixer.music.play()
            
            # 更新播放状态
            self.is_playing = True
            logger.info("开始播放音频...")

            # 如果提供了回调函数，启动监控线程
            if callback:
                def monitor_playback():
                    """监控播放状态的内部函数"""
                    # 持续检查音频是否还在播放
                    while pygame.mixer.music.get_busy():
                        time.sleep(0.1)  # 每100毫秒检查一次
                    
                    # 播放完成后更新状态并调用回调
                    self.is_playing = False
                    callback()
                
                # 创建守护线程来监控播放状态
                threading.Thread(target=monitor_playback, daemon=True).start()
            
            return True
            
        except Exception as e:
            logger.error(f"播放音频数据失败: {e}")
            self.is_playing = False
            return False

    def stop_audio(self):
        """停止音频播放"""
        if self.is_playing:
            pygame.mixer.music.stop()  # 停止pygame音乐播放
            self.is_playing = False     # 更新播放状态


class ListenEngine:
    """听写引擎，只负责播放"""

    def __init__(self):
        # 初始化TTS引擎和音频播放器
        self.tts_engine = TTSEngine()
        self.player = AudioPlayer()
        
        # 当前正在处理的文本
        self.current_text = ""
        
        # 播放完成后的回调函数
        self.playback_callback = None

    def play_text(self, text: str, callback: Callable = None) -> bool:
        """
        将文本转换为语音并播放
        
        Args:
            text: 需要播放的文本内容
            callback: 播放完成后的回调函数
            
        Returns:
            bool: 播放是否成功启动
        """
        # 保存当前文本和回调函数
        self.current_text = text
        self.playback_callback = callback
        
        try:
            # 将文本转换为音频数据
            audio_data = self.tts_engine.text_to_audio(text)
            
            # 播放音频数据
            return self.player.play_audio_data(audio_data, callback)
            
        except Exception as e:
            # 记录错误信息（只显示文本的前30个字符）
            logger.error(f"播放文本 '{text[:30]}...' 失败: {e}")
            return False


# 全局听写引擎实例
_listen_engine = None

def get_listen_engine() -> ListenEngine:
    """
    获取全局唯一的听写引擎实例（单例模式）
    
    Returns:
        ListenEngine: 全局听写引擎实例
    """
    global _listen_engine
    if _listen_engine is None:
        _listen_engine = ListenEngine()
    return _listen_engine