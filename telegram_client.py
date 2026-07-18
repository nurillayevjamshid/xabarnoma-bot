import os
import asyncio
from telethon import TelegramClient, events
from telethon.tl.types import MessageMediaPhoto, MessageMediaDocument, MessageService
from config_insta import API_ID, API_HASH, SESSION_NAME, SOURCE_CHANNEL, DOWNLOAD_DIR
from utils import logger

class TelegramMonitor:
    def __init__(self, callback):
        self.client = TelegramClient(SESSION_NAME, API_ID, API_HASH)
        self.callback = callback
        self.media_groups = {}

    async def start(self):
        logger.info("Starting Telegram Monitor...")
        await self.client.start()
        
        @self.client.on(events.NewMessage(chats=SOURCE_CHANNEL))
        async def handler(event):
            if isinstance(event.message, MessageService):
                return

            # Handle Media Groups (Albums)
            if event.message.grouped_id:
                gid = event.message.grouped_id
                if gid not in self.media_groups:
                    self.media_groups[gid] = {'messages': [], 'timer': None}
                
                self.media_groups[gid]['messages'].append(event.message)
                
                # Reset timer to wait for all parts of the album
                if self.media_groups[gid]['timer']:
                    self.media_groups[gid]['timer'].cancel()
                
                self.media_groups[gid]['timer'] = asyncio.create_task(self.process_media_group(gid))
            else:
                # Single post
                await self.process_single_message(event.message)

        logger.info(f"Monitoring channel: {SOURCE_CHANNEL}")
        await self.client.run_until_disconnected()

    async def process_media_group(self, gid):
        await asyncio.sleep(2)  # Wait for all messages in the group
        group_data = self.media_groups.pop(gid, None)
        if not group_data:
            return
        
        messages = sorted(group_data['messages'], key=lambda m: m.id)
        caption = ""
        media_paths = []

        for msg in messages:
            if msg.text and not caption:
                caption = msg.text
            
            path = await self.download_media(msg)
            if path:
                media_paths.append(path)

        if media_paths:
            await self.callback(caption, media_paths)

    async def process_single_message(self, message):
        caption = message.text or ""
        path = await self.download_media(message)
        if path:
            await self.callback(caption, [path])
        elif caption:
            # Text only post - Instagram requires media, but we'll handle it in the callback
            await self.callback(caption, [])

    async def download_media(self, message):
        if not message.media:
            return None
        
        path = await self.client.download_media(message, file=DOWNLOAD_DIR)
        if path:
            logger.info(f"Downloaded media to: {path}")
            return path
        return None
