import asyncio
import logging
from http.server import BaseHTTPRequestHandler
from main import pick_and_publish
from aiogram import Bot
from config import BOT_TOKEN
from dedup import init_db

log = logging.getLogger("xabarnoma")

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        # Vercel Serverless function entry point
        # This will be triggered by a Cron Job or a manual GET request
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        import io
        log_capture = io.StringIO()
        ch = logging.StreamHandler(log_capture)
        ch.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
        log.addHandler(ch)
        
        try:
            init_db()
            bot = Bot(token=BOT_TOKEN)
            
            # Set a timeout for the entire operation (Vercel limit is usually 10s for Hobby)
            async def run_with_timeout():
                try:
                    return await asyncio.wait_for(pick_and_publish(bot), timeout=25)
                except asyncio.TimeoutError:
                    log.error("Operation timed out after 25 seconds")
                    return False

            success = loop.run_until_complete(run_with_timeout())
            
            self.send_response(200)
            self.send_header('Content-type', 'text/plain; charset=utf-8')
            self.end_headers()
            
            output = log_capture.getvalue()
            if success:
                self.wfile.write(f"STATUS: SUCCESS\n\nLOGS:\n{output}".encode())
            else:
                self.wfile.write(f"STATUS: NO_NEW_POSTS_OR_TIMEOUT\n\nLOGS:\n{output}".encode())
                
        except Exception as e:
            self.send_response(500)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            self.wfile.write(f"CRITICAL ERROR: {str(e)}\n\nLOGS:\n{log_capture.getvalue()}".encode())
        finally:
            log.removeHandler(ch)
            loop.run_until_complete(bot.session.close())
            loop.close()

    def do_POST(self):
        # Optional: Handle webhooks if needed
        self.send_response(200)
        self.end_headers()
        self.wfile.write("OK".encode())
