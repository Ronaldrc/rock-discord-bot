import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("/var/log/rock-test-discord-bot.log"),   # FIXME change the pathway to /var/log/rock-discord-bot.log
        logging.StreamHandler()
    ]
)

# Create a logger for use in other modules
def get_logger(module_name):
    return logging.getLogger(module_name)
