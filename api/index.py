import asyncio
from http.server import BaseHTTPRequestHandler
from main import pick_and_publish
from aiogram import Bot
from config import BOT_TOKEN

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        # Vercel Serverless function entry point
        # This will be triggered by a Cron Job or a manual GET request
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        bot = Bot(token=BOT_TOKEN)
        try:
            # Run the pick_and_publish logic once
            success = loop.run_until_complete(pick_and_publish(bot))
            
            self.send_response(200)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            
            if success:
                self.wfile.write("Success: New post published.".encode())
            else:
                self.wfile.write("No new posts to publish.".encode())
                
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
