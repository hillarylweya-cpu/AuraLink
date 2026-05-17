"""AuraLink Phone App - Mobile-optimized Kivy application."""

import asyncio
import logging
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.popup import Popup
from kivy.clock import Clock
from kivy.core.window import Window

import sys
sys.path.insert(0, '.')

from database.db import init_db, save_message, load_messages
from networking.client import send_message
from messaging.queue import queue_message, get_pending
from messaging.sync import start_sync, stop_sync
from security.encryption import EncryptionManager

# Configure window for mobile
Window.size = (400, 800)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class AuraLinkApp(App):
    """Mobile-optimized AuraLink application."""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.title = 'AuraLink'
        self.encryption_manager = None
        self.sync_task = None
        self.messages = []
    
    def build(self):
        """Build the application UI."""
        logger.info("Building AuraLink Phone App")
        
        # Main layout
        main_layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        
        # Title
        title = Label(
            text='🔗 AuraLink - Communication without barriers',
            size_hint_y=0.1,
            font_size='16sp',
            bold=True
        )
        main_layout.add_widget(title)
        
        # Status bar
        self.status_label = Label(
            text='Status: Initializing...',
            size_hint_y=0.08,
            font_size='12sp'
        )
        main_layout.add_widget(self.status_label)
        
        # Messages display
        scroll_view = ScrollView(size_hint=(1, 0.6))
        self.messages_label = Label(
            text='Messages will appear here...\n',
            size_hint_y=None,
            markup=True,
            font_size='13sp'
        )
        self.messages_label.bind(texture_size=self.messages_label.setter('size'))
        scroll_view.add_widget(self.messages_label)
        main_layout.add_widget(scroll_view)
        
        # Input area
        input_layout = BoxLayout(size_hint_y=0.15, spacing=5)
        
        self.input_box = TextInput(
            hint_text='Type a message...',
            multiline=False,
            size_hint_x=0.75,
            font_size='12sp'
        )
        input_layout.add_widget(self.input_box)
        
        send_btn = Button(
            text='Send',
            size_hint_x=0.25,
            background_color=(0, 0.6, 1, 1)
        )
        send_btn.bind(on_press=self.send_message)
        input_layout.add_widget(send_btn)
        
        main_layout.add_widget(input_layout)
        
        # Menu buttons
        menu_layout = GridLayout(cols=3, size_hint_y=0.07, spacing=5)
        
        sync_btn = Button(text='Sync', background_color=(0, 1, 0, 1))
        sync_btn.bind(on_press=self.sync_now)
        menu_layout.add_widget(sync_btn)
        
        clear_btn = Button(text='Clear', background_color=(1, 0.5, 0, 1))
        clear_btn.bind(on_press=self.clear_messages)
        menu_layout.add_widget(clear_btn)
        
        settings_btn = Button(text='Settings', background_color=(0.5, 0, 1, 1))
        settings_btn.bind(on_press=self.show_settings)
        menu_layout.add_widget(settings_btn)
        
        main_layout.add_widget(menu_layout)
        
        # Initialize app
        Clock.schedule_once(self.init_app, 0.1)
        
        return main_layout
    
    def init_app(self, dt):
        """Initialize app components."""
        try:
            # Initialize database
            asyncio.run(init_db())
            self.update_status('Database: OK')
            logger.info("Database initialized")
            
            # Initialize encryption
            self.encryption_manager = EncryptionManager()
            logger.info("Encryption initialized")
            
            # Load messages
            self.load_message_history()
            
            # Start sync
            asyncio.run(start_sync())
            self.update_status('Connected ✓')
            logger.info("Sync started")
        
        except Exception as e:
            logger.error(f"Init error: {e}")
            self.update_status(f'Error: {str(e)[:30]}')
    
    def load_message_history(self):
        """Load and display message history."""
        try:
            history = asyncio.run(load_messages())
            self.messages = []
            for sender, content, *_ in history:
                msg = f"[b]{sender}:[/b] {content}\n"
                self.messages.append(msg)
            
            self.messages_label.text = ''.join(self.messages) if self.messages else 'No messages yet\n'
            logger.info(f"Loaded {len(self.messages)} messages")
        except Exception as e:
            logger.error(f"Load history error: {e}")
    
    def send_message(self, instance):
        """Send a message."""
        msg = self.input_box.text.strip()
        
        if not msg:
            return
        
        try:
            logger.info(f"Sending: {msg}")
            
            # Display locally
            self.messages.append(f"[b]You:[/b] {msg}\n")
            self.messages_label.text = ''.join(self.messages)
            
            # Save to database
            asyncio.run(save_message("You", "Peer", msg))
            
            # Send
            try:
                asyncio.run(send_message(msg))
                self.update_status('Sent ✓')
            except Exception as e:
                logger.warning(f"Send failed: {e}")
                queue_message(msg, "Peer")
                self.messages.append("[i][color=ff9900][System]: Queued (offline)[/color][/i]\n")
                self.messages_label.text = ''.join(self.messages)
                self.update_status('Queued (offline)')
            
            # Clear input
            self.input_box.text = ""
        
        except Exception as e:
            logger.error(f"Send error: {e}")
            self.messages.append(f"[color=ff0000][Error]: {e}[/color]\n")
            self.messages_label.text = ''.join(self.messages)
    
    def sync_now(self, instance):
        """Sync pending messages now."""
        try:
            pending = get_pending()
            self.update_status(f'Syncing {len(pending)} messages...')
            logger.info("Manual sync triggered")
        except Exception as e:
            logger.error(f"Sync error: {e}")
            self.update_status('Sync failed')
    
    def clear_messages(self, instance):
        """Clear message display."""
        self.messages = []
        self.messages_label.text = 'Messages cleared\n'
        self.update_status('Cleared')
    
    def show_settings(self, instance):
        """Show settings popup."""
        content = BoxLayout(orientation='vertical', padding=10, spacing=10)
        
        content.add_widget(Label(text='[b]AuraLink Settings[/b]', markup=True))
        content.add_widget(Label(text='Version: 1.0.0'))
        content.add_widget(Label(text='Status: Active'))
        
        close_btn = Button(text='Close', size_hint_y=0.3)
        content.add_widget(close_btn)
        
        popup = Popup(
            title='Settings',
            content=content,
            size_hint=(0.8, 0.5)
        )
        close_btn.bind(on_press=popup.dismiss)
        popup.open()
    
    def update_status(self, status):
        """Update status label."""
        self.status_label.text = f'Status: {status}'
    
    def on_stop(self):
        """Clean up on app close."""
        logger.info("Stopping AuraLink")
        try:
            asyncio.run(stop_sync())
        except Exception as e:
            logger.error(f"Cleanup error: {e}")
        return True


if __name__ == '__main__':
    app = AuraLinkApp()
    app.run()
