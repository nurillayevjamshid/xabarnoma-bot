import asyncio
import logging
from http.server import BaseHTTPRequestHandler
from main import pick_and_publish
from aiogram import Bot
from config import BOT_TOKEN

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
        ch.setLevel(logging.INFO)
        log.addHandler(ch)
        
        bot = Bot(token=BOT_TOKEN)
        try:
            # Run the pick_and_publish logic once
            success = loop.run_until_complete(pick_and_publish(bot))
            
            self.send_response(200)
            self.send_header('Content-type', 'text/plain; charset=utf-8')
            self.end_headers()
            
            output = log_capture.getvalue()
            if success:
                self.wfile.write(f"Success: New post published.\n\nLogs:\n{output}".encode())
            else:
                self.wfile.write(f"No new posts to publish.\n\nLogs:\n{output}".encode())
                
        except Exception as e:
            self.send_response(500)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            self.wfile.write(f"Error: {str(e)}".encode())
        finally:
            loop.run_until_complete(bot.session.close())
            loop.close()

    def do_POST(self):
        # Optional: Handle webhooks if needed
        self.send_response(200)
        self.end_headers()
        self.wfile.write("OK".encode())
